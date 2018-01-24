import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnChanges, SimpleChanges, ViewEncapsulation } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { MOBILE_TYPES } from '../../../../rogerthat_api/client/interfaces';
import { FirebaseFlowRun, FlowRunStatus, TickerEntryType } from '../../interfaces';
import { TickerEntry } from '../../interfaces/dashboard';
import { AggregatedFlowRunStats, AggregatedInstallationStats } from '../../interfaces/flow-statistics.interfaces';
import { getStepTitle } from '../../util';
import ChartArea = google.visualization.ChartArea;
import ChartSpecs = google.visualization.ChartSpecs;
import ChartTextStyle = google.visualization.ChartTextStyle;
import PieChartOptions = google.visualization.PieChartOptions;

export interface ChartCard {
  title: string;
  chart: PieChart;
}

export interface PieChart extends ChartSpecs {
  options: PieChartOptions;
}

export enum ChartColor {
  GREEN = '#109618',
  RED = '#dc3912',
  BLUE = '#3366cc',
  ORANGE = '#ff9900',
  PURPLE = '#990099',
}

@Component({
  selector: 'tff-dashboard',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.Emulated,
  templateUrl: 'dashboard.component.html',
  styleUrls: [ 'dashboard.component.css' ],
})
export class DashboardComponent implements OnChanges {
  @Input() flowStats: AggregatedFlowRunStats[];
  @Input() tickerEntries: TickerEntry[];
  @Input() installationStats: AggregatedInstallationStats;
  timeDuration = 86400 * 7;
  TickerEntryType = TickerEntryType;
  cards: ChartCard[];
  defaultChartOptions = {
    is3D: true,
    legend: <'none'>'none',
    pieSliceText: 'label',
    width: 220,
    height: 220,
    chartArea: <ChartArea>{ width: '100%', height: '100%' },
    backgroundColor: 'transparent',
    pieSliceTextStyle: <ChartTextStyle>{ fontSize: 13 },
  };

  nameMapping: { [ key: string ]: string } = {
    'kyc_part_1': 'tff.kyc_procedure',
    'order_node_v4': 'tff.order_node',
    'error_message': 'tff.error_message',
    'buy_tokens_ITO_v3_async_KYC': 'tff.buy_tokens',
    'sign_investment': 'tff.sign_investment',
    'sign_hosting_agreement': 'tff.sign_hosting_agreement',
  };

  constructor(private translate: TranslateService,
              private datePipe: DatePipe) {
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.flowStats || changes.installationStats) {
      if (this.flowStats && this.flowStats.length && this.installationStats) {
        const flowCards = this.flowStats.map(f => ({
          title: this.getFlowName(f.flowName),
          chart: {
            chartType: 'PieChart',
            options: {
              ...this.defaultChartOptions,
              slices: {
                0: { color: ChartColor.BLUE },
                1: { color: ChartColor.ORANGE },
                2: { color: ChartColor.PURPLE },
                3: { color: ChartColor.RED },
                4: { color: ChartColor.GREEN },
              },
            },
            dataTable: [
              [ 'Title', 'Value' ],
              [ this.translate.instant('tff.started'), f.stats[ FlowRunStatus.STARTED ] ],
              [ this.translate.instant('tff.in_progress'), f.stats[ FlowRunStatus.IN_PROGRESS ] ],
              [ this.translate.instant('tff.stalled'), f.stats[ FlowRunStatus.STALLED ] ],
              [ this.translate.instant('tff.canceled'), f.stats[ FlowRunStatus.CANCELED ] ],
              [ this.translate.instant('tff.finished'), f.stats[ FlowRunStatus.FINISHED ] ],
            ],
          },
        }));
        const installationCard = {
          title: this.translate.instant('tff.app_installations'),
          chart: {
            chartType: 'PieChart',
            options: {
              ...this.defaultChartOptions,
              slices: {
                0: { color: ChartColor.BLUE },
                1: { color: ChartColor.ORANGE },
                2: { color: ChartColor.GREEN },
              },
            },
            dataTable: [
              [ 'title', 'Status' ],
              [ this.translate.instant('tff.started'), this.installationStats.started ],
              [ this.translate.instant('tff.in_progress'), this.installationStats.in_progress ],
              [ this.translate.instant('tff.finished'), this.installationStats.finished ],
            ],
          },
        };
        this.cards = [ installationCard, ...flowCards ];
      }
    }
  }

  getTickerText(entry: TickerEntry): string {
    if (entry.type === TickerEntryType.FLOW) {
      const flowRun = entry.data;
      const flowName = this.getFlowName(flowRun.flow_name);
      if (flowRun.status === FlowRunStatus.STARTED) {
        return flowName;
      }
      if (flowRun.status === FlowRunStatus.FINISHED) {
        return flowName;
      }
      if (flowRun.status === FlowRunStatus.IN_PROGRESS) {
        if (flowRun.last_step) {
          return `${flowName}: ${getStepTitle(flowRun.last_step.step_id)} -> Clicked "${getStepTitle(flowRun.last_step.button)}"`;
        }
        return flowName;
      }
      if (flowRun.status === FlowRunStatus.CANCELED) {
        return `${flowName}: Canceled at "${getStepTitle(flowRun.last_step.step_id)}" step`;
      }
      if (flowRun.status === FlowRunStatus.STALLED) {
        if (flowRun.last_step) {
          const time = this.datePipe.transform(entry.date, 'HH:mm');
          return `${flowName}: Stopped at step "${getStepTitle(flowRun.last_step.step_id)}" since ${time}`;
        }
        return flowName;
      }
    } else if (entry.type === TickerEntryType.INSTALLATION) {
      const platform = this.translate.instant(MOBILE_TYPES[ entry.data.platform ]);
      if (entry.data.name) {
        return this.translate.instant('tff.user_x_installed_on_platform', { name: entry.data.name, platform: platform });
      }
      return `${platform} installation`;
    } else {
      return JSON.stringify(entry);
    }
    return '';
  }

  trackCards(index: number, chart: ChartCard) {
    return chart.title;
  }

  trackTickerEntries(index: number, flowRun: FirebaseFlowRun) {
    return flowRun.id;
  }

  getTickerEntryUrl(tickerEntry: TickerEntry) {
    if (tickerEntry.type === TickerEntryType.FLOW) {
      return `/flow-statistics/${tickerEntry.data.flow_name}/${tickerEntry.data.id}`;
    } else {
      return `/installations/${tickerEntry.data.id}`;
    }
  }

  private getFlowName(flowName: string): string {
    if (flowName in this.nameMapping) {
      return this.translate.instant(this.nameMapping[ flowName ]);
    }
    return flowName;
  }

}
