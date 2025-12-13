import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CalculateSettlement(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: Optional[str] = None, email: Optional[str] = None, cycle_id: Optional[str] = None) -> str:
        """
        Calculate financial settlement for an employee based on payroll cycle, assets, and existing settlements.
        
        Args:
            data: Environment data containing employees, payroll data, assets, and settlements
            employee_id: The employee identifier (optional)
            email: The employee email address (optional)
            cycle_id: The payroll cycle identifier (required for settlement calculation)
            
        Note: At least one of employee_id or email must be provided, and cycle_id is required
        """
        timestamp = "2025-11-22T12:00:00"
        
        # Get all necessary data
        employees = data.get("employees", {})
        employee_assets = data.get("employee_assets", {})
        finance_settlements = data.get("finance_settlements", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payroll_inputs = data.get("payroll_inputs", {})
        payroll_earnings = data.get("payroll_earnings", {})
        deductions = data.get("deductions", {})
        exit_cases = data.get("exit_cases", {})
        
        # Validate required parameters
        if not employee_id and not email:
            return json.dumps({
                "success": False,
                "error": "At least one identifier (employee_id or email) must be provided"
            })
        
        if not cycle_id:
            return json.dumps({
                "success": False,
                "error": "Halt: cycle_id is required for settlement calculation"
            })
        
        # Find employee by email if employee_id not provided
        if employee_id is None and email is not None:
            found = False
            for emp_id, emp_data in employees.items():
                if emp_data.get("email") == email:
                    employee_id = emp_id
                    found = True
                    break
            if not found:
                return json.dumps({
                    "success": False,
                    "error": f"Halt: Employee with email not found"
                })
        
        # Validate that employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"Halt: Employee not found"
            })
        
        # Get employee details
        employee = employees[employee_id]
        
        # Verify email matches if both provided
        if email is not None and employee.get("email") != email:
            return json.dumps({
                "success": False,
                "error": f"Halt: Email does not match employee record"
            })
        
        # Validate payroll cycle exists
        if cycle_id not in payroll_cycles:
            return json.dumps({
                "success": False,
                "error": f"Halt: Payroll cycle not found"
            })
        
        payroll_cycle = payroll_cycles[cycle_id]
        
        # Validate exit case exists and is cleared (SOP 189 requirement)
        exit_case = None
        for exit_id, exit_data in exit_cases.items():
            if exit_data.get("employee_id") == employee_id:
                exit_case = exit_data
                break
        
        if not exit_case:
            return json.dumps({
                "success": False,
                "error": f"Halt: Exit case not found for employee"
            })
        
        if exit_case.get("exit_clearance_status") != "cleared":
            return json.dumps({
                "success": False,
                "error": f"Halt: Exit clearance status must be 'cleared' before settlement calculation"
            })
        
        # Get base salary
        base_salary = float(employee.get("base_salary", 0))
        
        # Calculate payroll inputs (hours worked, overtime, allowances)
        hours_worked = 0.0
        overtime_hours = 0.0
        allowance_amount = 0.0
        
        for input_id, payroll_input in payroll_inputs.items():
            if (payroll_input.get("employee_id") == employee_id and 
                payroll_input.get("cycle_id") == cycle_id):
                hours_worked += float(payroll_input.get("hours_worked", 0))
                overtime_hours += float(payroll_input.get("overtime_hours", 0))
                allowance_amount += float(payroll_input.get("allowance_amount", 0))
        
        # Calculate approved earnings (bonus, incentive, allowance, overtime)
        total_earnings = 0.0
        earnings_breakdown = {
            "bonus": 0.0,
            "incentive": 0.0,
            "allowance": 0.0,
            "overtime": 0.0
        }
        earnings_list = []
        
        for earning_id, earning in payroll_earnings.items():
            if (earning.get("employee_id") == employee_id and 
                earning.get("cycle_id") == cycle_id and
                earning.get("status") == "approved"):
                amount = float(earning.get("amount", 0))
                earning_type = earning.get("earning_type")
                total_earnings += amount
                if earning_type in earnings_breakdown:
                    earnings_breakdown[earning_type] += amount
                earnings_list.append({
                    "earning_id": earning_id,
                    "type": earning_type,
                    "amount": amount
                })
        
        # Calculate valid deductions
        total_deductions = 0.0
        deductions_list = []
        
        for deduction_id, deduction in deductions.items():
            if (deduction.get("employee_id") == employee_id and
                deduction.get("status") == "valid"):
                amount = float(deduction.get("amount", 0))
                total_deductions += amount
                deductions_list.append({
                    "deduction_id": deduction_id,
                    "amount": amount,
                    "date": deduction.get("deduction_date")
                })
        
        # Calculate asset-related charges
        asset_charges = 0.0
        missing_assets = []
        damaged_assets = []
        
        for asset_id, asset in employee_assets.items():
            if asset.get("employee_id") == employee_id:
                asset_status = asset.get("status")
                asset_name = asset.get("item_name")
                
                if asset_status == "missing":
                    # Standard replacement cost per missing item
                    charge = 500.0
                    asset_charges += charge
                    missing_assets.append({
                        "asset_id": asset_id,
                        "name": asset_name,
                        "charge": charge
                    })
                elif asset_status == "damaged":
                    # Standard repair cost per damaged item
                    charge = 250.0
                    asset_charges += charge
                    damaged_assets.append({
                        "asset_id": asset_id,
                        "name": asset_name,
                        "charge": charge
                    })
        
        # Calculate final settlement
        gross_pay = base_salary + total_earnings + allowance_amount
        total_charges = total_deductions + asset_charges
        net_settlement = gross_pay - total_charges
        
        # Determine payment direction
        if net_settlement > 0:
            payment_direction = "to_employee"
            payment_description = "Company owes employee"
        elif net_settlement < 0:
            payment_direction = "from_employee"
            payment_description = "Employee owes company"
        else:
            payment_direction = "balanced"
            payment_description = "No payment required"
        
        # Generate new settlement ID
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        new_settlement_id = generate_id(finance_settlements)
        
        # Create new settlement entry in finance_settlements
        new_settlement = {
            "settlement_id": new_settlement_id,
            "employee_id": employee_id,
            "amount": net_settlement,  # Store actual value (positive or negative)
            "is_cleared": False,  # Initially not cleared
            "created_at": timestamp,
            "last_updated": timestamp
        }
        
        # Add to finance_settlements in data
        finance_settlements[new_settlement_id] = new_settlement
        
        # Prepare comprehensive settlement breakdown
        settlement_calculation = {
            "success": True,
            "employee_id": employee_id,
            "employee_name": employee.get("full_name"),
            "employee_email": employee.get("email"),
            "cycle_id": cycle_id,
            "cycle_period": {
                "start_date": payroll_cycle.get("start_date"),
                "end_date": payroll_cycle.get("end_date"),
                "frequency": payroll_cycle.get("frequency")
            },
            "exit_date": exit_case.get("exit_date"),
            "exit_reason": exit_case.get("reason"),
            "calculation_breakdown": {
                "gross_pay_components": {
                    "base_salary": base_salary,
                    "earnings": {
                        "total": total_earnings,
                        "breakdown": earnings_breakdown,
                        "details": earnings_list
                    },
                    "allowances": allowance_amount,
                    "total_gross_pay": gross_pay
                },
                "deductions_and_charges": {
                    "payroll_deductions": {
                        "total": total_deductions,
                        "details": deductions_list
                    },
                    "asset_charges": {
                        "total": asset_charges,
                        "missing_assets": {
                            "count": len(missing_assets),
                            "items": missing_assets,
                            "subtotal": len(missing_assets) * 500.0
                        },
                        "damaged_assets": {
                            "count": len(damaged_assets),
                            "items": damaged_assets,
                            "subtotal": len(damaged_assets) * 250.0
                        }
                    },
                    "total_charges": total_charges
                },
                "payroll_inputs": {
                    "hours_worked": hours_worked,
                    "overtime_hours": overtime_hours,
                    "allowance_amount": allowance_amount
                }
            },
            "net_settlement_amount": net_settlement,
            "payment_direction": payment_direction,
            "payment_description": payment_description,
            "requires_payment": abs(net_settlement) > 0,
            "calculated_at": timestamp,
            "new_settlement_record": {
                "settlement_id": new_settlement_id,
                "created": True
            }
        }
        
        return json.dumps(settlement_calculation)
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "calculate_settlement",
                "description": "Calculate comprehensive financial settlement for an employee during offboarding. This tool computes the total settlement amount by: (1) Calculating gross pay from base salary, approved earnings (bonus, incentive, allowance, overtime), and allowances for the specified payroll cycle; (2) Subtracting all valid deductions and asset-related charges ($500 per missing item, $250 per damaged item); (3) Determining net settlement amount and payment direction; (4) Creating a new finance_settlement record. Requires exit clearance status to be 'cleared'. Returns detailed breakdown of all components.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee identifier (optional if email is provided, must exist in system)"
                        },
                        "email": {
                            "type": "string",
                            "description": "Employee email address (optional if employee_id is provided, must exist in system)"
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Payroll cycle identifier for settlement calculation (required)"
                        }
                    },
                    "required": ["cycle_id"]
                }
            }
        }