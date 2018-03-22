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

import base64
import json
import logging

from google.appengine.api import users
from google.appengine.ext import ndb, deferred

from framework.consts import get_base_url
from framework.plugin_loader import get_config
from framework.utils import now
from mcfw.consts import DEBUG, MISSING
from mcfw.exceptions import HttpBadRequestException
from mcfw.properties import object_factory
from mcfw.rpc import returns, arguments
from plugins.rogerthat_api.api import messaging, system
from plugins.rogerthat_api.to import UserDetailsTO, MemberTO
from plugins.rogerthat_api.to.messaging import AttachmentTO, Message
from plugins.rogerthat_api.to.messaging.flow import FLOW_STEP_MAPPING
from plugins.rogerthat_api.to.messaging.forms import SignTO, SignFormTO, FormTO, SignWidgetResultTO
from plugins.rogerthat_api.to.messaging.service_callback_results import TYPE_FLOW, FlowCallbackResultTypeTO, \
    FlowMemberResultCallbackResultTO
from plugins.tff_backend.bizz import get_rogerthat_api_key
from plugins.tff_backend.bizz.agreements import create_hosting_agreement_pdf
from plugins.tff_backend.bizz.authentication import RogerthatRoles
from plugins.tff_backend.bizz.email import send_emails_to_support
from plugins.tff_backend.bizz.gcs import upload_to_gcs
from plugins.tff_backend.bizz.intercom_helpers import tag_intercom_users, IntercomTags
from plugins.tff_backend.bizz.iyo.see import get_see_document, sign_see_document, create_see_document
from plugins.tff_backend.bizz.iyo.utils import get_iyo_username, get_iyo_organization_id
from plugins.tff_backend.bizz.messages import send_message_and_email
from plugins.tff_backend.bizz.nodes.stats import assign_nodes_to_user
from plugins.tff_backend.bizz.odoo import create_odoo_quotation, update_odoo_quotation, QuotationState, \
    confirm_odoo_quotation, get_nodes_from_odoo
from plugins.tff_backend.bizz.rogerthat import put_user_data, create_error_message
from plugins.tff_backend.bizz.service import add_user_to_role
from plugins.tff_backend.bizz.todo import update_hoster_progress
from plugins.tff_backend.bizz.todo.hoster import HosterSteps
from plugins.tff_backend.configuration import TffConfiguration
from plugins.tff_backend.consts.hoster import REQUIRED_TOKEN_COUNT_TO_HOST
from plugins.tff_backend.dal.node_orders import get_node_order
from plugins.tff_backend.exceptions.hoster import OrderAlreadyExistsException, InvalidContentTypeException
from plugins.tff_backend.models.hoster import NodeOrder, NodeOrderStatus, ContactInfo
from plugins.tff_backend.models.investor import InvestmentAgreement
from plugins.tff_backend.plugin_consts import KEY_NAME, KEY_ALGORITHM, NAMESPACE, FLOW_HOSTER_SIGNATURE_RECEIVED, \
    FLOW_SIGN_HOSTING_AGREEMENT
from plugins.tff_backend.to.nodes import NodeOrderTO, NodeOrderDetailsTO, CreateNodeOrderTO
from plugins.tff_backend.utils import get_step_value, get_step
from plugins.tff_backend.utils.app import create_app_user_by_email, get_app_user_tuple


@returns()
@arguments(message_flow_run_id=unicode, member=unicode, steps=[object_factory("step_type", FLOW_STEP_MAPPING)],
           end_id=unicode, end_message_flow_id=unicode, parent_message_key=unicode, tag=unicode, result_key=unicode,
           flush_id=unicode, flush_message_flow_id=unicode, service_identity=unicode, user_details=[UserDetailsTO],
           flow_params=unicode)
def order_node(message_flow_run_id, member, steps, end_id, end_message_flow_id, parent_message_key, tag, result_key,
               flush_id, flush_message_flow_id, service_identity, user_details, flow_params):
    order_key = NodeOrder.create_key()
    deferred.defer(_order_node, order_key, user_details[0].email, user_details[0].app_id, steps)


