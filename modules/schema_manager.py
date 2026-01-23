import os
import json
import zipfile
import tempfile
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
import mysql.connector
from mysql.connector import Error

schema_manager_bp = Blueprint('schema_manager', __name__)

# Configuration
DATABASES_DIR = "databases"
SCHEMAS_DIR = "schemas"

# Ensure directories exist
os.makedirs(DATABASES_DIR, exist_ok=True)
os.makedirs(SCHEMAS_DIR, exist_ok=True)


def validate_db_name(db_name):
    """
    Validate database name to prevent path traversal and SQL injection.
    Returns True if valid, False otherwise.
    """
    if not db_name or not isinstance(db_name, str):
        return False
    # Only allow alphanumeric characters and underscores
    if not db_name.replace('_', '').isalnum():
        return False
    # Prevent excessively long names
    if len(db_name) > 64:
        return False
    return True


def safe_extract_zip(zip_path, extract_dir):
    """
    Safely extract a zip file, preventing zip slip attacks (path traversal).
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            # Get the absolute path of where the file would be extracted
            member_path = os.path.abspath(os.path.join(extract_dir, member))
            extract_dir_abs = os.path.abspath(extract_dir)

            # Ensure the path is within the extract directory
            if not member_path.startswith(extract_dir_abs + os.sep) and member_path != extract_dir_abs:
                raise ValueError(f"Attempted path traversal in zip file: {member}")

            # Extract the member
            zip_ref.extract(member, extract_dir)


class SchemaConverter:
    """Converts JSON schema to MySQL Tables"""
    
    TYPE_MAPPING = {
        'string': 'VARCHAR(255)',
        'int': 'INT',
        'bigint': 'BIGINT',
        'boolean': 'BOOLEAN',
        'text': 'TEXT',
        'timestamp': 'TIMESTAMP',
        'date': 'DATE',
        'varchar': 'VARCHAR',
        'enum': 'ENUM'
    }
    
    @staticmethod
    def parse_dbml_type(dbml_type):
        """Parse DBML type notation to MySQL type"""
        dbml_type = dbml_type.strip()
        
        # Handle varchar with length
        if dbml_type.startswith('varchar('):
            return dbml_type.upper()
        
        # Handle enum types
        if dbml_type.startswith('enum('):
            # Extract enum values and convert to MySQL format
            enum_values = dbml_type[5:-1]  # Remove 'enum(' and ')'
            return f'ENUM({enum_values})'
        
        # Handle basic types
        base_type = dbml_type.split('(')[0].lower()
        return SchemaConverter.TYPE_MAPPING.get(base_type, 'VARCHAR(255)')
    
    @staticmethod
    def parse_schema_file(schema_content):
        """Parse DBML-like schema content to extract tables and columns"""
        tables = {}
        current_table = None
        current_column_lines = []
        in_multiline_enum = False
        
        lines = schema_content.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect table definition
            if line_stripped.startswith('Table '):
                table_name = line_stripped.split()[1].replace('{', '').strip()
                current_table = table_name
                tables[current_table] = {
                    'columns': [],
                    'primary_key': None
                }
                continue
            
            # End of table
            if line_stripped == '}' and current_table and not in_multiline_enum:
                current_table = None
                continue
            
            # Skip comments and references
            if line_stripped.startswith('//') or line_stripped.startswith('Ref:') or line_stripped.startswith('Note:'):
                continue
            
            if not current_table:
                continue
            
            # Check if we're starting a multi-line enum
            if 'enum(' in line_stripped and ')' not in line_stripped:
                in_multiline_enum = True
                current_column_lines = [line_stripped]
                continue
            
            # Continue collecting multi-line enum
            if in_multiline_enum:
                current_column_lines.append(line_stripped)
                if ')' in line_stripped:
                    in_multiline_enum = False
                    # Join all lines and process
                    full_line = ' '.join(current_column_lines)
                    SchemaConverter._parse_column_line(full_line, tables[current_table])
                    current_column_lines = []
                continue
            
            # Regular column line
            if line_stripped and any(keyword in line_stripped for keyword in 
                                    ['[primary key]', 'varchar', 'int', 'text', 'timestamp', 
                                    'boolean', 'enum', 'bigint', 'date', 'string']):
                SchemaConverter._parse_column_line(line_stripped, tables[current_table])
        
        return tables

    @staticmethod
    def _parse_column_line(line, table_def):
        """Parse a single column definition line"""
        parts = line.split()
        if len(parts) < 2:
            return
        
        col_name = parts[0]
        
        # Find the type - it might span multiple parts for enum
        if 'enum(' in line:
            # Extract everything from 'enum(' to the closing ')'
            enum_start = line.index('enum(')
            enum_end = line.index(')', enum_start) + 1
            col_type = line[enum_start:enum_end]
        else:
            col_type = parts[1]
        
        # Check for constraints
        is_primary = '[primary key]' in line
        not_null = '[not null]' in line or is_primary
        unique = '[unique]' in line or is_primary
        default_value = None
        
        # Extract default value
        if '[default:' in line:
            default_start = line.index('[default:') + 9
            default_end = line.index(']', default_start)
            default_value = line[default_start:default_end].strip().strip('`').strip("'").strip('"')
        
        mysql_type = SchemaConverter.parse_dbml_type(col_type)
        
        column_def = {
            'name': col_name,
            'type': mysql_type,
            'not_null': not_null,
            'unique': unique,
            'default': default_value
        }
        
        table_def['columns'].append(column_def)
        
        if is_primary:
            table_def['primary_key'] = col_name
    
    @staticmethod
    def generate_create_table_sql(table_name, table_def):
        """Generate CREATE TABLE SQL statement"""
        columns = []
        primary_key_col = table_def.get('primary_key')
        
        for col in table_def['columns']:
            col_sql = f"`{col['name']}` {col['type']}"
            
            # Add AUTO_INCREMENT for integer primary keys
            if col['name'] == primary_key_col and col['type'] in ['INT', 'BIGINT']:
                col_sql += " AUTO_INCREMENT"
            
            if col['not_null']:
                col_sql += " NOT NULL"
            
            # Handle default values properly
            if col['default'] is not None:
                default_val = col['default']
                
                if default_val.upper() == 'NOW()':
                    col_sql += " DEFAULT CURRENT_TIMESTAMP"
                elif default_val.lower() in ['true', 'false']:
                    col_sql += f" DEFAULT {default_val.upper()}"
                elif col['type'] in ['INT', 'BIGINT'] and default_val.isdigit():
                    # Numeric defaults don't need quotes
                    col_sql += f" DEFAULT {default_val}"
                elif col['type'].startswith('ENUM'):
                    # Enum defaults need single quotes
                    col_sql += f" DEFAULT '{default_val}'"
                elif col['type'].startswith('VARCHAR') or col['type'] == 'TEXT':
                    # String defaults need single quotes
                    col_sql += f" DEFAULT '{default_val}'"
                else:
                    # For other types, quote the value to be safe
                    col_sql += f" DEFAULT '{default_val}'"
            
            if col['unique'] and col['name'] != primary_key_col:
                col_sql += " UNIQUE"
            
            columns.append(col_sql)
        
        # Add primary key constraint
        if primary_key_col:
            columns.append(f"PRIMARY KEY (`{primary_key_col}`)")
        
        sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  "
        sql += ",\n  ".join(columns)
        sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        
        return sql


class DatabaseManager:
    """Manages MySQL database connections and operations"""
    
    def __init__(self, db_config):
        self.config = db_config
    
    def connect(self):
        """Create database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def create_database(self, db_name):
        """Create a new database"""
        connection = self.connect()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating database: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def execute_sql(self, db_name, sql_statements):
        """Execute multiple SQL statements"""
        config = self.config.copy()
        config['database'] = db_name
        
        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            
            for i, sql in enumerate(sql_statements):
                if sql.strip():
                    try:
                        # print(f"\n=== Executing SQL {i+1} ===")
                        # print(sql[:500])  # Print first 500 chars
                        cursor.execute(sql)
                    except Error as e:
                        # print(f"\n!!! ERROR in statement {i+1} !!!")
                        # print(f"Full SQL:\n{sql}")
                        # print(f"Error: {e}")
                        raise
            
            connection.commit()
            return True, "Success"
        except Error as e:
            return False, str(e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def query(self, db_name, query):
        """Execute a SELECT query"""
        config = self.config.copy()
        config['database'] = db_name
        
        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return True, results
        except Error as e:
            return False, str(e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def insert_json_data(self, db_name, table_name, json_data):
        """Insert JSON data into a table"""
        config = self.config.copy()
        config['database'] = db_name
        
        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            
            # Handle different JSON structures
            records = []
            
            if isinstance(json_data, list):
                # Already a list of records
                records = json_data
            elif isinstance(json_data, dict):
                # Check if it's a dict of records (with numeric/string keys)
                # or a single record
                first_key = next(iter(json_data.keys())) if json_data else None
                first_value = json_data.get(first_key) if first_key else None
                
                # If the first value is a dict with column-like keys, 
                # assume it's a dict of records
                if isinstance(first_value, dict):
                    # Extract all the nested records
                    records = list(json_data.values())
                    # print(f"Detected dict-of-dicts structure, extracted {len(records)} records")
                else:
                    # It's a single record
                    records = [json_data]
            else:
                return False, "Invalid JSON format"
            
            if not records:
                return True, "No records to insert"
            
            # print(f"Processing {len(records)} records for table {table_name}")
            # print(f"Sample record keys: {list(records[0].keys())}")
            
            # Get table columns from database
            cursor.execute(f"DESCRIBE `{table_name}`")
            table_columns = {row[0] for row in cursor.fetchall()}
            
            # print(f"Table columns: {table_columns}")
            
            # Get columns that exist in both data and table
            data_columns = set(records[0].keys())
            valid_columns = list(data_columns.intersection(table_columns))
            
            # print(f"Data columns: {data_columns}")
            # print(f"Valid matching columns: {valid_columns}")
            
            if not valid_columns:
                return False, f"No matching columns found between data and table {table_name}"
            
            # Prepare INSERT statement
            placeholders = ', '.join(['%s'] * len(valid_columns))
            column_names = ', '.join([f'`{col}`' for col in valid_columns])
            insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"
            
            # Insert each record
            inserted = 0
            failed = 0
            
            for record in records:
                try:
                    # Convert values, handling nested objects
                    values = []
                    for col in valid_columns:
                        val = record.get(col)
                        
                        # Convert dict/list to JSON string
                        if isinstance(val, (dict, list)):
                            values.append(json.dumps(val))
                        # Handle None/null
                        elif val is None:
                            values.append(None)
                        # Handle boolean
                        elif isinstance(val, bool):
                            values.append(val)
                        # Everything else as-is
                        else:
                            values.append(val)
                    
                    cursor.execute(insert_sql, values)
                    inserted += 1
                except Error as e:
                    failed += 1
                    print(f"Warning: Failed to insert record {inserted + failed} into {table_name}: {e}")
                    if failed == 1:  # Print first failure for debugging
                        print(f"Failed record: {record}")
                    # Continue with next record instead of failing completely
                    continue
            
            connection.commit()
            
            message = f"Inserted {inserted} records"
            if failed > 0:
                message += f" ({failed} failed)"
            
            return True, message
            
        except Error as e:
            import traceback
            print(f"Database error: {e}")
            print(traceback.format_exc())
            return False, str(e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


def get_db_config():
    """Get database configuration from environment or defaults"""
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }


@schema_manager_bp.route('/schema_manager', methods=['GET'])
def schema_manager():
    """Render the schema manager page"""
    return render_template('schema_manager.html')


@schema_manager_bp.route('/schema_manager/list_databases', methods=['GET'])
def list_databases():
    """List all managed databases"""
    db_list = []
    
    if os.path.exists(DATABASES_DIR):
        for filename in os.listdir(DATABASES_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(DATABASES_DIR, filename)
                with open(filepath, 'r') as f:
                    db_info = json.load(f)
                    db_list.append(db_info)
    
    return jsonify({
        'status': 'success',
        'databases': db_list
    })


@schema_manager_bp.route('/schema_manager/upload_schema', methods=['POST'])
def upload_schema():
    """Upload and process a schema zip file"""
    if 'zipFile' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
    
    zip_file = request.files['zipFile']
    db_name = request.form.get('dbName', '').strip()
    
    if not db_name:
        return jsonify({'status': 'error', 'message': 'Database name is required'}), 400
    
    # Validate database name
    if not db_name.replace('_', '').isalnum():
        return jsonify({'status': 'error', 'message': 'Invalid database name. Use only letters, numbers, and underscores'}), 400
    
    # Check if database already exists and delete it
    try:
        db_manager = DatabaseManager(get_db_config())
        if db_manager.database_exists(db_name):
            print(f"\n⚠ Database '{db_name}' already exists. Deleting it first...")
            success = db_manager.delete_database(db_name)
            if success:
                print(f"✓ Existing database '{db_name}' deleted successfully")
                
                # Also remove metadata files
                db_info_path = os.path.join(DATABASES_DIR, f'{db_name}.json')
                schema_path = os.path.join(SCHEMAS_DIR, f'{db_name}.sql')
                
                if os.path.exists(db_info_path):
                    os.remove(db_info_path)
                if os.path.exists(schema_path):
                    os.remove(schema_path)
            else:
                return jsonify({'status': 'error', 'message': f'Failed to delete existing database "{db_name}"'}), 500
    except Exception as e:
        print(f"Warning: Error checking for existing database: {e}")
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'upload.zip')
            zip_file.save(zip_path)
            
            # Extract zip safely to prevent zip slip attacks
            safe_extract_zip(zip_path, temp_dir)
            
            # Find schema file and data files
            schema_file = None
            data_files = []
            
            print("\n=== Scanning extracted files ===")
            for root, dirs, files in os.walk(temp_dir):
                print(f"Directory: {root}")
                print(f"Files: {files}")
                
                for file in files:
                    full_path = os.path.join(root, file)
                    
                    # Find schema file
                    if file.endswith('.dbml') or (file.endswith('.txt') and 'schema' in file.lower()):
                        schema_file = full_path
                        print(f"✓ Found schema file: {file}")
                    
                    # Find JSON data files
                    elif file.endswith('.json'):
                        # Check if it's in a 'data' folder or just any JSON file
                        if 'data' in root.lower() or root == temp_dir:
                            data_files.append(full_path)
                            print(f"✓ Found data file: {file}")
            
            print(f"\nTotal data files found: {len(data_files)}")
            print(f"Data files: {[os.path.basename(f) for f in data_files]}")
            
            if not schema_file:
                return jsonify({'status': 'error', 'message': 'No schema file found in zip'}), 400
            
            # Read schema
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            
            # Parse schema
            tables = SchemaConverter.parse_schema_file(schema_content)
            
            if not tables:
                return jsonify({'status': 'error', 'message': 'No tables found in schema'}), 400
            
            print(f"\nTables from schema: {list(tables.keys())}")
            
            # Generate SQL
            create_statements = []
            for table_name, table_def in tables.items():
                sql = SchemaConverter.generate_create_table_sql(table_name, table_def)
                create_statements.append(sql)
            
            # Create database
            db_manager = DatabaseManager(get_db_config())
            
            if not db_manager.create_database(db_name):
                return jsonify({'status': 'error', 'message': 'Failed to create database'}), 500
            
            # Execute CREATE TABLE statements
            success, message = db_manager.execute_sql(db_name, create_statements)
            
            if not success:
                return jsonify({'status': 'error', 'message': f'Failed to create tables: {message}'}), 500
            
            # Insert data from JSON files
            inserted_count = 0
            failed_count = 0
            
            print("\n=== Inserting data ===")
            for data_file in data_files:
                # Get table name from filename (without .json)
                table_name = os.path.basename(data_file).replace('.json', '')
                
                print(f"\nProcessing: {os.path.basename(data_file)}")
                print(f"Table name: {table_name}")
                
                # Check if table exists in schema
                if table_name not in tables:
                    print(f"⚠ Table '{table_name}' not found in schema. Skipping.")
                    print(f"Available tables: {list(tables.keys())}")
                    failed_count += 1
                    continue
                
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    print(f"Loaded {len(json_data) if isinstance(json_data, list) else 1} records")
                    
                    success, msg = db_manager.insert_json_data(db_name, table_name, json_data)
                    if success:
                        inserted_count += 1
                        print(f"✓ {msg}")
                    else:
                        failed_count += 1
                        print(f"✗ Failed: {msg}")
                        
                except Exception as e:
                    failed_count += 1
                    print(f"✗ Error loading {data_file}: {e}")
            
            print(f"\n=== Summary ===")
            print(f"Tables created: {len(tables)}")
            print(f"Data files processed: {inserted_count}/{len(data_files)}")
            print(f"Failed: {failed_count}")
            
            # Save database info
            db_info = {
                'name': db_name,
                'created_at': datetime.now().isoformat(),
                'tables': list(tables.keys()),
                'table_count': len(tables),
                'data_files_loaded': inserted_count,
                'data_files_failed': failed_count
            }
            
            db_info_path = os.path.join(DATABASES_DIR, f'{db_name}.json')
            with open(db_info_path, 'w') as f:
                json.dump(db_info, f, indent=2)
            
            # Save schema
            schema_path = os.path.join(SCHEMAS_DIR, f'{db_name}.sql')
            with open(schema_path, 'w') as f:
                f.write('\n\n'.join(create_statements))
            
            return jsonify({
                'status': 'success',
                'message': f'Database "{db_name}" created successfully with {inserted_count} data files loaded',
                'database': db_info
            })
    
    except Exception as e:
        import traceback
        # print(traceback.format_exc())
        return jsonify({'status': 'error', 'message': f'Error processing schema: {str(e)}'}), 500

@schema_manager_bp.route('/schema_manager/query', methods=['POST'])
def query_database():
    """Execute a query on a database"""
    data = request.get_json()
    db_name = data.get('dbName')
    query = data.get('query', '').strip()

    if not db_name or not query:
        return jsonify({'status': 'error', 'message': 'Database name and query are required'}), 400

    # Validate database name to prevent injection attacks
    if not validate_db_name(db_name):
        return jsonify({'status': 'error', 'message': 'Invalid database name'}), 400
    
    # Basic SQL injection prevention
    if not query.upper().startswith('SELECT'):
        return jsonify({'status': 'error', 'message': 'Only SELECT queries are allowed'}), 400
    
    db_manager = DatabaseManager(get_db_config())
    success, result = db_manager.query(db_name, query)
    
    if success:
        return jsonify({
            'status': 'success',
            'results': result,
            'count': len(result)
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Query failed: {result}'
        }), 400


@schema_manager_bp.route('/schema_manager/delete_database', methods=['POST'])
def delete_database():
    """Delete a database"""
    data = request.get_json()
    db_name = data.get('dbName')

    if not db_name:
        return jsonify({'status': 'error', 'message': 'Database name is required'}), 400

    # Validate database name to prevent injection and path traversal attacks
    if not validate_db_name(db_name):
        return jsonify({'status': 'error', 'message': 'Invalid database name'}), 400
    
    try:
        # Drop database
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
        connection.commit()
        cursor.close()
        connection.close()
        
        # Remove metadata files
        db_info_path = os.path.join(DATABASES_DIR, f'{db_name}.json')
        schema_path = os.path.join(SCHEMAS_DIR, f'{db_name}.sql')
        
        if os.path.exists(db_info_path):
            os.remove(db_info_path)
        if os.path.exists(schema_path):
            os.remove(schema_path)
        
        return jsonify({
            'status': 'success',
            'message': f'Database "{db_name}" deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete database: {str(e)}'
        }), 500