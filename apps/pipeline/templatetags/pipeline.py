from django import template
from django.conf import settings

register = template.Library()


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
