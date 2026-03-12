from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.inbox, name="inbox"),

    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="email_app/login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("inbox/", views.inbox, name="inbox"),
    path("sent/", views.sent, name="sent"),
    path("archive/", views.archive, name="archive"),
    path("trash/", views.trash, name="trash"),
    path("new_email/", views.new_email, name="new_email"),

    path("email_app/<int:pk>/open", views.open_email, name="open_email"),
    path("email_app/<int:pk>/delete", views.delete_email, name="delete_email"),
    path("email_app/<int:pk>/archive", views.archive_email, name="archive_email"),
    path("email_app/<int:pk>/restore", views.restore_email, name="restore_email")
]
