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

from framework.utils import now, try_or_defer
from mcfw.exceptions import HttpNotFoundException, HttpBadRequestException
from mcfw.properties import object_factory
from mcfw.rpc import returns, arguments, serialize_complex_value
from plugins.rogerthat_api.api import qr, messaging
from plugins.rogerthat_api.to import UserDetailsTO
from plugins.rogerthat_api.to.messaging import AttachmentTO, Message
from plugins.rogerthat_api.to.messaging.flow import FLOW_STEP_MAPPING
from plugins.rogerthat_api.to.messaging.forms import SignTO, SignFormTO, FormResultTO, FormTO, SignWidgetResultTO
from plugins.rogerthat_api.to.messaging.service_callback_results import FlowMemberResultCallbackResultTO, \
    FormAcknowledgedCallbackResultTO, MessageCallbackResultTypeTO, TYPE_MESSAGE
from plugins.tff_backend.bizz import get_rogerthat_api_key
from plugins.tff_backend.bizz.agreements import create_hosting_agreement_pdf
from plugins.tff_backend.bizz.authentication import Roles
from plugins.tff_backend.bizz.ipfs import store_pdf
from plugins.tff_backend.bizz.iyo.keystore import get_keystore
from plugins.tff_backend.bizz.iyo.see import create_see_document, sign_see_document, get_see_document
from plugins.tff_backend.bizz.iyo.utils import get_iyo_username, get_iyo_organization_id
from plugins.tff_backend.bizz.service import get_main_branding_hash, add_user_to_role
from plugins.tff_backend.bizz.todo import update_hoster_progress
from plugins.tff_backend.bizz.todo.hoster import HosterSteps
from plugins.tff_backend.models.hoster import NodeOrder, PublicKeyMapping, NodeOrderStatus
from plugins.tff_backend.plugin_consts import KEY_NAME, KEY_ALGORITHM
from plugins.tff_backend.to.iyo.see import IYOSeeDocumentView, IYOSeeDocumenVersion
from plugins.tff_backend.to.nodes import NodeOrderTO
from plugins.tff_backend.utils import get_step_value
from plugins.tff_backend.utils.app import create_app_user_by_email, get_app_user_tuple


@returns()
@arguments(message_flow_run_id=unicode, member=unicode, steps=[object_factory("step_type", FLOW_STEP_MAPPING)],
           end_id=unicode, end_message_flow_id=unicode, parent_message_key=unicode, tag=unicode, result_key=unicode,
           flush_id=unicode, flush_message_flow_id=unicode, service_identity=unicode, user_details=[UserDetailsTO],
           flow_params=unicode)
def order_node(message_flow_run_id, member, steps, end_id, end_message_flow_id, parent_message_key, tag, result_key,
               flush_id, flush_message_flow_id, service_identity, user_details, flow_params):
    app_user = create_app_user_by_email(user_details[0].email, user_details[0].app_id)
    order_key = NodeOrder.create_key()
    deferred.defer(_order_node, order_key, app_user, steps, 0)


def _order_node(order_key, app_user, steps, retry_count):
    logging.info('Receiving order of Zero-Node')
    name = get_step_value(steps, 'message_name')
    email = get_step_value(steps, 'message_email')
    phone = get_step_value(steps, 'message_phone')
    billing_address = get_step_value(steps, 'message_billing_address')
    shipping_address = get_step_value(steps, 'message_shipping_address')

    logging.debug('Creating Hosting agreement')
    pdf_name = 'node_%s.pdf' % order_key.id()
    pdf_contents = create_hosting_agreement_pdf(name, billing_address)
    ipfs_link = store_pdf(pdf_name, pdf_contents)
    if not ipfs_link:
        logging.error(u"Failed to create IPFS document with name %s and retry_count %s", pdf_name, retry_count)
        deferred.defer(_order_node, order_key, app_user, steps, retry_count + 1, _countdown=retry_count)
        return

    logging.debug('Storing order in the database')

    def trans():
        order = NodeOrder(key=order_key,
                          app_user=app_user,
                          tos_iyo_see_id=None,
                          name=name,
                          email=email,
                          phone=phone,
                          billing_address=billing_address,
                          shipping_address=shipping_address,
                          order_time=now(),
                          status=NodeOrderStatus.CREATED)
        order.put()
        deferred.defer(_create_order_arrival_qr, order_key.id(), _transactional=True)
        deferred.defer(_order_node_iyo_see, app_user, order_key, ipfs_link, _transactional=True)

    ndb.transaction(trans)


