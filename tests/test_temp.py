#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `temp` package."""

import pytest

from click.testing import CliRunner

from temp import temp
from temp import cli


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
    new_user = temp.User()
    assert temp.Storage().users[new_user.uuid] == new_user


def test_adding_one_follower():
    user1 = temp.User()

    user2 = temp.User()

    user1.add_follower(user2)

    assert temp.Storage().followers_list[user1.uuid] == {user2.uuid, }
    assert temp.Storage().followers_back_list[user2.uuid] == {user1.uuid, }


def test_adding_two_followers():
    user1 = temp.User()

    user2 = temp.User()

    user3 = temp.User()

    user1.add_follower(user2)
    user1.add_follower(user3)


    assert temp.Storage().followers_list[user1.uuid] == {user2.uuid, user3.uuid}
    assert temp.Storage().followers_back_list[user2.uuid] == {user1.uuid, }
    assert temp.Storage().followers_back_list[user3.uuid] == {user1.uuid, }
