import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { NodeOrdersQuery, ORDER_STATUSES } from '../../interfaces';

@Component({
  selector: 'tff-search-node-orders',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: 'search-node-orders.component.html',
})
export class SearchNodeOrdersComponent {
  statuses = ORDER_STATUSES;
  searchString: string | null;
  _query: NodeOrdersQuery;
  @Output() submitSearch = new EventEmitter();

  get query() {
    return { ...this._query, query: this.searchString };
  }

  @Input() set query(value: NodeOrdersQuery) {
    if (!this.searchString) {
      this.searchString = value.query;
    }
    this._query = { ...value, query: this.searchString };
  }


  submit() {
    this.query = { ...this.query, cursor: null };
    this.submitSearch.emit(this.query);
  }
}
