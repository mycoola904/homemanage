from __future__ import annotations

from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from households.forms import HouseholdCreateForm, MembershipAddForm, SettingsUserCreateForm, get_user_queryset
from households.models import Household, HouseholdMember
from households.services.authorization import is_global_admin
from households.services.settings import add_membership, create_household, create_user_with_memberships, remove_membership


def global_admin_required(view_func):
	@wraps(view_func)
	@login_required
	def _wrapped(request, *args, **kwargs):
		if not is_global_admin(request.user):
			return HttpResponseForbidden("Forbidden")
		return view_func(request, *args, **kwargs)

	return _wrapped


@method_decorator(login_required, name="dispatch")
class GlobalAdminRequiredMixin(View):
	def dispatch(self, request, *args, **kwargs):
		if not is_global_admin(request.user):
			return HttpResponseForbidden("Forbidden")
		return super().dispatch(request, *args, **kwargs)


def _settings_context(household_form=None, user_form=None, membership_error=None, membership_message=None):
	has_households = Household.objects.filter(is_archived=False).exists()
	memberships = HouseholdMember.objects.select_related("household", "user").order_by(
		"household__name",
		"user__username",
	)
	return {
		"household_form": household_form or HouseholdCreateForm(),
		"user_form": user_form or SettingsUserCreateForm(),
		"households": Household.objects.filter(is_archived=False).order_by("name", "created_at"),
		"users": get_user_queryset(),
		"memberships": memberships,
		"has_households": has_households,
		"membership_error": membership_error,
		"membership_message": membership_message,
		"membership_roles": HouseholdMember.Role.choices,
	}


@global_admin_required
def settings_index(request):
	template_name = "households/settings/_content.html" if request.headers.get("HX-Request") == "true" else "households/settings/index.html"
	return render(request, template_name, _settings_context())


@global_admin_required
def settings_household_create(request):
	if request.method != "POST":
		return HttpResponseNotAllowed(["POST"])

	form = HouseholdCreateForm(request.POST)
	status = 200
	if form.is_valid():
		try:
			create_household(name=form.cleaned_data["name"], created_by=request.user)
			form = HouseholdCreateForm()
		except ValidationError as error:
			status = 400
			if hasattr(error, "message_dict"):
				for field, messages in error.message_dict.items():
					for message in messages:
						if field in form.fields:
							form.add_error(field, message)
						else:
							form.add_error(None, message)
			else:
				form.add_error(None, error.message)
	else:
		status = 400

	return render(
		request,
		"households/settings/_household_panel.html",
		_settings_context(household_form=form),
		status=status,
	)


@global_admin_required
def settings_user_create(request):
	if request.method != "POST":
		return HttpResponseNotAllowed(["POST"])

	form = SettingsUserCreateForm(request.POST)
	status = 200

	if not Household.objects.filter(is_archived=False).exists():
		status = 400
		form.add_error(None, "Create a household before creating user accounts.")
		return render(
			request,
			"households/settings/_user_panel.html",
			_settings_context(user_form=form),
			status=status,
		)

	if form.is_valid():
		try:
			create_user_with_memberships(
				username=form.cleaned_data["username"],
				email=form.cleaned_data["email"],
				password=form.cleaned_data["password"],
				household_ids=[str(household.id) for household in form.cleaned_data["household_ids"]],
			)
			form = SettingsUserCreateForm()
		except ValidationError as error:
			status = 400
			if hasattr(error, "message_dict"):
				for field, messages in error.message_dict.items():
					for message in messages:
						if field in form.fields:
							form.add_error(field, message)
						else:
							form.add_error(None, message)
			else:
				form.add_error(None, error.message)
	else:
		status = 400

	return render(
		request,
		"households/settings/_user_panel.html",
		_settings_context(user_form=form),
		status=status,
	)


@global_admin_required
def settings_membership_add(request, household_id):
	if request.method != "POST":
		return HttpResponseNotAllowed(["POST"])

	household = Household.objects.filter(id=household_id, is_archived=False).first()
	if household is None:
		return render(
			request,
			"households/settings/_membership_panel.html",
			_settings_context(membership_error="Household not found."),
			status=400,
		)

	form = MembershipAddForm(request.POST)
	if not form.is_valid():
		message = form.errors.get("user_id", form.non_field_errors() or ["Invalid membership payload."])[0]
		return render(
			request,
			"households/settings/_membership_panel.html",
			_settings_context(membership_error=message),
			status=400,
		)

	user = get_user_model().objects.filter(pk=form.cleaned_data["user_id"]).first()
	if user is None:
		return render(
			request,
			"households/settings/_membership_panel.html",
			_settings_context(membership_error="Selected user does not exist."),
			status=400,
		)

	role = form.cleaned_data.get("role") or HouseholdMember.Role.MEMBER
	_, created = add_membership(household=household, user=user, role=role)
	message = "Member added." if created else "Membership already exists."
	return render(
		request,
		"households/settings/_membership_panel.html",
		_settings_context(membership_message=message),
	)


@global_admin_required
def settings_membership_remove(request, household_id, user_id):
	if request.method != "POST":
		return HttpResponseNotAllowed(["POST"])

	household = Household.objects.filter(id=household_id, is_archived=False).first()
	if household is None:
		return render(
			request,
			"households/settings/_membership_panel.html",
			_settings_context(membership_error="Household not found."),
			status=400,
		)

	user = get_user_model().objects.filter(pk=user_id).first()
	if user is None:
		return render(
			request,
			"households/settings/_membership_panel.html",
			_settings_context(membership_error="Selected user does not exist."),
			status=400,
		)

	try:
		was_removed = remove_membership(household=household, user=user)
	except ValidationError as error:
		message = error.messages[0] if error.messages else "Unable to remove membership."
		return render(
			request,
			"households/settings/_membership_panel.html",
			_settings_context(membership_error=message),
			status=400,
		)

	message = "Membership removed." if was_removed else "Membership already absent."
	return render(
		request,
		"households/settings/_membership_panel.html",
		_settings_context(membership_message=message),
	)
