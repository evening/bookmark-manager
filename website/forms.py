from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Account

from .models import Post


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
    class Meta:
        model = Post
        fields = ("title", "url", "fav", "to_read", "public")


class EditProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        for fieldname in ["username", "email"]:
            self.fields[fieldname].help_text = None

    class Meta:
        model = Account
        fields = ("username", "email")
