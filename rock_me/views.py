'''
These are the core HTML page views that determine the user facing interface
for DeCart.

For REST/AJAX endpoints see `endpoints.py`.
'''
import json
from itertools import chain

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.db import connection

from rock_user.models import RockUserDetails
from rock_user.forms import RockUserForm

from decart.core.utils import get_project_if_editable, \
    get_boundary_partners_and_markers, get_modal_form_html

from decart.core.forms import ContactForm, OrganisationForm, \
    EvaluationForm, OutcomeMarkerForm, OutcomeForm, \
    OutcomeIndicatorForm, IndicatorStateForm, ExternalLinkFormset

from decart.core.models import Project, Evaluation, Organisation, ExternalLink, Kpi, KpiCategory, Outcome

from .forms import RockProjectDetailsForm, BusinessModelForm, \
    FundingMechanismForm, NewProjectForm, RockProjectForm, DiaryForm

from .models import RockProjectDetails, BusinessModel, FundingMechanism, \
    DiaryEntry



# NOTE :: Middleware kicks the user back to the login screen if they aren't
#         authenticated so we don't need to confirm that again.

def index(request):
    '''
    If the user is logged in then we redirect them to the full
    project listing, otherwise we redirect them to the login.
    '''
    if request.user.is_authenticated:
        destination = 'myindex'
    else:
        destination = 'login'

    return HttpResponseRedirect(reverse(destination))


# ----------------------------------------------------------------------------
# Index Pages
def _add_rock_details(qset, rock_details):
    '''Bind in the other data required for ROCK'''
    for p in qset:
        if p.project_leader:
            try:
                p.leader_name = RockUserDetails.objects.get(
                    user=p.project_leader)  # this is always NULL, also in models, it is linked to Organisation NOT user
            except RockUserDetails.DoesNotExist:
                p.leader_name = 'Not Specified'
        else:
            p.leader_name = 'Not Specified'

        for r in rock_details:
            if r.project == p:
                p.rock = r
                break


def project_index(request):
    '''
    List all open projects that are not pending deletion.
    '''
    rock_details = RockProjectDetails.objects.all().prefetch_related(
        'project', 'city', 'lead_administrative_organisation', 'lead_scientific_organisation')
    ongoing = Project.objects.filter(complete=False, to_delete=False)
    completed = Project.objects.filter(complete=True, to_delete=False)

    _add_rock_details(chain(ongoing, completed), rock_details)

    # create rock user details record if not exists
    try:
        rock_user = RockUserDetails.objects.get(user=request.user)
    except RockUserDetails.DoesNotExist:
        rock_user = RockUserDetails(
            user=request.user,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
        )
        rock_user.save()

    context = {
        'rock_user': rock_user,
        'allow_edit': False,
        'ongoing_projects': ongoing,
        'completed_projects': completed,
    }

    return render(request, 'rock/project_index.html', context)


def my_project_index(request):
    '''
    List all open projects.
    '''
    if request.method == 'POST':
        action = request.POST['action']
        proj_id = request.POST['project-id']
        project = get_object_or_404(Project, id=proj_id)

        if action == 'delete':
            # Flag the requested project for deletion
            project.to_delete = True
            project.save()
            messages.success(request, 'Project marked for deletion successfully')
            return HttpResponseRedirect(reverse('myindex'))
        elif action == 'complete':
            # Flag the requested project as complete
            project.complete = True
            project.save()
            messages.success(request, 'Project marked as complete')
            return HttpResponseRedirect(reverse('myindex'))
        else:
            messages.error(request, 'Unexpected action: {}'.format(action))
            return HttpResponseRedirect(reverse('myindex'))

    rock_user = get_object_or_404(RockUserDetails, user=request.user)

    rock_details = RockProjectDetails.objects.all().prefetch_related(
        'project', 'city', 'lead_administrative_organisation', 'lead_scientific_organisation')
    ongoing = Project.objects.filter(complete=False, to_delete=False).filter(created_by=request.user)
    completed = Project.objects.filter(complete=True, to_delete=False).filter(created_by=request.user)

    _add_rock_details(chain(ongoing, completed), rock_details)

    context = {
        'rock_user': rock_user,
        'allow_edit': True,
        'ongoing_projects': ongoing,
        'completed_projects': completed,
    }

    return render(request, 'rock/project_index.html', context)


