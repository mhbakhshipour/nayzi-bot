from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class CustomAPIException(APIException):
    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        if code:
            self.code = code


def custom_rest_exception_handler(exc, context):
    if isinstance(exc, APIException):
        response = exception_handler(exc, context)
        if hasattr(exc, 'code'):
            if 'code' in exc.detail:
                try:
                    if exc.detail['code'] == 'token_not_valid':
                        response.data = {'status': 'error', 'data': {}, 'message': exc.detail['detail']}
                except:
                    response.data = {'status': 'error', 'data': {}, 'message': exc.detail}

            elif 'non_field_errors' in exc.detail:
                response.data = {'status': 'error', 'data': {}, 'message': exc.detail['non_field_errors'][0]}
            else:
                response.data = {'status': 'error', 'data': {}, 'message': exc.detail}
        else:
            if 'code' in exc.detail:
                try:
                    if exc.detail['code'] == 'token_not_valid':
                        response.data = {'status': 'error', 'data': {}, 'message': exc.detail['detail']}
                except:
                    response.data = {'status': 'error', 'data': {}, 'message': exc.detail}

            elif 'non_field_errors' in exc.detail:
                response.data = {'status': 'error', 'data': {}, 'message': exc.detail['non_field_errors'][0]}
            else:
                response.data = {'status': 'error', 'data': {}, 'message': exc.detail}
        return response


class HttpBadRequestException(CustomAPIException):
    status_code = status.HTTP_400_BAD_REQUEST


class HttpForbiddenRequestException(CustomAPIException):
    status_code = status.HTTP_403_FORBIDDEN


class HttpNotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND


class HttpUnauthorizedException(CustomAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED


class HttpUnProcessableEntityException(CustomAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class HttpConflictException(CustomAPIException):
    status_code = status.HTTP_409_CONFLICT


class HttpPreconditionFailedException(CustomAPIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED


class HttpServiceUnavailableException(CustomAPIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class HttpInternalServerException(CustomAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
