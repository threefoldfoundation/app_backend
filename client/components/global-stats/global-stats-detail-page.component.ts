import { ChangeDetectionStrategy, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { IAppState } from '../../../../framework/client/ngrx/state/app.state';
import { ActivatedRoute } from '@angular/router';
import { Store } from '@ngrx/store';
import { GlobalStats } from '../../interfaces/global-stats.interfaces';
import { Observable } from 'rxjs/Observable';
import { getGlobalStats, getGlobalStatsStatus, updateGlobalStatsStatus } from '../../tff.state';
import { GetGlobalStatsAction, UpdateGlobalStatsAction } from '../../actions/threefold.action';
import { ApiRequestStatus } from '../../../../framework/client/rpc/rpc.interfaces';

@Component({
  moduleId: module.id,
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <global-stats-detail [globalStats]="globalStats$ | async"
                         [status]="getStatus$ | async"
                         [updateStatus]="updateStatus$ | async"
                         (onSave)="save($event)"></global-stats-detail>`
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
    this.globalStats$ = this.store.let(getGlobalStats).filter(s => s !== null);
    this.getStatus$ = this.store.let(getGlobalStatsStatus);
    this.updateStatus$ = this.store.let(updateGlobalStatsStatus);
  }


  save(globalStats: GlobalStats) {
    this.store.dispatch(new UpdateGlobalStatsAction(globalStats));
  }
}
