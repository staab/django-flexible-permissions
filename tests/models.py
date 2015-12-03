from django.db import models

from flexible_permissions.mixins import PermTarget, PermAgent


class User(PermAgent):
    name = models.CharField(max_length=255)


class Group(PermAgent, PermTarget):
    name = models.CharField(max_length=255)
    user_set = models.ManyToManyField(User)


class Zoo(PermTarget):
    pass


class Exhibit(PermTarget):
    zoo = models.ForeignKey(Zoo)


class Animal(PermTarget):
    exhibit = models.ForeignKey(Exhibit)