def _order_node_iyo_see(app_user, order_key, ipfs_link):
    iyo_username = get_iyo_username(app_user)
    organization_id = get_iyo_organization_id()

    iyo_see_doc = IYOSeeDocumentView(username=iyo_username,
                                     globalid=organization_id,
                                     uniqueid=u'Zero-Node order %s' % NodeOrder.create_human_readable_id(
                                         order_key.id()),
                                     version=1,
                                     category=u'Terms and conditions',
                                     link=ipfs_link,
                                     content_type=u'application/pdf',
                                     markdown_short_description=u'Terms and conditions for ordering a Zero-Node',
                                     markdown_full_description=u'Terms and conditions for ordering a Zero-Node')
    logging.debug('Creating IYO SEE document: %s', iyo_see_doc)
    iyo_see_doc = create_see_document(iyo_username, iyo_see_doc)

    attachment_name = u' - '.join([iyo_see_doc.uniqueid, iyo_see_doc.category])

    def trans():
        order = order_key.get()
        order.tos_iyo_see_id = iyo_see_doc.uniqueid
        order.put()
        deferred.defer(_send_order_node_sign_message, app_user, order_key.id(), ipfs_link, attachment_name,
                       _transactional=True)

    ndb.transaction(trans)


@returns()
@arguments(app_user=users.User, order_id=(int, long), ipfs_link=unicode, attachment_name=unicode)
def _send_order_node_sign_message(app_user, order_id, ipfs_link, attachment_name):
    logging.debug('Sending SIGN widget to app user')
    widget = SignTO()
    widget.algorithm = KEY_ALGORITHM
    widget.caption = u'Please enter your PIN code to digitally sign the terms and conditions'
    widget.key_name = KEY_NAME
    widget.payload = base64.b64encode(ipfs_link).decode('utf-8')

    form = SignFormTO()
    form.negative_button = u'Abort'
    form.negative_button_ui_flags = 0
    form.positive_button = u'Accept'
    form.positive_button_ui_flags = Message.UI_FLAG_EXPECT_NEXT_WAIT_5
    form.type = SignTO.TYPE
    form.widget = widget

    attachment = AttachmentTO()
    attachment.content_type = u'application/pdf'
    attachment.download_url = ipfs_link
    attachment.name = attachment_name

    member_user, app_id = get_app_user_tuple(app_user)
    messaging.send_form(api_key=get_rogerthat_api_key(),
                        parent_message_key=None,
                        member=member_user.email(),
                        message=u'Please review the terms and conditions and press the "Sign" button to accept.',
                        form=form,
                        flags=0,
                        alert_flags=Message.ALERT_FLAG_VIBRATE,
                        branding=get_main_branding_hash(),
                        tag=json.dumps({u'__rt__.tag': u'sign_order_node_tos',
                                        u'order_id': order_id}).decode('utf-8'),
                        attachments=[attachment],
                        app_id=app_id,
                        step_id=u'sign_order_node_tos')


@returns(FormAcknowledgedCallbackResultTO)
@arguments(status=int, form_result=FormResultTO, answer_id=unicode, member=unicode, message_key=unicode, tag=unicode,
           received_timestamp=int, acked_timestamp=int, parent_message_key=unicode, result_key=unicode,
           service_identity=unicode, user_details=[UserDetailsTO])
