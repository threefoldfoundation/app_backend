import { CommonModule, CurrencyPipe, DatePipe, DecimalPipe, I18nPluralPipe } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { NgModule, Optional, SkipSelf } from '@angular/core';
import { FlexLayoutModule } from '@angular/flex-layout';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import {
  MAT_FORM_FIELD_DEFAULT_OPTIONS,
  MatAutocompleteModule,
  MatButtonModule,
  MatCardModule,
  MatCheckboxModule,
  MatChipsModule,
  MatDatepickerModule,
  MatExpansionModule,
  MatGridListModule,
  MatIconModule,
  MatInputModule,
  MatListModule,
  MatNativeDateModule,
  MatProgressSpinnerModule,
  MatSelectModule,
  MatSlideToggleModule,
  MatSortModule,
  MatTableModule,
  MatTabsModule,
  MatToolbarModule,
  MatTooltipModule,
} from '@angular/material';
import { RouterModule } from '@angular/router';
import { EffectsModule } from '@ngrx/effects';
import { Store, StoreModule } from '@ngrx/store';
// noinspection ES6UnusedImports
import {} from '@types/google.visualization';
import { Ng2GoogleChartsModule } from 'ng2-google-charts';
import { AddRoutesAction, AuthenticationService, ChannelModule, MultilingualModule, ToolbarItemTypes } from '../../framework/client';
import { AddToolbarItemAction } from '../../framework/client/';
import { SetThemeAction } from '../../framework/client/identity';
import { IAppState } from '../../framework/client/ngrx';
import {
  AgendaEventDetailComponent,
  AgendaEventDetailPageComponent,
  AgendaEventsListComponent,
  AgendaEventsListPageComponent,
  ApiRequestStatusComponent,
  CreateAgendaEventPageComponent,
  CreateNodeComponent,
  DashboardComponent,
  EditNodeComponent,
  EventParticipantsComponent,
  EventParticipantsPageComponent,
  FlowRunDetailComponent,
  FlowRunListComponent,
  FlowRunStatusComponent,
  GlobalStatsDetailComponent,
  GlobalStatsDetailPageComponent,
  GlobalStatsListPageComponent,
  InstallationComponent,
  InstallationLogsComponent,
  InstallationsComponent,
  InstallationStatusComponent,
  InvestmentAgreementAmountComponent,
  InvestmentAgreementDetailComponent,
  InvestmentAgreementDetailPageComponent,
  InvestmentAgreementListComponent,
  InvestmentAgreementListPageComponent,
  IyoSeeComponent,
  KycComponent,
  KycUpdatesComponent,
  NodesComponent,
  OrderDetailComponent,
  OrderDetailPageComponent,
  OrderListComponent,
  OrderListPageComponent,
  SearchInvestmentAgreementsComponent,
  SearchNodeOrdersComponent,
  TransactionListComponent,
  UserCardComponent,
  UserDetailsComponent,
  UserListComponent,
  UserSearchComponent,
  WalletBalanceComponent,
} from './components';
import { UserFieldComponent } from './components/users';
import { TffEffects } from './effects';
import {
  CreateInvestmentAgreementPageComponent,
  CreateNodePageComponent,
  CreateOrderPageComponent,
  DashboardPageComponent,
  EditNodePageComponent,
  FlowStatisticsDetailPageComponent,
  FlowStatisticsOverviewPageComponent,
  FlowStatisticsPageComponent,
  InstallationLogsPageComponent,
  InstallationsPageComponent,
  KycPageComponent,
  NodesPageComponent,
  UserDetailsPageComponent,
  UserFlowRunsDetailsPageComponent,
  UserFlowRunsPageComponent,
  UserListPageComponent,
  UserNodeOrdersPageComponent,
  UserPageComponent,
  UserPurchaseAgreementsPageComponent,
  UserTransactionsListPageComponent,
} from './pages';
import { AmountPipe } from './pipes/amount.pipe';
import { MarkdownPipe } from './pipes/markdown.pipe';
import { TimeDurationPipe } from './pipes/time-duration.pipe';
import { TimePipe } from './pipes/time.pipe';
import { TimestampPipe } from './pipes/timestamp.pipe';
import { tffReducer } from './reducers';
import { TffRoutes } from './routes';
import { ApiErrorService, CSVService, FlowStatisticsService, TffConfig, TffService } from './services';