def _order_node(order_key, user_email, app_id, steps):
    logging.info('Receiving order of Zero-Node')
    app_user = create_app_user_by_email(user_email, app_id)

    overview_step = get_step(steps, 'message_overview')
    if overview_step and overview_step.answer_id == u"button_use":
        api_key = get_rogerthat_api_key()
        user_data_keys = ['name', 'email', 'phone', 'billing_address', 'address', 'shipping_name', 'shipping_email',
                          'shipping_phone', 'shipping_address']
        user_data = system.get_user_data(api_key, user_email, app_id, user_data_keys)
        billing_info = ContactInfo(name=user_data['name'],
                                   email=user_data['email'],
                                   phone=user_data['phone'],
                                   address=user_data['billing_address'] or user_data['address'])

        if user_data['shipping_name']:
            shipping_info = ContactInfo(name=user_data['shipping_name'],
                                        email=user_data['shipping_email'],
                                        phone=user_data['shipping_phone'],
                                        address=user_data['shipping_address'])
        else:
            shipping_info = billing_info

        updated_user_data = None
    else:
        name = get_step_value(steps, 'message_name')
        email = get_step_value(steps, 'message_email')
        phone = get_step_value(steps, 'message_phone')
        billing_address = get_step_value(steps, 'message_billing_address')
        updated_user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'billing_address': billing_address,
        }

        billing_info = ContactInfo(name=name,
                                   email=email,
                                   phone=phone,
                                   address=billing_address)

        same_shipping_info_step = get_step(steps, 'message_choose_shipping_info')
        if same_shipping_info_step and same_shipping_info_step.answer_id == u"button_yes":
            shipping_info = billing_info
        else:
            shipping_name = get_step_value(steps, 'message_shipping_name')
            shipping_email = get_step_value(steps, 'message_shipping_email')
            shipping_phone = get_step_value(steps, 'message_shipping_phone')
            shipping_address = get_step_value(steps, 'message_shipping_address')
            updated_user_data.update({
                'shipping_name': shipping_name,
                'shipping_email': shipping_email,
                'shipping_phone': shipping_phone,
                'shipping_address': shipping_address,
            })

            shipping_info = ContactInfo(name=shipping_name,
                                        email=shipping_email,
                                        phone=shipping_phone,
                                        address=shipping_address)
    socket_step = get_step(steps, 'message_socket')
    socket = socket_step and socket_step.answer_id.replace('button_', '')

    # Only one node is allowed per user, and one per location
    if NodeOrder.has_order_for_user_or_location(app_user, billing_info.address) and not DEBUG:
        logging.info('User already has a node order, sending abort message')
        msg = u'Dear ThreeFold Member, we sadly cannot grant your request to host an additional ThreeFold Node:' \
              u' We are currently only allowing one Node to be hosted per ThreeFold Member and location.' \
              u' This will allow us to build a bigger base and a more diverse Grid.'
        subject = u'Your ThreeFold Node request'
        send_message_and_email(app_user, msg, subject)
        return

    # Check if user has invested >= 120 tokens
    paid_orders = InvestmentAgreement.list_by_status_and_user(app_user, InvestmentAgreement.STATUS_PAID)
    total_tokens = sum([o.token_count_float for o in paid_orders])
    can_host = total_tokens >= REQUIRED_TOKEN_COUNT_TO_HOST

    def trans():
        logging.debug('Storing order in the database')
        order = NodeOrder(key=order_key,
                          app_user=app_user,
                          tos_iyo_see_id=None,
                          billing_info=billing_info,
                          shipping_info=shipping_info,
                          order_time=now(),
                          status=NodeOrderStatus.APPROVED if can_host else NodeOrderStatus.WAITING_APPROVAL,
                          socket=socket)
        order.put()
        if can_host:
            logging.info('User has invested more than %s tokens, immediately creating node order PDF.',
                         REQUIRED_TOKEN_COUNT_TO_HOST)
            deferred.defer(_create_node_order_pdf, order_key.id(), _transactional=True)
        else:
            logging.info('User has not invested more than %s tokens, an admin needs to approve this order manually.',
                         REQUIRED_TOKEN_COUNT_TO_HOST)
            deferred.defer(_inform_support_of_new_node_order, order_key.id(), _transactional=True)
        deferred.defer(set_hoster_status_in_user_data, order.app_user, False, _transactional=True)
        if updated_user_data:
            deferred.defer(put_user_data, app_user, updated_user_data, _transactional=True)

    ndb.transaction(trans)


