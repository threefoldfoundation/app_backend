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

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb

from framework.consts import WEEK
from framework.models.common import NdbModel
from framework.plugin_loader import get_config
from framework.utils import chunks, now
from framework.utils.transactions import on_trans_committed
from plugins.tff_backend.plugin_consts import NAMESPACE


class NodeOrderStatus(object):
    CANCELED = -1
    APPROVED = 0
    SIGNED = 1
    SENT = 2
    ARRIVED = 3
    # Admins must manually check if user has invested >= REQUIRED_TOKEN_COUNT_TO_HOST tokens
    WAITING_APPROVAL = 4
    PAID = 5


class ContactInfo(NdbModel):
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    phone = ndb.StringProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)


def _validate_socket(prop, value):
    # type: (ndb.StringProperty, object) -> unicode
    socket_types = get_config(NAMESPACE).odoo.product_ids.keys()
    if value in socket_types:
        return value
    else:
        raise datastore_errors.BadValueError('Value %r for property %s is not an allowed choice' % (value, prop._name))


class NodeOrder(NdbModel):
    NAMESPACE = NAMESPACE
    NODE_ORDERS_PER_PAGE = 50

    app_user = ndb.UserProperty()
    billing_info = ndb.LocalStructuredProperty(ContactInfo)  # type: ContactInfo
    shipping_info = ndb.LocalStructuredProperty(ContactInfo)  # type: ContactInfo
    status = ndb.IntegerProperty()
    tos_iyo_see_id = ndb.StringProperty(indexed=False)
    signature_payload = ndb.StringProperty(indexed=False)
    signature = ndb.StringProperty(indexed=False)
    order_time = ndb.IntegerProperty()
    sign_time = ndb.IntegerProperty()
    send_time = ndb.IntegerProperty()
    arrival_time = ndb.IntegerProperty()
    cancel_time = ndb.IntegerProperty()
    modification_time = ndb.IntegerProperty()
    odoo_sale_order_id = ndb.IntegerProperty()
    socket = ndb.StringProperty(indexed=False, validator=_validate_socket)

    def _pre_put_hook(self):
        self.modification_time = now()

    def _post_put_hook(self, future):
        from plugins.tff_backend.dal.node_orders import index_node_order
        if ndb.in_transaction():
            from google.appengine.ext import deferred
            deferred.defer(index_node_order, self, _transactional=True)
        else:
            index_node_order(self)

    @property
    def iyo_username(self):
        from plugins.tff_backend.bizz.iyo.utils import get_iyo_username
        return get_iyo_username(self.app_user)

    @property
    def id(self):
        return self.key.id()

    @property
    def human_readable_id(self):
        return NodeOrder.create_human_readable_id(self.id)

    @classmethod
    def create_key(cls, order_id=None):
        if order_id is None:
            order_id = cls.allocate_ids(1)[0]
        return ndb.Key(cls, order_id, namespace=NAMESPACE)

    @classmethod
    def create_human_readable_id(cls, order_id):
        id_str = str(order_id)
        if len(id_str) % 4 == 0:
            return '.'.join(chunks(id_str, 4))
        return id_str

    @classmethod
    def list(cls):
        return cls.query()

    @classmethod
    def list_by_status(cls, status):
        return cls.query() \
            .filter(cls.status == status)

    @classmethod
    def list_by_user(cls, app_user):
        return cls.query() \
            .filter(cls.app_user == app_user)

    @classmethod
    def list_check_online(cls):
        two_weeks_ago = now() - (WEEK * 2)
        return cls.list_by_status(NodeOrderStatus.SENT).filter(cls.send_time < two_weeks_ago)


class PublicKeyMapping(NdbModel):
    NAMESPACE = NAMESPACE
    label = ndb.StringProperty()  # label on itsyou.online

    @classmethod
    def create_key(cls, public_key, user_email):
        return ndb.Key(cls, public_key, cls, user_email, namespace=NAMESPACE)