def organisation_index(request):
    '''Show all of the know organisations'''
    organisations = Organisation.objects.all().order_by('name')

    org_html = get_modal_form_html(
        request=request,
        title='',
        id_prefix='org',
        action='',
        form=OrganisationForm
    )

    context = {
        'organisations': organisations,
        'org_modal': org_html,
        'help_page_number': 3,
    }
    return render(request, 'rock/organisation_index.html', context)


def user_index(request):
    '''
    List all employees who are active/archived with the ability to edit
    details if the user has the correct admin rights.
    '''
    active_user_details = get_object_or_404(RockUserDetails, user=request.user)
    rock_users = RockUserDetails.objects.all().order_by(
        'first_name', 'last_name'
    ).prefetch_related('user', 'organisation')

    context = {
        'active_user_details': active_user_details,
        'user_is_admin': active_user_details.is_admin,
        'rock_users': rock_users
    }

    return render(request, 'rock/user_index.html', context)


# ----------------------------------------------------------------------------
# User Pages
def view_user(request, user_id):
    '''View an Employee's details'''
    active_user_details = get_object_or_404(RockUserDetails, user=request.user)
    requested_user = RockUserDetails.objects.get(id=user_id)

    context = {
        'active_user_details': active_user_details,
        'user_is_admin': active_user_details.is_admin,
        'requested_user': requested_user
    }
    return render(request, 'rock/view_user.html', context)


def edit_user(request, user_id):
    '''Edit a user's details'''
    active_user_details = get_object_or_404(RockUserDetails, user=request.user)
    requested_user = RockUserDetails.objects.get(id=user_id)

    if not active_user_details.is_admin:
        return HttpResponseForbidden()

    if request.method == 'POST':
        user_form = RockUserForm(request.POST, instance=requested_user)
        if user_form.is_valid():
            user_form.save()

            messages.success(request, 'User details saved successfully')
            return HttpResponseRedirect(reverse('user_index'))
        else:
            messages.error(request, 'There were errors in your details.')
    else:
        user_form = RockUserForm(instance=requested_user)

    context = {
        'active_user_details': active_user_details,
        'user_is_admin': active_user_details.is_admin,
        'user_form': user_form

    }
    return render(request, 'rock/edit_user.html', context)


def pending_deletion(request):
    '''
    List all projects that are currently pending deletion.
    Only accessible by a Leadership member or superuser.
    '''
    rock_user = get_object_or_404(RockUserDetails, user=request.user)

    if not (rock_user.is_admin or request.user.is_superuser):
        raise PermissionDenied

    if request.method == 'POST':
        action = request.POST['action']
        proj_id = request.POST['project-id']
        project = get_object_or_404(Project, id=proj_id)

        if action == 'delete':
            # Delete the requested project
            project.delete()
            messages.success(request, 'Project deleted successfully')
        elif action == 'reinstate':
            project.to_delete = False
            project.save()
            messages.success(request, 'Project reinstated successfully')
        else:
            messages.error(request, 'Unexpected action: {}'.format(action))

    rock_details = RockProjectDetails.objects.all()
    projects = Project.objects.filter(to_delete=True)

    _add_rock_details(projects, rock_details)

    context = {
        'rock_user': rock_user,
        'projects': projects,
    }

    return render(request, 'rock/pending_deletion.html', context)

# ----------------------------------------------------------------------------
# Project Details
def _get_user_and_project(user, project_id):
    '''
    Make sure that only users with correct auth are able to access give projects
    '''
    rock_user = get_object_or_404(RockUserDetails, user=user)
    project = get_object_or_404(Project, id=project_id)

    if not user.is_superuser:
        if project.to_delete and not rock_user.has_admin_rights:
            raise PermissionDenied

    return rock_user, project


def view_project(request, project_id):
    '''
    Display the details of a given project.
    '''
    rock_user, project = _get_user_and_project(request.user, project_id)

    rock = RockProjectDetails.objects.get(project=project)
    b_model = BusinessModel.objects.get(project=project)

    # Get the associated partners (BPs and partner orgs)
    _partners = project.partner_organisations.all().order_by('name')
    _bpartners = project.boundary_partners.all().order_by('name')
    partners = []
    for role, orgs in [('Partner', _partners), ('Audience', _bpartners)]:
        for org in orgs:
            org.role = role
            partners.append(org)

    context = {
        'rock_user': rock_user,
        'project_id': project.id,
        'project': project,
        'rock': rock,
        'b_model': b_model,
        'audiences': _bpartners,
        'funding_mechanisms': FundingMechanism.objects.filter(project=project),
        'partners': partners,
        'help_page_number': 2,
    }

    return render(request, 'rock/view_project.html', context)


