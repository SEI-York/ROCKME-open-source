from django import forms
from allauth.account.forms import SignupForm

from .models import RockUserDetails


class RockUserForm(forms.ModelForm):
    class Meta:
        model = RockUserDetails
        exclude = []


class RocuUserSignupForm(SignupForm):

    first_name = forms.CharField(
        label='First name',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        label='Last name',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'}),
    )

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(RocuUserSignupForm, self).save(request)

        # create user details record
        rock_details = RockUserDetails(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        rock_details.save()

        # You must return the original result.
        return user
