from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"


class QuerystringMixin:
    """Exposes the current GET querystring (without `page`) for pagination links."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        querystring = self.request.GET.copy()
        querystring.pop("page", None)
        context["querystring"] = querystring.urlencode()
        return context


class NextUrlRedirectMixin:
    """On success, honours a safe `?next=` param (e.g. resuming a multi-step flow).

    Subclasses provide the ordinary target via get_default_success_url() instead of
    overriding get_success_url() directly. When next_url_param_name is set, the new
    object's pk is appended to `next` under that query param before redirecting.
    """

    next_url_param_name = None

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={self.request.get_host()}
        ):
            if self.next_url_param_name:
                separator = "&" if "?" in next_url else "?"
                next_url = f"{next_url}{separator}{self.next_url_param_name}={self.object.pk}"
            return next_url
        return self.get_default_success_url()

    def get_default_success_url(self):
        return super().get_success_url()
