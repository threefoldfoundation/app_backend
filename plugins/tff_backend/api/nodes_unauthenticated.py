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
from datetime import datetime

from mcfw.restapi import rest
from mcfw.rpc import returns, arguments
from plugins.tff_backend.bizz.nodes.stats import update_node_chain_status, save_node_stats
from plugins.tff_backend.to.nodes import NodeChainStatusTO, UpdateNodeStatusTO


@rest('/nodes/<node_id:[^/]+>/chain-status', 'put', [])
@returns(dict)
@arguments(node_id=unicode, data=NodeChainStatusTO)
def api_update_node(node_id, data):
    return update_node_chain_status(node_id, data).to_dict()


@rest('/nodes/<node_id:[^/]+>/status', 'put', [])
@returns()
@arguments(node_id=unicode, data=UpdateNodeStatusTO)
def api_save_node_stats(node_id, data):
    return save_node_stats(node_id, data, datetime.now())

