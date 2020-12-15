'''
Some quick hacks to enable extra functionality in templates.

For more details on writing custom filters see:
    https://docs.djangoproject.com/en/2.0/howto/custom-template-tags/
'''
from django import template

from decart.core.models import Project
from rock_me.models import RockProjectDetails


register = template.Library()


@register.simple_tag
def pending_deletion_count():
    '''Get a count of the projects currently pending deletion.'''
    return len(Project.objects.filter(to_delete=True))


