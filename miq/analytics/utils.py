
from urllib.parse import urlparse, parse_qs

from django.apps import apps

from ..core.utils import get_ip

from .models import Hit, SearchTerm

exclude = [
    '/admin/', 'staff',
    '/media/', '/favicon.ico',
]


def create_hit(request, response, /, source: str = None) -> Hit:
    for match in exclude:
        if match in request.path:
            return

    if not request.session.session_key:
        try:
            request.session.save()
        except Exception:
            return

    url = request.build_absolute_uri() \
        or request.get_full_path_info() \
        or request.get_full_path() \
        or request.path_info \
        or request.path

    #
    source = source or request.session.get('source')
    if not source and request.user.is_authenticated:
        source = f'{request.user.slug}-{request.user.username}___user_slug-user_username'

    session = request.session.session_key
    data = {
        'site_id': request.site.id,
        'ip': get_ip(request),
        'url': url,
        'path': request.path,
        'referrer': request.META.get('HTTP_REFERER'),
        'source_id': source,
        'method': request.method,
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'session': session,
        'response_status': response.status_code,
    }

    content = response.context_data.get('object')
    if content:
        try:
            hit_data = content.get_hit_data()
            data['session_data'] = hit_data
            data['app'] = hit_data.get('app')
            data['model'] = hit_data.get('model')

        except Exception as e:
            print(e)

    query = parse_qs(urlparse(url).query).get('q', [])
    for q in query:
        if not q:
            continue

        term, new = SearchTerm.objects.get_or_create(session=session, value=q)
        if not new:
            term.count += 1
            term.save()

    return Hit.objects.create(**data)
