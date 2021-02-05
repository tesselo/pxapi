import datetime

import boto3


def push(funk, *args, array_size=None, cpu=2, gpu=False):
    """
    Push batch job.
    """
    # Create job dict, inserting job name and command to execute.
    job = {
        "jobName": "{}-{}".format(
            funk.replace(".", "-"),
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        ),
        "jobQueue": "fetch-and-run-queue",
        "jobDefinition": "first-run-job-definition",
        "containerOverrides": {
            "command": ["runpixels.py", funk, *args],
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
                "vcpus": 8,
                "memory": int(1024 * 30.5),
                "resourceRequirements": [
                    {
                        "type": "GPU",
                        "value": "1",
                    }
                ],
            }
        )
    else:
        # Without GPU, use multiples of 1 CPU with 1024 MB of memory. This is
        # the step size of EC2 instances.
        job["containerOverrides"].update(
            {
                "vcpus": cpu,
                "memory": 1024 * cpu,
            }
        )

    # Push job to batch.
    batch = boto3.client("batch", region_name="eu-central-1")
    return batch.submit_job(**job)
