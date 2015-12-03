from django.test import TestCase

from tests.models import User, Zoo
from tests.utils import create_test_models


class TargetTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_get_action_prefix(self):
        self.assertEqual('zoo', Zoo.objects.all()._get_action_prefix())

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

        results = Zoo.objects.for_action('open', admin)
        self.assertEqual(1, results.count())


class AgentTestCase(TestCase):
    def setUp(self):
        create_test_models()
