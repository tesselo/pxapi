from batch.models import BatchJob


def scan_active_tasks():
    """
    Refresh job status and description until they reach a non-active status.
    """
    active_jobs = BatchJob.objects.exclude(
        status__in=[BatchJob.UNKNOWN, BatchJob.FAILED, BatchJob.FAILED]
    )
    for job in active_jobs:
        job.update()
