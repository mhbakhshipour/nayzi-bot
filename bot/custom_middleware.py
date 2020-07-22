import uuid

from django.core.exceptions import PermissionDenied

request_ip = None
correlation_id = None


def set_correlation_id(cid):
    global correlation_id
    correlation_id = cid


def get_correlation_id():
    global correlation_id
    if correlation_id is None:
        correlation_id = 'ThisIsNotGeneratedInsideARequest-' + str(uuid.uuid4())
    return correlation_id


def set_request_ip_globally(ip):
    global request_ip
    request_ip = ip


def get_current_request_ip():
    global request_ip
    return request_ip


def global_identifier_extractor_middleware(get_response):
    def extract_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    def generate_correlation_id():
        return str(uuid.uuid4())

    def middleware(request):
        set_request_ip_globally(extract_ip(request))
        set_correlation_id(generate_correlation_id())
        response = get_response(request)
        return response

    return middleware
