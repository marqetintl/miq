import threading

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.middleware import CurrentSiteMiddleware
from django.contrib.sites.shortcuts import get_current_site

from .models.setting import SiteSetting


local = threading.local()


class SiteMiddleware(CurrentSiteMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        local.user = request.user
        self.process_request(request)

        response = self.get_response(request)
        return response

    def process_request(self, request):
        site = get_current_site(request)
        request.site = site
        local.site = site

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):

        # DRF DATA
        # self.process_drf_response(request, response)

        # DJANGO CONTEXT DATA
        self.process_response_context_data(request, response)

        return response

    def process_drf_response(self, request, response):
        if not hasattr(response, 'data') or not response.data:
            return

    def process_response_context_data(self, request, response):
        ctx = response.context_data
        if not ctx:
            return response

        site = get_current_site(request)
        if not site:
            return response

        ctx['is_live'] = False

        # SITE
        site = Site.objects.filter(id=site.id).first()
        ctx['site'] = site

        # SHARED DATA
        if 'sharedData' not in ctx.keys():
            ctx['sharedData'] = {}

        sD = ctx.get('sharedData')

        # SITE SETTING

        settings = SiteSetting.objects.filter(site=site).first()
        if settings:
            ctx['is_live'] = settings.is_live
            ctx['close_template'] = {
                'html': settings.ct_html,
                'title': settings.ct_title,
                'text': settings.ct_text
            }

            if number := settings.contact_number:
                ctx['contact_number'] = number
                ctx['contact_number_display'] = settings.contact_number_display or number
                ctx['contact_number_title'] = settings.contact_number_title or ''

                sD['contact_number'] = number
                sD['contact_number_display'] = settings.contact_number_display or number
                sD['contact_number_title'] = settings.contact_number_title or ''

            if email := settings.contact_email:
                ctx['contact_email'] = email

            if number := settings.whatsapp_number:
                title = settings.whatsapp_link_title or ''
                link = settings.whatsapp_link or ''

                ctx['whatsapp_number'] = number
                ctx['whatsapp_link'] = link
                ctx['whatsapp_link_title'] = title

                sD['whatsapp_number'] = number
                sD['whatsapp_link'] = link
                sD['whatsapp_link_title'] = title

            if ga := settings.ga_tracking:
                ctx['ga_tracking'] = ga.strip()

            if fb := settings.fb_pixel:
                ctx['fb_pixel'] = fb.strip()
            if fb := settings.fb_app_id:
                ctx['fb_app_id'] = fb.strip()
                sD['fb_app_id'] = fb.strip()

            if fb := settings.fb_app_secret:
                ctx['fb_app_secret'] = fb.strip()
                sD['fb_app_secret'] = fb.strip()

        display_live = ctx.get('is_live', False) is True or request.path == '/login/'

        view_mode = 'user'
        if request.user.is_authenticated and request.user.is_staff:
            display_live = True

        if display_live and not ctx.get('is_live', False):
            view_mode = 'admin'

        ctx['display_live'] = display_live
        ctx['view_mode'] = view_mode
        sD['view_mode'] = view_mode

        if 'site' not in sD:
            sD.update({
                'site': {'name': site.name, 'domain': site.domain}
            })

        return response


class CORSMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.process_response(response)

        # from pprint import pprint
        # print(request.headers.__dict__)

        return response

    def process_response(self, response):
        if origin := settings.CORS_ORIGIN:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Headers"] = "X-CSRFTOKEN, x-requested-with, Content-Type, Accept, Origin"
            response["Access-Control-Allow-Methods"] = "OPTIONS, GET, POST, PUT, DELETE, PATCH"
            response["Access-Control-Max-Age"] = 86400
            response["Access-Control-Allow-Credentials"] = 'true'
