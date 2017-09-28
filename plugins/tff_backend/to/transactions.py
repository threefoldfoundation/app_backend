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
from types import NoneType

from google.appengine.ext import ndb

from framework.to import TO
from mcfw.properties import typed_property, long_property, unicode_property, bool_property, unicode_list_property, \
    long_list_property
from plugins.tff_backend.to import PaginatedResultTO


class NewTransactionTO(TO):
    token_count = long_property('token_count')
    memo = unicode_property('memo')
    date_signed = long_property('date_signed')
    token_type = long_property('token_type')


class BaseTransactionTO(TO):
    timestamp = long_property('timestamp')
    unlock_timestamps = long_list_property('unlock_timestamps')
    unlock_amounts = long_list_property('unlock_amounts')
    token = unicode_property('token')
    token_type = unicode_property('token_type')
    amount = long_property('amount')
    memo = unicode_property('memo')
    app_users = unicode_list_property('app_users')
    from_user = unicode_property('from_user')
    to_user = unicode_property('to_user')


class PendingTransactionTO(BaseTransactionTO):
    id = unicode_property('id')
    synced = bool_property('synced')
    synced_status = unicode_property('synced_status')


class TransactionTO(BaseTransactionTO):
    id = long_property('id')
    amount_left = long_property('amount_left')
    height = long_property('height')
    fully_spent = bool_property('fully_spent')


class PendingTransactionListTO(PaginatedResultTO):
    results = typed_property('results', PendingTransactionTO, True)

    @classmethod
    def from_query(cls, models, cursor, more):
        # type: (list[PendingTransaction], unicode, boolean) -> PendingTransactionListTO
        assert isinstance(cursor, (ndb.Cursor, NoneType))
        results = [PendingTransactionTO.from_model(model) for model in models]
        return cls(cursor and cursor.to_websafe_string().decode('utf-8'), more, results)
