# encoding: utf-8
import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from todo.models import TodoItem

logger = logging.getLogger(__name__)

def json_response(resp, **kwargs):
    '''returns a django HttpResponse with input json-encoded and
    content_type set to application/json. Additinal keyword arguments
    will be passed down
    '''
    return HttpResponse(json.dumps(resp), content_type='application/json', **kwargs)

def error_json_response(err_str, **kwargs):
    '''wrapper around json_response for json-encoded error responses,
    expects error string
    '''
    response = {'success': False, 'error': err_str}
    return json_response(response, **kwargs)

def handle_get(request, pk=None):
    '''handle GET request'''
    if pk is None:
        items = [item.to_json() for item in TodoItem.objects.all()]
        return json_response(items)
    try:
        item = TodoItem.objects.get(pk=pk)
        return json_response(item.to_json())
    except TodoItem.DoesNotExist:
        return error_json_response('Not found', status=404)

def handle_post(request, data):
    '''handle POST (create) request'''
    if 'pk' in data or 3 != len(data):  # bad request
        response = {'success': False, 'error': 'unexpected data: pk'}
        return json_response(response, status=400)
    # create and save new TodoItem
    new_todo = TodoItem(**data)
    new_todo.save()
    return json_response({'success': True}, status=201)

def handle_put(request, data, pk=None):
    '''handle PUT (update) requets'''
    if data['pk'] != pk:
        print 'PK err'
        print data, type(pk)
        return error_json_response('Data does not match resource', status=400)
    try:
        item = TodoItem.objects.get(pk=pk)
    except TodoItem.DoesNotExist:
        return error_json_response('Not found', status=404)
    for k, v in data.items():
        setattr(item, k, v)
    try:
        item.full_clean()
        item.save()
        return json_response({'success': True})
    except ValidationError:
        print 'VAL err'
        return error_json_response('Did not validate', status=400)

def handle_delete(request, pk=None):
    '''handle DELETE request'''
    try:
        item = TodoItem.objects.get(pk=pk)
    except TodoItem.DoesNotExist:
        return error_json_response('Not found', status=404)
    item.delete()
    return json_response({'success': True})

def request_valid(request, pk=None):
    '''Check if request is correct eg. pk can be converted to int
    or POST has no pk & PUT has pk etc
    '''
    if pk is not None and not pk.isdigit():
        return False
    elif 'POST' == request.method and pk is not None:
        return False
    elif request.method in ('PUT', 'DELETE') and pk is None:
        return False
    return True

@csrf_exempt
def handle_rest_call(request, pk=None, **kwargs):
    '''Handle API calls, checks request validity and routes to
    specific handlers for methods
    '''
    if not request_valid(request, pk=pk):
        return error_json_response('Bad Request', status=400)
    pk = int(pk) if pk is not None else pk
    if 'GET' == request.method:
        return handle_get(request, pk=pk)
    elif 'DELETE' == request.method:
        return handle_delete(request, pk=pk)
    try:
        data = json.loads(request.body)
    except ValueError:
        return error_json_response('JSON request body expected', status=400)
    if 'POST' == request.method:
        return handle_post(request, data)
    elif 'PUT' == request.method:
        return handle_put(request, data, pk=pk)

