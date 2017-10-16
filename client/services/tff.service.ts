import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Profile, SearchUsersQuery, UserList } from '../../../its_you_online_auth/client/interfaces/user.interfaces';
import {
  CreateTransactionPayload,
  GlobalStats,
  InvestmentAgreement,
  InvestmentAgreementList,
  InvestmentAgreementsQuery,
  NodeOrder,
  NodeOrderList,
  NodeOrdersQuery,
  Transaction,
  TransactionList,
  WalletBalance
} from '../interfaces/index';
import { TffConfig } from './tff-config.service';

@Injectable()
export class TffService {

  constructor(private http: HttpClient) {
  }

  getNodeOrders(payload: NodeOrdersQuery) {
    const params = this._getQueryParams(payload);
    return this.http.get<NodeOrderList>(`${TffConfig.API_URL}/orders`, { params });
  }

  getNodeOrder(orderId: string) {
    return this.http.get<NodeOrder>(`${TffConfig.API_URL}/orders/${orderId}`);
  }

  updateNodeOrder(nodeOrder: NodeOrder) {
    return this.http.put<NodeOrder>(`${TffConfig.API_URL}/orders/${nodeOrder.id}`, nodeOrder);
  }

  getInvestmentAgreements(payload: InvestmentAgreementsQuery) {
    const params = this._getQueryParams(payload);
    return this.http.get<InvestmentAgreementList>(`${TffConfig.API_URL}/investment-agreements`, { params });
  }

  getInvestmentAgreement(agreementId: string) {
    return this.http.get<InvestmentAgreement>(`${TffConfig.API_URL}/investment-agreements/${agreementId}`);
  }

  updateInvestmentAgreement(agreement: InvestmentAgreement) {
    return this.http.put<InvestmentAgreement>(`${TffConfig.API_URL}/investment-agreements/${agreement.id}`, agreement);
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
    const params = this._getQueryParams(payload);
    return this.http.get<UserList>(`${TffConfig.API_URL}/users`, { params });
  }

  getUser(username: string) {
    return this.http.get<Profile>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}`);
  }

  getBalance(username: string) {
    return this.http.get<WalletBalance[]>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}/balance`);
  }

  getUserTransactions(username: string) {
    return this.http.get<TransactionList>(`${TffConfig.API_URL}/users/${encodeURIComponent(username)}/transactions`);
  }

  createTransaction(payload: CreateTransactionPayload) {
    let data: Partial<CreateTransactionPayload> = { ...payload };
    delete data.username;
    return this.http.post<Transaction>(`${TffConfig.API_URL}/users/${encodeURIComponent(payload.username)}/transactions`, data);
  }

  private _getQueryParams<T>(queryObject: T): HttpParams {
    let params = new HttpParams();
    const q = <[ keyof T ]>Object.keys(queryObject);
    for (const key of q) {
      if (queryObject[ key ] !== null) {
        params = params.set(key, encodeURIComponent(queryObject[ key ].toString()));
      }
    }
    return params;
  }
}
