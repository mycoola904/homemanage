from django.urls import path
from django.views.generic import TemplateView
from .views import ProtectedView, HomeView, htmx_ping, htmx_echo

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("htmx-ping/", htmx_ping, name="htmx_ping"),
    path("styleguide/", TemplateView.as_view(template_name="pages/styleguide.html"), name="styleguide"),
    path("protected/", ProtectedView.as_view(), name="protected"),
    path("htmx/echo/", htmx_echo, name="htmx_echo"),

]