def order_node_signed(status, form_result, answer_id, member, message_key, tag, received_timestamp, acked_timestamp,
                      parent_message_key, result_key, service_identity, user_details):
    """
    Args:
        status (int)
        form_result (FormResultTO)
        answer_id (unicode)
        member (unicode)
        message_key (unicode)
        tag (unicode)
        received_timestamp (int)
        acked_timestamp (int)
        parent_message_key (unicode)
        result_key (unicode)
        service_identity (unicode)
        user_details(list[UserDetailsTO])

    Returns:
        FormAcknowledgedCallbackResultTO
    """
    try:
        user_detail = user_details[0]
        tag_dict = json.loads(tag)
        order = NodeOrder.create_key(tag_dict['order_id']).get()  # type: NodeOrder

        if answer_id != FormTO.POSITIVE:
            logging.info('Zero-Node order was canceled')
            order.status = NodeOrderStatus.CANCELED
            order.cancel_time = now()
            order.put()
            return None

        logging.info('Received signature for Zero-Node order')

        sign_result = form_result.result.get_value()
        assert isinstance(sign_result, SignWidgetResultTO)
        payload_signature = sign_result.payload_signature

        iyo_organization_id = get_iyo_organization_id()
        iyo_username = get_iyo_username(user_detail)

        logging.debug('Getting IYO SEE document %s', order.tos_iyo_see_id)
        doc = get_see_document(iyo_organization_id, iyo_username, order.tos_iyo_see_id)
        doc_view = IYOSeeDocumentView(username=doc.username,
                                      globalid=doc.globalid,
                                      uniqueid=doc.uniqueid,
                                      **serialize_complex_value(doc.versions[-1], IYOSeeDocumenVersion, False))
        doc_view.signature = payload_signature
        keystore_label = get_publickey_label(sign_result.public_key.public_key, user_detail)
        if not keystore_label:
            return _create_error_message(FormAcknowledgedCallbackResultTO())
        doc_view.keystore_label = keystore_label
        logging.debug('Signing IYO SEE document')
        sign_see_document(iyo_organization_id, iyo_username, doc_view)

        logging.debug('Storing signature in DB')
        order.populate(status=NodeOrderStatus.SIGNED,
                       signature=payload_signature,
                       sign_time=now())
        order.put()

        # TODO: send mail to TF support
        deferred.defer(add_user_to_role, user_detail, Roles.HOSTER)
        deferred.defer(update_hoster_progress, user_detail.email, user_detail.app_id, HosterSteps.FLOW_SIGN)

        logging.debug('Sending confirmation message')
        message = MessageCallbackResultTypeTO()
        message.alert_flags = Message.ALERT_FLAG_VIBRATE
        message.answers = []
        message.branding = get_main_branding_hash()
        message.dismiss_button_ui_flags = 0
        message.flags = Message.FLAG_ALLOW_DISMISS | Message.FLAG_AUTO_LOCK
        message.message = u'Thank you. Your order with ID "%s" has been placed successfully.\n\n' \
                          u'You can check the status of your order using' \
                          u' the "Check on node transit" functionality.' % order.human_readable_id
        message.step_id = u'order_completed'
        message.tag = None

        result = FormAcknowledgedCallbackResultTO()
        result.type = TYPE_MESSAGE
        result.value = message
        return result
    except:
        logging.exception('An unexpected error occurred')
        return _create_error_message(FormAcknowledgedCallbackResultTO())


def get_publickey_label(public_key, user_details):
    # type: (unicode, UserDetailsTO) -> unicode
    mapping = PublicKeyMapping.create_key(public_key, user_details.email).get()
    if mapping:
        return mapping.label
    else:
        logging.error('No PublicKeyMapping found! falling back to doing a request to itsyou.online')
        iyo_keys = get_keystore(get_iyo_username(user_details))
        results = filter(lambda k: public_key in k.key, iyo_keys)  # some stuff is prepended to the key
        if len(results):
            return results[0].label
        else:
            logging.error('Could not find label for public key %s on itsyou.online', public_key)
            return None


@returns()
@arguments(order_id=(int, long))
def _create_order_arrival_qr(order_id):
    human_readable_id = NodeOrder.create_human_readable_id(order_id)
    api_key = get_rogerthat_api_key()
    qr_details = qr.create(api_key,
                           description=u'Confirm arrival of order\n%s' % human_readable_id,
                           tag=json.dumps({u'__rt__.tag': u'node_arrival',
                                           u'order_id': order_id}),
                           flow=u'node_arrival',
                           branding=get_main_branding_hash())

    try_or_defer(_store_order_arrival_qr, order_id, qr_details.image_uri)


