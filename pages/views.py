from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.http import require_POST


class HomeView(TemplateView):
    template_name = "pages/home.html"

def htmx_ping(request):
    return HttpResponse(
        '<div class="alert alert-success">HTMX GET works ✅</div>'
    )


class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = "pages/protected.html"

@require_POST
def htmx_echo(request):
    msg = request.POST.get("msg", "")
    return HttpResponse(f'<div class="alert alert-info">You posted: {msg}</div>')
