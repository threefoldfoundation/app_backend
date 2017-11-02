import { ChangeDetectionStrategy, Component, OnDestroy, OnInit, ViewEncapsulation } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs/Observable';
import { Subscription } from 'rxjs/Subscription';
import { IAppState } from '../../../../framework/client/ngrx/state/app.state';
import { ApiRequestStatus } from '../../../../framework/client/rpc/rpc.interfaces';
import { GetInvestmentAgreementsAction } from '../../actions/threefold.action';
import { InvestmentAgreementList, InvestmentAgreementsQuery } from '../../interfaces/index';
import { getInvestmentAgreements, getInvestmentAgreementsQuery, getInvestmentAgreementsStatus } from '../../tff.state';

@Component({
  moduleId: module.id,
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  template: `
    <tff-investment-agreements [investmentAgreements]="investmentAgreements$ | async"
                               [listStatus]="listStatus$ | async"
                               [query]="query$ | async"
                               (onQuery)="onQuery($event)"></tff-investment-agreements>`
})
export class InvestmentAgreementListPageComponent implements OnInit, OnDestroy {
  investmentAgreements$: Observable<InvestmentAgreementList>;
  listStatus$: Observable<ApiRequestStatus>;
  query$: Observable<InvestmentAgreementsQuery>;

  private _sub: Subscription;

  constructor(private store: Store<IAppState>) {
  }

  ngOnInit() {
    this.query$ = this.store.select(getInvestmentAgreementsQuery);
    this.listStatus$ = this.store.select(getInvestmentAgreementsStatus);
    this.investmentAgreements$ = this.store.select(getInvestmentAgreements).withLatestFrom(this.query$)
      .map(([ result, query ]) => ({ ...result, results: result.results.filter(o => query.status ? o.status === query.status : true) }));
    this._sub = this.investmentAgreements$.first().subscribe(result => {
      // Load some investments on page load
      if (!result.results.length) {
        this.onQuery({ cursor: null, status: null, query: null });
      }
    });
  }

  ngOnDestroy() {
    this._sub.unsubscribe();
  }

  onQuery(payload: InvestmentAgreementsQuery) {
    this.store.dispatch(new GetInvestmentAgreementsAction(payload));
  }
}