@returns()
@arguments(order_id=(int, long), qr_image_uri=unicode)
def _store_order_arrival_qr(order_id, qr_image_uri):
    logging.info('Setting arrival QR code %s for order %s', qr_image_uri, order_id)
    order = NodeOrder.create_key(order_id).get()
    order.arrival_qr_code_url = qr_image_uri
    order.put()


@returns(FlowMemberResultCallbackResultTO)
@arguments(message_flow_run_id=unicode, member=unicode, steps=[object_factory("step_type", FLOW_STEP_MAPPING)],
           end_id=unicode, end_message_flow_id=unicode, parent_message_key=unicode, tag=unicode, result_key=unicode,
           flush_id=unicode, flush_message_flow_id=unicode, service_identity=unicode, user_details=[UserDetailsTO],
           flow_params=unicode)
def node_arrived(message_flow_run_id, member, steps, end_id, end_message_flow_id, parent_message_key, tag, result_key,
                 flush_id, flush_message_flow_id, service_identity, user_details, flow_params):
    try_or_defer(_store_order_arrival, tag, now())
    return None


@returns(tuple)
@arguments(cursor=unicode, status=(int, long))
def get_node_orders(cursor=None, status=None):
    return NodeOrder.fetch_page(cursor, status)


@returns(NodeOrder)
@arguments(order_id=(int, long))
def get_node_order(order_id):
    order = NodeOrder.get_by_id(order_id)
    if not order:
        raise HttpNotFoundException('order_not_found')
    return order


@returns(NodeOrder)
@arguments(order_id=(int, long), order=NodeOrderTO)
def put_node_order(order_id, order):
    # type: (long, NodeOrderTO) -> NodeOrder
    order_model = NodeOrder.get_by_id(order_id)  # type: NodeOrder
    if not order_model:
        raise HttpNotFoundException('order_not_found')
    if order_model.status == NodeOrderStatus.CANCELED:
        raise HttpBadRequestException('order_canceled')
    if order.status not in (NodeOrderStatus.CANCELED, NodeOrderStatus.SENT):
        raise HttpBadRequestException('invalid_status')
    # Only support updating the status for now
    if order_model.status != order.status:
        order_model.status = order.status
        # todo: send message to user ?
        if order_model.status == NodeOrderStatus.CANCELED:
            order_model.cancel_time = now()
        elif order_model.status == NodeOrderStatus.SENT:
            order_model.send_time = now()
            human_user, app_id = get_app_user_tuple(order_model.app_user)
            deferred.defer(update_hoster_progress, human_user.email(), app_id, HosterSteps.NODE_SENT)

    order_model.put()
    return order_model


@returns()
@arguments(tag=unicode, arrival_time=(int, long))
def _store_order_arrival(tag, arrival_time):
    tag_dict = json.loads(tag)
    order_id = tag_dict['order_id']
    logging.info('Marking order %s as arrived', order_id)
    order = NodeOrder.create_key(order_id).get()  # type: NodeOrder
    order.arrival_time = arrival_time
    order.status = NodeOrderStatus.ARRIVED
    order.put()

    human_user, app_id = get_app_user_tuple(order.app_user)
    deferred.defer(update_hoster_progress, human_user.email(), app_id, HosterSteps.NODE_DELIVERY_CONFIRMED)


def _create_error_message(callback_result):
    logging.debug('Sending error message')
    message = MessageCallbackResultTypeTO()
    message.alert_flags = Message.ALERT_FLAG_VIBRATE
    message.answers = []
    message.branding = get_main_branding_hash()
    message.dismiss_button_ui_flags = 0
    message.flags = Message.FLAG_ALLOW_DISMISS | Message.FLAG_AUTO_LOCK
    message.message = u'Oh no! An error occurred.\nHow embarrassing :-(\n\nPlease try again later.'
    message.step_id = u'error'
    message.tag = None

    callback_result.type = TYPE_MESSAGE
    callback_result.value = message
    return callback_result
