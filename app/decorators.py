from app.ajax import HttpResponseAjaxError

def login_required_ajax(view):
    def decorated_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        else:
            return HttpResponseAjaxError(
                code='no_auth',
                message='Auth required',
            )
    return decorated_view