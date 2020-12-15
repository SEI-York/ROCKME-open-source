from django.contrib import admin

from .models import Project, Evaluation, ExternalLink, \
    Organisation, Outcome, OutcomeIndicator, OutcomeProgressMarker, Kpi, KpiCategory


admin.site.register(OutcomeProgressMarker)
admin.site.register(OutcomeIndicator)
admin.site.register(Organisation)
admin.site.register(ExternalLink)
admin.site.register(Evaluation)
admin.site.register(Outcome)
admin.site.register(Project)


class KpiAdmin(admin.ModelAdmin):
    list_select_related = ('category', )
    list_display = ('name', 'get_category_name', )
    search_fields = ('name',)
    list_filter = ('category', )

    def get_category_name(self, obj):
        return obj.category.name
    get_category_name.admin_order_field = 'category'  # Allows column order sorting
    get_category_name.short_description = 'Category Name'  # Renames column head


admin.site.register(Kpi, KpiAdmin)
admin.site.register(KpiCategory)