def edit_project(request, project_id):
    '''
    Edit the details of a given project.
    '''
    rock_user, project = _get_user_and_project(request.user, project_id)

    rock = RockProjectDetails.objects.get(project=project)
    b_model = BusinessModel.objects.get(project=project)

    if request.method == 'POST':
        p_form = RockProjectForm(
            request.POST,
            request.FILES,
            instance=project
        )
        r_form = RockProjectDetailsForm(
            request.POST,
            request.FILES,
            instance=rock
        )
        b_form = BusinessModelForm(
            request.POST,
            request.FILES,
            instance=b_model
        )
        link_formset = ExternalLinkFormset(request.POST)

        # Only save if all three are valid together
        if all(f.is_valid() for f in [p_form, r_form, b_form, link_formset]):
            proj = p_form.save()
            r_form.save()
            b_form.save()

            proj.external_links.clear()
            for field in link_formset.cleaned_data:
                url = field.get('url')
                # Could be a blank field that was removed by the user
                if url:
                    link, _ = ExternalLink.objects.get_or_create(url=url)
                    proj.external_links.add(link)
            proj.save()

            messages.success(request, 'Project saved successfully')
        else:
            messages.error(request, 'There were errors in your project.')

    # Otherwise, render the form for the user to fill in.

    # Canned templates for modal form execution
    funding_html = get_modal_form_html(
        request=request,
        title='Add A Funding Mechanism',
        id_prefix='funding-creator',
        action=reverse('addfunding', args=[project_id]),
        form=FundingMechanismForm
    )

    org_html = get_modal_form_html(
        request=request,
        title='Create a new organisation',
        id_prefix='org',
        action='',
        form=OrganisationForm
    )

    link_formset = ExternalLinkFormset(
        initial=[{'url': l.url} for l in project.external_links.all()]
    )

    # Get the associated partners (BPs and partner orgs)
    _partners = project.partner_organisations.all().order_by('name')
    _bpartners = project.boundary_partners.all().order_by('name')
    partners = []
    for role, orgs in [('Partner', _partners), ('Audience', _bpartners)]:
        for org in orgs:
            org.role = role
            partners.append(org)

    context = {
        'rock_user': rock_user,
        'project_id': project_id,
        'project_title': project.title,
        'project_type': rock.project_type,
        'funding_mechanisms': FundingMechanism.objects.filter(project=project),
        'project_form': RockProjectForm(instance=project),
        'rock_form': RockProjectDetailsForm(instance=rock),
        'business_form': BusinessModelForm(instance=b_model),
        'partners': partners,
        'audiences': _bpartners,
        'all_organisations': Organisation.objects.all().order_by('name'),
        'funding_modal': funding_html,
        'org_modal': org_html,
        'link_formset': link_formset,
        'help_page_number': 2,
    }

    return render(request, 'rock/edit_project.html', context)


# ----------------------------------------------------------------------------
# Diary

def view_diary(request, project_id):
    '''
    View the current state of a project's diary.
    '''
    project = get_object_or_404(Project, id=project_id)
    entries = DiaryEntry.objects.filter(project=project)

    context = {
        'project': project,
        'project_id': project.id,
        'existing_entries': entries,
        'help_page_number': 16,
    }
    return render(request, 'rock/view_diary.html', context)


