from django.test import TestCase
from flexible_permissions._utils import (
    ANY,
    NULL,
    is_plural,
    identity,
    ensure_plural,
    get_key,
    filter_isnull,
    is_value,
    normalize_value,
    generic_in,
    validate_roles_with_targets,
    get_single_crud_kwargs,
    get_multi_crud_query,
)
from flexible_permissions.models import Permission

from tests.utils import create_test_models
from tests.models import Exhibit, Zoo, User


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

    def test_get_key(self):
        self.assertEqual('key', get_key('key'))
        self.assertEqual('x__key__y', get_key('key', 'x', 'y'))

    def test_filter_isnull(self):
        results = Permission.objects.filter(filter_isnull('role'))
        self.assertEqual(0, results.count())

        results = Permission.objects.filter(filter_isnull('agent'))
        self.assertEqual(1, results.count())

        results = Permission.objects.filter(filter_isnull('target'))
        self.assertEqual(0, results.count())

    def test_is_value(self):
        self.assertEqual(True, is_value('whatever'))
        self.assertEqual(False, is_value(ANY))
        self.assertEqual(False, is_value(NULL))

    def test_normalize_value(self):
        self.assertEqual(13, normalize_value(3, lambda x, y: x + y, 10))

    def test_generic_in(self):
        exhibits = Exhibit.objects.all()
        permissions = Permission.objects.filter(generic_in('target', exhibits))
        self.assertEqual(1, permissions.count())

    def test_validate_roles_with_targets(self):
        zoo = Zoo.objects.first()
        exhibit = Exhibit.objects.first()

        # Singular

        validate_roles_with_targets('zoo.open', zoo)

        with self.assertRaises(ValueError):
            validate_roles_with_targets('zoo.open', exhibit)

        # Plural

        validate_roles_with_targets(['zoo.open'], [zoo])

        with self.assertRaises(ValueError):
            validate_roles_with_targets(['zoo.open'], [exhibit])

    def test_get_single_crud_kwargs(self):
        role = 'zoo.admin'
        exhibit = Exhibit.objects.first()

        kwargs = get_single_crud_kwargs(role, ANY, ANY)
        self.assertEqual(kwargs['role'], role)
        self.assertNotIn('agent_id', kwargs)
        self.assertNotIn('agent_type', kwargs)
        self.assertNotIn('target_id', kwargs)
        self.assertNotIn('target_type', kwargs)

        kwargs = get_single_crud_kwargs(ANY, exhibit, ANY)
        self.assertNotIn('role', kwargs)
        self.assertEqual(kwargs['agent_id'], exhibit.id)
        self.assertIn('agent_type', kwargs)
        self.assertNotIn('target_id', kwargs)
        self.assertNotIn('target_type', kwargs)

        kwargs = get_single_crud_kwargs(ANY, ANY, exhibit)
        self.assertNotIn('role', kwargs)
        self.assertNotIn('agent_id', kwargs)
        self.assertNotIn('agent_type', kwargs)
        self.assertEqual(kwargs['target_id'], exhibit.id)
        self.assertIn('target_type', kwargs)

        kwargs = get_single_crud_kwargs(role, exhibit, exhibit)
        self.assertEqual(kwargs['role'], role)
        self.assertEqual(kwargs['agent_id'], exhibit.id)
        self.assertEqual(kwargs['target_id'], exhibit.id)
        self.assertIn('agent_type', kwargs)
        self.assertIn('target_type', kwargs)

    def test_get_multi_crud_query(self):
        admin = User.objects.get(name='admin user')
        zoo = Zoo.objects.first()

        # Everything defaults to isnull
        query = get_multi_crud_query()
        self.assertEqual(0, Permission.objects.filter(query).count())

        # It gets the one entry with null agent
        query = get_multi_crud_query(role='zoo.visitor', target=ANY)
        self.assertEqual(1, Permission.objects.filter(query).count())

        # It filters agents and targets properly
        query = get_multi_crud_query(role=ANY, agent=admin, target=zoo)
        self.assertEqual(1, Permission.objects.filter(query).count())
