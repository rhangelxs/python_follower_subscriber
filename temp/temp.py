# -*- coding: utf-8 -*-

"""Main module."""
from collections import defaultdict

import uuid
from datetime import datetime

import operator

import functools


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

    # def save(self):
    #     pass
    #
    # def load(self):
    #     pass

    def __init__(self):
        self.users = {}

        self.subscription_list = defaultdict(set)
        self.followers_back_list = defaultdict(set)

        self.messages_list = defaultdict(list)

        self.messages_by_users = defaultdict(list)

    def clear(self):
        self.__init__()

    # Shouldn't be that way, make like that:
    # def user_save(self):
    #     pass

    # def add_uuid(_list, _uuid):
    #     if not _list:
    #         _list = set()
    #     _list.add(_uuid)
    #     return _list


class User(object):
    def __init__(self):
        self.uuid = None

    def get(self, user_uuid):
        if Storage().users.get(user_uuid):
            self.uuid = user_uuid
            return self
        else:
            raise AttributeError("User not found")

    def create(self):
        self.uuid = generate_uuid()
        Storage().users[self.uuid] = self
        # Storage().subscription_list[self.uuid] = set()
        # Storage().followers_back_list[self.uuid] = set()
        return self

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "%s" % self.uuid[0:5]

    def subscribe_to(self, user):
        if not self.uuid == user.uuid:
            Storage().subscription_list[self.uuid].add(user.uuid)
            Storage().followers_back_list[user.uuid].add(self.uuid)

    def unsubscribe_to(self, user):
        Storage().subscription_list[self.uuid].remove(user.uuid)
        Storage().followers_back_list[user.uuid].remove(self.uuid)

    def subscription_list(self):
        return Storage().subscription_list.get(self.uuid) or []


@functools.total_ordering
class Message(object):
    def __init__(self, user, body, in_reply_to=None):
        self.uuid = generate_uuid()
        self.author = user.uuid
        self.body = body
        self.created = datetime.now()
        self.in_reply_to = in_reply_to

    def post(self):
        in_reply_message = None

        # In_reply_check
        if self.in_reply_to:
            in_reply_message = Storage().messages_list.get(self.in_reply_to)
        if in_reply_message:
            Storage().messages_by_users[in_reply_message.author].append(self.uuid)
        elif self.in_reply_to and not in_reply_message:
            raise AttributeError("Linked message by \"in_relpy\" is not exist")

        # User validity check
        User().get(self.author)

        Storage().messages_list[self.uuid] = self
        Storage().messages_by_users[self.author].append(self.uuid)
        return self

    def __eq__(self, other):
        return self.created == other.created

    def __gt__(self, other):
        return self.created > other.created

    def __repr__(self):
        return '({}: {} at {:%m:%S}, {})'.format(
            self.author[0:5], self.body, self.created, self.uuid[0:5])


class Timeline(object):
    def generate_timeline(self, user, k_limit=50):
        timeline = set()
        temp = set()
        for _uuid in user.subscription_list():
            if _uuid != user.uuid:
                temp.update(Storage().messages_by_users[_uuid])

        if temp:
            timeline = [Storage().messages_list[key] for key in temp]

        def include_in_timeline(message, _user=user):
            if message.author == _user.uuid:
                return False
            # elif message.author in user.subscription_list():
            #     return True
            # elif Storage().messages_list.get(message.in_reply_to).author in user.subscription_list():
            #     return True
            else:
                return True

        data = list(filter(lambda x: include_in_timeline(x), timeline))

        # Sort the data
        data.sort(key=operator.attrgetter('created'), reverse=True)

        return data[0:k_limit]


class Messaging(object):
    def post(self, body, user_uuid, in_reply_to_uuid=None):
        user = User().get(user_uuid)
        message = Message(user=user, body=body, in_reply_to=in_reply_to_uuid)
        return message.post()

    def follow(self, who, subscribe_to):
        # User User1 now follows user User2
        who = User().get(who)
        subscribe_to = User().get(subscribe_to)
        who.subscribe_to(subscribe_to)

    def unfollow(self, who, subscribe_to):
        # User User1 now follows user User2
        who = User().get(who)
        subscribe_to = User().get(subscribe_to)
        who.unsubscribe_to(subscribe_to)

    def timeline(self, user, k_limit=50):
        """
        Return the first (most recent) K messages of the timeline of user X
        """
        return Timeline().generate_timeline(user, k_limit=k_limit)
