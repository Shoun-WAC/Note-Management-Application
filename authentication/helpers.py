from django.http import JsonResponse
from rest_framework import status

def success_response(data=None, success_message='Success', status=status.HTTP_200_OK):
    response_data = {'status': True, 'message': success_message, 'results': {}}
    if data is not None:
        response_data['results']['data'] = data
    return JsonResponse(response_data, status=status)

def error_response(errors={}, error_message='error', status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception_info = None):
    response_data = {'status': False, 'message': error_message, 'errors': errors, "exception_info": exception_info}
    return JsonResponse(response_data, status=status)