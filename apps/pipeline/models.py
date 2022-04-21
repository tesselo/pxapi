import json
import math
import uuid

import structlog
from batch import jobs
from batch.const import BATCH_JOB_ID_KEY
from batch.models import BatchJob
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from pipeline import const
from pixels.generator.stac_utils import get_catalog_length
from pixels.utils import load_dictionary

logger = structlog.getLogger(__name__)


class NamedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250, help_text="Short name of the object.")
    description = models.TextField(
        default="", blank=True, help_text="Detailed description of the object."
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created"]

    def __str__(self):
        return self.name


def training_data_zip_upload_to(instance, filename):
    return f"trainingdata/{instance.pk}/{filename}"


class TrainingData(NamedModel):
    zipfile = models.FileField(
        upload_to=training_data_zip_upload_to,
        help_text="A zip file containing the training data.",
    )
    categorical = models.BooleanField(
        default=True,
        help_text="Determines if the training data is categorical or continuous.",
    )
    reference_date = models.DateField(
        null=True,
        blank=True,
        help_text="Set a reference date for all input tiles. Will be used by the stac parser.",
    )
    batchjob_parse = models.ForeignKey(
        BatchJob,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
        help_text="Background job that creates a STAC catalog from the input data.",
    )

    def save(self, *args, **kwargs):
        # Pre-create batch job.
        if not self.batchjob_parse:
            self.batchjob_parse = BatchJob.objects.create()
        # Save object data.
        super().save(*args, **kwargs)
        # If media bucket was specified, run job.
        if hasattr(settings, "AWS_S3_BUCKET_NAME"):
            # Get S3 uri for zipfile and other parse variables.
            uri = "s3://{}/{}".format(settings.AWS_S3_BUCKET_NAME, self.zipfile.name)
            logger.debug(f"The zipfile uri is {uri}.")
            save_files = "True"
            description = self.name
            if self.reference_date:
                reference_date = str(self.reference_date)
            else:
                reference_date = None
            # Push job.
            job = jobs.push(
                const.TRAINING_DATA_PARSE_FUNCTION,
                uri,
                str(self.categorical),
                save_files,
                description,
                reference_date,
            )
            # Register job id and submitted state.
            self.batchjob_parse.job_id = job[BATCH_JOB_ID_KEY]
            self.batchjob_parse.status = BatchJob.SUBMITTED
            self.batchjob_parse.save()

    @property
    def catalog_uri(self):
        return f"s3://{settings.AWS_S3_BUCKET_NAME}/trainingdata/{self.id}/{const.TRAINING_DATA_CATALOG_LOCATION}"


def pixels_data_json_upload_to(instance, filename):
    return f"pixelsdata/{instance.pk}/{const.CONFIG_FILE_NAME}"


class PixelsData(NamedModel):
    config = models.JSONField(default=dict)
    trainingdata = models.ForeignKey(TrainingData, on_delete=models.PROTECT)
    config_file = models.FileField(
        upload_to=pixels_data_json_upload_to, null=True, editable=False
    )
    batchjob_collect_pixels = models.ForeignKey(
        BatchJob,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="pixels_data_collect",
    )
    batchjob_create_catalog = models.ForeignKey(
        BatchJob,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="pixels_data_catalog",
    )

    @property
    def collection_uri(self):
        return f"s3://{settings.AWS_S3_BUCKET_NAME}/pixelsdata/{self.pk}/{const.PIXELS_DATA_COLLECTION_LOCATION}"

    @property
    def catalogs_dict_uri(self):
        return f"s3://{settings.AWS_S3_BUCKET_NAME}/pixelsdata/{self.pk}/{const.PIXELS_DATA_CATALOGS_DICT_LOCATION}"

    def save(self, *args, **kwargs):
        # Save a copy of the config data as file for the DB independent batch
        # processing.
        self.config_file = ContentFile(
            json.dumps(self.config), name=const.CONFIG_FILE_NAME
        )
        # Pre-create batch jobs.
        if not self.batchjob_collect_pixels:
            self.batchjob_collect_pixels = BatchJob.objects.create()
        if not self.batchjob_create_catalog:
            self.batchjob_create_catalog = BatchJob.objects.create()
        super().save(*args, **kwargs)

        # If media bucket was specified, run job.
        if hasattr(settings, "AWS_S3_BUCKET_NAME"):
            # Get S3 uri for pixels config file.
            config_uri = "s3://{}/{}".format(
                settings.AWS_S3_BUCKET_NAME, self.config_file.name
            )
            logger.debug(f"The config uri is {config_uri}.")
            # Get S3 uri for Y catalog file.
            logger.debug(f"The catalog uri is {self.trainingdata.catalog_uri}.")
            # TODO: Make sure the catalog exists, i.e. that the previous job
            # has finished. This currently leads to a server error.
            # Count number of items in the catalog.
            number_of_items = get_catalog_length(self.trainingdata.catalog_uri)
            # TODO: Item per job definition.
            # Set number of jobs based on catolog length, with maximun ceiling.
            max_number_jobs = 250
            item_per_job = 10
            number_of_jobs = math.ceil(number_of_items / item_per_job)
            if number_of_jobs > max_number_jobs:
                number_of_jobs = max_number_jobs
                item_per_job = math.ceil(number_of_items / number_of_jobs)
            # Prevent array mode if only one job is necessary. By setting the
            # the value to None, one single job is triggered without the array
            # capability.
            if number_of_jobs == 1:
                number_of_jobs = None
                item_per_job = number_of_items
            # Compute number of items per job and convert to string because all
            # batch config arguments are required to be str.
            # Push collection job.
            collect_job = jobs.push(
                const.COLLECT_PIXELS_FUNCTION,
                self.trainingdata.catalog_uri,
                config_uri,
                str(item_per_job),
                array_size=number_of_jobs,
            )
            # Register collection job id and submitted state.
            self.batchjob_collect_pixels.job_id = collect_job[BATCH_JOB_ID_KEY]
            self.batchjob_collect_pixels.status = BatchJob.SUBMITTED
            self.batchjob_collect_pixels.save()
            # Construct catalog base url from config url by stripping the config
            # file name from the config uri.
            new_catalog_uri = config_uri.rstrip(const.CONFIG_FILE_NAME)
            logger.debug(f"The new catalog uri is {new_catalog_uri}.")
            # Get zip file path to pass to collection.
            source_path = "s3://{}/{}".format(
                settings.AWS_S3_BUCKET_NAME, self.trainingdata.zipfile.name
            )
            # Push cataloging job, with the collection job as dependency.
            catalog_job = jobs.push(
                const.CREATE_CATALOG_FUNCTION,
                new_catalog_uri,
                source_path,
                depends_on=[collect_job[BATCH_JOB_ID_KEY]],
            )
            # Register parse job id and submitted state.
            self.batchjob_create_catalog.job_id = catalog_job[BATCH_JOB_ID_KEY]
            self.batchjob_create_catalog.status = BatchJob.SUBMITTED
            self.batchjob_create_catalog.save()


def model_configuration_file_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/{const.MODEL_CONFIGURATION_FILE_NAME}"


def model_compile_arguments_file_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/{const.MODEL_COMPILE_ARGUMENTS_FILE_NAME}"


def model_fit_arguments_file_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/{const.MODEL_FIT_ARGUMENTS_FILE_NAME}"


def generator_arguments_file_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/{const.GENERATOR_ARGUMENTS_FILE_NAME}"


class KerasModel(NamedModel):
    """
    Train and save keras models.
    """

    pixelsdata = models.ForeignKey(PixelsData, on_delete=models.PROTECT)

    model_configuration = models.JSONField(default=dict, blank=True)
    model_configuration_file = models.FileField(
        upload_to=model_configuration_file_upload_to, null=True, editable=False
    )
    model_compile_arguments = models.JSONField(default=dict, blank=True)
    model_compile_arguments_file = models.FileField(
        upload_to=model_compile_arguments_file_upload_to, null=True, editable=False
    )
    model_fit_arguments = models.JSONField(default=dict, blank=True)
    model_fit_arguments_file = models.FileField(
        upload_to=model_fit_arguments_file_upload_to, null=True, editable=False
    )
    generator_arguments = models.JSONField(default=dict, blank=True)
    generator_arguments_file = models.FileField(
        upload_to=generator_arguments_file_upload_to, null=True, editable=False
    )

    batchjob_train = models.ForeignKey(
        BatchJob,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
    )

    @property
    def model_uri(self):
        """
        S3 uri of stored model in h5 format.
        """
        return f"s3://{settings.AWS_S3_BUCKET_NAME}/kerasmodel/{self.pk}/{const.MODEL_H5_FILE_NAME}"

    def save(self, *args, **kwargs):
        # Save a copy of the model definition as file for the DB independent
        # batch processing.
        self.model_configuration_file = ContentFile(
            json.dumps(self.model_configuration),
            name=const.MODEL_CONFIGURATION_FILE_NAME,
        )
        self.model_compile_arguments_file = ContentFile(
            json.dumps(self.model_compile_arguments),
            name=const.MODEL_COMPILE_ARGUMENTS_FILE_NAME,
        )
        self.model_fit_arguments_file = ContentFile(
            json.dumps(self.model_fit_arguments),
            name=const.MODEL_FIT_ARGUMENTS_FILE_NAME,
        )
        self.generator_arguments_file = ContentFile(
            json.dumps(self.generator_arguments),
            name=const.GENERATOR_ARGUMENTS_FILE_NAME,
        )
        # Pre-create batch jobs.
        if not self.batchjob_train:
            self.batchjob_train = BatchJob.objects.create()
        super().save(*args, **kwargs)
        # If media bucket was specified, run job.
        if hasattr(settings, "AWS_S3_BUCKET_NAME"):
            # Get model definition uris.
            model_config_uri = "s3://{}/{}".format(
                settings.AWS_S3_BUCKET_NAME, self.model_configuration_file.name
            )
            model_compile_arguments_uri = "s3://{}/{}".format(
                settings.AWS_S3_BUCKET_NAME, self.model_compile_arguments_file.name
            )
            model_fit_arguments_uri = "s3://{}/{}".format(
                settings.AWS_S3_BUCKET_NAME, self.model_fit_arguments_file.name
            )
            generator_arguments_uri = "s3://{}/{}".format(
                settings.AWS_S3_BUCKET_NAME, self.generator_arguments_file.name
            )
            # Push cataloging job, with the collection job as dependency.
            train_job = jobs.push(
                const.TRAIN_MODEL_FUNCTION,
                self.pixelsdata.collection_uri,
                model_config_uri,
                model_compile_arguments_uri,
                model_fit_arguments_uri,
                generator_arguments_uri,
                gpu=True,
            )
            # Register job id and submitted state.
            self.batchjob_train.job_id = train_job[BATCH_JOB_ID_KEY]
            self.batchjob_train.status = BatchJob.SUBMITTED
            self.batchjob_train.save()


def training_generator_arguments_file_upload_to(instance, filename):
    return f"prediction/{instance.pk}/{const.PREDICTION_GENERATOR_ARGUMENTS_FILE_NAME}"


class Prediction(NamedModel):
    pixelsdata = models.ForeignKey(PixelsData, on_delete=models.PROTECT)
    kerasmodel = models.ForeignKey(KerasModel, on_delete=models.PROTECT)
    generator_arguments = models.JSONField(default=dict, blank=True)
    generator_arguments_file = models.FileField(
        upload_to=training_generator_arguments_file_upload_to, null=True, editable=False
    )
    batchjob_predict = models.ForeignKey(
        BatchJob,
        blank=True,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
    )

    @property
    def generator_arguments_uri(self):
        """
        The S3 uri pointing to the generator arguments file.
        """
        return f"s3://{settings.AWS_S3_BUCKET_NAME}/prediction/{self.pk}/{const.PREDICTION_GENERATOR_ARGUMENTS_FILE_NAME}"

    def save(self, *args, **kwargs):
        # Save a copy of the config data as file for the DB independent batch
        # processing.
        self.generator_arguments_file = ContentFile(
            json.dumps(self.generator_arguments),
            name=const.PREDICTION_GENERATOR_ARGUMENTS_FILE_NAME,
        )
        # Pre-create batch jobs.
        if not self.batchjob_predict:
            self.batchjob_predict = BatchJob.objects.create()

        super().save(*args, **kwargs)

        # If media bucket was specified, run job.
        if hasattr(settings, "AWS_S3_BUCKET_NAME"):
            # Log uris in debug mode.
            logger.debug(
                f"The generator arguments uri is {self.generator_arguments_uri}."
            )
            logger.debug(f"The collection uri is {self.pixelsdata.collection_uri}.")
            logger.debug(
                f"The catalogs_dict uri is {self.pixelsdata.catalogs_dict_uri}."
            )
            # TODO: Make sure the catalog exists, i.e. that the previous job
            # has finished. This currently leads to a server error.
            # Count number of items in the catalog.
            number_of_items = len(load_dictionary(self.pixelsdata.catalogs_dict_uri))
            # TODO: Item per job definition.
            # Set number of jobs based on catolog length, with maximun ceiling.
            max_number_jobs = 1000
            item_per_job = 10
            number_of_jobs = math.ceil(number_of_items / item_per_job)
            if number_of_jobs > max_number_jobs:
                number_of_jobs = max_number_jobs
                item_per_job = math.ceil(number_of_items / number_of_jobs)
            # Prevent array mode if only one job is necessary. By setting the
            # the value to None, one single job is triggered without the array
            # capability.
            if number_of_jobs == 1:
                number_of_jobs = None
                item_per_job = number_of_items
            # Compute number of items per job and convert to string because all
            # batch config arguments are required to be str.
            # Push prediction job.
            predict_job = jobs.push(
                const.PREDICTION_FUNCTION,
                self.kerasmodel.model_uri,
                self.pixelsdata.collection_uri,
                self.generator_arguments_uri,
                str(item_per_job),
                array_size=number_of_jobs,
                gpu=True,
            )
            # Register collection job id and submitted state.
            self.batchjob_predict.job_id = predict_job[BATCH_JOB_ID_KEY]
            self.batchjob_predict.status = BatchJob.SUBMITTED
            self.batchjob_predict.save()
