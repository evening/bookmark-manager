from django import forms
from django.contrib.auth.forms import UserCreationForm

from website.models import Account, Post


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = None

    class Meta:
        model = Account
        fields = ("email", "username", "password1", "password2")


class AddPostForm(forms.ModelForm):
    archive = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = Post
        fields = ("title", "url", "fav")

    def __init__(self, *args, **kwargs):
        super(AddPostForm, self).__init__(*args, **kwargs)
        self.fields["url"].widget.attrs = {"value": "http://"}


class EditProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        for fieldname in ["username", "email"]:
            self.fields[fieldname].help_text = None

    class Meta:
        model = Account
        fields = ("username", "email")
