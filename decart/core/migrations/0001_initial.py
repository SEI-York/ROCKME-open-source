# Generated by Django 3.0.6 on 2020-10-13 23:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=255)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('evidence', models.TextField(blank=True, null=True)),
                ('external_links', models.ManyToManyField(blank=True, to='core.ExternalLink')),
            ],
        ),
        migrations.CreateModel(
            name='Kpi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='KpiCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('group', models.CharField(choices=[('A', 'Accessibility'), ('C', 'Collaboration'), ('S', 'Sustainability'), ('L', 'Legacy')], default='A', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('scale', models.CharField(choices=[('local', 'Local'), ('national', 'National'), ('regional', 'Regional'), ('global', 'Global'), ('other', 'Other')], default='local', max_length=8)),
                ('organisation_type', models.CharField(choices=[('academia', 'Academia'), ('association', 'Association'), ('CSO', 'Civil Society Organisation (CSO)'), ('collectives', 'Collectives'), ('CSC', 'Cooperative and social cooperative'), ('cultural_association', 'Cultural Association'), ('funder', 'Funder'), ('government', 'Government'), ('initiatives', 'Initiatives'), ('local_community', 'Local Community'), ('NGO', 'Non-Governmental Organisation'), ('platform_network', 'Platform/Network'), ('policy_maker', 'Policy Maker'), ('private_sector', 'Private Sector'), ('social_enterprise', 'Social Enterprise'), ('Other', 'Other')], default='Other', max_length=30)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('website', models.URLField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('other_info', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('boundary_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organisation')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('goal', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('to_delete', models.BooleanField(default=False)),
                ('complete', models.BooleanField(default=False)),
                ('boundary_partners', models.ManyToManyField(blank=True, related_name='getboundarypartners', to='core.Organisation')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='getcreator', to=settings.AUTH_USER_MODEL)),
                ('external_links', models.ManyToManyField(blank=True, to='core.ExternalLink')),
                ('partner_organisations', models.ManyToManyField(blank=True, related_name='getpartners', to='core.Organisation')),
                ('project_leader', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Organisation')),
            ],
        ),
        migrations.CreateModel(
            name='OutcomeProgressMarker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('level', models.CharField(choices=[('Early', 'Early (Expected to see)'), ('Increasing', 'Increasing (Like to see)'), ('Deep', 'Deep (Love to see)')], default='Early', max_length=10)),
                ('planned_completion_date', models.DateField(blank=True, null=True)),
                ('outcome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Outcome')),
            ],
        ),
        migrations.CreateModel(
            name='OutcomeIndicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('measure', models.CharField(max_length=255)),
                ('verification', models.CharField(max_length=255)),
                ('baseline', models.CharField(max_length=255)),
                ('baseline_date', models.DateField(blank=True, null=True)),
                ('kpi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicators', to='core.Kpi')),
                ('states', models.ManyToManyField(blank=True, to='core.IndicatorState')),
            ],
        ),
        migrations.AddField(
            model_name='outcome',
            name='indicators',
            field=models.ManyToManyField(blank=True, to='core.OutcomeIndicator'),
        ),
        migrations.AddField(
            model_name='outcome',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Project'),
        ),
        migrations.AddField(
            model_name='kpi',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kpis', to='core.KpiCategory'),
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(blank=True, null=True)),
                ('outcomes', models.TextField(blank=True, null=True)),
                ('unexpected_changes', models.TextField(blank=True, null=True)),
                ('future_changes', models.TextField(blank=True, null=True)),
                ('budget_status', models.CharField(choices=[('Under Budget', 'Under Budget'), ('Within Budget', 'Within Budget'), ('Over Budget', 'Over Budget')], default='Within Budget', max_length=13)),
                ('budget_comments', models.TextField(blank=True, null=True)),
                ('budget_comments_disclosure', models.BooleanField(default=True)),
                ('time_status', models.CharField(choices=[('Early', 'Early'), ('On Time', 'On Time'), ('Delayed', 'Delayed')], default='On Time', max_length=7)),
                ('time_comments', models.TextField(blank=True, null=True)),
                ('time_comments_disclosure', models.BooleanField(default=True)),
                ('team_cooperation', models.TextField(blank=True, null=True)),
                ('team_cooperation_disclosure', models.BooleanField(default=True)),
                ('partner_contribution', models.TextField(blank=True, null=True)),
                ('partner_contribution_disclosure', models.BooleanField(default=True)),
                ('communication', models.TextField(blank=True, null=True)),
                ('communication_disclosure', models.BooleanField(default=True)),
                ('management_recommendations', models.TextField(blank=True, null=True)),
                ('management_recommendations_disclosure', models.BooleanField(default=True)),
                ('tips', models.TextField(blank=True, null=True)),
                ('tips_disclosure', models.BooleanField(default=True)),
                ('external_links', models.ManyToManyField(blank=True, to='core.ExternalLink')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Project')),
            ],
        ),
    ]
