from batch.const import BATCH_JOB_FINAL_STATUSES
from batch.models import BatchJob
from botocore.exceptions import NoCredentialsError
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class BatchJobSerializer(ModelSerializer):

    status = SerializerMethodField()

    class Meta:
        model = BatchJob
        fields = "__all__"

    def get_status(self, obj):
        """
        Get status of this job, if necessary, refresh from batch.
        """
        if obj.status not in BATCH_JOB_FINAL_STATUSES:
            try:
                obj.update()
            except NoCredentialsError:
                pass
        return obj.status
