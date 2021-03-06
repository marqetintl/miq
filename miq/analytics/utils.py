
from urllib.parse import urlparse, parse_qs

from ..core.utils import get_ip

from .models import Campaign, Hit, SearchTerm

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
        source = f'{request.user.username}-{request.user.slug}___user_slug-user_username'

    session = request.session.session_key
    ip = get_ip(request)
    data = {
        'url': url,
        'session': session,
        'source_id': source,
        'path': request.path,
        'ip': ip,
        'method': request.method,
        'site_id': request.site.id,
        'response_status': response.status_code,
        'referrer': request.META.get('HTTP_REFERER'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
    }

    ctx = getattr(response, 'context_data', {})
    if ctx and (obj := ctx.get('object')):
        try:
            if hit_data := obj.get_hit_data():
                data['session_data'] = hit_data
                data['app'] = hit_data.get('app')
                data['model'] = hit_data.get('model')
        except Exception as e:
            print(e)

    query = parse_qs(urlparse(url).query)
    for key in query.keys():
        if key == 'q':
            continue

        for value in query.get(key, []):
            Campaign.objects.get_or_create(key=key.lower(), value=value.lower(), ip=ip)

    for q in query.get('q', []):
        if not q:
            continue

        term, new = SearchTerm.objects.get_or_create(session=session, value=q)
        if not new:
            term.count += 1
            term.save()

    return Hit.objects.create(**data)
