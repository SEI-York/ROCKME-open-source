from django.contrib import admin

from .models import RockUserDetails, RockUserOrganisation


admin.site.register(RockUserOrganisation)
admin.site.register(RockUserDetails)
