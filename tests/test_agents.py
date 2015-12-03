from django.test import TestCase
from flexible_permissions.agents import normalize_agent
from flexible_permissions.shortcuts import ISNULL

from tests.models import User, Group, Exhibit
from tests.utils import create_test_models


class AgentsTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_normalize_agent(self):
        group = Group.objects.first()
        user = User.objects.get(name='staff user')

        # It should validate input
        with self.assertRaises(KeyError):
            normalize_agent('invalid', infer_agents=False)

        with self.assertRaises(KeyError):
            normalize_agent('invalid')

        self.assertEqual([user], normalize_agent(user, infer_agents=False))
        self.assertEqual([group, user], normalize_agent(user))

    def test_member_of_group(self):
        user = User.objects.get(name='staff user')
        result = Exhibit.objects.for_action('clean', user)
        self.assertEqual(1, result.count())

    def test_null_agent(self):
        results = Exhibit.objects.for_action('visit', ISNULL)
        self.assertEqual(2, results.count())
