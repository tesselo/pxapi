import os
import uuid

from batch import jobs
from batch.const import BATCH_JOB_ID_KEY
from batch.models import BatchJob
from django.db import models


class NamedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250, help_text="Short name of the object.")
    description = models.TextField(
        default="", blank=True, help_text="Detailed description of the object."
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


def training_data_zip_upload_to(instance, filename):
    return f"trainingdata/{instance.pk}/{filename}"


class TrainingData(NamedModel):
    zipfile = models.FileField(
        upload_to=training_data_zip_upload_to,
        help_text="A zip file containing the training data.",
    )
    batchjob_parse = models.ForeignKey(
        BatchJob, blank=True, null=True, editable=False, on_delete=models.PROTECT
    )

    TRAINING_DATA_PARSE_FUNCTION = "pixels.stac.parse_training_data"

    def save(self, *args, **kwargs):
        # Pre-create batch job.
        if not self.batchjob_parse:
            self.batchjob_parse = BatchJob.objects.create()
        # Save object data.
        super().save(*args, **kwargs)
        # Construct S3 uri for the zipfile.
        bucket = os.environ.get("AWS_STORAGE_BUCKET_NAME_MEDIA", None)
        # If bucket was specified, run job.
        if bucket:
            # Get S3 uri for zipfile.
            uri = "s3://{}/{}".format(bucket, self.zipfile.name)
            # Push job.
            job = jobs.push(TRAINING_DATA_PARSE_FUNCTION, uri)
            # Register job id and submitted state.
            self.batchjob_parse.job_id = job[BATCH_JOB_ID_KEY]
            self.batchjob_parse.status = BatchJob.SUBMITTED
            self.batchjob_parse.save()


def pixels_data_json_upload_to(instance, filename):
    return f"pixelsdata/{instance.pk}/config.json"


class PixelsData(NamedModel):
    config = models.JSONField(default=dict)
    trainingdata = models.ForeignKey(TrainingData, on_delete=models.PROTECT)
    config_file = models.FileField(
        upload_to=pixels_data_json_upload_to, null=True, editable=False
    )


def keras_model_json_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/model.json"


def keras_model_h5_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/model.h5"


class KerasModel(NamedModel):
    definition = models.JSONField(default=dict, blank=True)
    model_h5 = models.FileField(
        upload_to=keras_model_h5_upload_to, null=True, editable=False
    )
    model_json = models.FileField(
        upload_to=keras_model_json_upload_to, null=True, editable=False
    )