def _create_node_order_pdf(node_order_id):
    node_order = get_node_order(node_order_id)
    user_email, app_id = get_app_user_tuple(node_order.app_user)
    logging.debug('Creating Hosting agreement')
    pdf_name = NodeOrder.filename(node_order_id)
    pdf_contents = create_hosting_agreement_pdf(node_order.billing_info.name, node_order.billing_info.address)
    pdf_size = len(pdf_contents)
    pdf_url = upload_to_gcs(pdf_name, pdf_contents, 'application/pdf')
    deferred.defer(_order_node_iyo_see, node_order.app_user, node_order_id, pdf_url, pdf_size)
    deferred.defer(update_hoster_progress, user_email.email(), app_id, HosterSteps.FLOW_ADDRESS)


def _order_node_iyo_see(app_user, node_order_id, pdf_url, pdf_size, create_quotation=True):
    iyo_username = get_iyo_username(app_user)
    doc_id = u'Zero-Node order %s' % NodeOrder.create_human_readable_id(node_order_id)
    category = u'Terms and conditions'
    content_type = u'application/pdf'
    description = u'Terms and conditions for ordering a Zero-Node'
    create_see_document(doc_id, category, description, iyo_username, pdf_url, content_type)
    attachment_name = u' - '.join([doc_id, category])

    def trans():
        order = get_node_order(node_order_id)
        order.tos_iyo_see_id = doc_id
        order.put()
        if create_quotation:
            deferred.defer(_create_quotation, app_user, node_order_id, pdf_url, attachment_name, pdf_size,
                           _transactional=True)

    ndb.transaction(trans)


@returns()
@arguments(app_user=users.User, order_id=(int, long), pdf_url=unicode, attachment_name=unicode, pdf_size=(int, long))
def _create_quotation(app_user, order_id, pdf_url, attachment_name, pdf_size):
    order = get_node_order(order_id)
    config = get_config(NAMESPACE)
    assert isinstance(config, TffConfiguration)
    product_id = config.odoo.product_ids.get(order.socket)
    if not product_id:
        logging.warn('Could not find appropriate product for socket %s. Falling back to EU socket.', order.socket)
        product_id = config.odoo.product_ids['EU']
    odoo_sale_order_id, odoo_sale_order_name = create_odoo_quotation(order.billing_info, order.shipping_info,
                                                                     product_id)

    order.odoo_sale_order_id = odoo_sale_order_id
    order.put()

    deferred.defer(_send_order_node_sign_message, app_user, order_id, pdf_url, attachment_name,
                   odoo_sale_order_name, pdf_size)


@returns()
@arguments(order_id=(int, long))
def _cancel_quotation(order_id):
    def trans():
        node_order = get_node_order(order_id)
        if node_order.odoo_sale_order_id:
            update_odoo_quotation(node_order.odoo_sale_order_id, {'state': QuotationState.CANCEL.value})

        node_order.populate(status=NodeOrderStatus.CANCELED, cancel_time=now())
        node_order.put()

    ndb.transaction(trans)


@returns()
@arguments(app_user=users.User, order_id=(int, long), pdf_url=unicode, attachment_name=unicode, order_name=unicode,
           pdf_size=(int, long))
