import re

from django.http import HttpResponseRedirect
from django.conf import settings


class LoginRequiredMiddleware:
    '''
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    '''
    def __init__(self, get_response):
        self.get_response = get_response

        # URLS that will be allowed without auth
        self.exempt_urls = [re.compile(settings.LOGIN_URL.lstrip('/'))]

        # Bring in any additional URLs defined in settings.py
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            self.exempt_urls += [re.compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

    def __call__(self, request):
        '''
        Redirect the user to the login page if the current page is not exempt
        and they aren't currently logged in.
        '''
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in self.exempt_urls):
                return HttpResponseRedirect(settings.LOGIN_URL)

        return self.get_response(request)
