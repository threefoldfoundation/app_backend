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


class InvestorSteps(object):
    DOWNLOAD = 'DOWNLOAD'
    ITO_INVITES = 'ITO_INVITES'
    FLOW_INIT = 'FLOW_INIT'
    FLOW_AMOUNT = 'FLOW_AMOUNT'
    FLOW_SIGN = 'FLOW_SIGN'
    PAY = 'PAY'
    PAY_PROCESS = 'PAY_PROCESS'
    ASSIGN_TOKENS = 'ASSIGN_TOKENS'

    DESCRIPTIONS = {
        DOWNLOAD: 'Download the ThreeFold app',
        ITO_INVITES: 'Register using an invitation code',
        FLOW_INIT: 'Initiate “purchase iTokens” in the TF app',
        FLOW_AMOUNT: 'Select currency and how much you want to invest',
        FLOW_SIGN: 'Sign the purchase agreement',
        PAY: 'We send you payment information',
        PAY_PROCESS: 'We process the payment',
        ASSIGN_TOKENS: 'Tokens are assigned',
    }

    @classmethod
    def all(cls):
        return [cls.DOWNLOAD,
                cls.ITO_INVITES,
                cls.FLOW_INIT,
                cls.FLOW_AMOUNT,
                cls.FLOW_SIGN,
                cls.PAY,
                cls.PAY_PROCESS,
                cls.ASSIGN_TOKENS]

    @classmethod
    def should_archive(cls, step):
        return cls.ASSIGN_TOKENS == step or step is None

    @classmethod
    def get_name_for_step(cls, step):
        if step not in cls.DESCRIPTIONS:
            logging.error('Investor description for step \'%s\' not set', step)
        return cls.DESCRIPTIONS.get(step, step)

    @classmethod
    def get_progress(cls, last_checked_step):
        checked = False
        items = []
        for step in reversed(cls.all()):
            if not checked and step == last_checked_step:
                checked = True

            item = {
                'id': step,
                'name': cls.get_name_for_step(step),
                'checked': checked
            }
            items.append(item)

        return {
            'id': 'investor',
            'name': 'Become a token holder',
            'items': list(reversed(items))
        }