def _send_order_node_sign_message(app_user, order_id, pdf_url, attachment_name, order_name, pdf_size):
    logging.debug('Sending SIGN widget to app user')
    widget = SignTO(algorithm=KEY_ALGORITHM,
                    key_name=KEY_NAME,
                    payload=base64.b64encode(pdf_url).decode('utf-8'))
    form = SignFormTO(positive_button_ui_flags=Message.UI_FLAG_EXPECT_NEXT_WAIT_5,
                      widget=widget)
    attachment = AttachmentTO(content_type=u'application/pdf',
                              download_url=pdf_url,
                              name=attachment_name,
                              size=pdf_size)

    member_user, app_id = get_app_user_tuple(app_user)

    members = [MemberTO(member=member_user.email(), app_id=app_id, alert_flags=0)]
    tag = json.dumps({
        u'__rt__.tag': u'sign_order_node_tos',
        u'order_id': order_id
    }).decode('utf-8')
    flow_params = json.dumps({
        'order_name': order_name,
        'form': form.to_dict(),
        'attachments': [attachment.to_dict()]
    })
    messaging.start_local_flow(get_rogerthat_api_key(), None, members, None, tag=tag, context=None,
                               flow=FLOW_SIGN_HOSTING_AGREEMENT, flow_params=flow_params)


@returns(FlowMemberResultCallbackResultTO)
@arguments(message_flow_run_id=unicode, member=unicode, steps=[object_factory("step_type", FLOW_STEP_MAPPING)],
           end_id=unicode, end_message_flow_id=unicode, parent_message_key=unicode, tag=unicode, result_key=unicode,
           flush_id=unicode, flush_message_flow_id=unicode, service_identity=unicode, user_details=[UserDetailsTO],
           flow_params=unicode)
def order_node_signed(message_flow_run_id, member, steps, end_id, end_message_flow_id, parent_message_key, tag,
                      result_key, flush_id, flush_message_flow_id, service_identity, user_details, flow_params):
    try:
        user_detail = user_details[0]
        tag_dict = json.loads(tag)
        order = get_node_order(tag_dict['order_id'])

        last_step = steps[-1]
        if last_step.answer_id != FormTO.POSITIVE:
            logging.info('Zero-Node order was canceled')
            deferred.defer(_cancel_quotation, order.id)
            return None

        logging.info('Received signature for Zero-Node order')

        sign_result = last_step.form_result.result.get_value()
        assert isinstance(sign_result, SignWidgetResultTO)
        iyo_username = get_iyo_username(user_detail)
        sign_see_document(iyo_username, order.tos_iyo_see_id, sign_result, user_detail)

        logging.debug('Storing signature in DB')
        order.populate(status=NodeOrderStatus.SIGNED,
                       signature=sign_result.payload_signature,
                       sign_time=now())
        order.put()

        # TODO: send mail to TF support
        deferred.defer(add_user_to_role, user_detail, RogerthatRoles.HOSTERS)
        deferred.defer(update_hoster_progress, user_detail.email, user_detail.app_id, HosterSteps.FLOW_SIGN)
        intercom_tags = get_intercom_tags_for_node_order(order)
        for intercom_tag in intercom_tags:
            deferred.defer(tag_intercom_users, intercom_tag, [iyo_username])

        logging.debug('Sending confirmation message')
        result = FlowCallbackResultTypeTO(flow=FLOW_HOSTER_SIGNATURE_RECEIVED,
                                          tag=None,
                                          force_language=None,
                                          flow_params=json.dumps({'orderId': order.human_readable_id}))
        return FlowMemberResultCallbackResultTO(type=TYPE_FLOW,
                                                value=result)
    except:
        logging.exception('An unexpected error occurred')
        return create_error_message()


@returns(NodeOrderDetailsTO)
@arguments(order_id=(int, long))
def get_node_order_details(order_id):
    # type: (long) -> NodeOrderDetailsTO
    node_order = get_node_order(order_id)
    if node_order.tos_iyo_see_id:
        iyo_organization_id = get_iyo_organization_id()
        username = get_iyo_username(node_order.app_user)
        see_document = get_see_document(iyo_organization_id, username, node_order.tos_iyo_see_id)
    else:
        see_document = None
    return NodeOrderDetailsTO.from_model(node_order, see_document)