def edit_diary(request, project_id):
    '''
    Edit the current state of a project's diary.
    '''
    project = get_object_or_404(Project, id=project_id)

    form = DiaryForm(project_instance=project)
    link_formset = ExternalLinkFormset()

    # form for edit diary
    edit_form = DiaryForm(project_instance=project, prefix="edit")
    edit_link_formset = ExternalLinkFormset(prefix="edit")

    if request.method == 'POST':
        form = DiaryForm(request.POST, project_instance=project)
        link_formset = ExternalLinkFormset(request.POST)

        if form.is_valid() and link_formset.is_valid():
            # NOTE: Need to manually save in order to add in the project
            entry = DiaryEntry()
            entry.project = project
            entry.content = form.cleaned_data['content']
            entry.start_date = form.cleaned_data['start_date']
            entry.end_date = form.cleaned_data['end_date']
            entry.outcome = form.cleaned_data['outcome']
            entry.category = form.cleaned_data['category']
            entry.save()

            # Add in the links
            entry.external_links.clear()
            for field in link_formset.cleaned_data:
                url = field.get('url')
                # Could be a blank field that was removed by the user
                if url:
                    link, _ = ExternalLink.objects.get_or_create(url=url)
                    entry.external_links.add(link)

            entry.save()

            msg = 'Diary entry created successfully.'
            if entry.outcome:
                url = reverse('editprogress', args=[project.id])
                msg += (' It looks like you have linked this entry to an outcome. You can'
                        ' head over to the <a href={}>KPI Progress</a> page if you'
                        ' would like to record a new KPI state.').format(url[0])
            messages.success(request, mark_safe(msg))
            return redirect('editdiary', project_id=project.id)
        else:
            messages.error(request, 'There were errors in your diary entry. Please see below for details.')

    entries = DiaryEntry.objects.filter(project=project).order_by('start_date')

    context = {
        'project': project,
        'project_id': project.id,
        'existing_entries': entries,
        'form': form,
        'link_formset': link_formset,
        'edit_form': edit_form,
        'edit_link_formset': edit_link_formset,
        'help_page_number': 16,
    }

    return render(request, 'rock/edit_diary.html', context)


# ----------------------------------------------------------------------------
# Progress

def view_progress(request, project_id):
    '''
    View the current state of a project's progress indicators.
    '''
    rock_user, project = _get_user_and_project(request.user, project_id)
    partners, _ = get_boundary_partners_and_markers(project)

    context = {
        'rock_user': rock_user,
        'project': project,
        'project_id': project.id,
        'partners': partners,
        'help_page_number':14,
    }
    return render(request, 'rock/view_progress.html', context)


def edit_progress(request, project_id):
    '''
    Edit the current state of a project's progress indicators.
    '''
    rock_user, project = _get_user_and_project(request.user, project_id)
    partners, _ = get_boundary_partners_and_markers(project)
    link_formset = ExternalLinkFormset()

    context = {
        'rock_user': rock_user,
        'project': project,
        'partners': partners,
        'project_id': project_id,
        'state_form': IndicatorStateForm(),
        'link_formset': link_formset,
        'help_page_number':14,
    }
    return render(request, 'rock/edit_progress.html', context)


# ----------------------------------------------------------------------------
# Final Evaluation

def view_evaluation(request, project_id):
    '''
    View the current state of a project's final evaluation.
    '''
    rock_user, project = _get_user_and_project(request.user, project_id)
    evaluation = Evaluation.objects.get(project=project)

    context = {
        'rock_user': rock_user,
        'project': project,
        'project_id': project.id,
        'evaluation': evaluation,
        'help_page_number': 18,
    }
    return render(request, 'rock/view_final_evaluation.html', context)


