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
        self.fields["public"].label = "Enable public profile"

    class Meta:
        model = Account
        fields = ("username", "email", "public")


class AccountDeleteForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(), label="Enter password")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Confirm password")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(AccountDeleteForm, self).__init__(*args, **kwargs)

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("passwords do not match")
        if not self.request.user.check_password(password2):
            raise forms.ValidationError("invalid password")
        return password2
