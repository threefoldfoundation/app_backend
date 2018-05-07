import { ChangeDetectionStrategy, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs';
import { filterNull, IAppState } from '../../../../framework/client/ngrx';
import { ApiRequestStatus } from '../../../../framework/client/rpc';
import { GetGlobalStatsAction, UpdateGlobalStatsAction } from '../../actions';
import { GlobalStats } from '../../interfaces';
import { getGlobalStats, getGlobalStatsStatus, updateGlobalStatsStatus } from '../../tff.state';

@Component({
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <tff-global-stats-detail [globalStats]="globalStats$ | async"
                             [status]="getStatus$ | async"
                             [updateStatus]="updateStatus$ | async"
                             (save)="onSubmit($event)"></tff-global-stats-detail>`,
})

export class GlobalStatsDetailPageComponent implements OnInit {
  globalStats$: Observable<GlobalStats>;
  getStatus$: Observable<ApiRequestStatus>;
  updateStatus$: Observable<ApiRequestStatus>;

  constructor(private store: Store<IAppState>,
              private route: ActivatedRoute) {
  }

  ngOnInit() {
    const statsId = this.route.snapshot.params.globalStatsId;
    this.store.dispatch(new GetGlobalStatsAction(statsId));
    this.globalStats$ = this.store.select(getGlobalStats).pipe(filterNull());
    this.getStatus$ = this.store.select(getGlobalStatsStatus);
    this.updateStatus$ = this.store.select(updateGlobalStatsStatus);
  }


  onSubmit(globalStats: GlobalStats) {
    this.store.dispatch(new UpdateGlobalStatsAction(globalStats));
  }
}
