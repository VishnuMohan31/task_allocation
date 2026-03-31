from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.config import settings
from core.logging import get_logger
from models.error import ErrorResponse
from utils.exceptions import StoreCorruptedError, TaskAlreadyCompletedError, TaskNotFoundError

logger = get_logger("app.error_handlers")


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            exc_info=(type(exc), exc, exc.__traceback__),
            extra={"method": request.method, "path": request.url.path},
        )
        body = ErrorResponse(
            error_code=settings.error_code_internal,
            message=settings.error_msg_internal,
            details={},
        )
        return JSONResponse(status_code=500, content=body.model_dump())

    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
        logger.warning(
            "task_not_found",
            extra={"task_id": exc.task_id, "path": request.url.path},
        )
        body = ErrorResponse(
            error_code=settings.error_code_not_found,
            message=str(exc),
            details={},
        )
        return JSONResponse(status_code=404, content=body.model_dump())

    @app.exception_handler(TaskAlreadyCompletedError)
    async def task_already_completed_handler(request: Request, exc: TaskAlreadyCompletedError) -> JSONResponse:
        logger.warning(
            "task_already_completed",
            extra={"task_id": exc.task_id, "path": request.url.path},
        )
        body = ErrorResponse(
            error_code=settings.error_code_task_already_completed,
            message=str(exc),
            details={},
        )
        return JSONResponse(status_code=409, content=body.model_dump())

    @app.exception_handler(StoreCorruptedError)
    async def store_corrupted_handler(request: Request, exc: StoreCorruptedError) -> JSONResponse:
        logger.error(
            "store_corrupted",
            exc_info=(type(exc), exc, exc.__traceback__),
            extra={"path": request.url.path},
        )
        body = ErrorResponse(
            error_code=settings.error_code_store_corrupted,
            message=str(exc),
            details={},
        )
        return JSONResponse(status_code=500, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(
            "validation_error",
            extra={"path": request.url.path, "errors": str(exc.errors())},
        )
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
