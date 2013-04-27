"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json

from django.core.urlresolvers import reverse

from django.test import TestCase
from todo.models import TodoItem


class TodoItemTest(TestCase):

    def test_json(self):
        """Checking json serialization"""
        item = TodoItem(
            title='the title',
            order=2,
            done=False)
        result = item.to_json()
        self.assertEqual(
            result,
            {'title': 'the title',
             'order': 2,
             'done': False})
        item.save()
        result = item.to_json()
        self.assertEqual(
            result,
            {'pk':1,
             'title': 'the title',
             'order': 2,
             'done': False})

class RestApiTests(TestCase):
    def test_base(self):
        '''Test bad request and empty GET response'''
        response = self.client.get(reverse('todo_api:handle_rest_call'))
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual('[]', response.content)
        for method in ('post', 'put', 'delete'):
            http_method = getattr(self.client, method)
            bad_response = http_method(
                reverse('todo_api:handle_rest_call'), data={'foo': 'bar'})
            self.assertEqual(400, bad_response.status_code)
        not_found_response = self.client.get(
            reverse('todo_api:handle_rest_call_id', args=('1',)))
        self.assertEqual(404, not_found_response.status_code)

    def test_post_get(self):
        saved = []
        for pk in xrange(1, 6):
            item = TodoItem(title='Title %d' % pk, order=pk, done=False)
            self.client.post(
                reverse('todo_api:handle_rest_call'),
                data=json.dumps(item.to_json()),
                content_type='application/json')
            item.pk = pk
            saved.append(item)
        expected = json.dumps([item.to_json() for item in saved])
        response = self.client.get(reverse('todo_api:handle_rest_call'))
        self.assertEqual(expected, response.content)


    def test_delete(self):
        not_found_response = self.client.delete(
            reverse('todo_api:handle_rest_call_id', args=('1')))
        self.assertEqual(404, not_found_response.status_code)
        bad_response = self.client.delete(
            reverse('todo_api:handle_rest_call'))
        self.assertEqual(400, bad_response.status_code)
        item = TodoItem(title='foo', order=42, done=False)
        item.save()
        response = self.client.delete(
            reverse('todo_api:handle_rest_call_id', args=('1')))
        self.assertEqual(0, TodoItem.objects.count())
        response = self.client.get(reverse('todo_api:handle_rest_call'))
        self.assertEqual('[]', response.content)

