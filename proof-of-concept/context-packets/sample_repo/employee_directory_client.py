"""Client for the internal employee directory service — org chart, manager
lookups, department codes. Used by reporting and org-chart features, not by the
expense submission/approval/notification flow itself.
"""

from http_client import request_with_retry

DIRECTORY_API_BASE_URL = "https://directory.internal.example.com/v1"

_department_cache: dict[str, str] = {}


def get_manager_id(employee_id: str) -> str | None:
    response = request_with_retry("GET", f"{DIRECTORY_API_BASE_URL}/employees/{employee_id}")
    return response.json().get("manager_id")


def get_department_code(employee_id: str) -> str:
    if employee_id in _department_cache:
        return _department_cache[employee_id]
    response = request_with_retry("GET", f"{DIRECTORY_API_BASE_URL}/employees/{employee_id}")
    department_code = response.json().get("department_code", "UNKNOWN")
    _department_cache[employee_id] = department_code
    return department_code


def get_org_chart(root_employee_id: str, max_depth: int = 3) -> dict:
    """Builds a nested org-chart dict rooted at the given employee, used by the
    (separate) org-chart reporting UI. Not used by expense approval at all.
    """
    response = request_with_retry(
        "GET", f"{DIRECTORY_API_BASE_URL}/employees/{root_employee_id}/reports", params={"depth": max_depth}
    )
    return response.json()
