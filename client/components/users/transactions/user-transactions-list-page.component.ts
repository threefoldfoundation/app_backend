import { ChangeDetectionStrategy, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs/Observable';
import { IAppState } from '../../../../../framework/client/ngrx/state/app.state';
import { ApiRequestStatus } from '../../../../../framework/client/rpc/rpc.interfaces';
import { GetBalanceAction, GetUserTransactionsAction } from '../../../actions/threefold.action';
import { TransactionList, WalletBalance } from '../../../interfaces/transactions.interfaces';
import { getBalance, getBalanceStatus, getUserTransactions, getUserTransactionsStatus } from '../../../tff.state';

@Component({
  selector: 'user-transactions-list-page',
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="default-component-padding">
      <h2>{{ 'tff.wallet' | translate }}</h2>
      <wallet-balance [balance]="balance$ | async" [status]="balanceStatus$ | async"></wallet-balance>
      <h2>{{ 'tff.transactions' | translate }}</h2>
      <transaction-list [transactionList]="transactionList$ | async"
                        [status]="transactionListStatus$ | async"></transaction-list>
    </div>
    <div class="fab-bottom-right">
      <a md-fab [routerLink]="['create']">
        <md-icon>add</md-icon>
      </a>
    </div>`,
})

export class UserTransactionsListPageComponent implements OnInit {
  transactionList$: Observable<TransactionList>;
  transactionListStatus$: Observable<ApiRequestStatus>;
  balance$: Observable<WalletBalance[]>;
  balanceStatus$: Observable<ApiRequestStatus>;

  constructor(private store: Store<IAppState>,
              private route: ActivatedRoute) {
  }

  ngOnInit() {
    const username = this.route.parent.snapshot.params.username;
    this.store.dispatch(new GetUserTransactionsAction(username));
    this.store.dispatch(new GetBalanceAction(username));
    this.transactionList$ = this.store.select(getUserTransactions);
    this.balance$ = this.store.select(getBalance);
    this.balanceStatus$ = this.store.select(getBalanceStatus);
    this.transactionListStatus$ = this.store.select(getUserTransactionsStatus);
  }
}
