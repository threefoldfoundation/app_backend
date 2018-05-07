import { ChangeDetectionStrategy, Component, Input, ViewEncapsulation } from '@angular/core';
import { ApiRequestStatus } from '../../../../framework/client/rpc/rpc.interfaces';
import { Transaction, TransactionList } from '../../interfaces/transactions.interfaces';

@Component({
  selector: 'tff-transaction-list',
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: 'transaction-list.component.html',
})

export class TransactionListComponent {
  @Input() transactionList: TransactionList;
  @Input() status: ApiRequestStatus;

  getAmount(transaction: Transaction) {
    return transaction.amount / Math.pow(10, transaction.precision || 2);
  }
}
