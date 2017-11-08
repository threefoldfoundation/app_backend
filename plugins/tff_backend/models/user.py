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

from enum import IntEnum
from framework.models.common import NdbModel
from plugins.tff_backend.plugin_consts import NAMESPACE


class KYCStatus(IntEnum):
    DENIED = -10
    UNVERIFIED = 0  # Not verified, and not applied to be verified yet
    PENDING_SUBMIT = 10  # KYC flow has been sent to the user
    SUBMITTED = 20  # KYC flow has been set by user
    # Admin verified the info sent in by the user, completed any missing data (e.g. MRZ1 from uploaded photo)
    # Info is now ready to be sent to Trulioo
    INFO_SET = 30
    PENDING_APPROVAL = 40  # API call to Trulioo done, admin has to mark user as approved/denied now
    VERIFIED = 50  # Approved by admin


KYC_STATUSES = map(int, KYCStatus)


class KYCApiCall(NdbModel):
    NAMESPACE = NAMESPACE
    transaction_id = ndb.StringProperty()
    record_id = ndb.StringProperty()
    result = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class KYCStatusUpdate(NdbModel):
    comment = ndb.StringProperty()
    author = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    from_status = ndb.IntegerProperty(choices=KYC_STATUSES)
    to_status = ndb.IntegerProperty(choices=KYC_STATUSES)


class KYCDataFields(NdbModel):
    NAMESPACE = NAMESPACE
    country_code = ndb.StringProperty()
    # key / value of information. Example: {'Profile': {'FirstGivenName': 'test'}}
    data = ndb.JsonProperty()


class KYCInformation(NdbModel):
    """
    Args:
        api_calls(list[KYCApiCall])
        updates(list[KYCStatusUpdate])
        pending_information(KYCDataFields)
        verified_information(KYCDataFields)
    """
    NAMESPACE = NAMESPACE
    status = ndb.IntegerProperty(choices=KYC_STATUSES)
    api_calls = ndb.LocalStructuredProperty(KYCApiCall, repeated=True, compressed=True)
    updates = ndb.LocalStructuredProperty(KYCStatusUpdate, repeated=True, compressed=True)
    pending_information = ndb.LocalStructuredProperty(KYCDataFields)
    verified_information = ndb.LocalStructuredProperty(KYCDataFields)

    def set_status(self, new_status, author, comment=None):
        self.updates.append(KYCStatusUpdate(from_status=self.status,
                                            to_status=new_status,
                                            author=author,
                                            comment=comment))
        self.status = new_status


class TffProfile(NdbModel):
    NAMESPACE = NAMESPACE
    app_user = ndb.UserProperty()

    referrer_user = ndb.UserProperty()
    referrer_username = ndb.StringProperty()
    kyc = ndb.StructuredProperty(KYCInformation)  # type: KYCInformation

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
