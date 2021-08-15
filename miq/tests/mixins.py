from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
# from django.contrib.contenttypes.models import ContentType

from miq.utils import create_staffuser

User = get_user_model()


class UserMixin:

    username = 'usr'
    password = 'pwd'
    user = None

    def get_user(self, username=None, password=None):
        if not username and not self.user:
            self.user = self.create_user(self.username, self.password)
            return self.user

        if not username and self.user:
            return self.user

        if not username or not password:
            raise Exception('Username/password required.')

        return self.create_user(username, password)

    def add_user_perm(self,  user, codename):
        perm = self.get_user_perm(codename)
        user.user_permissions.add(perm)
        return user

    def get_user_perm(self, codename):
        return Permission.objects.get(codename=codename)

    def create_user(self, username, password):
        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.save()
        return user

    def create_staffuser(self, username, password):
        return create_staffuser(username, password)

        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.is_staff = True
        user.save()
        return user

    def create_superuser(self, username, password):
        user = User.objects.create_superuser(username=username)
        user.set_password(password)
        user.save()
        return user

    def refresh_user(self, username):
        self.user = User.objects.get(username=username)


class SiteMixin:
    @property
    def site(self):
        return Site.objects.first()

    def create_site(self):
        return Site.objects.create()


class TestMixin(SiteMixin, UserMixin):
    pass
