class PixelsJobIsRunningException(Exception):
    """
    Raise error if a user tries to change a model that has a running job.

    This prevents having job data and object data out of sync.
    """

    msg = "Background job is not finished."

    def __init__(self, msg=msg, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class PixelsJobDoesNotExistException(Exception):
    pass
