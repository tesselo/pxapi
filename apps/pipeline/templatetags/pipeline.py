from django import template
from django.conf import settings
from pipeline.const import DATADOG_VIEWS

register = template.Library()


def datadog_view(step):
    return DATADOG_VIEWS.get(step, DATADOG_VIEWS["default"])


@register.filter
def to_class_name(value):
    return value.__class__.__name__.lower()


@register.filter
def s3_console_link(value):
    bucket = (
        settings.AWS_S3_BUCKET_NAME
        if hasattr(settings, "AWS_S3_BUCKET_NAME")
        else "pxapi-media-dev"
    )
    return f"https://s3.console.aws.amazon.com/s3/buckets/{bucket}?region=eu-central-1&prefix={value.__class__.__name__.lower()}/{value.id}/&showversions=false"


@register.filter
def job_id(value, arg):
    job = getattr(value, f"batchjob_{arg}")
    return job.job_id


@register.filter
def logs_link(value, arg):
    return f"https://app.datadoghq.eu/logs?saved_view={datadog_view(arg)}&query=%40AWS_BATCH_JOB_ID%3A{value}%2A"
