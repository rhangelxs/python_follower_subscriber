# -*- coding: utf-8 -*-

"""Main module."""
import uuid


def generate_uuid():
    return "%s" % uuid.uuid4()


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class Storage:
    users = {}

    followers_list = {}
    followers_back_list = {}

    def __init__(self):
        pass

    # Shouldn't be that way, make like that:
    # def user_save(self):
    #     pass


class User:
    def __init__(self):
        self.uuid = generate_uuid()
        Storage().users[self.uuid] = self

    def add_follower(self, user):
        def add_id(_list, _uuid):
            if not _list:
                _list = set()
            _list.add(_uuid)
            return _list

        Storage().followers_list[self.uuid] = add_id(Storage().followers_list.get(self.uuid), user.uuid)

        Storage().followers_back_list[user.uuid] = add_id(Storage().followers_back_list.get(user.uuid), self.uuid)

    # def remove_follower(self, user):
    #     pass

