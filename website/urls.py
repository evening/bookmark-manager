from django.contrib.auth import views as auth_views
from django.urls import path

from website import views

urlpatterns = [
    path("", views.ProfileView.as_view(), name="index"),
    path("account", views.EditProfile.as_view(), name="account"),
    path("account/delete", views.AccountDelete.as_view(), name="account_delete"),
    path(
        "account/password", views.PasswordChangeView.as_view(), name="password_change"
    ),
    path("add", views.Add.as_view(), name="add"),
    path("archive/<uuid:uuid>", views.view_archive, name="archive"),
    path("autoadd", views.autoadd, name="autoadd"),
    path("delete/", views.delete, name="delete"),
    path("edit/", views.edit, name="edit"),
    path("fav/", views.fav, name="fav"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
    path("signup/", views.SignUp.as_view(), name="signup"),
    path("u:<str:username>", views.ProfileView.as_view(), name="profile"),
    path(
        "u:<str:username>/fav/", views.FavoriteView.as_view(), name="profile_favorite"
    ),
]
