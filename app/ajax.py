from django.http import JsonResponse


class HttpResponseAjax(JsonResponse):
    def __init__(self, status='ok', **kwargs):
        kwargs['status'] = status
        super().__init__(kwargs)


class HttpResponseAjaxError(HttpResponseAjax):
    def __init__(self, code, message):
        super().__init__(status='error', code=code, message=message)