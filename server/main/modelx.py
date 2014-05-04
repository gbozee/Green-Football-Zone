# -*- coding: utf-8 -*-

import hashlib

from helpers import NDBJsonSerializer

class BaseX(object):
    @classmethod
    def retrieve_one_by(cls, name, value):
        cls_db_list = cls.query(getattr(cls, name) == value).fetch(1)
        if cls_db_list:
            return cls_db_list[0]
        return None


class ConfigX(object):
    @classmethod
    def get_master_db(cls):
        return cls.get_or_insert('master')

class LeagueSerializer(NDBJsonSerializer):
    __json_hidden__ = ['version','created','modified']


class LeagueX(LeagueSerializer):
    pass


class TeamX(object):
    pass




class UserX(object):
    @property
    def avatar_url(self):
        return '//gravatar.com/avatar/%s?d=identicon&r=x' % (
            hashlib.md5((self.email or self.name).encode('utf-8')).hexdigest().lower()
        )

    @property
    def image_url(self):
        if self.google_image_url:
            return self.google_image_url
        else:
            return self.avatar_url

    @property
    def gplus_login(self):
        return self.access_token != "" and self.access_token is not None

    @property
    def facebook_login(self):
        return self.facebook_username != "" and self.facebook_username is not None