def edit_evaluation(request, project_id):
    '''
    Edit the current state of a project's final evaluation.
    '''
    rock_user, project = _get_user_and_project(request.user, project_id)
    evaluation = Evaluation.objects.get(project=project)

    if request.method == 'POST':
        form = EvaluationForm(
            request.POST,
            request.FILES,
            instance=evaluation
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Evaluation saved successfully')
        else:
            messages.error(request, 'There were errors in your project.')

    # GET form
    # if outcome is not set, fill it with existing outcomes
    initials = {}
    if evaluation.outcomes is None or evaluation.outcomes == '':
        outcome_str = ''
        outcomes = Outcome.objects.filter(project=project)
        for outcome in outcomes:
            outcome_str += '• ' + outcome.description +'\n\n'

        initials['outcomes'] = outcome_str

    context = {
        'rock_user': rock_user,
        'project': project,
        'project_id': project_id,
        'form': EvaluationForm(instance=evaluation, initial=initials),
        'help_page_number': 18,
    }
    return render(request, 'rock/edit_final_evaluation.html', context)


# ----------------------------------------------------------------------------
# Monitoring & Evaluation Plan

def view_monitoring(request, project_id):
    '''
    View the outcomes listed for a given project's monitoring and evaluation
    plan.
    '''
    rock_user, project = _get_user_and_project(request.user, project_id)
    # Get the list of boundary partners and their associated outcomes
    partners, markers = get_boundary_partners_and_markers(project)

    context = {
        'rock_user': rock_user,
        'project': project,
        'project_id': project.id,
        'partners': partners,
        'markers': markers,
        'help_page_number': 10,
    }
    return render(request, 'rock/view_monitoring.html', context)


def edit_monitoring(request, project_id):
    '''
    View the outcomes listed for a given project's monitoring and evaluation
    plan.
    '''
    project = get_project_if_editable(project_id, request.user)
    rock_user, project = _get_user_and_project(request.user, project_id)
    all_partners = Organisation.objects.all()

    # Get the list of this project's boundary partners and their associated outcomes
    partners, markers = get_boundary_partners_and_markers(project)

    # NOTE :: The actions of each of the following models are overwritten in the
    #         jQuery code so if things are acting strangely that's probably why!
    #         >>> This can probably be tidied up by parsing the action out of the
    #             form and then passing it to the jQuery POST.
    outcome_html = get_modal_form_html(
        request=request,
        title='',
        id_prefix='outcome',
        action='',
        form=OutcomeForm(project_instance=project)
    )

    indicator_form = OutcomeIndicatorForm()

    # generate data for filtering KPI select
    kpi_data = {}
    kpi_categories = KpiCategory.objects.all().order_by('pk')
    kpis = Kpi.objects.select_related('category').all().order_by('id')

    for kpi_category in kpi_categories:
        group = kpi_category.group
        if group not in kpi_data:
            kpi_data[group] = []
        heading = kpi_category.name
        _kpis = []
        for kpi in kpis:
            if kpi.category == kpi_category:
                _kpis.append({
                    'id': kpi.id,
                    'name': kpi.name,
                    'desc': kpi.description
                })
        kpi_data[group] += [{'heading': heading, 'kpis': _kpis}, ]

    marker_html = get_modal_form_html(
        request=request,
        title='Add A Progress Marker',
        id_prefix='marker',
        action=reverse('addprogressmarker', args=[project_id]),
        form=OutcomeMarkerForm(project_instance=project)
    )

    context = {
        'rock_user': rock_user,
        'project': project,
        'project_id': project_id,
        'all_partners': all_partners,
        'partners': partners,
        'markers': markers,
        'outcome_modal': outcome_html,
        'indicator_form': indicator_form,
        'create_marker_modal': marker_html,
        'kpi_data': json.dumps(kpi_data),
        'help_page_number': 10,
    }
    return render(request, 'rock/edit_monitoring.html', context)


# ----------------------------------------------------------------------------
# Stand alone pages

def new_project(request):
    '''
    Initial project creation screen.

    This is a simple stub that determines a project type and summary before
    redirecting the user to the project edit page.
    '''
    rock_user = get_object_or_404(RockUserDetails, user=request.user)
    form_class = NewProjectForm

    if not rock_user.is_non_guest_user:
        raise PermissionDenied

    if request.method == 'POST':
        form = NewProjectForm(request.POST, request.FILES)
        if form.is_valid():
            # Stub out the project
            project = Project()
            project.title = form.cleaned_data.get('title')
            project.summary = form.cleaned_data.get('summary')
            project.start_date = form.cleaned_data.get('start_date')
            project.end_date = form.cleaned_data.get('end_date')
            project.created_by = request.user
            project.save()

            # Stub out the rest of the reuired table entries
            rock = RockProjectDetails()
            rock.project_type = form.cleaned_data.get('project_type')
            rock.project = project
            rock.save()

            business = BusinessModel()
            business.project = project
            business.save()

            evaluation = Evaluation()
            evaluation.project = project
            evaluation.save()

            return redirect('editproject', project_id=project.id)

    # Otherwise, render the form for the user to fill in.
    # context = {'form': form_class(initial={'created_by': request.user})}
    context = {
        'rock_user': rock_user,
        'form': form_class
    }
    return render(request, 'rock/new_project.html', context)


def contact_support(request):
    '''
    Allow for users to send a support email to the main pymec repo.
    '''
    rock_user = get_object_or_404(RockUserDetails, request.user)
    form_class = ContactForm

    if request.method == 'POST':
        # Find the support email address
        if hasattr(settings, 'SUPPORT_EMAIL'):
            support_email = settings.SUPPORT_EMAIL
        else:
            # Default to the primary pymec support desk
            support_email = 'incoming+SEI-York/pymec@gitlab.com'

        context = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'nature': request.POST.get('nature'),
            'url': request.POST.get('url'),
            'details': request.POST.get('details')
        }

        template = get_template('core/fragments/contact_template.txt')
        email_body = template.render(context)

        email = EmailMessage(
            subject='New DeCart support submission',
            body=email_body,
            from_email=context['email'],
            to=[support_email],
            headers={'Reply-To': context['email']}
        )
        email.send()
        return redirect('contact')

    # Otherwise, render the form for the user to fill in.
    context = {
        'rock_user': rock_user,
        'form': form_class
    }
    return render(request, 'rock/contact.html', context)

