#!/usr/bin/env python3
"""
SOP-Based Scenario Counter

This script analyzes an SOP (Standard Operating Procedure) to:
1. Identify which tables are referenced by the SOP's tools
2. Build a dependency graph based on FK->PK relationships
3. Load seeded JSON data for those tables
4. Count the number of valid leaf nodes (complete scenarios) that can be executed

Usage:
    python sop_scenario_counter.py \
        --schema schema.txt \
        --sop sop.md \
        --data-dir ./seeded_data \
        --sop-name "SOP 1"
"""

import argparse
import json
import os
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Any


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class FKRelationship:
    """Foreign Key relationship: child_table.fk_column -> parent_table.pk_column"""
    child_table: str
    child_fk_column: str
    parent_table: str
    parent_pk_column: str


@dataclass
class SchemaInfo:
    tables: Set[str]
    pk_by_table: Dict[str, Set[str]]
    fk_relationships: List[FKRelationship]


# -----------------------------
# Schema Parsing
# -----------------------------

_TABLE_BLOCK_RE = re.compile(
    r"Table\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{(?P<body>.*?)\}",
    re.DOTALL,
)

_COL_LINE_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_()'\",\s-]*)\s*(\[[^\]]*\])?\s*$"
)

_REF_RE = re.compile(
    r"Ref:\s*([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*>\s*([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)"
)


def parse_schema(schema_text: str) -> SchemaInfo:
    """Parse DBML-like schema to extract tables, PKs, and FK relationships"""
    tables: Set[str] = set()
    pk_by_table: Dict[str, Set[str]] = {}
    fk_relationships: List[FKRelationship] = []

    # Parse table blocks for PKs
    for m in _TABLE_BLOCK_RE.finditer(schema_text):
        table = m.group(1)
        tables.add(table)
        body = m.group("body") or ""
        pk_by_table.setdefault(table, set())

        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            colm = _COL_LINE_RE.match(line)
            if not colm:
                continue
            col_name = colm.group(1)
            bracket = colm.group(3) or ""
            if "primary key" in bracket.lower():
                pk_by_table[table].add(col_name)

    # Parse FK references
    for rm in _REF_RE.finditer(schema_text):
        child_table, child_fk = rm.group(1), rm.group(2)
        parent_table, parent_pk = rm.group(3), rm.group(4)
        
        fk_relationships.append(FKRelationship(
            child_table=child_table,
            child_fk_column=child_fk,
            parent_table=parent_table,
            parent_pk_column=parent_pk
        ))
        
        tables.add(child_table)
        tables.add(parent_table)
        pk_by_table.setdefault(child_table, set())
        pk_by_table.setdefault(parent_table, set())

    return SchemaInfo(
        tables=tables,
        pk_by_table=pk_by_table,
        fk_relationships=fk_relationships
    )


# -----------------------------
# SOP Analysis
# -----------------------------

def extract_tools_from_sop(sop_text: str) -> Set[str]:
    """Extract tool names from SOP text - only 'using tool_name' pattern"""
    tools = set()
    
    # Look for "using tool_name" pattern where tool_name contains underscore
    # This filters out English words like "using their"
    using_pattern = re.compile(r'using\s+([a-z_][a-z0-9_]*_[a-z0-9_]*)')
    for match in using_pattern.finditer(sop_text):
        tools.add(match.group(1))
    
    return tools


def extract_tables_from_sop(sop_text: str, known_tables: Set[str]) -> Set[str]:
    """Extract table names explicitly mentioned in SOP"""
    mentioned_tables = set()
    
    # Look for table names in the text
    words = re.findall(r'\b[a-z_][a-z0-9_]*\b', sop_text.lower())
    
    for word in words:
        if word in known_tables:
            mentioned_tables.add(word)
    
    return mentioned_tables


# -----------------------------
# Tool-to-Table Mapping
# -----------------------------

