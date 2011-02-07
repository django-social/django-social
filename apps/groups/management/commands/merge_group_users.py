# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from apps.groups.documents import Group, GroupUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        (src_group_id, dst_group_id, ) = args

        src_group = Group.objects.with_id(src_group_id)
        dst_group = Group.objects.with_id(dst_group_id)

        if not src_group:
            raise CommandError('incorrect src group id')

        if not dst_group:
            raise CommandError('incorrect dst group id')

        if src_group == dst_group:
            raise CommandError('src and dst group are same')

        src_group_users = src_group.members
        dst_group_users = dst_group.members

        for user in src_group_users:
            if not user in dst_group_users:
                if not dst_group.add_member(user):
                    print 'Can not add',  user