# ----------------------------------------------------------------------------
# Stats

def stats(request):
    '''View an Employee's details'''
    rock_user = get_object_or_404(RockUserDetails, user=request.user)

    if not (rock_user.is_admin or request.user.is_superuser):
        raise PermissionDenied

    cursor = connection.cursor()
    cursor.execute("""SELECT T2.name AS "ctiy", T1.project_type, COUNT(DISTINCT T1.project_id) AS "num_of_project", 
COUNT(DISTINCT CASE WHEN (T4.partners<>'' OR T4.activities<>'' OR T4.resources<>'' OR T4.value_proposition<>'' OR T4.customer_relationship<>'' OR T4.channels<>'' OR T4.customer_segments<>'' OR T4.costs<>'' OR T4.revenues<>'') THEN T1.project_id  ELSE NULL END) AS "has_businessmodel" ,
COUNT(DISTINCT CASE WHEN T3.id IS NOT NULL THEN T1.project_id  ELSE NULL END) AS "has_fundingmechanism",
COUNT(DISTINCT CASE WHEN T7.id IS NOT NULL THEN T1.project_id  ELSE NULL END) AS "has_KPI",
COUNT(DISTINCT CASE WHEN T9.id IS NOT NULL THEN T1.project_id  ELSE NULL END) AS "has_MRE",
COUNT(DISTINCT CASE WHEN (T11.id IS NOT NULL OR T13.id IS NOT NULL) THEN T1.project_id  ELSE NULL END) AS "has_stakeholders",
COUNT(DISTINCT CASE WHEN T14.id IS NOT NULL AND LENGTH(TRIM(summary))>0 THEN T1.project_id  ELSE NULL END) AS "has_Final_Evaluation"
FROM rock_me_rockprojectdetails AS T1 LEFT JOIN rock_me_city AS T2
ON T1.city_id = T2.id LEFT JOIN rock_me_fundingmechanism AS T3 
ON T1.project_id = T3.project_id LEFT JOIN rock_me_businessmodel AS T4
ON T1.project_id = T4.project_id LEFT JOIN core_outcome AS T5
ON T1.project_id = T5.project_id LEFT JOIN core_outcome_indicators AS T6
ON T5.id = T6.outcome_id LEFT JOIN core_outcomeindicator AS T7
ON T6.outcomeindicator_id = T7.id LEFT JOIN core_outcomeindicator_states AS T8
ON T8.outcomeindicator_id = T7.id LEFT JOIN core_indicatorstate AS T9
ON T8.indicatorstate_id = T9.id LEFT JOIN core_project_boundary_partners AS T10
ON T1.project_id = T10.project_id LEFT JOIN core_organisation AS T11
ON T10.organisation_id = T11.id LEFT JOIN core_project_partner_organisations AS T12
ON T12.project_id = T1.project_id LEFT JOIN core_organisation AS T13
ON T12.organisation_id = T13.id LEFT JOIN core_evaluation AS T14
ON T14.project_id=T1.project_id
GROUP BY T1.project_type, T2.name
ORDER BY T2.name, T1.project_type
""")
    rows = cursor.fetchall()

    context = {
        'rock_user': rock_user,
        'rows': rows
    }
    return render(request, 'rock/stats.html', context)