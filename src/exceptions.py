class EnvironmentConfigError(RuntimeError):
    """Raised when required environment variables are missing or invalid"""
    def __init__(self, missing_vars: list[str]):
        self.missing_vars = missing_vars
        message = f"Missing required environment variables: {', '.join(missing_vars)}"
        super().__init__(message)