TOOL_TABLE_MAP = {
    'list_users': {'users'},
    'list_access_tokens': {'access_tokens'},
    'list_organizations': {'organizations'},
    'list_org_members': {'organization_members'},
    'list_repositories': {'repositories'},
    'get_repository_permissions': {'repository_collaborators', 'organization_members', 'repositories'},
    'upsert_repository': {'repositories'},
    'update_repository_permissions': {'repository_collaborators'},
    'create_organization': {'organizations', 'organization_members'},
    'invite_org_member': {'organization_members'},
    'remove_org_member': {'organization_members'},
    'fork_repository': {'repositories', 'branches', 'commits', 'directories', 'files', 'file_contents'},
    'create_branch': {'branches'},
    'erase_branch': {'branches'},
    'list_branches': {'branches'},
    'upsert_file_directory': {'files', 'directories', 'commits', 'file_contents'},
    'delete_file': {'files', 'commits'},
    'list_files_directories': {'files', 'directories'},
    'create_pull_request': {'pull_requests'},
    'update_pull_request': {'pull_requests'},
    'list_pull_requests': {'pull_requests'},
    'upsert_comment': {'comments'},
    'submit_pr_review': {'pull_request_reviews'},
    'list_labels': {'labels'},
    'upsert_label': {'labels'},
    'create_workflow': {'workflows'},
    'update_workflow': {'workflows'},
    'delete_workflow': {'workflows'},
    'list_workflows': {'workflows'},
    'upsert_release': {'releases'},
    'delete_release': {'releases'},
    'list_releases': {'releases'},
    'star_unstar_repo': {'stars'},
    'list_stars': {'stars'},
    'update_issues': {'issues'},
    'delete_issue': {'issues'},
    'search_issues': {'issues'},
    'list_comments': {'comments'},
    'delete_comment': {'comments'},
}


def get_tables_from_tools(tools: Set[str]) -> Set[str]:
    """Map tools to their associated tables"""
    tables = set()
    for tool in tools:
        if tool in TOOL_TABLE_MAP:
            tables.update(TOOL_TABLE_MAP[tool])
    return tables


# -----------------------------
# Data Loading
# -----------------------------

