import logging

from batch.models import BatchJob

logger = logging.getLogger(__name__)


def scan_active_tasks():
    """
    Refresh job status and description.

    Active jobs are jobs that do not have an unknown state, or that have
    finished (successfully or not). The job status is updated regularly until
    the job reaches a non-active status.
    """
    active_jobs = BatchJob.objects.exclude(
        status__in=[BatchJob.UNKNOWN, BatchJob.SUCCEEDED, BatchJob.FAILED]
    )
    logger.info("Updating active jobs. Found {}.".format(active_jobs.count()))
    for job in active_jobs:
        job.update()
