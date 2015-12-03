from django.test import TestCase
from flexible_permissions.agents import (
    _agent_registry,
    register_agent,
    normalize_agent,
)

from tests.models import User, Group
from tests.utils import create_test_models


class AgentsTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_register_agent(self):
        register_agent('x', 'test')
        self.assertEqual(_agent_registry['x'], 'test')

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
