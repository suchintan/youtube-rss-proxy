from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, RedirectView
from youtube_rss_proxy.models import Rss
from youtube_rss_proxy.utils import get_auth_url, get_tokens, get_rss, get_username
from uuid import uuid1


class HomeView(TemplateView):
    template_name = "home.html"


class AuthRedirectView(RedirectView):
    def get_redirect_url(self):
        obj = Rss.objects.create(
            uuid=str(uuid1()),
        )
        return get_auth_url(obj.uuid)


class OAuthCallbackView(TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        # TODO handle error
        obj = get_object_or_404(Rss, uuid=self.request.GET["state"])
        if not obj.access_token:
            access_token, refresh_token = get_tokens(self.request.GET["code"])
            obj.access_token = access_token
            obj.refresh_token = refresh_token
            obj.save()
        if not obj.username:
            obj.username = get_username(obj.access_token)
            obj.save()
        context = {
            "url": self.request.build_absolute_uri(reverse("rss-proxy", kwargs={"uuid": obj.uuid})),
        }
        context.update(kwargs)
        return context


def rss_proxy(request, uuid):
    obj = get_object_or_404(Rss, uuid=uuid)
    rss, content_type = get_rss(obj.username, obj.access_token)
    return HttpResponse(rss, content_type=content_type)
