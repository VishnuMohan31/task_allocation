from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.config import settings
from models.error import ErrorResponse
from utils.exceptions import StoreCorruptedError, TaskAlreadyCompletedError, TaskNotFoundError


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        body = ErrorResponse(
            error_code=settings.error_code_internal,
            message=settings.error_msg_internal,
            details={},
        )
        return JSONResponse(status_code=500, content=body.model_dump())

    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
        body = ErrorResponse(
            error_code=settings.error_code_not_found,
            message=str(exc),
            details={},
        )
        return JSONResponse(status_code=404, content=body.model_dump())

    @app.exception_handler(TaskAlreadyCompletedError)
    async def task_already_completed_handler(request: Request, exc: TaskAlreadyCompletedError) -> JSONResponse:
        body = ErrorResponse(
            error_code=settings.error_code_task_already_completed,
            message=str(exc),
            details={},
        )
        return JSONResponse(status_code=409, content=body.model_dump())

    @app.exception_handler(StoreCorruptedError)
    async def store_corrupted_handler(request: Request, exc: StoreCorruptedError) -> JSONResponse:
        body = ErrorResponse(
            error_code=settings.error_code_store_corrupted,
            message=str(exc),
            details={},
        )
        return JSONResponse(status_code=500, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        safe_errors = []
        for err in exc.errors():
            safe_err = {}
            for k, v in err.items():
                if k == "ctx" and isinstance(v, dict):
                    safe_err[k] = {ck: str(cv) for ck, cv in v.items()}
                else:
                    safe_err[k] = v
            safe_errors.append(safe_err)
        body = ErrorResponse(
            error_code=settings.error_code_validation,
            message=settings.error_msg_validation,
            details={"errors": safe_errors},
        )
        return JSONResponse(status_code=422, content=body.model_dump())
