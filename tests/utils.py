from flexible_permissions.models import Permission
from flexible_permissions.roles import register_role

from tests.models import User, Group, Zoo, Cage, Animal


def create_test_models():
    users = {
        'admin': User.objects.create(name='admin'),
        'staff': User.objects.create(name='staff'),
        'visitor': User.objects.create(name='visitor')
    }

    staff_group = Group.objects.create(name='staff')
    staff_group.user_set.add(users['staff'])

    zoo = Zoo.objects.create()

    cages = [
        Cage.objects.create(zoo=zoo),
        Cage.objects.create(zoo=zoo),
    ]

    animals = [
        Animal.objects.create(cage=cages[0]),
        Animal.objects.create(cage=cages[0]),
        Animal.objects.create(cage=cages[1]),
        Animal.objects.create(cage=cages[1]),
    ]

    Permission.objects.bulk_create([
        Permission(role='zoo.admin', agent=users['admin'], target=zoo),
        Permission(role='cage.staff', agent=staff_group, target=cages[0]),
        Permission(role='zoo.visitor', target=zoo),
    ])
