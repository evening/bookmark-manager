from django import forms
from django.contrib.auth.forms import UserCreationForm

from website.models import Account, Post, Tag
from website.utils import clean_tags


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
    snapshot = forms.BooleanField(initial=False, required=False)
    close_after = forms.BooleanField(required=False, widget=forms.HiddenInput())
    tags = forms.CharField(label="Tags", required=False)

    class Meta:
        model = Post
        fields = ("title", "url", "fav")

    def __init__(self, *args, **kwargs):
        url_value = kwargs.pop("url", None)
        close_after_value = kwargs.pop("close_after", None)
        title_value = kwargs.pop("title", None)
        super(AddPostForm, self).__init__(*args, **kwargs)
        self.fields["url"].widget.attrs = {"value": url_value}
        self.fields["title"].widget.attrs = {"value": title_value}
        self.fields["close_after"].widget.attrs = {"value": close_after_value}
        self.fields["tags"].widget.attrs = {"name": "tags"}
        self.fields["tags"].widget.attrs = {
            "onkeyup": "predict_tag()",
            "onkeydown": "no_tab()",
            "onblur": "remove_suggestions()",
        }

    def clean_tags(self):
        cleaned_data = super().clean()
        return clean_tags(self.cleaned_data["tags"])


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
        self.user = kwargs.pop("user", None)
        super(AccountDeleteForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("passwords do not match")
        if not self.user.check_password(password2):
            raise forms.ValidationError("invalid password")
        return password2
