from flexible_permissions.models import Permission
from flexible_permissions.roles import register_role

from tests.models import User, Group, Zoo, Exhibit, Animal


def create_test_models():
    users = {
        'admin': User.objects.create(name='admin user'),
        'staff': User.objects.create(name='staff user'),
        'visitor': User.objects.create(name='visiting user')
    }

    staff = Group.objects.create(name='staff')
    staff.user_set.add(users['staff'])

    zoo = Zoo.objects.create()

    exhibits = [
        Exhibit.objects.create(zoo=zoo),
        Exhibit.objects.create(zoo=zoo),
    ]

    animals = [
        Animal.objects.create(exhibit=exhibits[0]),
        Animal.objects.create(exhibit=exhibits[0]),
        Animal.objects.create(exhibit=exhibits[1]),
        Animal.objects.create(exhibit=exhibits[1]),
    ]

    Permission.objects.bulk_create([
        Permission(role='zoo.admin', agent=users['admin'], target=zoo),
        Permission(role='exhibit.staff', agent=staff, target=exhibits[0]),
        Permission(role='zoo.visitor', target=zoo),
    ])
