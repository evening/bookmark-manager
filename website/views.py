from django.shortcuts import redirect
from django.views import generic
from website.models import Post, Account
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm, AddPostForm, EditProfileForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
    LoginView,
)
from django.db.models import Q
import json
from django.forms.models import model_to_dict

website_title = "Bookmark Manager :: "


def delete(request):
    post_id = request.POST.get("id")
    query = Post.objects.get(id=post_id)
    if query.author == request.user:
        query.delete()
    return HttpResponse(status=200)


def view_archive(request, post_id):
    try:
        archive_obj = Post.objects.get(pk=post_id).archive
        return HttpResponse(archive_obj.content, status=200)
    except Post.DoesNotExist:
        return HttpResponse("Not archived", status=200)


def edit(request):
    r = request.POST
    p = Post.objects.get(id=r.get("id"))
    for k, v in r.items():
        if hasattr(p, k):
            setattr(p, k, v)
    p.save()
    return HttpResponse(json.dumps(model_to_dict(p)), status=200)


def fav(request):
    post_id = request.POST.get("id")
    query = Post.objects.get(id=post_id)
    if query.author == request.user:
        query.fav ^= True
        query.save()
    return HttpResponse(status=200)


class LoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Log in"
        data["title"] = title
        return data


class PasswordChangeView(PasswordChangeView):
    template_name = "change_password.html"
    success_url = reverse_lazy("account")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Change password"
        data["title"] = title
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
        data["title"] = title
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
                .filter(
                    Q(title__icontains=q)
                    | Q(url__icontains=q)
                    | Q(archive__content__iregex=rf"\b{q}\b")  # search archive/snapshot
                )
                .order_by("-date")
            )
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Searching " + self.request.GET.get("q")
        data["title"] = title
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
        data["title"] = title
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
        data["title"] = title
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
        data["title"] = title
        return data
