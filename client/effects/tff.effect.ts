import { Injectable } from '@angular/core';
import { Actions, Effect, ofType } from '@ngrx/effects';
import { catchError, debounceTime, map, switchMap } from 'rxjs/operators';
import { handleApiError } from '../../../framework/client/rpc';
import * as actions from '../actions/threefold.action';
import { FlowStatisticsService, TffService } from '../services';

const SEARCH_DEBOUNCE_TIME = 400;

@Injectable()
export class TffEffects {

  @Effect() getNodeOrders$ = this.actions$.pipe(
    ofType<actions.GetOrdersAction>(actions.TffActionTypes.GET_ORDERS),
    debounceTime(SEARCH_DEBOUNCE_TIME),
    switchMap(action => this.tffService.getNodeOrders(action.payload).pipe(
      map(payload => new actions.GetOrdersCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetOrdersFailedAction, err)),
    )));

  @Effect() getNodeOrder$ = this.actions$.pipe(
    ofType<actions.GetOrderAction>(actions.TffActionTypes.GET_ORDER),
    switchMap(action => this.tffService.getNodeOrder(action.payload).pipe(
      map(payload => new actions.GetOrderCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetOrderFailedAction, err)),
    )));

  @Effect() createOrder$ = this.actions$.pipe(
    ofType<actions.CreateOrderAction>(actions.TffActionTypes.CREATE_ORDER),
    switchMap(action => this.tffService.createNodeOrder(action.payload).pipe(
      map(payload => new actions.CreateOrderCompleteAction(payload)),
      catchError(err => handleApiError(actions.CreateOrderFailedAction, err)),
    )));

  @Effect() updateNodeOrdes$ = this.actions$.pipe(
    ofType<actions.UpdateOrderAction>(actions.TffActionTypes.UPDATE_ORDER),
    switchMap(action => this.tffService.updateNodeOrder(action.payload).pipe(
      map(payload => new actions.UpdateOrderCompleteAction(payload)),
      catchError(err => handleApiError(actions.UpdateOrderFailedAction, err)),
    )));

  @Effect() getInvestmentAgreements$ = this.actions$.pipe(
    ofType<actions.GetInvestmentAgreementsAction>(actions.TffActionTypes.GET_INVESTMENT_AGREEMENTS),
    debounceTime(SEARCH_DEBOUNCE_TIME),
    switchMap(action => this.tffService.getInvestmentAgreements(action.payload).pipe(
      map(payload => new actions.GetInvestmentAgreementsCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetInvestmentAgreementsFailedAction, err)),
    )));

  @Effect() getInvestmentAgreement$ = this.actions$.pipe(
    ofType<actions.GetInvestmentAgreementAction>(actions.TffActionTypes.GET_INVESTMENT_AGREEMENT),
    switchMap(action => this.tffService.getInvestmentAgreement(action.payload).pipe(
      map(payload => new actions.GetInvestmentAgreementCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetInvestmentAgreementFailedAction, err)),
    )));

  @Effect() updateInvestmentAgreement$ = this.actions$.pipe(
    ofType<actions.UpdateInvestmentAgreementAction>(actions.TffActionTypes.UPDATE_INVESTMENT_AGREEMENT),
    switchMap(action => this.tffService.updateInvestmentAgreement(action.payload).pipe(
      map(payload => new actions.UpdateInvestmentAgreementCompleteAction(payload)),
      catchError(err => handleApiError(actions.UpdateInvestmentAgreementFailedAction, err)),
    )));

  @Effect() createInvestmentAgreement$ = this.actions$.pipe(
    ofType<actions.CreateInvestmentAgreementAction>(actions.TffActionTypes.CREATE_INVESTMENT_AGREEMENT),
    switchMap(action => this.tffService.createInvestmentAgreement(action.payload).pipe(
      map(payload => new actions.CreateInvestmentAgreementCompleteAction(payload)),
      catchError(err => handleApiError(actions.CreateInvestmentAgreementFailedAction, err)),
    )));

  @Effect() getGlobalStatsList$ = this.actions$.pipe(
    ofType<actions.GetGlobalStatsListAction>(actions.TffActionTypes.GET_GLOBAL_STATS_LIST),
    switchMap(() => this.tffService.getGlobalStatsList().pipe(
      map(payload => new actions.GetGlobalStatsListCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetGlobalStatsListFailedAction, err)),
    )));

  @Effect() getGlobalStats$ = this.actions$.pipe(
    ofType<actions.GetGlobalStatsAction>(actions.TffActionTypes.GET_GLOBAL_STATS),
    switchMap(action => this.tffService.getGlobalStats(action.payload).pipe(
      map(payload => new actions.GetGlobalStatsCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetGlobalStatsFailedAction, err)),
    )));

  @Effect() updateGlobalStats$ = this.actions$.pipe(
    ofType<actions.UpdateGlobalStatsAction>(actions.TffActionTypes.UPDATE_GLOBAL_STATS),
    switchMap(action => this.tffService.updateGlobalStats(action.payload).pipe(
      map(payload => new actions.UpdateGlobalStatsCompleteAction(payload)),
      catchError(err => handleApiError(actions.UpdateGlobalStatsFailedAction, err)),
    )));

  @Effect() searchUsers$ = this.actions$.pipe(
    ofType<actions.SearchUsersAction>(actions.TffActionTypes.SEARCH_USERS),
    debounceTime(SEARCH_DEBOUNCE_TIME),
    switchMap(action => this.tffService.searchUsers(action.payload).pipe(
      map(payload => new actions.SearchUsersCompleteAction(payload)),
      catchError(err => handleApiError(actions.SearchUsersFailedAction, err)),
    )));

  @Effect() getUser$ = this.actions$.pipe(
    ofType<actions.GetUserAction>(actions.TffActionTypes.GET_USER),
    switchMap(action => this.tffService.getUser(action.payload).pipe(
      map(payload => new actions.GetUserCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetUserFailedAction, err)),
    )));

  @Effect() getTffProfile$ = this.actions$.pipe(
    ofType<actions.GetTffProfileAction>(actions.TffActionTypes.GET_TFF_PROFILE),
    switchMap(action => this.tffService.getTffProfile(action.payload).pipe(
      map(payload => new actions.GetTffProfileCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetTffProfileFailedAction, err)),
    )));

  @Effect() setKYCStatus$ = this.actions$.pipe(
    ofType<actions.SetKYCStatusAction>(actions.TffActionTypes.SET_KYC_STATUS),
    switchMap(action => this.tffService.setKYCStatus(action.username, action.payload).pipe(
      map(payload => new actions.SetKYCStatusCompleteAction(payload)),
      catchError(err => handleApiError(actions.SetKYCStatusFailedAction, err)),
    )));

  @Effect() verifyUtilityBill$ = this.actions$.pipe(
    ofType<actions.VerityUtilityBillAction>(actions.TffActionTypes.VERIFY_UTILITY_BILL),
    switchMap(action => this.tffService.verifyUtilityBill(action.username).pipe(
      map(payload => new actions.VerityUtilityBillCompleteAction(payload)),
      catchError(err => handleApiError(actions.VerityUtilityBillFailedAction, err)),
    )));

  @Effect() getBalance$ = this.actions$.pipe(
    ofType<actions.GetBalanceAction>(actions.TffActionTypes.GET_BALANCE),
    switchMap(action => this.tffService.getBalance(action.payload).pipe(
      map(payload => new actions.GetBalanceCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetBalanceFailedAction, err)),
    )));

  @Effect() getUserTransactions$ = this.actions$.pipe(
    ofType<actions.GetUserTransactionsAction>(actions.TffActionTypes.GET_USER_TRANSACTIONS),
    switchMap(action => this.tffService.getUserTransactions(action.payload).pipe(
      map(payload => new actions.GetUserTransactionsCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetUserTransactionsFailedAction, err)),
    )));

  @Effect() createTransaction$ = this.actions$.pipe(
    ofType<actions.CreateTransactionAction>(actions.TffActionTypes.CREATE_TRANSACTION),
    switchMap(action => this.tffService.createTransaction(action.payload).pipe(
      map(payload => new actions.CreateTransactionCompleteAction(payload)),
      catchError(err => handleApiError(actions.CreateTransactionFailedAction, err)),
    )));

  @Effect() getAgendaEvents$ = this.actions$.pipe(
    ofType<actions.GetAgendaEventsAction>(actions.TffActionTypes.GET_AGENDA_EVENTS),
    switchMap(action => this.tffService.getAgendaEvents(action.payload).pipe(
      map(payload => new actions.GetAgendaEventsCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetAgendaEventsFailedAction, err)),
    )));

  @Effect() getAgendaEvent$ = this.actions$.pipe(
    ofType<actions.GetAgendaEventAction>(actions.TffActionTypes.GET_AGENDA_EVENT),
    switchMap(action => this.tffService.getAgendaEvent(action.payload).pipe(
      map(payload => new actions.GetAgendaEventCompleteAction(payload)),
      catchError(err => handleApiError(actions.GetAgendaEventFailedAction, err)),
    )));

  @Effect() updateAgendaEvent$ = this.actions$.pipe(
    ofType<actions.UpdateAgendaEventAction>(actions.TffActionTypes.UPDATE_AGENDA_EVENT),
    switchMap(action => this.tffService.updateAgendaEvent(action.payload).pipe(
      map(result => new actions.UpdateAgendaEventCompleteAction(result)),
      catchError(err => handleApiError(actions.UpdateAgendaEventFailedAction, err)),
    )));

  @Effect() createAgendaEvent$ = this.actions$.pipe(
    ofType<actions.CreateAgendaEventAction>(actions.TffActionTypes.CREATE_AGENDA_EVENT),
    switchMap(action => this.tffService.createAgendaEvent(action.payload).pipe(
      map(result => new actions.CreateAgendaEventCompleteAction(result)),
      catchError(err => handleApiError(actions.CreateAgendaEventFailedAction, err)),
    )));

  @Effect() getEventPresence$ = this.actions$.pipe(
    ofType<actions.GetEventParticipantsAction>(actions.TffActionTypes.GET_EVENT_PARTICIPANTS),
    switchMap(action => this.tffService.getEventParticipants(action.payload).pipe(
      map(result => new actions.GetEventParticipantsCompleteAction(result)),
      catchError(err => handleApiError(actions.GetEventParticipantsFailedAction, err)),
    )));

  @Effect() getKYCChecks$ = this.actions$.pipe(
    ofType<actions.GetKYCChecksAction>(actions.TffActionTypes.GET_KYC_CHECKS),
    switchMap(action => this.tffService.getKYCChecks(action.payload).pipe(
      map(result => new actions.GetKYCChecksCompleteAction(result)),
      catchError(err => handleApiError(actions.GetKYCChecksFailedAction, err)),
    )));

  @Effect() getUserFlowRuns$ = this.actions$.pipe(
    ofType<actions.GetUserFlowRunsAction>(actions.TffActionTypes.GET_USER_FLOW_RUNS),
    switchMap(action => this.flowStatisticsService.getUserFlowRuns(action.payload).pipe(
      map(result => new actions.GetUserFlowRunsCompleteAction(result)),
      catchError(err => handleApiError(actions.GetUserFlowRunsFailedAction, err)),
    )));

  @Effect() getDistinctFlows$ = this.actions$.pipe(
    ofType<actions.GetFlowRunFlowsAction>(actions.TffActionTypes.GET_FLOW_RUN_FLOWS),
    switchMap(() => this.flowStatisticsService.getDistinctFlows().pipe(
      map(result => new actions.GetFlowRunFlowsCompleteAction(result)),
      catchError(err => handleApiError(actions.GetFlowRunFlowsFailedAction, err)),
    )));

  @Effect() getFlowRuns$ = this.actions$.pipe(
    ofType<actions.GetFlowRunsAction>(actions.TffActionTypes.GET_FLOW_RUNS),
    switchMap(action => this.flowStatisticsService.getFlowRuns(action.payload).pipe(
      map(result => new actions.GetFlowRunsCompleteAction(result)),
      catchError(err => handleApiError(actions.GetFlowRunsFailedAction, err)),
    )));

  @Effect() getFlowRun$ = this.actions$.pipe(
    ofType<actions.GetFlowRunAction>(actions.TffActionTypes.GET_FLOW_RUN),
    switchMap(action => this.flowStatisticsService.getFlowRun(action.payload).pipe(
      map(result => new actions.GetFlowRunCompleteAction(result)),
      catchError(err => handleApiError(actions.GetFlowRunFailedAction, err)),
    )));

  @Effect() getFlowStats$ = this.actions$.pipe(
    ofType<actions.GetFlowStatsAction>(actions.TffActionTypes.GET_FLOW_STATS),
    switchMap(action => this.flowStatisticsService.getFlowStats(action.payload).pipe(
      map(result => new actions.GetFlowStatsCompleteAction(result)),
      catchError(err => handleApiError(actions.GetFlowStatsFailedAction, err)),
    )));

  @Effect() getInstallations$ = this.actions$.pipe(
    ofType<actions.GetInstallationsAction>(actions.TffActionTypes.GET_INSTALLATIONS),
    switchMap(action => this.tffService.getInstallations(action.payload).pipe(
      map(result => new actions.GetInstallationsCompleteAction(result)),
      catchError(err => handleApiError(actions.GetInstallationsFailedAction, err)),
    )));

  @Effect() getInstallation$ = this.actions$.pipe(
    ofType<actions.GetInstallationAction>(actions.TffActionTypes.GET_INSTALLATION),
    switchMap(action => this.tffService.getInstallation(action.payload).pipe(
      map(result => new actions.GetInstallationCompleteAction(result)),
      catchError(err => handleApiError(actions.GetInstallationFailedAction, err)),
    )));

  @Effect() getInstallationLogs$ = this.actions$.pipe(
    ofType<actions.GetInstallationLogsAction>(actions.TffActionTypes.GET_INSTALLATION_LOGS),
    switchMap(action => this.tffService.getInstallationLogs(action.payload).pipe(
      map(result => new actions.GetInstallationLogsCompleteAction(result)),
      catchError(err => handleApiError(actions.GetInstallationLogsFailedAction, err)),
    )));

  @Effect() getNodes$ = this.actions$.pipe(
    ofType<actions.GetNodesAction>(actions.TffActionTypes.GET_NODES),
    switchMap(action => this.tffService.getNodes(action.payload).pipe(
      map(result => new actions.GetNodesCompleteAction(result)),
      catchError(err => handleApiError(actions.GetNodesFailedAction, err)),
    )));

  @Effect() getNode$ = this.actions$.pipe(
    ofType<actions.GetNodeAction>(actions.TffActionTypes.GET_NODE),
    switchMap(action => this.tffService.getNode(action.payload).pipe(
      map(result => new actions.GetNodeCompleteAction(result)),
      catchError(err => handleApiError(actions.GetNodeFailedAction, err)),
    )));

  @Effect() updateNode$ = this.actions$.pipe(
    ofType<actions.UpdateNodeAction>(actions.TffActionTypes.UPDATE_NODE),
    switchMap(action => this.tffService.updateNode(action.id, action.payload).pipe(
      map(result => new actions.UpdateNodeCompleteAction(result)),
      catchError(err => handleApiError(actions.UpdateNodeFailedAction, err)),
    )));

  @Effect() deleteNode$ = this.actions$.pipe(
    ofType<actions.DeleteNodeAction>(actions.TffActionTypes.DELETE_NODE),
    switchMap(action => this.tffService.deleteNode(action.payload).pipe(
      map(result => new actions.DeleteNodeCompleteAction(result)),
      catchError(err => handleApiError(actions.DeleteNodeFailedAction, err)),
    )));

  constructor(private actions$: Actions<actions.TffActions>,
              private tffService: TffService,
              private flowStatisticsService: FlowStatisticsService) {
  }
}
