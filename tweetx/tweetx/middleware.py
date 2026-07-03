import traceback
from django.http import HttpResponse

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        error_msg = f"GLOBAL EXCEPTION CAUGHT:\\n\\n{str(exception)}\\n\\n{traceback.format_exc()}"
        return HttpResponse(error_msg, content_type="text/plain", status=500)
