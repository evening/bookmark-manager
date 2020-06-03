import copy
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
)
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import Http404

from website.forms import AddPostForm, EditProfileForm, SignUpForm
from website.models import Archive, Post, Account

website_title = "Bookmark Manager :: "


def delete(request):
    post_id = request.POST.get("id")
    query = Post.objects.get(id=post_id)
    if query.author == request.user:
        query.delete()
    return HttpResponse(status=200)


def view_archive(request, uuid):
    try:
        archive_obj = Archive.objects.get(id=uuid)
        return HttpResponse(
            archive_obj.content, status=200, content_type=archive_obj.content_type
        )
    except Archive.DoesNotExist:
        return HttpResponse("Not archived", status=500)


def edit(request):
    r = request.POST
    p = Post.objects.get(id=r.get("id"))
    to_delete = None
    if (
        p.archive and r.get("url") != p.url
    ):  # if changing url when there's an archive, just delete
        to_delete = p.archive
        p.archive = None

    for k, v in r.items():
        if hasattr(p, k):
            setattr(p, k, v)
    p.save()
    if to_delete:
        to_delete.delete()
    ret = model_to_dict(p)
    ret.pop("archive")
    return HttpResponse(json.dumps(ret), status=200)


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
    r = copy.deepcopy(request.GET.dict())
    to_archive = r.pop("archive", None)
    p = Post.objects.create(**r, author=request.user)
    if to_archive:
        p.queue_download()
    return HttpResponse(status=200)


class ProfileView(generic.ListView):
    template_name = "index.html"
    model = Post
    context_object_name = "posts"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not self.kwargs.get("username"):
            if request.user.is_authenticated:
                return redirect("profile", username=request.user)
            return redirect("login")

        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        try:
            user = Account.objects.get(username=self.kwargs.get("username"))
        except Account.DoesNotExist:
            raise Http404
        return Post.objects.filter(author=user).order_by("-date")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title
        data["title"] = title
        return data


# TODO: search in other profiles
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
        self.p_obj = form.save(commit=False)
        self.p_obj.author = self.request.user
        self.p_obj.save()
        if self.request.POST.get("archive"):
            self.p_obj.queue_download()
        return redirect("index")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Add new link"
        data["title"] = title
        return data
