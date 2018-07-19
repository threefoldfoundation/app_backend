# -*- coding: utf-8 -*-
# Copyright 2018 GIG Technology NV
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
# @@license_version:1.4@@
import webapp2

from framework.bizz.i18n import get_user_language
from framework.handlers import render_page
from framework.plugin_loader import get_config
from plugins.tff_backend.plugin_consts import NAMESPACE


class UpdateAppPageHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        parameters = {
            'lang': get_user_language(),
            'url': 'https://rogerth.at/install/%s' % get_config(NAMESPACE).rogerthat.app_id
        }
        render_page(self.response, 'update-app.html', template_parameters=parameters)
