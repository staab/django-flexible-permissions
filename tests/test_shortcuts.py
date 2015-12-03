from django.test import TestCase
from flexible_permissions.shortcuts import (
    NOFILTER,
    ISNULL,
    get_perms,
    add_perm,
    remove_perm,
    assign_role,
)

from tests.models import User, Zoo
from tests.utils import create_test_models


class ShortcutsTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_get_perms(self):
        user = User.objects.get(name='admin user')
        zoo = Zoo.objects.first()

        self.assertEqual(0, get_perms().count())
        self.assertEqual(3, get_perms(NOFILTER, NOFILTER, NOFILTER).count())
        self.assertEqual(1, get_perms(
            role='zoo.admin',
            agent=user,
            target=zoo
        ).count())

    def test_add_perm(self):
        user = User.objects.get(name='visiting user')
        zoo = Zoo.objects.first()

        # Do it twice - we should get no exceptions
        add_perm('zoo.admin', user, zoo)
        add_perm('zoo.admin', user, zoo)

        self.assertEqual(1, get_perms('zoo.admin', user, zoo).count())

    def test_remove_perm(self):
        with self.assertRaises(TypeError):
            remove_perm('zoo.admin')

        remove_perm('zoo.admin', NOFILTER, NOFILTER)
        self.assertEqual(0, get_perms('zoo.admin', NOFILTER, NOFILTER).count())

    def test_assign_role(self):
        pass
