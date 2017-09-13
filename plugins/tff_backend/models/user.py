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

from google.appengine.ext import ndb

from framework.models.common import NdbModel
from plugins.tff_backend.plugin_consts import NAMESPACE


class TffProfileInfo(NdbModel):
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    phone = ndb.StringProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)

    odoo_id = ndb.IntegerProperty(indexed=False)


class TffProfile(NdbModel):
    NAMESPACE = NAMESPACE
    app_user = ndb.UserProperty()
    
    referrer_user = ndb.UserProperty()
    referrer_username = ndb.StringProperty()
    
    billing_info = ndb.LocalStructuredProperty(TffProfileInfo)
    shipping_info = ndb.LocalStructuredProperty(TffProfileInfo)

    @classmethod
    def create_key(cls, username):
        return ndb.Key(cls, username, namespace=NAMESPACE)


class ProfilePointer(NdbModel):
    NAMESPACE = NAMESPACE

    username = ndb.StringProperty()

    @property
    def user_code(self):
        return self.key.string_id().decode('utf8')

    @classmethod
    def create_key(cls, username):
        from plugins.tff_backend.bizz.user import user_code
        return ndb.Key(cls, user_code(username), namespace=NAMESPACE)

    @classmethod
    def get_by_user_code(cls, user_code):
        return ndb.Key(cls, user_code, namespace=NAMESPACE).get()
