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

from framework.bizz.authentication import get_current_session
from mcfw.restapi import rest
from mcfw.rpc import returns, arguments
from plugins.its_you_online_auth.bizz.profile import search_profiles, get_profile
from plugins.tff_backend.bizz.audit.audit import audit
from plugins.tff_backend.bizz.audit.mapping import AuditLogType
from plugins.tff_backend.bizz.authentication import Scopes
from plugins.tff_backend.bizz.flow_statistics import list_flow_runs_by_user
from plugins.tff_backend.bizz.user import get_tff_profile, set_kyc_status, list_kyc_checks, set_utility_bill_verified
from plugins.tff_backend.to.user import SetKYCPayloadTO, TffProfileTO
from plugins.tff_backend.utils.search import sanitise_search_query


@rest('/users', 'get', Scopes.BACKEND_READONLY, silent_result=True)
@returns(dict)
@arguments(page_size=(int, long), cursor=unicode, query=unicode, kyc_status=(int, long, NoneType))
def api_search_users(page_size=50, cursor=None, query='', kyc_status=None):
    filters = {'kyc_status': kyc_status}
    profiles, cursor, more = search_profiles(sanitise_search_query(query, filters), page_size, cursor)
    return {
        'cursor': cursor and cursor.web_safe_string.encode('utf-8'),
        'more': more,
        'results': [profile.to_dict() for profile in profiles],
    }


@rest('/users/<username:[^/]+>', 'get', Scopes.BACKEND_READONLY, silent_result=True)
@returns(dict)
@arguments(username=str)
def api_get_user(username):
    username = username.decode('utf-8')  # username must be unicode
    return get_profile(username).to_dict()


@rest('/users/<username:[^/]+>/profile', 'get', Scopes.BACKEND_READONLY, silent_result=True)
@returns(TffProfileTO)
@arguments(username=str)
def api_get_tff_user(username):
    username = username.decode('utf-8')  # username must be unicode
    return TffProfileTO.from_model(get_tff_profile(username))


@audit(AuditLogType.SET_KYC_STATUS, 'username')
@rest('/users/<username:[^/]+>/profile/kyc', 'put', Scopes.BACKEND_ADMIN)
@returns(TffProfileTO)
@arguments(username=str, data=SetKYCPayloadTO)
def api_set_kyc_status(username, data):
    username = username.decode('utf-8')  # username must be unicode
    return TffProfileTO.from_model(set_kyc_status(username, data, get_current_session().user_id))


@rest('/users/<username:[^/]+>/profile/kyc/utility-bill', 'put', Scopes.BACKEND_ADMIN)
@returns(TffProfileTO)
@arguments(username=str)
def api_set_utility_bill_verified(username):
    username = username.decode('utf-8')  # username must be unicode
    return TffProfileTO.from_model(set_utility_bill_verified(username))


@rest('/users/<username:[^/]+>/kyc/checks', 'get', Scopes.BACKEND_READONLY, silent_result=True)
@returns([dict])
@arguments(username=str)
def api_kyc_list_checks(username):
    username = username.decode('utf-8')  # username must be unicode
    return list_kyc_checks(username)


@rest('/users/<username:[^/]+>/flows', 'get', Scopes.BACKEND_READONLY, silent_result=True)
@returns(dict)
@arguments(username=str, page_size=(int, long), cursor=unicode)
def api_list_flow_runs_by_user(username=None, cursor=None, page_size=50):
    username = username.decode('utf-8')  # username must be unicode
    results, cursor, more = list_flow_runs_by_user(username, cursor, page_size)
    return {
        'cursor': cursor and cursor.to_websafe_string(),
        'more': more,
        'results': [r.to_dict(exclude={'steps'}) for r in results]
    }
