'''
Utility functions for use within decart
'''
import json

from django.core.exceptions import PermissionDenied
from django.template.context import RequestContext
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Project, Outcome, OutcomeProgressMarker


# Used in get_modal_form_html to render bootstrap modals
MODAL_FORM_TEMPLATE = get_template('core/fragments/modal_form.html')


def get_project_if_editable(project_id, user):
    '''
    Retrieve the request project details if the user is
    able to edit it.

    Raises 404 if the project doesn't exist and 403 if the
    user doesn't have edit rights.
    '''
    project = get_object_or_404(Project, id=project_id)

    # TODO: At the moment this is a very simple check that
    #       the project was created by this user. We need
    #       to set up a more sophisticated system eventually.
    if project.created_by != user:
        raise PermissionDenied

    return project


def get_boundary_partners_and_markers(project):
    '''
    Get the list of a project's boundary partners and their associated outcomes.
    '''
    partners = []
    markers = []

    for partner in project.boundary_partners.all():
        partner.outcomes = Outcome.objects.filter(
            boundary_partner=partner
        ).filter(
            project=project
        ).prefetch_related('indicators').order_by('pk')

        for outcome in partner.outcomes:
            outcome.indicator_list = outcome.indicators.all()

            for marker in OutcomeProgressMarker.objects.filter(outcome=outcome):
                markers.append(marker)

        partners.append(partner)

    return partners, markers


def get_modal_form_html(request, title, id_prefix, action, form):
    '''Render out a form as a Bootstrap modal'''
    return MODAL_FORM_TEMPLATE.template.render(
        RequestContext(request, {
            'modal_id': '{}-modal'.format(id_prefix),
            'form_id': '{}-form'.format(id_prefix),
            'table_id': '{}-table'.format(id_prefix),
            'modal_title': title,
            'action': action,
            'form': form
        })
    )


# Helper functions for common AJAX API behaviour
def ajax_delete_by_id(request, table):
    '''
    Delete a database table entry via AJAX
    '''
    if request.is_ajax():
        if request.method == 'POST':
            body = json.loads(request.body.decode('utf-8'))
            table_id = body['id']
            item = table.objects.get(pk=table_id)
            pk = item.pk
            item.delete()
            return JsonResponse({
                'success': True,
                'pk': pk
            })

    return JsonResponse({'success': False})


def ajax_create_from_json(request, table, defaults=None):
    '''
    Create a database table entry using jQuery form data in array format.
    '''
    if request.is_ajax():
        if request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            new_entry = table()

            for field in data:
                if field['name'] != 'csrfmiddlewaretoken':
                    setattr(new_entry, field['name'], field['value'])

            if defaults:
                # Set any required default fields
                for attr, val in defaults.items():
                    setattr(new_entry, attr, val)

            new_entry.save()
            return JsonResponse({
                'success': True,
                'pk': new_entry.pk
            })

    return JsonResponse({'success': False})
