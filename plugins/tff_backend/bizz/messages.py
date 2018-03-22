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
import logging

from google.appengine.ext import deferred, ndb

from mcfw.consts import DEBUG
from plugins.rogerthat_api.to import MemberTO
from plugins.tff_backend.bizz.intercom_helpers import send_intercom_email
from plugins.tff_backend.bizz.iyo.utils import get_iyo_username
from plugins.tff_backend.bizz.rogerthat import send_rogerthat_message
from plugins.tff_backend.utils.app import get_app_user_tuple


def send_message_and_email(app_user, message, subject):
    if not DEBUG:
        human_user, app_id = get_app_user_tuple(app_user)
        member = MemberTO(member=human_user.email(), app_id=app_id, alert_flags=0)
        deferred.defer(send_rogerthat_message, member, message, _transactional=ndb.in_transaction())
        iyo_username = get_iyo_username(app_user)
        message += '\n\nKind regards,\nThe ThreeFold Team'
        if iyo_username is None:
            logging.error('Could not find itsyou.online username for app_user %s, not sending intercom email'
                          '\nSubject: %s\nMessage:%s', app_user, subject, message)
        else:
            deferred.defer(send_intercom_email, iyo_username, subject, message, _transactional=ndb.in_transaction())
    else:
        logging.info('send_message_and_email %s %s %s', app_user, message, subject)
