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

from framework.bizz.authentication import get_current_session
from framework.plugin_loader import get_auth_plugin
from mcfw.restapi import rest
from mcfw.rpc import returns, arguments
from plugins.tff_backend.bizz.authentication import Scopes
from plugins.tff_backend.bizz.investor import get_investment_agreements, put_investment_agreement, \
    get_investment_agreement_details
from plugins.tff_backend.to.investor import InvestmentAgreementListTO, InvestmentAgreementTO, \
    InvestmentAgreementDetailsTO


@rest('/investment-agreements', 'get', Scopes.TEAM)
@returns(InvestmentAgreementListTO)
@arguments(cursor=unicode, status=(int, long))
def api_get_investment_agreements(cursor=None, status=None):
    return InvestmentAgreementListTO.from_query(*get_investment_agreements(cursor, status))


@rest('/investment-agreements/<agreement_id:[^/]+>', 'get', Scopes.TEAM)
@returns(InvestmentAgreementDetailsTO)
@arguments(agreement_id=(int, long))
def api_get_investment_agreement(agreement_id):
    return get_investment_agreement_details(agreement_id)


@rest('/investment-agreements/<agreement_id:[^/]+>', 'put', Scopes.ADMINS)
@returns(InvestmentAgreementTO)
@arguments(agreement_id=(int, long), data=InvestmentAgreementTO)
def api_put_investment_agreement(agreement_id, data):
    user = users.User('%s@%s' % (get_current_session().user_id, get_auth_plugin().configuration.api_domain))
    agreement = put_investment_agreement(agreement_id, data, user)
    return InvestmentAgreementTO.from_model(agreement)
