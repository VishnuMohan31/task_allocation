from models.error import ErrorResponse


def test_error_response_valid_construction():
    err = ErrorResponse(error_code="TASK_NOT_FOUND", message="Task abc-123 not found")
    assert err.error_code == "TASK_NOT_FOUND"
    assert err.message == "Task abc-123 not found"
    assert err.details == {}


def test_error_response_default_details_is_empty_dict():
    err = ErrorResponse(error_code="INTERNAL_ERROR", message="Unexpected error")
    assert isinstance(err.details, dict)
    assert err.details == {}


def test_error_response_with_explicit_details():
    err = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Invalid input",
        details={"field": "priority", "issue": "must be between 1 and 5"},
    )
    assert err.details == {"field": "priority", "issue": "must be between 1 and 5"}
