import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { FirebaseFlowStats, FlowRun, FlowRunList, FlowRunQuery, UserFlowRunsQuery } from '../interfaces';
import { getQueryParams } from '../util';
import { TffConfig } from './tff-config.service';

@Injectable()
export class FlowStatisticsService {
  flowNameMapping: { [ key: string ]: string } = {
    'KYC_inhouse_nocode': 'tff.inhouse_kyc',
    'kyc_part_1': 'tff.kyc_procedure',
    'order_node_v3': 'tff.order_node',
    'order_node_v4': 'tff.order_node',
    'error_message': 'tff.error_message',
    'buy_tokens_ITO_v3_async_KYC': 'tff.buy_tokens',
    'buy_tokens_ITO_v5': 'tff.buy_tokens',
    'buy_tokens_v6': 'tff.buy_tokens',
    'sign_investment': 'tff.sign_investment',
    'sign_hosting_agreement': 'tff.sign_hosting_agreement',
    'utility_bill_received': 'tff.utility_bill_received',
    'hoster_reminder': 'tff.hoster_reminder',
    'sign_token_value_addendum': 'tff.sign_token_value_addendum',
    'nodes_sold_out': 'tff.nodes_sold_out',
    'buy_tokens_stopped': 'tff.buy_tokens_stopped',
  };

  constructor(private http: HttpClient,
              private translate: TranslateService) {
  }

  getFlowName(flowName: string): string {
    if (flowName in this.flowNameMapping) {
      return this.translate.instant(this.flowNameMapping[ flowName ]);
    }
    return flowName;
  }

  getDistinctFlows() {
    return this.http.get<string[]>(`${TffConfig.API_URL}/flow-statistics/flows`);
  }

  getFlowRuns(query: FlowRunQuery): Observable<FlowRunList> {
    const params = getQueryParams(query);
    return this.http.get<FlowRunList<string>>(`${TffConfig.API_URL}/flow-statistics`, { params }).pipe(
      map(result => ({ ...result, results: result.results.map(flowRun => this.convertFlowRun(flowRun)) })),
    );
  }

  getFlowRun(id: string): Observable<FlowRun> {
    return this.http.get<FlowRun<string>>(`${TffConfig.API_URL}/flow-statistics/details/${id}`).pipe(
      map(result => this.convertFlowRun(result)),
    );
  }

  getFlowStats(startDate: string) {
    const params = getQueryParams({ start_date: startDate });
    return this.http.get<FirebaseFlowStats[]>(`${TffConfig.API_URL}/flow-statistics/stats`, { params });
  }

  getUserFlowRuns(query: UserFlowRunsQuery) {
    const params = getQueryParams({ cursor: query.cursor, page_size: query.page_size });
    return this.http.get<FlowRunList<string>>(`${TffConfig.API_URL}/users/${encodeURIComponent(query.username)}/flows`, { params }).pipe(
      map(result => ({ ...result, results: result.results.map(flowRun => this.convertFlowRun(flowRun)) })));
  }

  /**
   * Converts string dates in the FlowRun object to Date objects
   */
  private convertFlowRun(flowRun: FlowRun<string>): FlowRun<Date> {
    return {
      ...flowRun,
      start_date: new Date(flowRun.start_date),
      statistics: { ...flowRun.statistics, last_step_date: new Date(flowRun.statistics.last_step_date) },
    };
  }
}
