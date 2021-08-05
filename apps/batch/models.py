import datetime
import uuid

import boto3
from batch import const
from django.conf import settings
from django.db import models


class BatchJob(models.Model):
    UNKNOWN = "UNKNOWN"
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    RUNNABLE = "RUNNABLE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    STATUS_CHOICES = (
        (UNKNOWN, UNKNOWN),
        (SUBMITTED, SUBMITTED),
        (PENDING, PENDING),
        (RUNNABLE, RUNNABLE),
        (STARTING, STARTING),
        (RUNNING, RUNNING),
        (SUCCEEDED, SUCCEEDED),
        (FAILED, FAILED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_id = models.CharField(max_length=500, blank=True, default="")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=UNKNOWN)

    description = models.JSONField(default=dict, blank=True)
    log_stream_name = models.CharField(max_length=1500, default="", blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return "{} | {}".format(self.job_id, self.status)

    def update(self):
        # Only attempt update if region was specified.
        if not hasattr(settings, "AWS_REGION"):
            return
        # Only attempt update if job id exists.
        if not self.job_id:
            return
        # Instantiate batch client.
        batch = boto3.client("batch", region_name=settings.AWS_REGION)
        # Retrieve job descriptions.
        desc = batch.describe_jobs(jobs=[self.job_id])
        if not len(desc["jobs"]):
            self.status = self.UNKNOWN
        else:
            # Get job description of first job result.
            job = desc["jobs"][0]
            # Remove container environment, as it may contain secret keys.
            if "container" in job and "environment" in job["container"]:
                del job["container"]["environment"]
            # Store description and status.
            self.description = job
            self.status = job["status"]
            # Get log stream name of last attempt (there might be multiple attempts.)
            if "container" in job and "logStreamName" in job["container"]:
                # This is the case during running state.
                self.log_stream_name = job["container"]["logStreamName"]
            elif len(job["attempts"]):
                # This is the case after completion.
                self.log_stream_name = job["attempts"][0]["container"]["logStreamName"]
            else:
                self.log_stream_name = ""
        self.save()

    def get_log(self, limit=500):
        if not self.log_stream_name:
            return {"error": "Log stream name is not specified for this job."}
        client = boto3.client("logs", region_name=settings.AWS_REGION)
        try:
            log_data = client.get_log_events(
                logGroupName=const.LOG_GROUP_NAME,
                logStreamName=self.log_stream_name,
                limit=limit,
            )
        except client.exceptions.ResourceNotFoundException:
            return {"error": "Log stream does not yet exist. Wait for job to start."}

        return [
            "{} | {}".format(
                datetime.datetime.fromtimestamp(dat["timestamp"] / 1000), dat["message"]
            )
            for dat in log_data["events"]
        ]
