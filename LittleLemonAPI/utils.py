from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404


def add_user_to_group(username, group_name):
    user = get_object_or_404(User, username=username)
    group = get_object_or_404(Group, name=group_name)
    group.user_set.add(user)


def remove_user_from_group(user_id, group_name):
    user = get_object_or_404(User, pk=user_id)
    group = get_object_or_404(Group, name=group_name)
    group.user_set.remove(user)


def get_group_users(group_name):
    group = get_object_or_404(Group, name=group_name)
    return group.user_set.all()