const MATERIAL_IMPORTS = [
  MatAutocompleteModule,
  MatButtonModule,
  MatCardModule,
  MatCheckboxModule,
  MatChipsModule,
  MatDatepickerModule,
  MatExpansionModule,
  MatGridListModule,
  MatIconModule,
  MatInputModule,
  MatListModule,
  MatNativeDateModule,
  MatProgressSpinnerModule,
  MatSelectModule,
  MatSlideToggleModule,
  MatTableModule,
  MatTabsModule,
  MatToolbarModule,
  MatTooltipModule,
  MatSortModule,
];

const PIPES = [
  AmountPipe,
  TimestampPipe,
  MarkdownPipe,
  TimePipe,
  TimeDurationPipe,
];

export const TFF_PROVIDERS = [
  ApiErrorService,
  CSVService,
  FlowStatisticsService,
  TffConfig,
  TffService,
  DecimalPipe,
];

export const TFF_PAGES = [
  CreateInvestmentAgreementPageComponent,
  CreateNodePageComponent,
  CreateOrderPageComponent,
  DashboardPageComponent,
  EditNodePageComponent,
  FlowStatisticsDetailPageComponent,
  FlowStatisticsOverviewPageComponent,
  FlowStatisticsPageComponent,
  InstallationLogsPageComponent,
  InstallationsPageComponent,
  KycPageComponent,
  NodesPageComponent,
  UserDetailsPageComponent,
  UserFlowRunsDetailsPageComponent,
  UserFlowRunsPageComponent,
  UserListPageComponent,
  UserNodeOrdersPageComponent,
  UserPageComponent,
  UserPurchaseAgreementsPageComponent,
  UserTransactionsListPageComponent,
];

export const TFF_COMPONENTS: any[] = [
  AgendaEventDetailComponent,
  AgendaEventDetailPageComponent,
  AgendaEventsListComponent,
  AgendaEventsListPageComponent,
  ApiRequestStatusComponent,
  CreateAgendaEventPageComponent,
  CreateNodeComponent,
  DashboardComponent,
  EditNodeComponent,
  EventParticipantsComponent,
  EventParticipantsPageComponent,
  FlowRunDetailComponent,
  FlowRunListComponent,
  FlowRunStatusComponent,
  GlobalStatsDetailComponent,
  GlobalStatsDetailPageComponent,
  GlobalStatsListPageComponent,
  InstallationComponent,
  InstallationLogsComponent,
  InstallationsComponent,
  InstallationStatusComponent,
  InvestmentAgreementAmountComponent,
  InvestmentAgreementDetailComponent,
  InvestmentAgreementDetailPageComponent,
  InvestmentAgreementListComponent,
  InvestmentAgreementListPageComponent,
  IyoSeeComponent,
  KycComponent,
  KycUpdatesComponent,
  NodesComponent,
  OrderDetailComponent,
  OrderDetailPageComponent,
  OrderListComponent,
  OrderListPageComponent,
  SearchInvestmentAgreementsComponent,
  SearchNodeOrdersComponent,
  TransactionListComponent,
  UserCardComponent,
  UserDetailsComponent,
  UserFieldComponent,
  UserListComponent,
  UserSearchComponent,
  WalletBalanceComponent,
  ...TFF_PAGES,
];

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    RouterModule,
    MultilingualModule,
    RouterModule.forChild(TffRoutes),
    StoreModule.forFeature('tff', tffReducer),
    EffectsModule.forFeature([ TffEffects ]),
    MATERIAL_IMPORTS,
    FlexLayoutModule,
    ChannelModule,
    Ng2GoogleChartsModule,
  ],
  declarations: [
    TFF_COMPONENTS,
    PIPES,
  ],
  providers: [
    DatePipe,
    CurrencyPipe,
    I18nPluralPipe,
    TFF_PROVIDERS,
    PIPES,
    {
      provide: MAT_FORM_FIELD_DEFAULT_OPTIONS,
      useValue: {
        appearance: 'standard',
      },
    },
  ],
  exports: [
    TFF_COMPONENTS,
  ],
})
export class TffBackendModule {
  constructor(@Optional() @SkipSelf() parentModule: TffBackendModule,
              private store: Store<IAppState>,
              private authService: AuthenticationService) {
    if (parentModule) {
      throw new Error('TffBackendModule already loaded; Import in root module only.');
    }
    this.store.dispatch(new AddRoutesAction(TffRoutes));
    const themeItem = {
      id: 'change_theme',
      type: ToolbarItemTypes.ICON,
      icon: 'format_color_fill',
      persistent: true,
      onclick: () => {
        const newTheme = this.authService.getLocalTheme() ? null : { cssClass: 'dark-theme', dark: true };
        this.store.dispatch(new SetThemeAction(newTheme));
      },
    };
    this.store.dispatch(new AddToolbarItemAction(themeItem));
  }
}
