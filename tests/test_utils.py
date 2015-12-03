from django.test import TestCase
from flexible_permissions._utils import (
    is_plural,
    identity,
    ensure_plural,
    generic_in,
    get_single_crud_kwargs,
    get_multi_crud_query,
)
from flexible_permissions.models import Permission

from tests.utils import create_test_models
from tests.models import Cage


class UtilsTestCase(TestCase):
    def setUp(self):
        create_test_models()

    def test_is_plural(self):
        self.assertTrue(is_plural([]))
        self.assertFalse(is_plural({}))
        self.assertTrue(is_plural(set()))

    def test_identity(self):
        self.assertEqual(self, identity(self))

    def test_ensure_plural(self):
        self.assertEqual([1], ensure_plural(1))
        self.assertEqual([1], ensure_plural([1]))

    def test_generic_in(self):
        cages = Cage.objects.all()
        permissions = Permission.objects.filter(generic_in('target', cages))
        self.assertEqual(1, permissions.count())

    def test_get_single_crud_kwargs(self):
        role = 'zoo.admin'
        cage = Cage.objects.first()

        kwargs = get_single_crud_kwargs(role, None, None)
        self.assertEqual(kwargs['role'], role)
        self.assertNotIn('agent_id', kwargs)
        self.assertNotIn('agent_type', kwargs)
        self.assertNotIn('target_id', kwargs)
        self.assertNotIn('target_type', kwargs)

        kwargs = get_single_crud_kwargs(None, cage, None)
        self.assertNotIn('role', kwargs)
        self.assertEqual(kwargs['agent_id'], cage.id)
        self.assertIn('agent_type', kwargs)
        self.assertNotIn('target_id', kwargs)
        self.assertNotIn('target_type', kwargs)

        kwargs = get_single_crud_kwargs(None, None, cage)
        self.assertNotIn('role', kwargs)
        self.assertNotIn('agent_id', kwargs)
        self.assertNotIn('agent_type', kwargs)
        self.assertEqual(kwargs['target_id'], cage.id)
        self.assertIn('target_type', kwargs)

        kwargs = get_single_crud_kwargs(role, cage, cage)
        self.assertEqual(kwargs['role'], role)
        self.assertEqual(kwargs['agent_id'], cage.id)
        self.assertEqual(kwargs['target_id'], cage.id)
        self.assertIn('agent_type', kwargs)
        self.assertIn('target_type', kwargs)

    def test_get_multi_crud_query(self):
        pass