def _get_allowed_status(current_status):
    # type: (long, long) -> list[long]
    next_statuses = {
        NodeOrderStatus.CANCELED: [],
        NodeOrderStatus.WAITING_APPROVAL: [NodeOrderStatus.CANCELED, NodeOrderStatus.APPROVED],
        NodeOrderStatus.APPROVED: [NodeOrderStatus.CANCELED, NodeOrderStatus.SIGNED],
        NodeOrderStatus.SIGNED: [NodeOrderStatus.CANCELED, NodeOrderStatus.PAID],
        NodeOrderStatus.PAID: [NodeOrderStatus.SENT],
        NodeOrderStatus.SENT: [],
        NodeOrderStatus.ARRIVED: [],
    }
    return next_statuses.get(current_status)


def _can_change_status(current_status, new_status):
    # type: (long, long) -> bool
    return new_status in _get_allowed_status(current_status)


@returns(NodeOrder)
@arguments(order_id=(int, long), order=NodeOrderTO)
def put_node_order(order_id, order):
    # type: (long, NodeOrderTO) -> NodeOrder
    order_model = get_node_order(order_id)
    if order_model.status == NodeOrderStatus.CANCELED:
        raise HttpBadRequestException('order_canceled')
    if order.status not in (NodeOrderStatus.CANCELED, NodeOrderStatus.SENT, NodeOrderStatus.APPROVED,
                            NodeOrderStatus.PAID):
        raise HttpBadRequestException('invalid_status')
    # Only support updating the status for now
    if order_model.status != order.status:
        if not _can_change_status(order_model.status, order.status):
            raise HttpBadRequestException('cannot_change_status',
                                          {'from': order_model.status, 'to': order.status,
                                           'allowed_new_statuses': _get_allowed_status(order_model.status)})
        order_model.status = order.status
        human_user, app_id = get_app_user_tuple(order_model.app_user)
        if order_model.status == NodeOrderStatus.CANCELED:
            order_model.cancel_time = now()
            if order_model.odoo_sale_order_id:
                deferred.defer(update_odoo_quotation, order_model.odoo_sale_order_id,
                               {'state': QuotationState.CANCEL.value})
            deferred.defer(update_hoster_progress, human_user.email(), app_id,
                           HosterSteps.NODE_POWERED)  # nuke todo list
            deferred.defer(set_hoster_status_in_user_data, order_model.app_user, _countdown=2)
        elif order_model.status == NodeOrderStatus.SENT:
            if not order_model.odoo_sale_order_id or not get_nodes_from_odoo(order_model.odoo_sale_order_id):
                raise HttpBadRequestException('cannot_mark_sent_no_serial_number_configured_yet',
                                              {'sale_order': order_model.odoo_sale_order_id})
            order_model.send_time = now()
            deferred.defer(update_hoster_progress, human_user.email(), app_id, HosterSteps.NODE_SENT)
            deferred.defer(_send_node_order_sent_message, order_id)
        elif order_model.status == NodeOrderStatus.APPROVED:
            deferred.defer(_create_node_order_pdf, order_id)
        elif order_model.status == NodeOrderStatus.PAID:
            deferred.defer(confirm_odoo_quotation, order_model.odoo_sale_order_id)
    else:
        logging.debug('Status was already %s, not doing anything', order_model.status)
    order_model.put()
    return order_model


def _inform_support_of_new_node_order(node_order_id):
    node_order = get_node_order(node_order_id)
    iyo_username = get_iyo_username(node_order.app_user)

    subject = 'New Node Order by %s' % node_order.billing_info.name
    body = """Hello,

We just received a new Node order from %(name)s (IYO username %(iyo_username)s) with id %(node_order_id)s.
This order needs to be manually approved since this user has not invested more than %(tokens)s tokens yet via the app.
Check the old purchase agreements to verify if this user can sign up as a hoster and if not, contact him.

Please visit %(base_url)s/orders/%(node_order_id)s to approve or cancel this order.
""" % {
        'name': node_order.billing_info.name,
        'iyo_username': iyo_username,
        'base_url': get_base_url(),
        'node_order_id': node_order.id,
        'tokens': REQUIRED_TOKEN_COUNT_TO_HOST
    }

    send_emails_to_support(subject, body)


