from django import forms
from django.contrib.auth.models import User

from decart.core.forms import ProjectForm
from decart.core.models import Organisation, Outcome
from rock_user.models import RockUserDetails

from .models import BusinessModel, RockProjectDetails, FundingMechanism, \
    DiaryEntry


class RockProjectForm(ProjectForm):
    '''Customise the default DeCart ProjectForm using RockUser details'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only display users that are ROCK users (i.e not admin)
        _user_list = RockUserDetails.objects.all().prefetch_related('user')
        user_id_list = [r.user.id for r in _user_list]
        self.fields['project_leader'].queryset = User.objects.all().filter(
            id__in=user_id_list
        )


class NewProjectForm(forms.Form):
    '''Form for users to send a support request'''
    title = forms.CharField(
        label='Title', required=True,
        widget=forms.TextInput(
            attrs={'style': 'width: 99% !important; resize: vertical !important;'}
        )
    )
    project_type = forms.ChoiceField(
        label='Project Type',
        choices=[
            ('ACTIVITY', 'Activity'),
            # ('TASK', 'Task'),
            ('CASE-STUDY', 'Case Study'),
        ],
        required=True
    )
    summary = forms.CharField(
        label='Project Summary',
        widget=forms.Textarea(
            attrs={'style': 'width: 99% !important; resize: vertical !important;'}
        ),
        help_text='Give a brief summary of the project.'
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if end is not None and start > end:
            raise forms.ValidationError(
                'Start date can not be after end date.'
            )


class RockProjectDetailsForm(forms.ModelForm):
    class Meta:
        model = RockProjectDetails
        exclude = ['project',]
        widgets = {
            'associated_wps': forms.SelectMultiple(
                attrs={'class': 'select2-selection-box'}
            ),
            'consortium_members': forms.SelectMultiple(
                attrs={'class': 'select2-selection-box'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['lead_administrative_organisation'].queryset =  Organisation.objects.all().order_by('name')
        self.fields['lead_scientific_organisation'].queryset =  Organisation.objects.all().order_by('name')


class BusinessModelForm(forms.ModelForm):
    class Meta:
        model = BusinessModel
        exclude = ['project']
        widgets = {
            'partners': forms.Textarea(attrs={'placeholder': 'Who are your key partners/suppliers? What are the motivations for the partnerships?'}),
            'activities': forms.Textarea(attrs={'placeholder': 'What key activities does your value proposition require? What activities are important the most in distribution channels, customer relationships, revenue stream…?'}),
            'resources': forms.Textarea(attrs={'placeholder': 'What key resources does your value proposition require? What resources are important the most in distribution channels, customer relationships, revenue stream…?'}),
            'value_proposition': forms.Textarea(attrs={'placeholder': 'What core value do you deliver to the customer? Which customer needs are you satisfying?'}),
            'customer_relationship': forms.Textarea(attrs={'placeholder': 'What relationship that the target customer expects you to establish? How can you integrate that into your business in terms of cost and format?'}),
            'channels': forms.Textarea(attrs={'placeholder': 'Through which channels that your customers want to be reached? Which channels work best? How much do they cost? How can they be integrated into your and your customers’ routines?'}),
            'customer_segments': forms.Textarea(attrs={'placeholder': 'Which classes are you creating values for? Who is your most important customer?'}),
            'costs': forms.Textarea(attrs={'placeholder': 'What are the most cost in your business? Which key resources/ activities are most expensive?'}),
            'revenues': forms.Textarea(attrs={'placeholder': 'For what value are your customers willing to pay? What and how do they recently pay? How would they prefer to pay? How much does every revenue stream contribute to the overall revenues?'}),
        }


class FundingMechanismForm(forms.ModelForm):
    class Meta:
        model = FundingMechanism
        exclude = ['project']


class DiaryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        exclude = ['project', 'external_links']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project_instance')
        super().__init__(*args, **kwargs)
        self.fields['outcome'].queryset = Outcome.objects.filter(project=project)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if end and start > end:
            raise forms.ValidationError(
                'Start date can not be after end date.'
            )
