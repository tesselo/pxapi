from rest_framework.exceptions import APIException


class UpdateBeforeFinishedExeption(APIException):
    status_code = 403
    default_detail = "Updates are not allowed until batch jobs have finished."
    default_code = "no_updates_until_finished"
