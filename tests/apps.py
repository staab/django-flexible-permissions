from django.apps import AppConfig
from flexible_permissions.agents import register_agent
from flexible_permissions.roles import register_role
from flexible_permissions.relations import register_relation

from tests.models import User, Group, Zoo, Exhibit, Animal


class TestsConfig(AppConfig):
    name = 'tests'
    verbose_name = "Tests"

    def ready(self):
        """
        Register roles
        """

        admin_actions = ['zoo.open', 'exhibit.create']
        staff_actions = ['animal.feed', 'exhibit.clean']
        visitor_actions = ['zoo.visit', 'exhibit.visit', 'animal.see']

        register_role('zoo.admin', admin_actions + staff_actions)
        register_role('exhibit.staff', staff_actions)
        register_role('zoo.visitor', visitor_actions)

        """
        Register Relations
        """

        register_relation(Animal, {
            'exhibit': 'exhibit',
            'zoo': 'exhibit__zoo'
        })

        register_relation(Exhibit, {
            'zoo': 'zoo'
        })

        """
        Register Agents
        """

        register_agent(User, lambda user: [user] + list(user.group_set.all()))
        register_agent(Group, lambda group: [group])
