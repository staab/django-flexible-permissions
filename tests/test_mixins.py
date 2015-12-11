from django.test import TestCase

from tests.models import User, Zoo, Exhibit
from tests.utils import create_test_models


class TargetTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_prefix_actions(self):
        with self.assertRaises(ValueError):
            Zoo.objects.all()._prefix_actions('zoo.open')

        actions = Zoo.objects.all()._prefix_actions('open')
        self.assertEqual(['zoo.open'], actions)

    def test_for_role_no_filter(self):
        self.assertEqual(1, Zoo.objects.for_role().count())

    def test_for_role_filter_role(self):
        # It does an OR On role
        results = Zoo.objects.for_role(['zoo.admin', 'invalid'])
        self.assertEqual(1, results.count())

        # It successfully filters out results
        results = Zoo.objects.for_role('invalid')
        self.assertEqual(0, results.count())

    def test_for_role_filter_agent(self):
        admin = User.objects.get(name='admin user')
        staff = User.objects.get(name='staff user')

        # Normal call
        results = Zoo.objects.for_role(['zoo.admin'], admin)
        self.assertEqual(1, results.count())

        # With any role
        results = Zoo.objects.for_role(agent=admin)
        self.assertEqual(2, results.count())

        # Invalid role
        results = Zoo.objects.for_role(['invalid'], admin)
        self.assertEqual(0, results.count())

        # Invalid agent
        results = Zoo.objects.for_role(['zoo.admin'], staff)
        self.assertEqual(0, results.count())

    def test_for_action(self):
        admin = User.objects.get(name='admin user')

        # For requires unprefixed
        with self.assertRaises(ValueError):
            Zoo.objects.for_action('zoo.open', admin)

        results = Zoo.objects.for_action('open', admin)
        self.assertEqual(1, results.count())


class AgentTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_with_role_no_filter(self):
        self.assertEqual(3, User.objects.with_action().count())

    def test_with_role_filter_role(self):
        # It does an OR On role
        results = User.objects.with_role(['zoo.admin', 'invalid'])
        self.assertEqual(1, results.count())

        # It successfully filters out results
        results = User.objects.with_role('invalid')
        self.assertEqual(0, results.count())

    def test_with_role_filter_target(self):
        zoo = Zoo.objects.first()
        exhibit = Exhibit.objects.first()
        admin = User.objects.get(name='admin user')

        # Normal call
        results = User.objects.with_role('zoo.admin', zoo)
        self.assertEqual(1, results.count())

        # With any role
        results = User.objects.with_role(target=zoo)
        self.assertEqual(1, results.count())

        # Relational permission queries don't work
        with self.assertRaises(ValueError):
            User.objects.with_role('zoo.admin', exhibit)

        # Invalid role
        with self.assertRaises(ValueError):
            User.objects.with_role('invalid', zoo)

        # Invalid target
        with self.assertRaises(ValueError):
            User.objects.with_role('zoo.admin', admin)

    def test_action(self):
        zoo = Zoo.objects.first()
        admin = User.objects.get(name='admin user')

        # With requires prefixes
        with self.assertRaises(ValueError):
            User.objects.with_action('open', zoo)

        results = User.objects.with_action('zoo.open', zoo)
        self.assertEqual(1, results.count())
