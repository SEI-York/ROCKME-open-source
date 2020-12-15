'''
As far as possible, this is the common subset of models and relations
required for any DeCart system. In places where a field or method is specific
to a particular implementation (SEI, ROCK...) it is clearly marked.
'''
from django.db import models
from django.contrib.auth.models import User


class ExternalLink(models.Model):
    '''
    A link to an external resource that is associated with a project.
    '''
    url = models.URLField(max_length=255)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return self.url


class Organisation(models.Model):
    '''
    An organisation that can be associated with projects in multiple ways.

    Entries in this table can be:
        - Organisations leading/involved with projects.
        - Partner organisations on individual projects.
        - Boundary partners being influenced by projects.

    The specific role being fulfilled by an organisation may vary across
    projects and a single organisation may perform multiple roles within
    a single project.
    '''
    name = models.CharField(max_length=255, blank=True, null=True)
    scale = models.CharField(
        choices=(
            ('local', 'Local'),
            ('national', 'National'),
            ('regional', 'Regional'),
            ('global', 'Global'),
            ('other', 'Other'),
        ),
        max_length=8,
        default='local'
    )
    organisation_type = models.CharField(
        choices=(
            ('academia', 'Academia'),
            ('association', 'Association'),
            ('CSO', 'Civil Society Organisation (CSO)'),
            ('collectives', 'Collectives'),
            ('CSC', 'Cooperative and social cooperative'),
            ('cultural_association', 'Cultural Association'),
            ('funder', 'Funder'),
            ('government', 'Government'),
            ('initiatives', 'Initiatives'),
            ('local_community', 'Local Community'),
            ('NGO', 'Non-Governmental Organisation'),
            ('platform_network', 'Platform/Network'),
            ('policy_maker', 'Policy Maker'),
            ('private_sector', 'Private Sector'),
            ('social_enterprise', 'Social Enterprise'),
            ('Other', 'Other'),
        ),
        max_length=30,
        default='Other'
    )
    # Contact information and other meta-data.
    # NOTE: In light of GDPR regulations, we are only accepting details
    #       that are generic contact details for the organisation as a
    #       whole rather than personally identifyable information.
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return self.name if self.name else ''


class Project(models.Model):
    '''
    Universal details about a project being tracked in decart.
    '''
    title = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        related_name='getcreator',
        on_delete=models.CASCADE
    )
    summary = models.TextField(blank=True, null=True)
    goal = models.TextField(blank=True, null=True)
    project_leader = models.ForeignKey(
        Organisation, on_delete=models.CASCADE,
        blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    partner_organisations = models.ManyToManyField(
        Organisation,
        related_name='getpartners',
        blank=True
    )
    boundary_partners = models.ManyToManyField(
        Organisation,
        related_name='getboundarypartners',
        blank=True
    )
    to_delete = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    external_links = models.ManyToManyField(ExternalLink, blank=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return self.title


class Evaluation(models.Model):
    '''
    Evaluation of the success / impact of a project.
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    summary = models.TextField(blank=True, null=True)
    outcomes = models.TextField(blank=True, null=True)
    unexpected_changes = models.TextField(blank=True, null=True)
    future_changes = models.TextField(blank=True, null=True)

    # Financial and time management
    budget_status = models.CharField(
        choices=(
            ('Under Budget', 'Under Budget'),
            ('Within Budget', 'Within Budget'),
            ('Over Budget', 'Over Budget'),
        ),
        default='Within Budget',
        max_length=13,
    )
    budget_comments = models.TextField(blank=True, null=True)
    budget_comments_disclosure = models.BooleanField(default=True)
    time_status = models.CharField(
        choices=(
            ('Early', 'Early'),
            ('On Time', 'On Time'),
            ('Delayed', 'Delayed')
        ),
        default='On Time',
        max_length=7,
    )
    time_comments = models.TextField(blank=True, null=True)
    time_comments_disclosure = models.BooleanField(default=True)

    # Broader reflections
    team_cooperation = models.TextField(blank=True, null=True)
    team_cooperation_disclosure = models.BooleanField(default=True)
    partner_contribution = models.TextField(blank=True, null=True)
    partner_contribution_disclosure = models.BooleanField(default=True)
    communication = models.TextField(blank=True, null=True)
    communication_disclosure = models.BooleanField(default=True)
    management_recommendations = models.TextField(blank=True, null=True)
    management_recommendations_disclosure = models.BooleanField(default=True)
    tips = models.TextField(blank=True, null=True)
    tips_disclosure = models.BooleanField(default=True)
    external_links = models.ManyToManyField(ExternalLink, blank=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return str(self.project)


class IndicatorState(models.Model):
    '''
    The state of an Outcome's progress indicator at a specified point in time.
    '''
    state = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    evidence = models.TextField(blank=True, null=True)
    external_links = models.ManyToManyField(ExternalLink, blank=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return '{}: {} - {}'.format(self.state, self.start_date, self.end_date)


class KpiCategory(models.Model):
    '''KPIs have been classified into 4 categories'''
    # group
    class KpiGroup(models.TextChoices):
        ACCESSIBILITY = 'A', 'Accessibility'
        COLLABORATION = 'C', 'Collaboration'
        SUSTAINABILITY = 'S', 'Sustainability'
        LEGACY = 'L', 'Legacy'
    name = models.CharField(max_length=255)
    group = models.CharField(
        max_length=20,
        choices=KpiGroup.choices,
        default=KpiGroup.ACCESSIBILITY,
    )

    def __str__(self):
        '''Used in the django shell for introspection'''
        return '{} - {}'.format(self.get_group_display(), self.name)


class Kpi(models.Model):
    '''Each outcome indicator should be link to one KPI'''
    name = models.CharField(max_length=255)
    category = models.ForeignKey(KpiCategory, on_delete=models.CASCADE, related_name='kpis')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class OutcomeIndicator(models.Model):
    '''An indicator for evaluating the progress of a given Outcome'''
    name = models.CharField(max_length=255, blank=True)
    kpi = models.ForeignKey(Kpi, on_delete=models.CASCADE, related_name='indicators')
    measure = models.CharField(max_length=255)
    verification = models.CharField(max_length=255)
    baseline = models.CharField(max_length=255)
    baseline_date = models.DateField(blank=True, null=True)
    states = models.ManyToManyField(IndicatorState, blank=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        return '{} ({})'.format(self.name, self.pk)


class Outcome(models.Model):
    '''A project outcome associated with a Boundary Partner'''
    description = models.TextField(blank=True, null=True)
    boundary_partner = models.ForeignKey(
        Organisation, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    indicators = models.ManyToManyField(OutcomeIndicator, blank=True)

    def __str__(self):
        '''Used in the django shell for introspection'''
        short_desc = self.description[:30]
        return '{}: {}'.format(self.boundary_partner, short_desc)


class OutcomeProgressMarker(models.Model):
    '''A progress marker for tracking a given outcome'''
    description = models.TextField(blank=True, null=True)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    level = models.CharField(
        choices=(
            ('Early', 'Early (Expected to see)'),
            ('Increasing', 'Increasing (Like to see)'),
            ('Deep', 'Deep (Love to see)')
        ),
        default='Early',
        max_length=10,
    )
    planned_completion_date = models.DateField(blank=True, null=True)
