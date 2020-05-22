from django.shortcuts import render, redirect
from django.views import generic
from .models import Post
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm, AddPostForm, EditProfileForm
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import PasswordChangeForm
from .models import Account
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
    LoginView,
)
from django.db.models import Q
from django.http import HttpResponseRedirect

website_title = "Bookmark Manager :: "

# see if there are better ways to do this
def delete(request, post_id):
    query = Post.objects.get(id=post_id)
    if query.author == request.user:
        query.delete()
    return redirect("index")
    # catch exception
    
# see if there are better ways to do this
def fav(request, post_id):
    query = Post.objects.get(id=post_id)
    if query.author == request.user:
        query.fav ^= True
        query.save()
    return redirect("index")
    # catch exception


class LoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Log in"
        data['title'] = title
        return data


class PasswordChangeView(PasswordChangeView):
    template_name = "change_password.html"
    success_url = reverse_lazy("account")
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Change password"
        data['title'] = title
        return data


class PasswordChangeDoneView(PasswordChangeDoneView):
    template_view = "change_password.html"


def autoadd(request):
    Post.objects.create(**request.GET.dict(), author=request.user)
    return HttpResponseRedirect(request.GET.get("url"))


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = "index.html"
    model = Post
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by("-date")
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title
        data['title'] = title
        return data

class SearchView(generic.ListView):
    template_name = "search.html"
    model = Post
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get("q")
        if q:
            return (
                Post.objects.filter(author=self.request.user)
                .filter(Q(title__contains=q) | Q(url__contains=q))
                .order_by("-date")
            )
        return Post.objects.none()
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Searching " + self.request.GET.get("q")
        print(data)
        data['title'] = title
        return data

class SignUp(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("index")
    template_name = "signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("index")
        return super(SignUp, self).dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Sign up"
        data['title'] = title
        return data

class EditProfile(LoginRequiredMixin, generic.UpdateView):
    form_class = EditProfileForm
    template_name = "edit_profile.html"
    success_url = reverse_lazy("account")

    def get_object(self, queryset=None):
        return self.request.user
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Change account information"
        data['title'] = title
        return data

class Add(LoginRequiredMixin, generic.CreateView):
    template_name = "add.html"
    form_class = AddPostForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return redirect("index")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Add new link"
        data['title'] = title
        return data
