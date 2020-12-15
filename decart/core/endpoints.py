'''
These are the REST/AJAX endpoints called by the DeCart site itself.

For the main HTML page views see `views.py`.

TODO :: All of the JSON responses to should include any error information that
        can be identified and sent back.
'''
import json

from django.urls import reverse
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.contrib import messages

from .utils import get_project_if_editable, get_modal_form_html, \
    ajax_delete_by_id

from .forms import OrganisationForm, OutcomeForm, \
    OutcomeMarkerForm, OutcomeIndicatorForm, IndicatorStateForm

from .models import Project, Organisation, Outcome, \
    OutcomeIndicator, OutcomeProgressMarker, IndicatorState, Kpi


# NOTE :: Middleware kicks the user back to the login screen if they aren't
#         authenticated so we don't need to confirm that again.

# ----------------------------------------------------------------------------
# Partner Organisations

def create_organisation(request):
    '''
    Endpoint for accepting form data from the "Create A New
    Organisation" modal form within the Project Details Page.
    '''
    if request.is_ajax():
        if request.method == 'POST':
            form = OrganisationForm(request.POST, request.FILES)
            if form.is_valid():
                org = form.save()

                return JsonResponse({
                    'success': True,
                    'pk': org.pk,
                    'name': org.name,
                    'scale': org.scale,
                    'type': org.organisation_type,
                    'location': org.location,
                    'website': org.website,
                    'phone': org.phone,
                    'email': org.email,
                })

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


def edit_organisation(request, org_id):
    '''
    End point for editing Organisation
    '''
    if request.is_ajax():
        org = Organisation.objects.get(id=org_id)
        if request.method == 'GET':
            # Convert org to json
            return JsonResponse({
                'success': True,
                'name': org.name,
                'scale': org.scale,
                'type': org.organisation_type,
                'location': org.location,
                'website': org.website,
                'phone': org.phone,
                'email': org.email,
                'other_info': org.other_info
            })

        if request.method == 'POST':
            form = OrganisationForm(
                request.POST,
                instance=org,
            )
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def _modify_project_organisation(request, project_id, add=True):
    '''Add or remove a partner organisation'''
    if request.is_ajax():
        if request.method == 'POST':
            body = json.loads(request.body.decode('utf-8'))
            partner_id = body['id']
            role = body['role'].lower()
            partner = Organisation.objects.get(pk=partner_id)
            project = get_project_if_editable(project_id, request.user)

            if add:
                if role == 'partner':
                    project.partner_organisations.add(partner)
                elif role == 'audience':
                    project.boundary_partners.add(partner)
                else:
                    return JsonResponse({'success': False})
            else:
                if role == 'partner':
                    project.partner_organisations.remove(partner)
                elif role == 'audience':
                    project.boundary_partners.remove(partner)
                else:
                    return JsonResponse({'success': False})

            project.save()

            resp = {
                'success': True,
                'pk': partner.pk,
                'name': partner.name,
                'role': role.capitalize(),
                'scale': partner.scale,
                'type': partner.get_organisation_type_display(),
                'email': partner.email,
                'phone': partner.phone,
                'website': partner.website,
                'location': partner.location,
                'other': partner.other_info,
            }

            for k in resp:
                if resp[k] is None:
                    resp[k] = ''

            return JsonResponse(resp)

    return JsonResponse({'success': False})


def add_organisation(request, project_id):
    '''
    Endpoint for accepting form data from the "Add A New Partner Organisation"
    modal form within the Project Details Page.
    '''
    return _modify_project_organisation(request, project_id, add=True)


def remove_organisation(request, project_id):
    '''
    Remove a partner via AJAX
    '''
    return _modify_project_organisation(request, project_id, add=False)


# ----------------------------------------------------------------------------
# Monitoring & Evaluation :: Outcomes

def _save_and_get_outcome_details(form, project):
    '''
    Validate an outcome form and generate the payload required for redrawing
    the page with new information to be sent back to the AJAX handler.
    '''
    try:
        outcome = form.save()
    except IntegrityError:
        # Save the data
        outcome = Outcome()
        outcome.project = project
        outcome.boundary_partner = form.cleaned_data['boundary_partner']
        outcome.description = form.cleaned_data['description']
        outcome.save()

    # Build the payload for rendering the page
    resp = form.cleaned_data

    resp['outcomeNum'] = len(Outcome.objects.filter(
        boundary_partner=outcome.boundary_partner
    ).filter(project=project))
    resp['outcomePk'] = outcome.pk
    resp['partnerPk'] = resp['boundary_partner'].pk
    resp['boundary_partner'] = resp['boundary_partner'].name
    resp.update({'success': True})

    return JsonResponse(resp)


