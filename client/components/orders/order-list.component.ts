import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output, ViewEncapsulation } from '@angular/core';
import { GetNodeOrdersPayload, NodeOrderList, NodeOrderStatuses, ORDER_STATUSES } from '../../interfaces/index';
import { ApiRequestStatus } from '../../../../framework/client/rpc/rpc.interfaces';

@Component({
  moduleId: module.id,
  selector: 'tff-order-list',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  templateUrl: 'order-list.component.html',
  styles: [ `.orders-content {
    padding: 16px;
  }
  ` ]
})
export class OrderListComponent {
  @Input() orders: NodeOrderList;
  @Input() listStatus: ApiRequestStatus;
  @Input() status: NodeOrderStatuses;
  @Output() onLoadOrders = new EventEmitter<GetNodeOrdersPayload>();
  statuses = ORDER_STATUSES;

  getStatusString(): string {
    return ORDER_STATUSES.find(s => s.value === this.status).label;
  }

  onStatusChange() {
    this.onLoadOrders.emit({ cursor: null, status: this.status });
  }

  loadMore() {
    this.onLoadOrders.emit({ cursor: this.orders.cursor, status: this.status });
  }
}
