import datetime

import boto3
from django.conf import settings


def push(funk, *args, array_size=None, cpu=2, gpu=False, depends_on=None):
    """
    Push batch job.

    High level utility to push batch jobs. Allows running any module,
    specifying instance types, and job dependencies.

    Parameters
    ----------
    funk: str
        The module path to the function that shall be ran. For example,
        pixels.stac.parse_training_data.
    args: positional input arguments, optional
        Positional arguments that will be passed to "funk".
    array_size: int, optional
        Array size for the given input job. If this is not None, the batch job
        will be sent as array job, otherwise as regular batch job.
    cpu: int, optional
        Number of CPUs that are required for the job. Memory is automatically
        determined from the number of CPUs. This is ignored if gpu is True.
    gpu: boolean, optional
        Determines if the job shall be executed in a GPU enabled instance or
        not. If true, 1 GPU instance will be ran with 8 CPU cores and 32 GB of
        memory.
    depends_on: list of job IDs, optional
        A list of batch job IDs from which the new job depends. If specified,
        the new job will only be executed if the dependencies were successful.
    """
    job_queue = "fetch-and-run-queue-gpu" if gpu else "fetch-and-run-queue"
    # Create job dict, inserting job name and command to execute. The retry
    # strategy ensures that jobs that are terminated due to spot instance
    # reclaims are automatically restarted up to five times.
    # Ref: https://aws.amazon.com/blogs/compute/introducing-retry-strategies-for-aws-batch/
    job = {
        "jobName": "{}-{}".format(
            funk.replace(".", "-"),
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        ),
        "jobQueue": job_queue,
        "jobDefinition": "first-run-job-definition",
        "containerOverrides": {
            "command": ["runpixels.py", funk, *args],
        },
        "retryStrategy": {
            "attempts": 5,
            "evaluateOnExit": [
                {"onStatusReason": "Host EC2*", "action": "RETRY"},
                {"onReason": "*", "action": "EXIT"},
            ],
        },
    }

    # Set array size if desired.
    if array_size:
        job["arrayProperties"] = {"size": array_size}

    # Choose size of instances through resource requirements.
    if gpu:
        # For GPU at the moment fix one specific size.
        job["containerOverrides"].update(
            {
                "resourceRequirements": [
                    {
                        "type": "GPU",
                        "value": "1",
                    },
                    {
                        "type": "MEMORY",
                        "value": str(int(1024 * 15.25)),
                    },
                    {
                        "type": "VCPU",
                        "value": "4",
                    },
                ],
            }
        )
    else:
        # Without GPU, use multiples of 1 CPU with 1024 MB of memory. This is
        # the step size of EC2 instances.
        job["containerOverrides"].update(
            {
                "resourceRequirements": [
                    {
                        "type": "MEMORY",
                        "value": str(1024 * cpu),
                    },
                    {
                        "type": "VCPU",
                        "value": str(cpu),
                    },
                ],
            }
        )
    # Set job dependency.
    if depends_on is not None:
        job["dependsOn"] = [{"jobId": dependency} for dependency in depends_on]
    # Push job to batch.
    batch = boto3.client("batch", region_name=settings.AWS_REGION)
    return batch.submit_job(**job)
