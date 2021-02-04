import os

from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage


class MediaStorage(S3Boto3Storage):
    bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME_MEDIA")


class StaticStorage(S3StaticStorage):
    bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME_STATIC")
    querystring_auth = True
