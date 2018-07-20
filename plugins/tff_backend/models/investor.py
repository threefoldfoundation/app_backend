from google.appengine.ext import ndb

from enum import IntEnum
from framework.models.common import NdbModel
from framework.utils import now
from plugins.tff_backend.bizz.gcs import get_serving_url, encrypt_filename
from plugins.tff_backend.consts.payment import TOKEN_TFT
from plugins.tff_backend.plugin_consts import NAMESPACE


class PaymentInfo(IntEnum):
    UAE = 1
    HAS_MULTIPLIED_TOKENS = 2


class InvestmentAgreement(NdbModel):
    NAMESPACE = NAMESPACE
    STATUS_CANCELED = -1
    STATUS_CREATED = 0
    STATUS_SIGNED = 1
    STATUS_PAID = 2

    def _compute_token_count(self):
        return round(float(self.token_count) / pow(10, self.token_precision), self.token_precision)

    app_user = ndb.UserProperty()  # todo: remove after migration 014
    username = ndb.StringProperty()
    amount = ndb.FloatProperty(indexed=False)
    token = ndb.StringProperty(indexed=False, default=TOKEN_TFT)
    token_count_float = ndb.ComputedProperty(_compute_token_count, indexed=False)  # Real amount of tokens
    token_count = ndb.IntegerProperty(indexed=False, default=0)  # amount of tokens x 10 ^ token_precision
    token_precision = ndb.IntegerProperty(indexed=False, default=0)
    currency = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)
    reference = ndb.StringProperty(indexed=False)

    iyo_see_id = ndb.StringProperty(indexed=False)
    signature_payload = ndb.StringProperty(indexed=False)
    signature = ndb.StringProperty(indexed=False)

    status = ndb.IntegerProperty(default=STATUS_CREATED)
    creation_time = ndb.IntegerProperty()
    sign_time = ndb.IntegerProperty()
    paid_time = ndb.IntegerProperty()
    cancel_time = ndb.IntegerProperty()
    modification_time = ndb.IntegerProperty()
    version = ndb.StringProperty()
    payment_info = ndb.IntegerProperty(repeated=True, choices=map(int, PaymentInfo))

    def _pre_put_hook(self):
        self.modification_time = now()

    def _post_put_hook(self, future):
        from plugins.tff_backend.dal.investment_agreements import index_investment_agreement
        if ndb.in_transaction():
            from google.appengine.ext import deferred
            deferred.defer(index_investment_agreement, self, _transactional=True)
        else:
            index_investment_agreement(self)

    @property
    def id(self):
        return self.key.id()

    @property
    def document_url(self):
        return get_serving_url(self.filename(self.id))

    @classmethod
    def filename(cls, agreement_id):
        return u'purchase-agreements/%s.pdf' % encrypt_filename(agreement_id)

    @classmethod
    def create_key(cls, agreement_id):
        return ndb.Key(cls, agreement_id, namespace=NAMESPACE)

    @classmethod
    def list(cls):
        return cls.query()

    @classmethod
    def list_by_user(cls, username):
        return cls.query() \
            .filter(cls.username == username)

    @classmethod
    def list_by_status_and_user(cls, username, statuses):
        # type: (unicode, list[int]) -> list[InvestmentAgreement]
        statuses = [statuses] if isinstance(statuses, int) else statuses
        return [investment for investment in cls.list_by_user(username) if investment.status in statuses]

    def to_dict(self, extra_properties=[], include=None, exclude=None):
        return super(InvestmentAgreement, self).to_dict(extra_properties + ['document_url'], include, exclude)
