from django.test import TestCase
from flexible_permissions.relations import (
    get_relation_paths,
    get_related_target_prefixes,
    get_related_agent_prefixes,
)

from tests.models import User, Animal
from tests.utils import create_test_models


class AgentsTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_get_relation_paths(self):
        self.assertEqual(
            {'exhibit': 'exhibit', 'zoo': 'exhibit__zoo'},
            get_relation_paths(Animal)
        )

    def test_get_related_target_prefixes(self):
        self.assertEqual(
            set([
                'target_perms',
                'exhibit__target_perms',
                'exhibit__zoo__target_perms'
            ]),
            get_related_target_prefixes(
                Animal.objects.all(),
                'target_perms',
                'zoo.admin',
                'exhibit.staff'
            )
        )

    def test_get_related_agent_prefixes(self):
        self.assertEqual(
            set(['agent_perms']),
            get_related_agent_prefixes(User.objects.all(), 'agent_perms')
        )

    def test_get_using_relation(self):
        self.assertEqual(4, Animal.objects.for_role('zoo.admin').count())
