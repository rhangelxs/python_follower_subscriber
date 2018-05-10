#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `temp` package."""
import datetime
import pytest
import random
from click.testing import CliRunner

from temp import cli
from temp import temp


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'temp.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_adding_user():
    new_user = temp.User().create()
    assert temp.Storage().users[new_user.uuid] == new_user


def test_adding_one_follower():
    user1 = temp.User().create()

    user2 = temp.User().create()

    user1.subscribe_to(user2)

    assert temp.Storage().subscription_list[user1.uuid] == {user2.uuid, }
    assert temp.Storage().followers_back_list[user2.uuid] == {user1.uuid, }


def test_adding_two_followers():
    user1 = temp.User().create()

    user2 = temp.User().create()

    user3 = temp.User().create()

    user1.subscribe_to(user2)
    user1.subscribe_to(user3)

    assert temp.Storage().subscription_list[user1.uuid] == {user2.uuid, user3.uuid}
    assert temp.Storage().followers_back_list[user2.uuid] == {user1.uuid, }
    assert temp.Storage().followers_back_list[user3.uuid] == {user1.uuid, }


class TestSuperRichData:
    @classmethod
    def teardown_class(cls):
        """Runs at end of class"""
        temp.Storage().clear()

    @classmethod
    def setup_class(cls):
        """Runs once per class"""
        cls.total_number_of_messages = 1000

        cls.user1 = temp.User().create()
        cls.user2 = temp.User().create()
        cls.user3 = temp.User().create()

        cls.user1.subscribe_to(cls.user2)
        cls.user1.subscribe_to(cls.user3)

        for i in range(cls.total_number_of_messages):
            user = random.choice([cls.user1, cls.user2, cls.user3])
            in_reply_user = random.choice([None, None, None, cls.user1, cls.user2, cls.user3])
            text = temp.generate_uuid()[0:8]
            if in_reply_user:
                try:
                    in_reply_message = random.choice(temp.Storage.messages_by_users[in_reply_user.uuid])
                except AttributeError:
                    in_reply_message = None
            else:
                in_reply_message = None
            message = temp.Message(user=user, body=text, in_reply_to=in_reply_message)
            message.created = message.created + datetime.timedelta(seconds=i) + datetime.timedelta(
                seconds=random.choice([-5, 5]))
            message.post()

    def test_total_number_of_messages(self):
        assert len(temp.Storage().messages_list) == self.total_number_of_messages

    def test_timeline_subscribed_to_zero(self):
        assert temp.Timeline().generate_timeline(self.user2) == []
        assert temp.Timeline().generate_timeline(self.user3) == []

    def test_timeline_for_one_followers1(self):
        assert len(temp.Timeline().generate_timeline(self.user2)) <= 50

    def test_timeline_for_one_followers2(self):
        assert len(temp.Timeline().generate_timeline(self.user3)) <= 50

    def test_timeline_for_different_k(self):
        max_k = len(temp.Timeline().generate_timeline(self.user3))
        print("We generated maximum of %s messages" % max_k)
        for k in range(0, max_k):
            print("Test for %s timeline limit" % k)
            assert len(temp.Timeline().generate_timeline(self.user3, k_limit=k)) == k


class TestHandmadeData:
    @classmethod
    def teardown_class(cls):
        """Runs at end of class"""
        temp.Storage().clear()

    @classmethod
    def setup_class(cls):
        """Runs once per class"""

        cls.user1 = temp.User().create()
        cls.user2 = temp.User().create()
        cls.user3 = temp.User().create()

        cls.user1.subscribe_to(cls.user2)
        cls.user1.subscribe_to(cls.user3)

        cls.message1 = temp.Message(cls.user1, "M1: Body 1", in_reply_to=None)
        cls.message1.post()

        cls.message2 = temp.Message(cls.user2, "M2: In reply to M1 from first user", in_reply_to=cls.message1.uuid)
        cls.message2.created = cls.message2.created + datetime.timedelta(seconds=2)
        cls.message2.post()

        cls.message3 = temp.Message(cls.user2, "M3: Second reply to first user message", in_reply_to=cls.message1.uuid)
        cls.message3.created = cls.message3.created + datetime.timedelta(seconds=3)
        cls.message3.post()

    def test_message_name(self):
        assert str(self.message1) == \
               '({}: {} at {:%m:%S}, {})'.format(
                   self.message1.author[0:5], self.message1.body, self.message1.created, self.message1.uuid[0:5])

    def test_user_connection(self):
        assert temp.Storage().subscription_list[self.user1.uuid] == {self.user2.uuid, self.user3.uuid}
        assert temp.Storage().subscription_list[self.user2.uuid] == set()
        assert temp.Storage().subscription_list[self.user3.uuid] == set()

        assert temp.Storage().followers_back_list[self.user2.uuid] == {self.user1.uuid}
        assert temp.Storage().followers_back_list[self.user3.uuid] == {self.user1.uuid}

    def test_create_messages(self):
        assert temp.Storage().messages_list[self.message1.uuid] == self.message1
        assert temp.Storage().messages_list[self.message2.uuid] == self.message2
        assert temp.Storage().messages_list[self.message3.uuid] == self.message3

    def test_create_messages_in_reply(self):
        assert temp.Storage().messages_by_users[self.user1.uuid] == [self.message1.uuid, self.message2.uuid,
                                                                     self.message3.uuid]
        assert temp.Storage().messages_by_users[self.user2.uuid] == [self.message2.uuid, self.message3.uuid]

    def test_timeline_for_zero_followed(self):
        assert temp.Timeline().generate_timeline(self.user2) == []
        assert temp.Timeline().generate_timeline(self.user3) == []

        assert temp.Messaging().timeline(self.user2) == []
        assert temp.Messaging().timeline(self.user3) == []

    def test_timeline_for_two_followed(self):
        assert temp.Timeline().generate_timeline(self.user1) == [self.message3, self.message2]
        assert temp.Messaging().timeline(self.user1) == [self.message3, self.message2]

    def test_get_wrong_uuid(self):
        with pytest.raises(AttributeError):
            temp.User().get(temp.generate_uuid())

    def test_biased_in_reply_message(self):
        fake_message_object = temp.Message(self.user1, "")

        message_fake = temp.Message(self.user1, "Second in reply to 1", in_reply_to=fake_message_object.uuid)
        with pytest.raises(AttributeError, message="Linked message by \"in_relpy\" is not exist"):
            message_fake.post()

    def test_biased_in_user_message(self):
        fake_message_object = temp.Message(self.user1, "")
        fake_message_object.author = temp.generate_uuid()

        with pytest.raises(AttributeError):
            fake_message_object.post()

    def test_user_representation(self):
        assert str(self.user1) == self.user1.uuid[0:5]

    def test_message_order(self):
        assert self.message3 > self.message2

