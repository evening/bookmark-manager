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
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from website.forms import (
    AddPostForm,
    EditProfileForm,
    SignUpForm,
    AccountDeleteForm,
    AddPostForm,
)
from website.models import Account, Archive, Post, Tag
from website.utils import (
    clean_tags,
    create_tags,
    tags_as_strings,
    clean_tags_str,
    clean_create,
)

website_title = "Bookmark Manager :: "


def delete(request):
    post_id = request.POST.get("id")
    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404

    if not p.author == request.user:
        return HttpResponse("Not authorized", status=403)
    p.delete()
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
    r = copy.deepcopy(request.POST)
    try:
        p = Post.objects.get(id=r.get("id"))
    except Post.DoesNotExist:
        raise Http404

    if not p.author == request.user:
        return HttpResponse("Not authorized", status=403)

    archive_delete = None
    if (
        p.archive and r.get("url") != p.url
    ):  # if changing url when there's an archive, just delete
        archive_delete = p.archive
        p.archive = None

    new_tags = clean_create(r.pop("tags", list())[0])
    p_tags = p.tags.all()
    for t in set(new_tags) - set(p_tags):
        p.tags.add(t)
    for t in set(p_tags) - set(new_tags):
        p.tags.remove(t)

    for k, v in r.items():
        if hasattr(p, k):
            setattr(p, k, v)

    if archive_delete:
        to_delete.delete()

    p.save()
    ret = model_to_dict(p)
    ret["tags"] = list(map(lambda t: t.name, ret["tags"]))
    ret["archive"] = str(ret["archive"])

    return HttpResponse(json.dumps(ret), status=200)


def data(request, id):
    try:
        p = Post.objects.get(id=id)
    except Post.DoesNotExist:
        raise Http404
    if not p.author == request.user:
        return HttpResponse("Not authorized", status=403)
    ret = model_to_dict(p)
    ret["tags"] = list(map(lambda t: t.name, ret["tags"]))
    ret["archive"] = str(ret["archive"])
    return HttpResponse(json.dumps(ret), status=200)


def fav(request):
    post_id = request.POST.get("id")
    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404

    if not p.author == request.user:
        return HttpResponse("Not authorized", status=403)

    p.fav ^= True
    p.save()
    return HttpResponse(status=200)


class LoginView(LoginView):
    template_name = "forms/login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Log in"
        data["title"] = title
        return data


class PasswordChangeView(PasswordChangeView):
    template_name = "forms/change_password.html"
    success_url = reverse_lazy("account")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Change password"
        data["title"] = title
        return data


class AccountDelete(LoginRequiredMixin, generic.FormView):
    form_class = AccountDeleteForm
    template_name = "forms/account_delete.html"
    success_url = reverse_lazy("account_delete")

    def get_form_kwargs(self):
        kw = super(AccountDelete, self).get_form_kwargs()
        kw["request"] = self.request
        return kw

    def form_valid(self, form):
        self.request.user.is_active = False
        self.request.user.save()
        return redirect("index")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Delete account"
        data["title"] = title
        return data


def autoadd(request):
    r = copy.deepcopy(request.GET.dict())
    to_archive = r.pop("archive", None)
    p = Post.objects.create(**r, author=request.user)
    if to_archive:
        p.queue_download()
    return HttpResponse(status=200)


class ProfileView(generic.ListView):
    template_name = "profile.html"
    model = Post
    context_object_name = "posts"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get("username"):
            return super(ProfileView, self).dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect("login")
        return redirect("profile", username=request.user)

    def get_queryset(self):
        try:
            user = Account.objects.get(username=self.kwargs.get("username"))
        except Account.DoesNotExist:
            raise Http404
        if not user.is_active:  # don't show deleted accounts
            raise Http404
        ret = Post.objects.filter(author=user)
        if self.request.user.is_authenticated:
            ret = ret.filter(Q(author__public=True) | Q(author=self.request.user))
        else:
            ret = ret.filter(author__public=True)

        q = self.request.GET.get("q", None)
        if q:
            ret = ret.filter(
                Q(title__icontains=q)
                | Q(url__icontains=q)
                | Q(archive__content__iregex=rf"\b{q}\b")  # search archive/snapshot
            )
        return ret.order_by("-date")

    def get_context_data(self, **kwargs):
        from django.db.models import Count

        data = super().get_context_data(**kwargs)
        title = website_title
        q = self.request.GET.get("q")
        if q:
            title = title + "Searching " + self.request.GET.get("q", "")
        data["title"] = title
        # if i decide to make specific urls private instead of accounts, this will leak total number
        data["count"] = Post.objects.filter(
            author__username=self.kwargs.get("username")
        ).count()
        tags_sidebar = Tag.objects.filter(
            post_tag__author__username=self.kwargs.get("username")
        )
        if self.request.user.is_authenticated:
            tags_sidebar = tags_sidebar.filter(
                Q(post_tag__author__public=True) | Q(post_tag__author=self.request.user)
            ).distinct()
        else:
            tags_sidebar = tags_sidebar.filter(post_tag__author__public=True).distinct()
        data["tags"] = tags_sidebar.annotate(t_count=Count("post_tag")).order_by(
            "-t_count"
        )  # sort by usage
        return data


class TagView(ProfileView):
    def get_queryset(self):
        tag = self.kwargs.get("tag")
        try:
            tag = Tag.objects.get(name=tag)
            data = super().get_queryset()
            data = data.filter(tags__in=[tag])
            return data
        except:
            return Post.objects.none()


class FavoriteView(ProfileView):
    def get_queryset(self):
        data = super().get_queryset()
        data = data.filter(fav=True)
        return data


class SignUp(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("index")
    template_name = "forms/signup.html"

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
    template_name = "forms/edit_profile.html"
    success_url = reverse_lazy("account")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Change account information"
        posts = Post.objects.filter(author=self.request.user)
        data["title"] = title
        if posts.count() == 0:
            data["total_bookmarks"] = 0
            data["faved_bookmarks"] = 0
            data["last_added"] = None
        else:
            data["total_bookmarks"] = posts.count()
            data["faved_bookmarks"] = posts.filter(fav=True).count()
            data["last_added"] = posts.filter(fav=True).latest("date").date

        data["date_joined"] = self.request.user.date_joined
        data["last_login"] = self.request.user.last_login
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
        for tag in create_tags(form.cleaned_data["tags"]):
            self.p_obj.tags.add(tag)
        return redirect("index")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        title = website_title + "Add new link"
        data["title"] = title
        return data
