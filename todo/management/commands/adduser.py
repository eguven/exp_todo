from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

'''manage.py command adduser <username password [email]>
to add new users to the todo app
'''

class Command(BaseCommand):
    args = '<username password [email]>'
    help = 'Creates a new django user for todo app'

    def handle(self, username, password, *args, **options):
        if User.objects.filter(username=username).count():
            raise CommandError('Username: "%s" is not available' % username)
        if args:
            email = args[0]
        else:
            email = '%s@todoapp.tmp' % username
        user = User.objects.create_user(username, email, password)
        self.stdout.write('\nSuccessfully created user "%s <%s>"\n' % (username, email))
