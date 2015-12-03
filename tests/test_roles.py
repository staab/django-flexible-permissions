from unittest import TestCase
from flexible_permissions.roles import (
    roles_to_actions,
    actions_to_roles,
)


class RolesTestCase(TestCase):
    def test_roles_to_actions(self):
        self.assertItemsEqual([
            'zoo.open',
            'exhibit.create',
            'animal.feed',
            'exhibit.clean',
            'zoo.visit',
            'exhibit.visit',
            'animal.see',
        ], roles_to_actions(['zoo.admin', 'zoo.visitor']))

    def test_actions_to_roles(self):
        self.assertItemsEqual([
            'zoo.admin',
            'exhibit.staff',
            'zoo.visitor'
        ], actions_to_roles(['zoo.visit']))
