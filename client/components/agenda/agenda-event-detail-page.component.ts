import { ChangeDetectionStrategy, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs/Observable';
import { ApiRequestStatus } from '../../../../framework/client/rpc/rpc.interfaces';
import { GetAgendaEventAction, UpdateAgendaEventAction } from '../../actions/threefold.action';
import { AgendaEvent } from '../../interfaces/agenda-events.interfaces';
import { ITffState } from '../../states/tff.state';
import { getAgendaEvent, getAgendaEventStatus, updateAgendaEventStatus } from '../../tff.state';

@Component({
  selector: 'tff-agenda-event-detail-page',
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="default-component-padding">
      <tff-agenda-event-detail [event]="agendaEvent$ | async" [status]="status$ | async" [updateStatus]="updateStatus$ | async"
                               (submitted)="onSubmitted($event)"></tff-agenda-event-detail>
    </div>`
})

export class AgendaEventDetailPageComponent implements OnInit {
  agendaEvent$: Observable<AgendaEvent>;
  status$: Observable<ApiRequestStatus>;
  updateStatus$: Observable<ApiRequestStatus>;

  constructor(private store: Store<ITffState>,
              private route: ActivatedRoute) {
  }

  ngOnInit() {
    const eventId = this.route.snapshot.params.eventId;
    this.store.dispatch(new GetAgendaEventAction(eventId));
    this.agendaEvent$ = this.store.select(getAgendaEvent);
    this.status$ = this.store.select(getAgendaEventStatus);
    this.updateStatus$ = this.store.select(updateAgendaEventStatus);
  }

  onSubmitted(agendaEvent: AgendaEvent) {
    this.store.dispatch(new UpdateAgendaEventAction(agendaEvent));
  }
}
