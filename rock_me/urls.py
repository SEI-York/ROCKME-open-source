"""rockme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include
from django.views import defaults as default_views
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static

import decart.core.endpoints as core_endpoints

from . import views
from . import endpoints

app_name = "core"

urlpatterns = [
    # Site login / landing page
    # url(r'^$', views.index, name='home'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='pages/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('accounts/', include('allauth.urls')),

    # Core DeCart interface
    # url(r'core/', include('core.urls')),

    # Index pages
    path(r'', views.project_index, name='index'),
    path(r'users', views.user_index, name='userindex'),
    path(r'my_projects', views.my_project_index, name='myindex'),
    path(r'organisations', views.organisation_index, name='orgindex'),
    path(r'pendingdeletion', views.pending_deletion, name='pendingdeletion'),

    # Users
    path(r'users/view/<int:user_id>', views.view_user, name='view_user'),
    path(r'users/edit/<int:user_id>', views.edit_user, name='edit_user'),

    # Projects
    path(r'project/new', views.new_project, name='newproject'),
    path(r'project/details/<int:project_id>', views.view_project, name='viewproject'),
    path(r'project/evaluation/<int:project_id>', views.view_evaluation, name='viewevaluation'),
    path(r'project/monitoring/<int:project_id>', views.view_monitoring, name='viewmonitoring'),
    path(r'project/progress/<int:project_id>', views.view_progress, name='viewprogress'),

    path(r'project/details/edit/<int:project_id>', views.edit_project, name='editproject'),
    path(r'project/evaluation/edit/<int:project_id>', views.edit_evaluation, name='editevaluation'),
    path(r'project/monitoring/edit/<int:project_id>', views.edit_monitoring, name='editmonitoring'),
    path(r'project/progress/edit/<int:project_id>', views.edit_progress, name='editprogress'),

    # Partners
    path(r'organisations/new', core_endpoints.create_organisation, name='neworg'),
    path(r'organisations/edit/<int:org_id>', core_endpoints.edit_organisation, name='editorg'),

    path(r'partner/add/<int:project_id>', core_endpoints.add_organisation, name='addorg'),
    path(r'partner/remove/<int:project_id>', core_endpoints.remove_organisation, name='removeorg'),

    # Boundary partners
    path(r'boundarypartner/add/<int:project_id>', core_endpoints.add_boundary_partner, name='addboundarypartner'),
    path(r'boundarypartner/remove/<int:project_id>/', core_endpoints.remove_boundary_partner, name='removeboundarypartner'),

    # Funding mechanisms
    path(r'funding/add/<int:project_id>', endpoints.add_funding_mechanism, name='addfunding'),
    path(r'funding/edit/<int:funding_id>', endpoints.edit_funding_mechanism, name='editfunding'),
    path(r'funding/delete', endpoints.delete_funding_mechanism, name='deletefunding'),

    # Monitoring and evaluation
    # XXX :: Edit URLS MUST stay with the id as the final element as the
    #        jQuery code is replacing it after it has been rendered
    #        in the HTML (yes I know this is horrible...)
    path(r'plan/outcome/edit/<int:outcome_id>', core_endpoints.edit_outcome, name='editoutcome'),
    path(r'plan/outcome/add/<int:project_id>', core_endpoints.add_outcome, name='addoutcome'),
    path(r'plan/outcome/delete', core_endpoints.delete_outcome, name='deleteoutcome'),

    path(r'plan/indicator/edit/<int:indicator_id>', core_endpoints.edit_indicator, name='editindicator'),
    path(r'plan/indicator/add/<int:project_id>', core_endpoints.add_indicator, name='addindicator'),
    path(r'plan/indicator/delete', core_endpoints.delete_indicator, name='deleteindicator'),

    path(r'plan/marker/edit/<int:marker_id>', core_endpoints.edit_marker, name='editprogressmarker'),
    path(r'plan/marker/add/<int:project_id>', core_endpoints.add_marker, name='addprogressmarker'),
    path(r'plan/marker/delete', core_endpoints.delete_marker, name='deleteprogressmarker'),

    # Diary
    path(r'diary/view/<int:project_id>', views.view_diary, name='viewdiary'),
    path(r'diary/edit/<int:project_id>', views.edit_diary, name='editdiary'),
    path(r'diary/entry/edit/<int:entry_id>', endpoints.edit_diary_entry, name='editdiaryentry'),
    path(r'diary/entry/delete/<int:entry_id>', endpoints.delete_diary_entry, name='deletediaryentry'),

    # Indicator states (progress page)
    path(r'plan/state/edit/<int:state_id>', endpoints.edit_state, name='editstate'),
    path(r'plan/state/add/<int:indicator_id>', endpoints.add_state, name='addstate'),
    path(r'plan/state/delete', endpoints.delete_state, name='deletestate'),

    # Misc
    path(r'contact/', views.contact_support, name='contact'),
    path(r'stats/', views.stats, name='stats'),

    # Admin backend
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
