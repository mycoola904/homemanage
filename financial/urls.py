from django.urls import path

from financial import views

app_name = "financial"

urlpatterns = [
    path("", views.AccountsIndexView.as_view(), name="accounts-index"),
    path("new/", views.AccountCreateView.as_view(), name="accounts-new"),
    path("<uuid:pk>/preview/", views.account_preview, name="accounts-preview"),
    path("<uuid:pk>/edit/", views.account_edit, name="accounts-edit"),
    path("<uuid:pk>/delete/confirm/", views.account_delete_confirm, name="accounts-delete-confirm"),
    path("<uuid:pk>/delete/", views.account_delete, name="accounts-delete"),
    path("<uuid:pk>/", views.AccountDetailView.as_view(), name="accounts-detail"),
]
