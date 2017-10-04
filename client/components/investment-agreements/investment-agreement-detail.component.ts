import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { InvestmentAgreement, InvestmentAgreementsStatuses, } from '../../interfaces/index';
import { TranslateService } from '@ngx-translate/core';
import { ApiRequestStatus } from '../../../../framework/client/rpc/rpc.interfaces';
import {
  INVESTMENT_AGREEMENT_STATUSES,
  InvestmentAgreementDetail,
  TOKEN_PRECISION_MULTIPLIER
} from '../../interfaces/investment-agreements.interfaces';
import { GlobalStats } from '../../interfaces/global-stats.interfaces';

@Component({
  moduleId: module.id,
  selector: 'investment-agreement',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: 'investment-agreement-detail.component.html',
  styles: [ `.investment-agreement-content {
    padding: 16px;
  }` ]
})
export class InvestmentAgreementDetailComponent {
  statuses = InvestmentAgreementsStatuses;
  @Input() investmentAgreement: InvestmentAgreementDetail;
  @Input() globalStats: GlobalStats;
  @Input() status: ApiRequestStatus;
  @Input() updateStatus: ApiRequestStatus;
  @Input() canUpdate: boolean = false;
  @Output() onUpdate = new EventEmitter<InvestmentAgreement>();

  private _btcPrice: number;

  constructor(private translate: TranslateService) {
  }

  get btcPrice() {
    // Defaults to the value
    let defaultPrice = 0;
    if (this.investmentAgreement && this.globalStats) {
      defaultPrice = (this.investmentAgreement.token_count_float * this.globalStats.value) / this.investmentAgreement.amount;
    }
    return this._btcPrice || defaultPrice;
  }

  set btcPrice(value: number) {
    this._btcPrice = value;
  }

  get canMarkAsPaid(): boolean {
    return InvestmentAgreementsStatuses.SIGNED === this.investmentAgreement.status && this.canUpdate;
  }

  get canCancelInvestment(): boolean {
    return [ InvestmentAgreementsStatuses.CREATED, InvestmentAgreementsStatuses.SIGNED ].includes(this.investmentAgreement.status)
      && this.canUpdate;
  }

  getStatus(): string {
    return this.translate.instant(INVESTMENT_AGREEMENT_STATUSES[ this.investmentAgreement.status ]);
  }

  getTokenCount(): number {
    const amount = this.globalStats ? (this.investmentAgreement.amount * this.btcPrice / this.globalStats.value) : 0;
    return Math.round(amount * TOKEN_PRECISION_MULTIPLIER) / TOKEN_PRECISION_MULTIPLIER;
  }

  markAsPaid() {
    // Mark as signed, a message will be sent to the current user his account in the threefold app.
    // When the admin user has signed that message, then it will be marked as paid
    let updatedProperties = {
      status: InvestmentAgreementsStatuses.SIGNED,
      token_count_float: this.getTokenCount()
    };
    this.onUpdate.emit(<InvestmentAgreement>{ ...this.investmentAgreement, ...updatedProperties });
  }

  cancelInvestment() {
    this.onUpdate.emit(<InvestmentAgreement>{ ...this.investmentAgreement, status: InvestmentAgreementsStatuses.CANCELED });
  }
}
