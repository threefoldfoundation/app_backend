import { SortDirection } from '@angular/material';

export const enum NodeStatus {
  RUNNING = 'running',
  HALTED = 'halted',
}

export const enum WalletStatus {
  ERROR = 'error',
  UNLOCKED = 'unlocked',
}

export interface ChainStatus {
  block_height: number;
  wallet_status: WalletStatus;
  active_blockstakes: number;
  network: 'devnet' | 'testnet' | 'standard';
  confirmed_balance: number;
  connected_peers: number;
  address: string | null;
}

export interface NodeInfo {
  status: NodeStatus;
  id: string;
  serial_number: string;
  username: string;
  status_date?: string;
  last_update?: string;
  info: {
    kernelVersion: string;
    virtualizationRole: string;
    virtualizationSystem: string;
    uptime: number;
    procs: number;
    os: string;
    hostname: string;
    platformVersion: string;
    platform: string;
    platformFamily: string;
    bootTime: number;
    hostid: string;
  } | null;
  chain_status: ChainStatus | null;
}

export interface CreateNodePayload {
  id: string;
  username: string | null;
}

export interface UpdateNodePayload {
  username: string | null;
}

export interface LimitedProfile {
  username: string;
  name: string | null;
  email: string | null;
}

export interface UserNodeStatus {
  profile: LimitedProfile | null;
  node: NodeInfo;
}

export interface NodesQuery {
  sort_by: string | null;
  direction: SortDirection;
}
