# -*- coding: utf-8 -*-
# Copyright 2017 GIG Technology NV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @@license_version:1.3@@

from google.appengine.api import users
from google.appengine.ext import ndb

from plugins.tff_backend.plugin_consts import NAMESPACE


class ThreeFoldBlockHeight(ndb.Model):
    timestamp = ndb.IntegerProperty()
    height = ndb.IntegerProperty()
    updating = ndb.BooleanProperty()

    @classmethod
    def create_key(cls):
        return ndb.Key(cls, u"TFFBlockHeight", namespace=NAMESPACE)

    @staticmethod
    def get_block_height():
        bh_key = ThreeFoldBlockHeight.create_key()
        bh = bh_key.get()
        if bh:
            return bh
        bh = ThreeFoldBlockHeight(key=bh_key)
        bh.height = -1
        bh.timestamp = 0
        bh.updating = False
        return bh


class ThreeFoldWallet(ndb.Model):
    tokens = ndb.StringProperty(repeated=True)
    next_unlock_timestamp = ndb.IntegerProperty()

    @property
    def app_user(self):
        return users.User(self.key.string_id().decode('utf8'))

    @classmethod
    def create_key(cls, app_user):
        return ndb.Key(cls, app_user.email(), namespace=NAMESPACE)

    @classmethod
    def query(cls, *args, **kwargs):
        kwargs['namespace'] = NAMESPACE
        return super(ThreeFoldWallet, cls).query(*args, **kwargs)

    @classmethod
    def list_update_needed(cls, now_):
        return ThreeFoldWallet.query() \
            .filter(ThreeFoldWallet.next_unlock_timestamp > 0) \
            .filter(ThreeFoldWallet.next_unlock_timestamp < now_)


class ThreeFoldTransaction(ndb.Model):
    timestamp = ndb.IntegerProperty()
    height = ndb.IntegerProperty()
    unlock_timestamps = ndb.IntegerProperty(repeated=True, indexed=False)
    unlock_amounts = ndb.IntegerProperty(repeated=True, indexed=False)
    token = ndb.StringProperty()
    token_type = ndb.StringProperty()
    amount = ndb.IntegerProperty()
    amount_left = ndb.IntegerProperty()
    fully_spent = ndb.BooleanProperty()
    memo = ndb.StringProperty()
    app_users = ndb.UserProperty(repeated=True)
    from_user = ndb.UserProperty()
    to_user = ndb.UserProperty()

    @property
    def id(self):
        return self.key.id()

    @classmethod
    def create_new(cls):
        return cls(namespace=NAMESPACE)

    @classmethod
    def query(cls, *args, **kwargs):
        kwargs['namespace'] = NAMESPACE
        return super(ThreeFoldTransaction, cls).query(*args, **kwargs)

    @classmethod
    def list_by_user(cls, app_user, token):
        return ThreeFoldTransaction.query() \
            .filter(ThreeFoldTransaction.app_users == app_user) \
            .filter(ThreeFoldTransaction.token == token) \
            .order(-ThreeFoldTransaction.timestamp)

    @classmethod
    def list_with_amount_left(cls, app_user, token):
        return ThreeFoldTransaction.query() \
            .filter(ThreeFoldTransaction.to_user == app_user) \
            .filter(ThreeFoldTransaction.token == token) \
            .filter(ThreeFoldTransaction.fully_spent == False) \
            .order(-ThreeFoldTransaction.timestamp)  # NOQA


class ThreeFoldPendingTransaction(ndb.Model):
    STATUS_PENDING = u'pending'
    STATUS_CONFIRMED = u"confirmed"
    STATUS_FAILED = u'failed'

    timestamp = ndb.IntegerProperty()
    unlock_timestamps = ndb.IntegerProperty(repeated=True, indexed=False)
    unlock_amounts = ndb.IntegerProperty(repeated=True, indexed=False)
    token = ndb.StringProperty()
    token_type = ndb.StringProperty()
    amount = ndb.IntegerProperty()
    memo = ndb.StringProperty()
    app_users = ndb.UserProperty(repeated=True)
    from_user = ndb.UserProperty()
    to_user = ndb.UserProperty()

    synced = ndb.BooleanProperty()
    synced_status = ndb.StringProperty()

    @property
    def id(self):
        return self.key.string_id().decode('utf8')

    @classmethod
    def create_key(cls, transaction_id):
        return ndb.Key(cls, u"%s" % transaction_id, namespace=NAMESPACE)

    @classmethod
    def query(cls, *args, **kwargs):
        kwargs['namespace'] = NAMESPACE
        return super(ThreeFoldPendingTransaction, cls).query(*args, **kwargs)

    @classmethod
    def count_pending(cls):
        return cls.query() \
            .filter(ThreeFoldPendingTransaction.synced == False) \
            .count(None) # NOQA

    @classmethod
    def list_by_user(cls, app_user, token):
        return ThreeFoldPendingTransaction.query() \
            .filter(ThreeFoldPendingTransaction.synced == False) \
            .filter(ThreeFoldPendingTransaction.app_users == app_user) \
            .filter(ThreeFoldPendingTransaction.token == token) \
            .order(-ThreeFoldPendingTransaction.timestamp) # NOQA