def delete_outcome(request):
    '''
    Delete an outcome via AJAX
    '''
    return ajax_delete_by_id(request, Outcome)


def add_outcome(request, project_id):
    '''
    Add a new outcome via ajax
    '''
    if request.is_ajax():
        if request.method == 'POST':
            project = Project.objects.get(id=project_id)
            form = OutcomeForm(request.POST, project_instance=project)
            if form.is_valid():
                return _save_and_get_outcome_details(form, project)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


def edit_outcome(request, outcome_id):
    '''
    Either serve a modal form for editing an existing outcome or handle the
    new data from the user and update the DB.
    '''
    if request.is_ajax():
        outcome = Outcome.objects.get(id=outcome_id)

        if request.method == 'GET':
            # Convert outcome to JSON
            return JsonResponse({
                'success': True,
                'description': outcome.description,
                'partnerId': outcome.boundary_partner.id,
            })

        elif request.method == 'POST':
            # Handle the update
            form = OutcomeForm(
                request.POST,
                instance=outcome,
                project_instance=outcome.project
            )

            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'outcomePk': outcome_id,
                    'description': form.cleaned_data['description']
                })

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


# ----------------------------------------------------------------------------
# Monitoring & Evaluation :: Indicators

def _save_and_get_indicator_details(form, project_id, partner_id, outcome_id):
    '''
    Validate a marker form and generate the payload required for redrawing
    the page with new information to be sent back to the AJAX handler.
    '''
    indicator = form.save()
    outcome = Outcome.objects.get(id=outcome_id)
    outcome.indicators.add(indicator)
    resp = form.cleaned_data
    resp['pk'] = indicator.pk
    kpi = resp['kpi'].name
    resp.update({'kpi': kpi})
    resp.update({'success': True})

    return JsonResponse(resp)


def delete_indicator(request):
    '''
    Delete an outcome indicator via AJAX
    '''
    return ajax_delete_by_id(request, OutcomeIndicator)


def add_indicator(request, project_id):
    '''
    Add a new indicator via ajax
    '''
    if request.is_ajax():
        if request.method == 'POST':
            form = OutcomeIndicatorForm(request.POST)
            partner_id = request.POST['partner-id']
            outcome_id = request.POST['outcome-id']
            if form.is_valid():
                return _save_and_get_indicator_details(
                    form, project_id, partner_id, outcome_id)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


def edit_indicator(request, indicator_id):
    '''
    Edit an outcome indicator via AJAX
    '''
    if request.is_ajax():
        indicator = OutcomeIndicator.objects.select_related('kpi', 'kpi__category').get(id=indicator_id)

        if request.method == 'GET':
            # Convert indicator to JSON
            return JsonResponse({
                'success': True,
                'kpi_group': indicator.kpi.category.group,
                'kpi': indicator.kpi.pk,
                'name': indicator.name,  # hidden field for now
                'measure': indicator.measure,
                'verification': indicator.verification,
                'baseline': indicator.baseline,
                'date': indicator.baseline_date,
            })

        elif request.method == 'POST':
            # Handle the update
            form = OutcomeIndicatorForm(
                request.POST,
                instance=indicator
            )

            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'pk': indicator_id
                })

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


# ----------------------------------------------------------------------------
# Monitoring & Evaluation :: Progress Markers

def _save_and_get_marker_details(form):
    '''
    Validate a marker form and generate the payload required for redrawing
    the page with new information to be sent back to the AJAX handler.
    '''
    marker = form.save()
    resp = form.cleaned_data
    outcome = resp['outcome']
    desc = outcome.description

    if len(desc) > 20:
        desc = desc[:20] + '...'

    resp['outcome'] = desc
    resp['partner'] = outcome.boundary_partner.name
    resp['pk'] = marker.pk
    resp.update({'success': True})

    return JsonResponse(resp)


def delete_marker(request):
    '''
    Delete a progress marker via AJAX
    '''
    return ajax_delete_by_id(request, OutcomeProgressMarker)


