from django.contrib import admin

from .models import RockProjectDetails, City, \
    BusinessModel, FundingMechanism, DiaryEntry


admin.site.register(RockProjectDetails)
admin.site.register(FundingMechanism)
admin.site.register(BusinessModel)
admin.site.register(DiaryEntry)
admin.site.register(City)
