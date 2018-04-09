import { SupportedAlgorithms } from 'rogerthat-plugin';

export interface CreateSignatureData {
  amount: number;
  precision: number;
  from_address: string;
  to_address: string;
}

export interface GetAddressPayload {
  algorithm: SupportedAlgorithms;
  keyName: string;
  index: number;
  message: string;
}

// Only used by UI
export interface ParsedTransaction {
  id: string;
  height: number;
  inputs: RivineOutput[];
  outputs: RivineOutput[];
  amount: number;
  minerfee: number;
  receiving: boolean;
}

export interface RivineCreateTransactionResult {
  transactionid: string;
}

export interface RivineBlockInternal {
  arbitrarydatacount: number;
  arbitrarydatatotalsize: number;
  blockid: string;
  blockstakeinputcount: number;
  blockstakeoutputcount: number;
  coininputcount: number;
  coinoutputcount: number;
  difficulty: string;
  estimatedactivebs: string;
  height: number;
  maturitytimestamp: number;
  minerfeecount: number;
  minerpayoutcount: number;
  minerpayoutids: null | string[];
  rawblock: {
    minerpayouts: null | RivineOutput[];
    parentid: string;
    timestamp: number;
    pobsindexes: {
      BlockHeight: number;
      OutputIndex: number;
      TransactionIndex: number;
    },
    transactions: null | RivineRawTransaction[];
  };
  target: number[];
  totalcoins: string;
  transactioncount: number;
  transactions: null | RivineTransaction[];
}

export interface RivineCreateTransaction {
  version: number;
  data: {
    coininputs: RivineInput[];
    coinoutputs: RivineOutput[];
    blockstakeinputs: null | RivineInput[];
    blockstakeoutputs: null | RivineInput[];
    minerfees: string[];
    arbitrarydata: null | string[];
  };
}

export interface RivineBlock {
  block: RivineBlockInternal;
}

export interface RivineInput {
  parentid: string;
  unlocker: {
    type: number;
    condition: {
      publickey: string;
    },
    fulfillment: {
      signature: string;
    }
  };
}

export interface RivineOutput {
  value: string;
  unlockhash: string;
}

export interface RivineRawTransaction {
  version: number;
  data: {
    coininputs: null | RivineInput[];
    coinoutputs?: null | RivineOutput[];
    blockstakeinputs?: null | RivineInput[];
    blockstakeoutputs?: null | RivineOutput[];
    minerfees: string[] | null;
  };
}

export interface RivineTransaction {
  id: string;
  height: number;
  parent: string;
  rawtransaction: RivineRawTransaction;
  coininputoutputs: null | RivineOutput[];
  coinoutputids: null | string[];
  blockstakeinputoutputs: null | RivineInput | RivineOutput[];
  blockstakeoutputids: null | string[];
}

export interface RivineHashInfo {
  block: RivineBlockInternal;
  blocks: null;
  hashtype: 'unlockhash';
  transaction: RivineTransaction;
  transactions: RivineTransaction[];
}

export const ADDRESS_LENGTH = 78;
export const COIN_TO_HASTINGS_PRECISION = 9;
export const COIN_TO_HASTINGS = Math.pow(10, COIN_TO_HASTINGS_PRECISION);
export const CURRENCY_TFT = 'TFT';
export const KEY_NAME = 'threefold';
export const PROVIDER_ID = 'threefold';
export const RIVINE_ALGORITHM = 'ed25519';
