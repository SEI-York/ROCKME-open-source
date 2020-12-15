from itertools import chain

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset
from crispy_forms.bootstrap import FormActions, InlineRadios

from .models import Project, Evaluation, Organisation, \
    Outcome, OutcomeProgressMarker, OutcomeIndicator, \
    IndicatorState, ExternalLink, Kpi, KpiCategory


class ContactForm(forms.Form):
    '''Form for users to send a support request'''
    name = forms.CharField(label='Name', required=True)
    email = forms.EmailField(label='Email', required=True)
    nature = forms.ChoiceField(
        label='Nature of the issue',
        choices=[
            ('bug', 'Bug'),
            ('feature', 'Feature Request'),
            ('error', 'Page Error')
        ],
        required=True
    )
    url = forms.URLField(label='URL', required=True)
    details = forms.CharField(
        label='Details (please provide as much information as possible)',
        widget=forms.Textarea()
    )

    # Crispy_forms
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_class = 'form-horizontal'
    # helper.label_class = 'col-sm-2'
    # helper.field_class = 'col-sm-6'
    helper.layout = Layout(
        Field('name', css_class='input-sm'),
        Field('email', css_class='input-sm'),
        InlineRadios('nature'),
        Field('url', css_class='input-sm'),
        Field('details', rows=5),
        FormActions(Submit('submit', 'submit', css_class='btn-primary'))
    )


class AddPartnerForm(forms.Form):
    '''Form for users to add a pre-existing partner to a project'''
    name = forms.CharField(label='Name', required=True)
    email = forms.EmailField(label='Email', required=True)
    nature = forms.ChoiceField(
        label='Nature of the issue',
        choices=[
            ('bug', 'Bug'),
            ('feature', 'Feature Request'),
            ('error', 'Page Error')
        ],
        required=True
    )
    url = forms.URLField(label='URL', required=True)
    details = forms.CharField(
        label='Details (please provide as much information as possible)',
        widget=forms.Textarea()
    )

    # Crispy_forms
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_class = 'form-horizontal'
    # helper.label_class = 'col-sm-2'
    # helper.field_class = 'col-sm-6'
    helper.layout = Layout(
        Field('name', css_class='input-sm'),
        Field('email', css_class='input-sm'),
        InlineRadios('nature'),
        Field('url', css_class='input-sm'),
        Field('details', rows=5),
        FormActions(Submit('submit', 'submit', css_class='btn-primary'))
    )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = [
            'completed', 'created_by',
            'partner_organisations', 'boundary_partners'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        exclude = []


class EvaluationForm(forms.ModelForm):
    budget_comments_disclosure = forms.BooleanField(required=False, label="Tick for public disclosure")
    time_comments_disclosure = forms.BooleanField(required=False, label="Tick for public disclosure")
    team_cooperation_disclosure = forms.BooleanField(required=False, label="Tick for public disclosure")
    partner_contribution_disclosure = forms.BooleanField(required=False, label="Tick for public disclosure")
    communication_disclosure = forms.BooleanField(required=False, label="Tick for public disclosure")
    management_recommendations_disclosure = forms.BooleanField(required=False, label="Tick for public disclosure")
    tips_disclosure = forms.BooleanField(required=False, label="Tick for public disclosure")
    class Meta:
        model = Evaluation
        exclude = ['project']


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = Outcome
        exclude = ['project', 'indicators']
        widgets = {
            'boundary_partner': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project_instance')
        super().__init__(*args, **kwargs)

        self.fields['boundary_partner'].queryset = project.boundary_partners.all()


class OutcomeMarkerForm(forms.ModelForm):
    class Meta:
        model = OutcomeProgressMarker
        exclude = []

    planned_completion_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project_instance')
        super().__init__(*args, **kwargs)

        self.fields['outcome'].queryset = Outcome.objects.filter(project=project)


class OutcomeIndicatorForm(forms.ModelForm):
    class Meta:
        model = OutcomeIndicator
        exclude = ['states']

    baseline_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    name = forms.CharField(widget=forms.HiddenInput(), required=False)
    kpi = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # populate kpi list
        choices = (('', '------- Select a KPI -------'), )

        kpi_categories = KpiCategory.objects.all().order_by('id')
        kpis = Kpi.objects.select_related('category').all().order_by('id')

        for kpi_category in kpi_categories:
            heading = kpi_category.name
            _kpis = ()
            for kpi in kpis:
                if kpi.category == kpi_category:
                    _kpis += ((kpi.id, kpi.name),)
            choices += ((heading, _kpis), )

        self.fields['kpi'].choices = choices

    def clean_kpi(self):
        kpi_id = self.cleaned_data['kpi']
        return Kpi.objects.get(pk=kpi_id)


class IndicatorStateForm(forms.ModelForm):
    class Meta:
        model = IndicatorState
        exclude = ['indicator']

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )


class ExternalLinkForm(forms.ModelForm):
    class Meta:
        model = ExternalLink
        exclude = []


# Allow for multiple external links to be recorded in a single form.
ExternalLinkFormset = forms.formset_factory(
    form=ExternalLinkForm,
    extra=1
)
