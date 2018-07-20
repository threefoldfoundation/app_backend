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

from google.appengine.api import users

from mcfw.consts import DEBUG
from mcfw.rpc import arguments, returns
from plugins.rogerthat_api.to import UserDetailsTO
from plugins.tff_backend.bizz.global_stats import ApiCallException
from plugins.tff_backend.bizz.iyo.utils import get_username
from plugins.tff_backend.bizz.nodes.stats import get_nodes_for_user, assign_nodes_to_user, \
    get_nodes_stats_from_influx
from plugins.tff_backend.models.nodes import Node
from plugins.tff_backend.utils.app import create_app_user


@returns([dict])
@arguments(params=dict, user_detail=UserDetailsTO)
def api_get_node_status(params, user_detail):
    # type: (dict, UserDetailsTO) -> list[dict]
    try:
        username = get_username(user_detail)
        nodes = Node.list_by_user(username)
        if not DEBUG and not nodes:
            # fallback, should only happen when user checks his node status before our cron job has ran.
            logging.warn('Fetching node serial number from odoo since no nodes where found for user %s',
                         username)
            new_nodes = get_nodes_for_user(username)
            if new_nodes:
                nodes = assign_nodes_to_user(username, new_nodes)
            else:
                raise ApiCallException(
                    u'It looks like you either do not have a node yet or it has never been online yet.')
        return get_nodes_stats_from_influx(nodes)
    except ApiCallException:
        raise
    except Exception as e:
        logging.exception(e)
        raise ApiCallException(u'Could not get node status. Please try again later.')