def _send_node_order_sent_message(node_order_id):
    node_order = get_node_order(node_order_id)
    subject = u'ThreeFold node ready to ship out'
    msg = u'Good news, your ThreeFold node (order id %s) has been prepared for shipment.' \
          u' It will be handed over to our shipping partner soon.' \
          u'\nThanks again for accepting hosting duties and helping to grow the ThreeFold Grid close to the users.' % \
          node_order_id
    send_message_and_email(node_order.app_user, msg, subject)


def get_intercom_tags_for_node_order(order):
    # type: (NodeOrder) -> list[IntercomTags]
    if order.status in [NodeOrderStatus.ARRIVED, NodeOrderStatus.SENT, NodeOrderStatus.SIGNED, NodeOrderStatus.PAID]:
        return [IntercomTags.HOSTER]
    return []


def set_hoster_status_in_user_data(app_user, can_order=None):
    # type: (users.User, bool) -> None
    if not isinstance(can_order, bool):
        can_order = all(o.status == NodeOrderStatus.CANCELED for o in NodeOrder.list_by_user(app_user))
    user_data = {
        'hoster': {
            'can_order': can_order
        }
    }
    api_key = get_rogerthat_api_key()
    email, app_id = get_app_user_tuple(app_user)
    current_user_data = system.get_user_data(api_key, email.email(), app_id, ['hoster'])
    if current_user_data != user_data:
        system.put_user_data(api_key, email.email(), app_id, user_data)


@returns(NodeOrder)
@arguments(data=CreateNodeOrderTO)
def create_node_order(data):
    # type: (CreateNodeOrderTO) -> NodeOrder
    if data.status not in (NodeOrderStatus.SIGNED, NodeOrderStatus.SENT, NodeOrderStatus.ARRIVED, NodeOrderStatus.PAID):
        data.sign_time = MISSING
    if data.status not in (NodeOrderStatus.SENT, NodeOrderStatus.ARRIVED):
        data.send_time = MISSING
    app_user = users.User(data.app_user)
    order_count = NodeOrder.list_by_so(data.odoo_sale_order_id).count()
    if order_count > 0:
        raise OrderAlreadyExistsException(data.odoo_sale_order_id)
    try:
        nodes = get_nodes_from_odoo(data.odoo_sale_order_id)
    except (IndexError, TypeError):
        logging.warn('Could not get nodes from odoo for order id %s' % data.odoo_sale_order_id, exc_info=True)
        raise HttpBadRequestException('cannot_find_so_x', {'id': data.odoo_sale_order_id})
    if not nodes:
        raise HttpBadRequestException('no_serial_number_configured_yet',
                                      {'sale_order': data.odoo_sale_order_id})
    prefix, doc_content_base64 = data.document.split(',')
    content_type = prefix.split(';')[0].replace('data:', '')
    if content_type != 'application/pdf':
        raise InvalidContentTypeException(content_type, ['application/pdf'])

    doc_content = base64.b64decode(doc_content_base64)
    order_key = NodeOrder.create_key()
    pdf_name = NodeOrder.filename(order_key.id())
    pdf_url = upload_to_gcs(pdf_name, doc_content, content_type)
    order = NodeOrder(key=order_key,
                      app_user=app_user,
                      **data.to_dict(exclude=['document', 'app_user']))
    order.put()
    iyo_username = get_iyo_username(app_user)
    email, app_id = get_app_user_tuple(app_user)
    deferred.defer(assign_nodes_to_user, iyo_username, nodes)
    deferred.defer(set_hoster_status_in_user_data, order.app_user, False)
    deferred.defer(add_user_to_role, UserDetailsTO(email=email.email(), app_id=app_id), RogerthatRoles.HOSTERS)
    deferred.defer(tag_intercom_users, IntercomTags.HOSTER, [iyo_username])
    deferred.defer(_order_node_iyo_see, order.app_user, order.id, pdf_url, len(doc_content), create_quotation=False)
    return order
