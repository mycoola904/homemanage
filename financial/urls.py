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
    path(
        "<uuid:pk>/transactions/",
        views.account_transactions_body,
        name="account-transactions-body",
    ),
    path(
        "<uuid:pk>/transactions/new/",
        views.account_transactions_new,
        name="account-transactions-new",
    ),
        path(
            "<uuid:pk>/transactions/<uuid:transaction_id>/edit/",
            views.account_transactions_edit,
            name="account-transactions-edit",
        ),
    path(
        "<uuid:pk>/transactions/categories/new/",
        views.account_transactions_category_new,
        name="account-transactions-category-new",
    ),
    path("<uuid:pk>/", views.AccountDetailView.as_view(), name="accounts-detail"),
]