def load_seeded_data(data_dir: str, tables: Set[str]) -> Dict[str, Dict[str, Any]]:
    """Load JSON data for specified tables"""
    data = {}
    
    for table in tables:
        json_path = os.path.join(data_dir, f"{table}.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data[table] = json.load(f)
        else:
            print(f"Warning: No data file found for table '{table}' at {json_path}")
            data[table] = {}
    
    return data


# -----------------------------
# Graph Building and Analysis
# -----------------------------

def build_dependency_graph(schema: SchemaInfo, relevant_tables: Set[str]) -> Dict[str, Set[str]]:
    """
    Build parent -> children dependency graph
    Only includes tables in relevant_tables
    """
    graph = defaultdict(set)
    
    for fk in schema.fk_relationships:
        if fk.parent_table in relevant_tables and fk.child_table in relevant_tables:
            graph[fk.parent_table].add(fk.child_table)
    
    # Ensure all relevant tables are in the graph
    for table in relevant_tables:
        if table not in graph:
            graph[table] = set()
    
    return dict(graph)


def find_leaf_tables(graph: Dict[str, Set[str]]) -> Set[str]:
    """Find tables with no children (leaf nodes)"""
    all_tables = set(graph.keys())
    tables_with_children = {table for table, children in graph.items() if children}
    return all_tables - tables_with_children


def count_valid_scenarios(
    data: Dict[str, Dict[str, Any]],
    schema: SchemaInfo,
    leaf_tables: Set[str]
) -> Dict[str, int]:
    """
    Count valid end-to-end scenarios by tracing complete FK chains
    from root tables to leaf tables
    """
    scenario_counts = {}
    
    for leaf_table in leaf_tables:
        if leaf_table not in data:
            scenario_counts[leaf_table] = 0
            continue
        
        valid_count = 0
        table_data = data[leaf_table]
        
        for record_id, record in table_data.items():
            # Trace the complete chain from this leaf back to roots
            if has_complete_chain_to_root(record, leaf_table, data, schema, visited=set()):
                valid_count += 1
        
        scenario_counts[leaf_table] = valid_count
    
    return scenario_counts


def has_complete_chain_to_root(
    record: Dict[str, Any],
    table_name: str,
    data: Dict[str, Dict[str, Any]],
    schema: SchemaInfo,
    visited: Set[Tuple[str, str]]
) -> bool:
    """
    Recursively check if a record has valid FK chains to all parent tables
    until we reach root tables (tables with no parent FKs)
    
    Returns True if all parent chains are valid
    """
    # Get current record identifier
    pk_cols = schema.pk_by_table.get(table_name, set())
    if pk_cols:
        pk_col = list(pk_cols)[0]  # Use first PK
        record_key = (table_name, str(record.get(pk_col, '')))
    else:
        record_key = (table_name, str(id(record)))  # Fallback
    
    # Avoid infinite loops (circular references)
    if record_key in visited:
        return True
    visited = visited | {record_key}
    
    # Find all FK relationships where this table is the child
    parent_fks = [
        fk for fk in schema.fk_relationships
        if fk.child_table == table_name
    ]
    
    # If no parent FKs, this is a root table - chain is complete
    if not parent_fks:
        return True
    
    # Check each parent FK relationship
    for fk in parent_fks:
        fk_value = record.get(fk.child_fk_column)
        
        # If FK is null, check if it's required
        # For now, treat null as valid (nullable FK)
        if fk_value is None:
            continue
        
        # Check if parent table exists in data
        if fk.parent_table not in data:
            return False
        
        # Find the parent record
        parent_table_data = data[fk.parent_table]
        parent_record = None
        
        for parent_rec in parent_table_data.values():
            if parent_rec.get(fk.parent_pk_column) == fk_value:
                parent_record = parent_rec
                break
        
        # Parent record must exist
        if parent_record is None:
            return False
        
        # Recursively check if parent has complete chain
        if not has_complete_chain_to_root(
            parent_record,
            fk.parent_table,
            data,
            schema,
            visited
        ):
            return False
    
    # All parent chains are valid
    return True


# -----------------------------
# Main
# -----------------------------

def main():
    parser = argparse.ArgumentParser(description="Count SOP scenarios from seeded data")
    parser.add_argument("--schema", required=True, help="Path to schema file")
    parser.add_argument("--sop", required=True, help="Path to SOP file")
    parser.add_argument("--data-dir", required=True, help="Directory containing seeded JSON files")
    parser.add_argument("--sop-name", default="SOP", help="Name of SOP for output")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--tools", nargs="+", help="Manually specify tool names (space-separated)")
    
    args = parser.parse_args()
    
    # Redirect output if specified
    output_file = None
    if args.output:
        output_file = open(args.output, 'w', encoding='utf-8')
        import sys
        sys.stdout = output_file
    
    try:
        # Load schema
        print(f"Loading schema from {args.schema}...")
        with open(args.schema, 'r', encoding='utf-8') as f:
            schema_text = f.read()
        schema = parse_schema(schema_text)
        
        # Load SOP
        print(f"Loading SOP from {args.sop}...")
        with open(args.sop, 'r', encoding='utf-8') as f:
            sop_text = f.read()
        
        # Extract tools and tables from SOP
        print(f"Analyzing {args.sop_name}...")
        
        # Use manually specified tools if provided, otherwise extract from SOP
        if args.tools:
            tools = set(args.tools)
            print(f"Using manually specified tools: {sorted(tools)}")
        else:
            tools = extract_tools_from_sop(sop_text)
        
        tables_from_tools = get_tables_from_tools(tools)
        
        # Only extract mentioned tables if no tools were manually specified
        if args.tools:
            tables_mentioned = set()  # Don't extract table names when tools are manual
        else:
            tables_mentioned = extract_tables_from_sop(sop_text, schema.tables)
        
        relevant_tables = tables_from_tools | tables_mentioned
        
        if args.verbose:
            print(f"\nTools identified: {sorted(tools)}")
            print(f"Tables from tools: {sorted(tables_from_tools)}")
            print(f"Tables mentioned: {sorted(tables_mentioned)}")
            print(f"All relevant tables: {sorted(relevant_tables)}")
        
        # Build dependency graph
        print(f"\nBuilding dependency graph...")
        graph = build_dependency_graph(schema, relevant_tables)
        leaf_tables = find_leaf_tables(graph)
        
        if args.verbose:
            print(f"\nDependency graph:")
            for parent, children in sorted(graph.items()):
                if children:
                    print(f"  {parent} -> {sorted(children)}")
            print(f"\nLeaf tables: {sorted(leaf_tables)}")
        
        # Load seeded data
        print(f"\nLoading seeded data from {args.data_dir}...")
        data = load_seeded_data(args.data_dir, relevant_tables)
        
        # Count scenarios
        print(f"\nCounting valid scenarios...")
        scenario_counts = count_valid_scenarios(data, schema, leaf_tables)
        
        # Output results
        print(f"\n{'='*60}")
        print(f"SCENARIO COUNT FOR {args.sop_name}")
        print(f"{'='*60}")
        
        total_scenarios = 0
        for table, count in sorted(scenario_counts.items()):
            print(f"{table}: {count} valid scenarios")
            total_scenarios += count
        
        print(f"\n{'='*60}")
        print(f"TOTAL DISTINCT SCENARIOS: {total_scenarios}")
        print(f"{'='*60}")
        
        # Output detailed breakdown
        if args.verbose:
            print(f"\nDetailed Breakdown:")
            for table in sorted(leaf_tables):
                print(f"\n{table}:")
                if table not in data:
                    print("  No data loaded")
                    continue
                
                table_data = data[table]
                print(f"  Total records: {len(table_data)}")
                print(f"  Valid records: {scenario_counts.get(table, 0)}")
    
    finally:
        if output_file:
            output_file.close()
            import sys
            sys.stdout = sys.__stdout__


if __name__ == "__main__":
    main()