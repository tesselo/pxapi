from batch.models import BatchJob
from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from pipeline.models import KerasModel, PixelsData, Prediction, TrainingData


class NamedGuardedModelAdmin(GuardedModelAdmin):
    search_fields = ["name", "description"]
    list_display = ["name", "status"]
    change_form_template = "change_form.html"

    status_keys = None

    def status(self, obj):
        """
        Obtain the status from a related batchjob object.

        The status_keys property is the name of the ForeignKey field linking to
        the batch job object.
        """
        # Ensure key was set.
        if not self.status_keys:
            raise NotImplementedError("Status key needs to be specified.")
        # Get related batch job using the key string of the last job in list.
        batchjob = getattr(obj, self.status_keys[-1], None)
        # If the batchjob object exists, use its status for display. Otherwise
        # return unknown.
        if batchjob:
            return batchjob.status.title()
        else:
            return "Unknown"

    def get_queryset(self, request):
        """
        Overriding the queryset for the pipeline admin views to update tasks on
        page load.
        """
        # Get original queryset.
        queryset = super().get_queryset(request)
        # Loop through related batch job keys.
        for status_key in self.status_keys:
            # Reduce objects with running jobs.
            running_queryset = queryset.exclude(
                **{
                    f"{status_key}__status__in": [
                        BatchJob.UNKNOWN,
                        BatchJob.SUCCEEDED,
                        BatchJob.FAILED,
                    ]
                }
            )
            # For all the running jobs, update status.
            for obj in running_queryset:
                batchjob = getattr(obj, status_key, None)
                if batchjob:
                    batchjob.update()
        # Return default queryset.
        return queryset


class TrainingDataAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_parse__status"]
    status_keys = ["batchjob_parse"]
    readonly_fields = ["batchjob_parse"]


class PixelsDataAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_collect_pixels__status", "batchjob_create_catalog__status"]
    status_keys = ["batchjob_collect_pixels", "batchjob_create_catalog"]
    readonly_fields = ["batchjob_collect_pixels", "batchjob_create_catalog"]


class KerasModelAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_train__status"]
    change_form_template = "change_form_kerasmodel.html"
    status_keys = ["batchjob_train"]
    readonly_fields = ["batchjob_train"]


class PredictionAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_predict__status", "batchjob_create_catalog__status"]
    status_keys = ["batchjob_predict", "batchjob_create_catalog"]
    readonly_fields = ["batchjob_predict", "batchjob_create_catalog"]


admin.site.register(TrainingData, TrainingDataAdmin)
admin.site.register(PixelsData, PixelsDataAdmin)
admin.site.register(KerasModel, KerasModelAdmin)
admin.site.register(Prediction, PredictionAdmin)
