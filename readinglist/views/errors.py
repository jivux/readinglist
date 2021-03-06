from __future__ import print_function
import sys
import traceback
from pyramid.httpexceptions import (
    HTTPForbidden, HTTPUnauthorized, HTTPNotFound, HTTPInternalServerError,
)
from pyramid.security import forget
from pyramid.view import (
    forbidden_view_config, notfound_view_config, view_config
)

from readinglist.errors import format_error, ERRORS


@forbidden_view_config()
def authorization_required(request):
    """Distinguish authentication required (``401 Unauthorized``) from
    not allowed (``403 Forbidden``).
    """
    if not request.authenticated_userid:
        response = HTTPUnauthorized(
            body=format_error(
                401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
                "Please authenticate yourself to use this endpoint."),
            content_type='application/json')
        response.headers.extend(forget(request))
        return response

    response = HTTPForbidden(
        body=format_error(
            403, ERRORS.FORBIDDEN, "Forbidden",
            "This user cannot access this resource."),
        content_type='application/json')
    return response


@notfound_view_config()
def page_not_found(request):
    """Return a JSON 404 error page."""
    response = HTTPNotFound(
        body=format_error(
            404, ERRORS.MISSING_RESOURCE, "Not Found",
            "The resource your are looking for could not be found."),
        content_type='application/json')
    return response


@view_config(context=Exception)
def error(context, request):
    """Display an error message and record it in Sentry."""
    # client = Client()
    try:
        raise
    except Exception:
        # client.captureException()
        print(traceback.format_exc(), file=sys.stderr)

    return HTTPInternalServerError(
        body=format_error(
            500,
            ERRORS.UNDEFINED,
            "Internal Server Error",
            "A programmatic error occured, developers have been informed.",
            "https://github.com/mozilla-services/readinglist/issues/"),
        content_type='application/json')
