'''
ROCK specific DeCart models.
'''
from django.db import models

from decart.core.models import Project, Outcome, ExternalLink, Organisation


# Languages used to provide help text in the site
LANGUAGES = (
    ('English', 'English'),
    ('Italian', 'Italian'),
    ('French', 'French'),
)

DIARY_CHOICES = (
    ('Note', 'Note'),
    ('Public Event', 'Public Event'),
    ('Media Coverage', 'Media Coverage'),
    ('Publication', 'Publication'),
    ('Meeting', 'Meeting'),
    ('Data Collection', 'Data Collection'),
)


class City(models.Model):
    '''A city where work is taking place'''
    name = models.CharField(max_length=255)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return self.name


class WorkPackage(models.Model):
    '''One of the work pagages within ROCK'''
    package_type = models.CharField(max_length=8)
    description = models.TextField()
    due_date = models.DateField()

    def __str__(self):
        '''Used in the django shell for introspection'''
        return self.description


class RockProjectDetails(models.Model):
    '''
    ROCK specific details about a project being tracked in DeCart.
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    project_type = models.CharField(
        choices=(
            ('ACTIVITY', 'Activity'),
            ('TASK', 'Task'),
            ('CASE-STUDY', 'Case Study'),
        ),
        max_length=10,
        default='ACTIVITY',
    )
    # Only have work package information for Tasks
    work_package = models.ForeignKey(
        WorkPackage,
        on_delete=models.CASCADE,
        related_name='getclaim_workpackage',
        blank=True, null=True
    )
    associated_wps = models.ManyToManyField(
        WorkPackage,
        related_name='getclaim_associatedwps',
        blank=True
    )
    lead_administrative_organisation = models.ForeignKey(
        Organisation, blank=True, null=True,
        related_name='projects_administrative_lead',
        on_delete=models.SET_NULL
    )
    lead_scientific_organisation = models.ForeignKey(
        Organisation, blank=True, null=True,
        related_name='projects_scientific_lead',
        on_delete=models.SET_NULL
    )
    contact_person = models.TextField(blank=True, null=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE,
        blank=True, null=True
    )
    budget_currency = models.CharField(
        choices=(
            ('EUR', 'EUR'),
            ('GBP', 'GBP'),
            ('USD', 'USD'),
            ('SEK', 'SEK'),
            ('THB', 'THB'),
            ('EEK', 'EEK'),
            ('AUD', 'AUD'),
            ('CAD', 'CAD'),
            ('NOK', 'NOK'),
        ),
        max_length=3,
        default='EUR',
    )
    budget_amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return self.project.title


class BusinessModel(models.Model):
    '''
    A business model for a given activity in ROCK.
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    partners = models.TextField(blank=True, null=True)
    activities = models.TextField(blank=True, null=True)
    resources = models.TextField(blank=True, null=True)
    value_proposition = models.TextField(blank=True, null=True)
    customer_relationship = models.TextField(blank=True, null=True)
    channels = models.TextField(blank=True, null=True)
    customer_segments = models.TextField(blank=True, null=True)
    costs = models.TextField(blank=True, null=True)
    revenues = models.TextField(blank=True, null=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return self.project.title


class FundingMechanism(models.Model):
    '''
    A source of funding for a given project.
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    mechanism = models.CharField(
        choices=(
            ('Loans', 'Loans'),
            ('Grants', 'Grants'),
            ('Crowdfunding', 'Crowdfunding'),
            ('Mutual Funding', 'Mutual Funding'),
            ('Microfinance', 'Microfinance'),
            ('Joint Venture', 'Joint Venture'),
            ('Venture Capital', 'Venture Capital'),
            ('Angel Investors', 'Angel Investors'),
            ('(Direct) Consulting Services', '(Direct) Consulting Services'),
            ('(Direct) Technologies', '(Direct) Technologies'),
            ('Insurances', 'Insurances'),
            ('Direct Investment', 'Direct Investment'),
            ('Foreign Direct Investment', 'Foreign Direct Investment'),
            ('Publicly leveraged private loans', 'Publicly leveraged private loans'),
            ('Publicly guaranteed private loans', 'Publicly guaranteed private loans'),
            ('Public Private Partnership', 'Public Private Partnership'),
            ('Sponsorships', 'Sponsorships'),
            ('Other', 'Other (Please specify below)')
        ),
        max_length=33,
        default='Loans',
    )
    other_details = models.CharField(max_length=255, blank=True, null=True)
    provider = models.CharField(max_length=255, blank=True, null=True)
    provider_ownership = models.CharField(
        choices=(
            ('Private', 'Private'),
            ('Public', 'Public'),
            ('Part private and part public', 'Part private and part public'),
            ('Public–private partnership (PPP)', 'Public–private partnership (PPP)'),
            ('Other', 'Other'),
        ),
        max_length=32,
        default='Private',
    )
    provider_type = models.CharField(
        choices=(
            ('Bank', 'Bank'),
            ('Insurance', 'Insurance'),
            ('Angel Investor', 'Angel Investor'),
            ('Investment Management Company', 'Investment Management Company'),
            ('Other Private Company (From Financial Sector)',
             'Other Private Company (From Financial Sector)'),
            ('Other Private Company (Not From Financial Sector)',
             'Other Private Company (Not From Financial Sector)'),
            ('Public Private Partnership', 'Public Private Partnership'),
            ('City', 'City'),
            ('Province / Department / Metropolitan area (NUTS 3)',
             'Province / Department / Metropolitan area (NUTS 3)'),
            ('Region (NUTS 2)', 'Region (NUTS 2)'),
            ('National', 'National'),
            ('European', 'European'),
            ('UNESCO or other UN agencies', 'UNESCO or other UN agencies'),
            ('World Bank', 'World Bank'),
            ('Other', 'Other')
        ),
        max_length=50,
        default='Bank',
    )
    currency = models.CharField(
        choices=(
            ('EUR', 'EUR'),
            ('GBP', 'GBP'),
            ('USD', 'USD'),
            ('SEK', 'SEK'),
            ('THB', 'THB'),
            ('EEK', 'EEK'),
            ('AUD', 'AUD'),
            ('CAD', 'CAD'),
            ('NOK', 'NOK'),
        ),
        max_length=3,
        default='EUR',
    )
    amount = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return '{}: {}'.format(self.project.title, self.provider)


class HelpText(models.Model):
    '''Help text for a given form field'''
    table = models.CharField(max_length=255)
    field = models.CharField(max_length=255)
    language = models.CharField(
        choices=LANGUAGES,
        max_length=255,
        default=LANGUAGES[0],
    )
    help_text = models.TextField()


class DiaryEntry(models.Model):
    '''
    A note of what has been done to advance the project.
    NOTE: This makes use of a Postgres only field type:
        https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#daterangefield
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    content = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    outcome = models.ForeignKey(Outcome, blank=True, null=True, on_delete=models.CASCADE)
    category = models.CharField(
        choices=DIARY_CHOICES,
        max_length=max([len(c[0]) for c in DIARY_CHOICES]),
        default=DIARY_CHOICES[0][0],
    )
    external_links = models.ManyToManyField(ExternalLink, blank=True)

    def __str__(self):
        return '{}: {}'.format(self.project, self.pk)
