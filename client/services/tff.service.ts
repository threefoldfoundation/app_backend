import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { Installation, InstallationLog, InstallationsList } from '../../../rogerthat_api/client/interfaces';
import {
  AgendaEvent,
  Check,
  CreateInvestmentAgreementPayload,
  CreateNodePayload,
  CreateOrderPayload,
  EventParticipant,
  GetEventParticipantsPayload,
  GetInstallationsQuery,
  GlobalStats,
  InvestmentAgreement,
  InvestmentAgreementList,
  InvestmentAgreementsQuery,
  NodeInfo,
  NodeOrder,
  NodeOrderList,
  NodeOrdersQuery,
  NodesQuery,
  PaginatedResult,
  SearchUsersQuery,
  SetKYCStatusPayload,
  TffProfile,
  TransactionList,
  UpdateNodePayload,
  UserList,
  UserNodeStatus,
  WalletBalance,
} from '../interfaces';
import { getQueryParams } from '../util';
import { TffConfig } from './tff-config.service';

@Injectable()
export class TffService {

  constructor(private http: HttpClient) {
  }

  getNodeOrders(payload: NodeOrdersQuery) {
    const params = getQueryParams(payload);
    return this.http.get<NodeOrderList>(`${TffConfig.API_URL}/orders`, { params });
  }

  getNodeOrder(orderId: string) {
    return this.http.get<NodeOrder>(`${TffConfig.API_URL}/orders/${orderId}`);
  }

  createNodeOrder(nodeOrder: CreateOrderPayload) {
    return this.http.post<NodeOrder>(`${TffConfig.API_URL}/orders`, nodeOrder);
  }

  updateNodeOrder(nodeOrder: NodeOrder) {
    return this.http.put<NodeOrder>(`${TffConfig.API_URL}/orders/${nodeOrder.id}`, nodeOrder);
  }

  getInvestmentAgreements(payload: InvestmentAgreementsQuery) {
    const params = getQueryParams(payload);
    return this.http.get<InvestmentAgreementList>(`${TffConfig.API_URL}/investment-agreements`, { params });
  }

  getInvestmentAgreement(agreementId: string) {
    return this.http.get<InvestmentAgreement>(`${TffConfig.API_URL}/investment-agreements/${agreementId}`);
  }

  updateInvestmentAgreement(agreement: InvestmentAgreement) {
    return this.http.put<InvestmentAgreement>(`${TffConfig.API_URL}/investment-agreements/${agreement.id}`, agreement);
  }

  createInvestmentAgreement(agreement: CreateInvestmentAgreementPayload) {
    return this.http.post<InvestmentAgreement>(`${TffConfig.API_URL}/investment-agreements`, agreement);
  }

  getGlobalStatsList() {
    return this.http.get<GlobalStats[]>(`${TffConfig.API_URL}/global-stats`);
  }

  getGlobalStats(statsId: string) {
    return this.http.get<GlobalStats>(`${TffConfig.API_URL}/global-stats/${statsId}`);
  }

  updateGlobalStats(stats: GlobalStats) {
    return this.http.put<GlobalStats>(`${TffConfig.API_URL}/global-stats/${stats.id}`, stats);
  }

  searchUsers(payload: SearchUsersQuery) {
    const params = getQueryParams(payload);
    return this.http.get<UserList>(`${TffConfig.API_URL}/users`, { params });
  }

  getTffProfile(username: string) {
    return this.http.get<TffProfile>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}`);
  }

  setKYCStatus(username: string, payload: SetKYCStatusPayload) {
    return this.http.put<TffProfile>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}/kyc`, payload);
  }

  verifyUtilityBill(username: string) {
    return this.http.put<TffProfile>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}/kyc/utility-bill`, {});
  }

  getBalance(username: string) {
    return this.http.get<WalletBalance[]>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}/balance`);
  }

  getUserTransactions(username: string) {
    return this.http.get<TransactionList>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}/transactions`);
  }

  getAgendaEvents(past: boolean) {
    const params = getQueryParams({ past });
    return this.http.get<AgendaEvent[]>(`${TffConfig.API_URL}/agenda-events`, { params });
  }

  getAgendaEvent(id: number) {
    return this.http.get<AgendaEvent>(`${TffConfig.API_URL}/agenda-events/${id}`);
  }

  createAgendaEvent(event: AgendaEvent) {
    return this.http.post<AgendaEvent>(`${TffConfig.API_URL}/agenda-events`, event);
  }

  updateAgendaEvent(event: AgendaEvent) {
    return this.http.put<AgendaEvent>(`${TffConfig.API_URL}/agenda-events/${event.id}`, event);
  }

  getEventParticipants(payload: GetEventParticipantsPayload) {
    let params = new HttpParams();
    params = params.set('page_size', String(payload.page_size));
    return this.http.get<PaginatedResult<EventParticipant>>(`${TffConfig.API_URL}/agenda-events/${payload.event_id}/participants`,
      { params });
  }

  getKYCChecks(username: string) {
    return this.http.get<Check[]>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}/kyc/checks`);
  }

  getInstallations(query: GetInstallationsQuery) {
    const params = getQueryParams(query);
    return this.http.get<InstallationsList>(`${TffConfig.API_URL}/installations`, { params });
  }

  getInstallation(installationId: string) {
    return this.http.get<Installation>(`${TffConfig.API_URL}/installations/${installationId}`);
  }

  getInstallationLogs(installationId: string) {
    return this.http.get<InstallationLog[]>(`${TffConfig.API_URL}/installations/${installationId}/logs`);
  }

  getNodes(query: NodesQuery) {
    let params = new HttpParams();
    params = params.set('direction', query.direction);
    if (query.sort_by) {
      params = params.set('sort_by', query.sort_by);
    }
    return this.http.get<UserNodeStatus[]>(`${TffConfig.API_URL}/nodes`, { params });
  }

  getNode(id: string) {
    return this.http.get<NodeInfo>(`${TffConfig.API_URL}/nodes/${id}`);
  }

  createNode(payload: CreateNodePayload) {
    return this.http.post<NodeInfo>(`${TffConfig.API_URL}/nodes`, payload);
  }

  updateNode(id: string, payload: UpdateNodePayload) {
    return this.http.put<NodeInfo>(`${TffConfig.API_URL}/nodes/${id}`, payload);
  }

  deleteNode(node: NodeInfo) {
    return this.http.delete(`${TffConfig.API_URL}/nodes/${node.id}`).pipe(map(() => node));
  }
}
