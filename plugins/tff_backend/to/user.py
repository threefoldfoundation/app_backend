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
from framework.to import TO
from mcfw.properties import unicode_property, typed_property, long_property


class SetKYCPayloadTO(TO):
    status = long_property('status')
    comment = unicode_property('comment')
    data = typed_property('data', dict)


class TffProfileTO(TO):
    username = unicode_property('username')
    app_user = unicode_property('app_user')
    referrer_user = unicode_property('referrer_user')
    referrer_username = unicode_property('referrer_username')
    nodes = typed_property('nodes', dict, True)
    referral_code = unicode_property('referral_code')
    kyc = typed_property('kyc', dict)
    info = typed_property('info', dict)


class SignedDocumentTO(TO):
    description = unicode_property('description')
    name = unicode_property('name')
    link = unicode_property('link')
    signature = unicode_property('signature')
