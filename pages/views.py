from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from households.services.households import can_switch_to_household, resolve_current_household, set_current_household


class HomeView(TemplateView):
    template_name = "pages/home.html"

def htmx_ping(request):
    return HttpResponse(
        '<div class="alert alert-success">HTMX GET works ✅</div>'
    )


class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = "pages/protected.html"


class HouseholdHomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/household_home.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        context = resolve_current_household(request)
        if context.redirect is not None:
            return context.redirect
        if context.household is None:
            return redirect("household:no-household-access")
        return super().dispatch(request, *args, **kwargs)


@login_required
def no_household_access(request):
    return render(request, "pages/no_household_access.html", status=403)


@login_required
@require_POST
def switch_household(request):
    household_id = request.POST.get("household_id")
    if not household_id or not can_switch_to_household(request.user, household_id):
        return render(request, "pages/no_household_access.html", status=403)

    from households.models import Household

    household = Household.objects.filter(pk=household_id, is_archived=False).first()
    if household is None:
        return render(request, "pages/no_household_access.html", status=403)

    set_current_household(request, household)
    return redirect("household:home")

@require_POST
def htmx_echo(request):
    msg = request.POST.get("msg", "")
    return HttpResponse(f'<div class="alert alert-info">You posted: {msg}</div>')
