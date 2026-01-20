from django.http import HttpResponseRedirect
from django_htmx.http import HttpResponseLocation, push_url, trigger_client_event, retarget


def redirect_back(*, url:str, request, message:str = None, is_success: bool = True):
    return htmx_redirect(url, request.htmx, message=message, is_success=is_success) if request.htmx else redirect_with_cookie(url)

def redirect_with_cookie(url: str):
    redirect_response = HttpResponseRedirect(url)
    redirect_response.set_cookie('redirect_url', url, httponly=False)
    return redirect_response


HTMX_ATTRS = {
    'target': "#main_body"
}


def htmx_redirect(url: str, htmx, message=None, is_success=True):
    HTMX_ATTRS['source'] = htmx.trigger
    # HTMX_ATTRS['event'] = htmx.event
    redirect_response = HttpResponseLocation(url, **HTMX_ATTRS)

    response = trigger_client_event(redirect_response, 'showMessage', {'message': message, 'is_success': is_success}) if message else push_url(redirect_response, url)
    return response


def htmx_render(response, message=None, is_success=True):
    return trigger_client_event(response, 'showMessage', {'message': message, 'is_success': is_success}) if message else response


def htmx_target(response, target='#main_body', message=None, is_success=True):
    response['HX-Retarget'] = target
    return trigger_client_event(response, 'showMessage', {'message': message, 'is_success': is_success})


def get_cookie(request, name):
    return request.COOKIES.get(name, None)


def set_cookie(response, name, value):
    response.set_cookie(name, value, httponly=False)
    return response