def add_marker(request, project_id):
    '''
    Add a new progress marker via ajax
    '''
    if request.is_ajax():
        if request.method == 'POST':
            project = Project.objects.get(id=project_id)
            form = OutcomeMarkerForm(request.POST, project_instance=project)
            if form.is_valid():
                return _save_and_get_marker_details(form)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


def edit_marker(request, marker_id):
    '''
    Either serve a modal form for editing an existing marker or handle the
    new data from the user and update the DB.
    '''
    if request.is_ajax():
        marker = OutcomeProgressMarker.objects.get(id=marker_id)

        if request.method == 'GET':
            # Generate and serve an edit modal for this marker
            form = OutcomeMarkerForm(
                instance=marker,
                project_instance=marker.outcome.project
            )

            html = get_modal_form_html(
                request=request,
                title='Edit This Progress Marker',
                id_prefix='marker-edit',
                action=reverse('editprogressmarker', args=[marker_id]),
                form=form
            )

            return JsonResponse({'success': True, 'html': html})

        elif request.method == 'POST':
            # Handle the update
            form = OutcomeMarkerForm(
                request.POST,
                instance=marker,
                project_instance=marker.outcome.project
            )

            if form.is_valid():
                return _save_and_get_marker_details(form)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


# ----------------------------------------------------------------------------
# Monitoring & Evaluation :: Boundary Partners

def remove_boundary_partner(request, project_id):
    '''
    Remove a boundary partner from a project.
    '''
    if request.is_ajax():
        if request.method == 'POST':
            body = json.loads(request.body.decode('utf-8'))
            partner_id = body['id']
            partner = Organisation.objects.get(pk=partner_id)

            # Remove the boundary partner
            project = Project.objects.get(pk=project_id)
            project.boundary_partners.remove(partner)

            # Remove the outcomes (cascades to indicators and progress markers)
            Outcome.objects.filter(
                boundary_partner=partner
            ).filter(
                project=project
            ).delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def add_boundary_partner(request, project_id):
    '''
    Add a new indicator via ajax
    '''
    if request.is_ajax():
        if request.method == 'POST':
            project = get_project_if_editable(project_id, request.user)
            body = json.loads(request.body.decode('utf-8'))

            for field in body:
                if field['name'] == 'boundary-partner-select':
                    partner = Organisation.objects.get(id=field['value'])
                    break
            else:
                return JsonResponse({'success': False})

            project.boundary_partners.add(partner)
            project.save()
            return JsonResponse(
                {'success': True,
                 'pk': partner.pk,
                 'name': partner.name})

    return JsonResponse({'success': False})


# ----------------------------------------------------------------------------
# Progress :: State

def _save_and_get_state_details(form, indicator):
    '''
    Validate an outcome form and generate the payload required for redrawing
    the page with new information to be sent back to the AJAX handler.
    '''
    state = form.save()
    indicator.states.add(state)

    # Build the payload for rendering the page
    resp = {
        'state': form.cleaned_data['state'],
        'pk': state.pk,
        'date': form.cleaned_data['date'].strftime('%B %d, %Y'),
        'success': True
    }

    return JsonResponse(resp)


def delete_state(request):
    '''
    Delete an state via AJAX
    '''
    return ajax_delete_by_id(request, IndicatorState)


def add_state(request, indicator_id):
    '''
    Add a new state via ajax
    '''
    if request.is_ajax():
        if request.method == 'POST':
            form = IndicatorStateForm(request.POST)
            if form.is_valid():
                indicator = OutcomeIndicator.objects.get(pk=indicator_id)
                return _save_and_get_state_details(form, indicator)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


def edit_state(request, state_id):
    '''
    Either serve a modal form for editing an existing indicator state
    or handle the new data from the user and update the DB.
    '''
    if request.is_ajax():
        state = IndicatorState.objects.get(id=state_id)

        if request.method == 'GET':
            # Generate and serve an edit modal for this marker
            form = IndicatorStateForm(instance=state)

            html = get_modal_form_html(
                request=request,
                title='Edit This State',
                id_prefix='state-edit',
                action=reverse('editstate', args=[state_id]),
                form=form
            )

            return JsonResponse({'success': True, 'html': html})

        elif request.method == 'POST':
            # Handle the update
            indicator_id = request.POST['indicator-id']
            form = IndicatorStateForm(
                request.POST,
                instance=state,
            )

            if form.is_valid():
                indicator = OutcomeIndicator.objects.get(pk=indicator_id)
                return _save_and_get_state_details(form, indicator)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})
