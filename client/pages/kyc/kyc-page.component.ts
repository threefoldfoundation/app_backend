import { ChangeDetectionStrategy, Component, OnDestroy, OnInit, ViewEncapsulation } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable, Subscription } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { filterNull, IAppState } from '../../../../framework/client/ngrx';
import { ApiRequestStatus } from '../../../../framework/client/rpc';
import { GetKYCChecksAction, SetKYCStatusAction, VerityUtilityBillAction } from '../../actions';
import { Check, SetKYCStatusPayload, TffProfile } from '../../interfaces';
import {
  getKYCChecks,
  getKYCChecksStatus,
  getTffProfile,
  getTffProfileStatus,
  setKYCStatus,
  verifyUtilityBillStatus,
} from '../../tff.state';

@Component({
  selector: 'tff-kyc-page',
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <mat-toolbar>
      <h2>{{ 'tff.kyc' | translate }}</h2>
    </mat-toolbar>
    <div class="default-component-padding">
      <tff-kyc [profile]="tffProfile$ | async"
               [status]="status$ | async"
               [updateStatus]="updateStatus$ | async"
               [checks]="checks$ | async"
               [checksStatus]="checksStatus$ | async"
               [utilityBillStatus]="utilityBillStatus$ | async"
               (setStatus)="onSetStatus($event)"
               (verifyUtilityBill)="onVerifyUtilityBill($event)"></tff-kyc>
    </div>`,
})

export class KycPageComponent implements OnInit, OnDestroy {
  tffProfile$: Observable<TffProfile>;
  status$: Observable<ApiRequestStatus>;
  updateStatus$: Observable<ApiRequestStatus>;
  checks$: Observable<Check[]>;
  checksStatus$: Observable<ApiRequestStatus>;
  utilityBillStatus$: Observable<ApiRequestStatus>;

  private _sub: Subscription;

  constructor(private store: Store<IAppState>) {
  }

  ngOnInit() {
    this.tffProfile$ = this.store.select(getTffProfile).pipe(
      filterNull<TffProfile>(),
      map(profile => ({
        ...profile, kyc: {
          ...profile.kyc,
          updates: profile.kyc.updates.concat().reverse(),
        },
      })));
    this.status$ = this.store.select(getTffProfileStatus);
    this.updateStatus$ = this.store.select(setKYCStatus);
    this.checks$ = this.store.select(getKYCChecks);
    this.checksStatus$ = this.store.select(getKYCChecksStatus);
    this.utilityBillStatus$ = this.store.select(verifyUtilityBillStatus);
    this._sub = this.tffProfile$.subscribe(user => {
      this.store.dispatch(new GetKYCChecksAction(user.username));
    });
  }

  ngOnDestroy() {
    this._sub.unsubscribe();
  }

  onSetStatus(setStatusPayload: SetKYCStatusPayload) {
    this.tffProfile$.pipe(take(1)).subscribe(profile => this.store.dispatch(new SetKYCStatusAction(profile.username, setStatusPayload)));
  }

  onVerifyUtilityBill(username: string) {
    this.store.dispatch(new VerityUtilityBillAction(username));
  }
}
