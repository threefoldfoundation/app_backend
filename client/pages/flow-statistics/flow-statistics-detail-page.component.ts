import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { select, Store } from '@ngrx/store';
import { combineLatest, Observable, Subscription } from 'rxjs';
import { filter, map, take, withLatestFrom } from 'rxjs/operators';
import { filterNull } from '../../../../framework/client/ngrx';
import { ApiRequestStatus } from '../../../../framework/client/rpc';
import { GetFlowRunAction, GetTffProfileAction } from '../../actions';
import { FlowRun, TffProfile } from '../../interfaces';
import { ITffState } from '../../states';
import { getFlowRun, getFlowRunStatus, getTffProfile, getTffProfileStatus } from '../../tff.state';

@Component({
  selector: 'tff-flow-statistics-detail-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="default-component-padding">
      <button mat-button [routerLink]="['..']">
        <mat-icon>arrow_back</mat-icon>
        {{ 'tff.back' | translate }}
      </button>
      <tff-flow-run-detail [flowRun]="flowRun$ | async" [profile]="profile$ | async" [status]="status$ | async"></tff-flow-run-detail>
    </div>`,
})
export class FlowStatisticsDetailPageComponent implements OnInit, OnDestroy {
  flowRun$: Observable<FlowRun>;
  profile$: Observable<TffProfile>;
  status$: Observable<ApiRequestStatus>;
  flowId: string;

  private _flowRunSubscription: Subscription;

  constructor(private route: ActivatedRoute,
              private store: Store<ITffState>) {
  }

  ngOnInit() {
    this.flowId = this.route.snapshot.params.flowId;
    this.flowRun$ = this.store.select(getFlowRun).pipe(filterNull());
    this.status$ = combineLatest(this.store.pipe(select(getFlowRunStatus)), this.store.pipe(select(getTffProfileStatus))).pipe(
      map(([ s1, s2 ]) => ({ success: s1.success && s2.success, loading: s1.loading || s2.loading, error: s1.error || s2.error })),
    );
    this.profile$ = this.store.pipe(select(getTffProfile), filterNull());
    this.getFlowRun();
    this._flowRunSubscription = this.store.select(getFlowRunStatus).pipe(
      filter(s => s.success),
      withLatestFrom(this.flowRun$),
      take(1),
    ).subscribe(([ _, f ]) => this.store.dispatch(new GetTffProfileAction(f.user)));
  }

  ngOnDestroy() {
    this._flowRunSubscription.unsubscribe();
  }

  getFlowRun() {
    this.store.dispatch(new GetFlowRunAction(this.flowId));
  }
}
