from batch.models import BatchJob
from django.contrib import admin


class BatchJobModelAdmin(admin.ModelAdmin):
    search_fields = ["job_id"]
    list_filter = ["status"]


admin.site.register(BatchJob, BatchJobModelAdmin)
