'''
Custom DB models for the ROCK version of DeCart

See here for details on setting up the custom auth.
https://docs.djangoproject.com/en/2.0/topics/auth/customizing/
'''
from django.contrib.auth.models import User
from django.db import models

from rock_me.models import LANGUAGES
from decart.core.models import Organisation


class RockUserOrganisation(models.Model):
    '''An organisation that a ROCK user works for.'''
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class RockUserDetails(models.Model):
    '''Meta-data for ROCK users.'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, blank=True,
                                     null=True)
    role = models.CharField(
        choices=(
            ('Guest', 'Guest'),
            ('User', 'User'),
            ('Admin', 'Admin'),
            ('SuperAdmin', 'SuperAdmin'),
        ),
        max_length=10,
        default='User'
    )
    help_text_language = models.CharField(
        choices=LANGUAGES,
        max_length=max(map(len, [lang[0] for lang in LANGUAGES])),
        default=LANGUAGES[0][0],
    )

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def display_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def is_admin(self):
        '''Check to see if the current user has admin privileges.'''
        return self.role in ['Admin', 'SuperAdmin'] or self.user.is_superuser

    @property
    def is_non_guest_user(self):
        '''Used for  filtering guest users explicitly in the UI'''
        return self.role in ['User', 'Admin', 'SuperAdmin']
