

class LogicError(Exception):
    error = "Logic error"
    error_code = "logic_error"

    def __init__(self, error_code: str = None, error: str = None, detail: dict = None):
        self.error = self.error if error is None else error
        self.error_code = self.error_code if error_code is None else error_code
        self.detail = detail


class ObjectNotFound(LogicError):
    def __init__(self, model: str, identifier=None):
        detail = {"model": model}
        error = f"Not found {model}"
        if identifier is not None:
            detail["identifier"] = identifier
            error += f"({identifier})"

        super().__init__(error_code="not_found", error=error, detail=detail)
