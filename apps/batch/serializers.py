from batch.models import BatchJob
from rest_framework.serializers import ModelSerializer


class BatchJobSerializer(ModelSerializer):
    class Meta:
        model = BatchJob
        fields = "__all__"
