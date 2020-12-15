'''
These are the REST/AJAX endpoints called by the DeCart site itself.

For the main HTML page views see `views.py`.

TODO :: All of the JSON responses to should include any error information that can
        be identified and sent back.
'''
import json

from django.db.utils import IntegrityError
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.core import serializers

from decart.core.utils import get_modal_form_html, ajax_delete_by_id
from decart.core.models import Project, ExternalLink, IndicatorState, OutcomeIndicator
from decart.core.forms import ExternalLinkFormset, IndicatorStateForm

from .forms import FundingMechanismForm, DiaryForm
from .models import FundingMechanism, DiaryEntry, RockProjectDetails


# NOTE :: Middleware kicks the user back to the login screen if they aren't
#         authenticated so we don't need to confirm that again.

# ----------------------------------------------------------------------------
# Funding Mechanisms

def _save_and_get_funding_details(form, project):
    '''
    Validate a funding mechanism form and generate the payload required for
    redrawing the page with new information to be sent back to the AJAX
    handler.
    '''
    try:
        funding = form.save()
    except IntegrityError:
        # Save the data
        funding = FundingMechanism()
        funding.project = project
        funding.mechanism = form.cleaned_data['mechanism']
        funding.other_details = form.cleaned_data['other_details']
        funding.provider = form.cleaned_data['provider']
        funding.provider_ownership = form.cleaned_data['provider_ownership']
        funding.provider_type = form.cleaned_data['provider_type']
        funding.currency = form.cleaned_data['currency']
        funding.amount = form.cleaned_data['amount']
        funding.note = form.cleaned_data['note']
        funding.save()

    resp = form.cleaned_data
    resp['pk'] = funding.pk
    if resp['mechanism'] == 'Other':
        resp['details'] = resp['other_details']
    else:
        resp['details'] = resp['mechanism']
    resp.update({'success': True})

    return JsonResponse(resp)


def add_funding_mechanism(request, project_id):
    '''
    Endpoint for accepting form data from the "Add A New Funding Mechanism"
    modal form within the Project Details Page.
    '''
    if request.is_ajax():
        if request.method == 'POST':
            form = FundingMechanismForm(request.POST)
            if form.is_valid():
                project = Project.objects.get(id=project_id)
                return _save_and_get_funding_details(form, project)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


def edit_funding_mechanism(request, funding_id):
    '''
    Edit an existing funding mechanism
    '''
    if request.is_ajax():
        funding = FundingMechanism.objects.get(id=funding_id)

        if request.method == 'GET':
            # Generate and serve an edit modal for this marker
            form = FundingMechanismForm(instance=funding)

            html = get_modal_form_html(
                request=request,
                title='Edit This Funding Mechanism',
                id_prefix='funding-edit',
                action=reverse('editfunding', args=[funding_id]),
                form=form
            )

            return JsonResponse({'success': True, 'html': html})

        elif request.method == 'POST':
            # Handle the update
            form = FundingMechanismForm(request.POST, instance=funding)

            if form.is_valid():
                return _save_and_get_funding_details(form, funding.project)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})


def delete_funding_mechanism(request):
    '''
    Remove a funding mechanism from a project
    '''
    return ajax_delete_by_id(request, FundingMechanism)


# ----------------------------------------------------------------------------
# Diary Entries
def edit_diary_entry(request, entry_id):
    '''
    Edit an existing diary entry.
    '''
    entry = DiaryEntry.objects.get(id=entry_id)

    if request.is_ajax():
        if request.method == 'GET':
            # convert "Diary" to json
            _external_links = []
            for link in entry.external_links.all():
                _external_links.append(link.url)
            data = {
                'content':entry.content,
                'start_date':entry.start_date,
                'end_date':entry.end_date,
                'outcome':entry.outcome.id if entry.outcome else None,
                'category':entry.category,
                'external_links': _external_links
            }
            

            return JsonResponse({'success': True, 'data': data})

    elif request.method == 'POST':
        # Handle the update
        form = DiaryForm(
            request.POST,
            instance=entry,
            project_instance=entry.project,
            prefix="edit"
        )

        link_formset = ExternalLinkFormset(request.POST, prefix="edit")

        if form.is_valid() and link_formset.is_valid():
            form.save()
            # save links
            if link_formset:
                entry.external_links.clear()
                for field in link_formset.cleaned_data:
                    url = field.get('url')
                    # Could be a blank field that was removed by the user
                    if url:
                        link, _ = ExternalLink.objects.get_or_create(url=url)
                        entry.external_links.add(link)
                entry.save()

            messages.success(request, 'Diary entry edited successfully')
            return redirect('editdiary', project_id=entry.project.id)

        # Return the form errors
        return JsonResponse({
            'success': False,
            'errors': str(form.errors)
        })

    return JsonResponse({'success': False})


def delete_diary_entry(request, entry_id):
    '''
    Remove a diary entry from a project.
    '''
    entry = DiaryEntry.objects.get(pk=entry_id)

    if request.method == 'POST':
        # body = json.loads(request.body.decode('utf-8'))
        # entry_id = body['id']
        entry.delete()
        messages.success(request, 'Diary entry deleted successfully')
        return redirect('editdiary', project_id=entry.project.id)

    messages.error(request, 'Unable to delete diary entry.')
    return redirect('editdiary', project_id=entry.project.id)


# ----------------------------------------------------------------------------
# Progress :: State

def _save_and_get_state_details(form, indicator, links=None):
    '''
    Validate an outcome form and generate the payload required for redrawing
    the page with new information to be sent back to the AJAX handler.
    '''
    state = form.save()
    indicator.states.add(state)

    if links:
        state.external_links.clear()
        for field in links.cleaned_data:
            url = field.get('url')
            # Could be a blank field that was removed by the user
            if url:
                link, _ = ExternalLink.objects.get_or_create(url=url)
                state.external_links.add(link)
        state.save()

    # Build the payload for rendering the page
    resp = {
        'state': form.cleaned_data['state'],
        'pk': state.pk,
        'start_date': form.cleaned_data['start_date'],
        'end_date': form.cleaned_data['end_date'],
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
            link_formset = ExternalLinkFormset(request.POST)
            if form.is_valid() and link_formset.is_valid():
                indicator = OutcomeIndicator.objects.get(pk=indicator_id)
                return _save_and_get_state_details(form, indicator, link_formset)

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
            # convert "state" to json
            _external_links = []
            for link in state.external_links.all():
                _external_links.append(link.url)
            data = {
                'state': state.state,
                'start_date': state.start_date,
                'end_date': state.end_date,
                'evidence':state.evidence,
                'external_links': _external_links
            }

            return JsonResponse({'success': True, 'data': data})

        if request.method == 'POST':
            # Handle the update
            indicator_id = request.POST['indicator-id']
            form = IndicatorStateForm(
                request.POST,
                instance=state,
            )
            link_formset = ExternalLinkFormset(request.POST)

            if form.is_valid() and link_formset.is_valid():
                indicator = OutcomeIndicator.objects.get(pk=indicator_id)
                return _save_and_get_state_details(form, indicator, link_formset)

            # Return the form errors
            return JsonResponse({
                'success': False,
                'errors': str(form.errors)
            })

    return JsonResponse({'success': False})
