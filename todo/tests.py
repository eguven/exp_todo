"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json

from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from todo.models import TodoItem, User


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
    def setUp(self):
        '''Create user and login with client'''
        self.client = Client(enforce_csrf_checks=True)
        credentials_1 = {'username': 'user1', 'password': 'pass1'}
        self.assertFalse(self.client.login(**credentials_1))
        call_command('adduser', *credentials_1.values())        
        self.assertTrue(self.client.login(**credentials_1))
        self.user = User.objects.get(username='user1')

    def test_nologin(self):
        '''Test 403 responses from REST api without authentication'''
        response = Client().get(reverse('todo_api:handle_rest_call'))
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(
            {'success': False, 'error': 'Forbidden'},
            json.loads(response.content))

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

    def test_put(self):
        not_found_response = self.client.put(
            reverse('todo_api:handle_rest_call_id', args=('1',)),
            data='{"pk": 1}', content_type='application/json')
        self.assertEqual(404, not_found_response.status_code)
        item = self.user.todoitem_set.create(title='foo', order=1, done=False)
        put_data = item.to_json()
        put_data['done'] = True
        put_data_json = json.dumps(put_data)
        response = self.client.put(
            reverse('todo_api:handle_rest_call_id', args=('1',)),
            data=put_data_json, content_type='application/json')
        self.assertEqual({'success': True}, json.loads(response.content))
        item = TodoItem.objects.get(pk=1)
        response = self.client.get(
            reverse('todo_api:handle_rest_call_id', args=('1',)))
        expected = json.loads(response.content)
        self.assertEqual(expected, item.to_json())
        self.assertTrue(item.done)

    def test_delete(self):
        not_found_response = self.client.delete(
            reverse('todo_api:handle_rest_call_id', args=('1')))
        self.assertEqual(404, not_found_response.status_code)
        bad_response = self.client.delete(
            reverse('todo_api:handle_rest_call'))
        self.assertEqual(400, bad_response.status_code)
        item = self.user.todoitem_set.create(title='foo', order=42, done=False)
        response = self.client.delete(
            reverse('todo_api:handle_rest_call_id', args=('1')))
        self.assertNotEqual(404, response.status_code)
        self.assertEqual(0, TodoItem.objects.count())
        response = self.client.get(reverse('todo_api:handle_rest_call'))
        self.assertEqual('[]', response.content)

