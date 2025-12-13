from .assign_position_to_worker import AssignPositionToWorker
from .assign_worker_to_department import AssignWorkerToDepartment
from .complete_onboarding_process import CompleteOnboardingProcess
from .compute_exit_settlement import ComputeExitSettlement
from .create_employee_benefit_enrollment import CreateEmployeeBenefitEnrollment
from .create_employment_contract import CreateEmploymentContract
from .create_new_checklist import CreateNewChecklist
from .create_worker import CreateWorker
from .disable_user_account import DisableUserAccount
from .edit_payroll_deduction import EditPayrollDeduction
from .fetch_benefit_plans import FetchBenefitPlans
from .generate_payslip import GeneratePayslip
from .get_active_department import GetActiveDepartment
from .get_deduction_data import GetDeductionData
from .get_exit_case import GetExitCase
from .get_onboarding_checklist import GetOnboardingChecklist
from .get_payment_details import GetPaymentDetails
from .get_payroll_data import GetPayrollData
from .get_payroll_input import GetPayrollInput
from .get_worker import GetWorker
from .initiate_worker_termination import InitiateWorkerTermination
from .manage_payroll_earning import ManagePayrollEarning
from .open_payroll_period import OpenPayrollPeriod
from .preview_payslip import PreviewPayslip
from .process_benefit_plan import ProcessBenefitPlan
from .process_payroll_cycle import ProcessPayrollCycle
from .process_payroll_input import ProcessPayrollInput
from .process_payroll_payment import ProcessPayrollPayment
from .produce_payroll_deduction import ProducePayrollDeduction
from .release_payslip import ReleasePayslip
from .switch_to_human import SwitchToHuman
from .terminate_employment_contract import TerminateEmploymentContract
from .update_checklist_data import UpdateChecklistData
from .update_payroll_payment import UpdatePayrollPayment
from .update_worker_info import UpdateWorkerInfo
from .upload_worker_document import UploadWorkerDocument
from .verify_worker_document import VerifyWorkerDocument

ALL_TOOLS_INTERFACE_2 = [
    AssignPositionToWorker,
    AssignWorkerToDepartment,
    CompleteOnboardingProcess,
    ComputeExitSettlement,
    CreateEmployeeBenefitEnrollment,
    CreateEmploymentContract,
    CreateNewChecklist,
    CreateWorker,
    DisableUserAccount,
    EditPayrollDeduction,
    FetchBenefitPlans,
    GeneratePayslip,
    GetActiveDepartment,
    GetDeductionData,
    GetExitCase,
    GetOnboardingChecklist,
    GetPaymentDetails,
    GetPayrollData,
    GetPayrollInput,
    GetWorker,
    InitiateWorkerTermination,
    ManagePayrollEarning,
    OpenPayrollPeriod,
    PreviewPayslip,
    ProcessBenefitPlan,
    ProcessPayrollCycle,
    ProcessPayrollInput,
    ProcessPayrollPayment,
    ProducePayrollDeduction,
    ReleasePayslip,
    SwitchToHuman,
    TerminateEmploymentContract,
    UpdateChecklistData,
    UpdatePayrollPayment,
    UpdateWorkerInfo,
    UploadWorkerDocument,
    VerifyWorkerDocument
]