class TestMoreMessages(TestHandmadeData):
    def test_create_one_message(self):
        new_message = temp.Message(self.user2, "M4: In reply to M3", in_reply_to=self.message3.uuid)
        new_message.created = new_message.created + datetime.timedelta(seconds=10)
        new_message.post()
        assert len(temp.Timeline().generate_timeline(self.user1)) == 3
        assert len(temp.Timeline().generate_timeline(self.user2)) == 0
        assert len(temp.Timeline().generate_timeline(self.user3)) == 0

class TestCircularConnection(TestHandmadeData):
    from collections import defaultdict
    temp.Storage().subscription_list = defaultdict(set)
    temp.Storage().followers_back_list = defaultdict(set)

    def test_circular_follow_timeline(self):
        # Let's start with following self

        self.user2.subscribe_to(self.user2)
        assert temp.Timeline().generate_timeline(self.user3) == []

        self.user3.subscribe_to(self.user3)
        assert temp.Timeline().generate_timeline(self.user3) == []

    def test_circular_connection_for_user2(self):
        self.user3.subscribe_to(self.user2)
        assert len(temp.Timeline().generate_timeline(self.user1)) == 2
        assert len(temp.Timeline().generate_timeline(self.user2)) == 0
        assert len(temp.Timeline().generate_timeline(self.user3)) == 2

    def test_circular_connection_for_user3(self):
        self.user3.subscribe_to(self.user1)
        self.user3.subscribe_to(self.user2)
        assert len(temp.Timeline().generate_timeline(self.user1)) == 2
        assert len(temp.Timeline().generate_timeline(self.user2)) == 0
        assert len(temp.Timeline().generate_timeline(self.user3)) == 3

    def test_case_for_user2(self):
        self.user2.subscribe_to(self.user1)
        assert len(temp.Timeline().generate_timeline(self.user1)) == 2
        assert len(temp.Timeline().generate_timeline(self.user2)) == 1
        assert len(temp.Timeline().generate_timeline(self.user3)) == 3

    def test_clear(self):
        self.user3.subscribe_to(self.user1)
        self.user3.subscribe_to(self.user2)

        assert len(temp.Timeline().generate_timeline(self.user3)) == 3


class TestAPIOnHandmadeData:
    def setup(self):
        """Runs once per class"""
        temp.Storage().clear()

        self.user1 = temp.User().create()
        self.user4 = temp.User().create()

        self.message1 = temp.Messaging().post("test", self.user1.uuid)
        self.message2 = temp.Messaging().post("test", self.user1.uuid, in_reply_to_uuid=self.message1.uuid)

    def test_post(self):
        assert self.message1.uuid in temp.Storage().messages_list
        assert self.message2.uuid in temp.Storage().messages_list
        assert len(temp.Storage().messages_list) == 2

    def test_no_follower(self):
        assert not any(temp.Storage().subscription_list.values())
        assert not any(temp.Storage().followers_back_list.values())

    def test_follower(self):
        temp.Messaging().follow(who=self.user4.uuid, subscribe_to=self.user1.uuid)

        assert self.user1.uuid in temp.Storage().subscription_list[self.user4.uuid]
        assert self.user4.uuid in temp.Storage().followers_back_list[self.user1.uuid]

    def test_unfollow(self):
        temp.Messaging().follow(who=self.user4.uuid, subscribe_to=self.user1.uuid)
        temp.Messaging().unfollow(who=self.user4.uuid, subscribe_to=self.user1.uuid)

        assert not any(temp.Storage().subscription_list.values())
        assert not any(temp.Storage().followers_back_list.values())
