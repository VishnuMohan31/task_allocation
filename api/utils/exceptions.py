from core.config import settings


class TaskNotFoundError(Exception):
    error_code = settings.error_code_not_found
    http_status = 404

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(settings.exc_task_not_found_template.format(task_id=task_id))


class StoreCorruptedError(Exception):
    error_code = settings.error_code_store_corrupted
    http_status = 500

    def __init__(self, message: str = "") -> None:
        super().__init__(message or settings.error_msg_store_corrupted)


class TaskAlreadyCompletedError(Exception):
    error_code = settings.error_code_task_already_completed
    http_status = 409

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(settings.exc_task_already_completed_template.format(task_id=task_id))
