class PostIntegrationError(Exception):
    """
    Raised when the SQL commit of an integration succeeded but a post-commit
    housekeeping step (backup or history logging) failed.

    Unlike a plain integration failure, the data is already durably stored in
    the database when this is raised. Callers must not report it as an
    insertion failure, nor allow the user to re-submit the same data.
    """

    def __init__(self, message: str, detection_ids: list[int]):
        super().__init__(message)
        self.detection_ids = detection_ids
