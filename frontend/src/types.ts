export type ActiveTab = 'model' | 'lexicon' | 'biology' | 'docs';

export interface LogMessage {
  id: string;
  timestamp: string;
  category: 'SYS' | 'I_LEX' | 'PHYLO' | 'REPAIR';
  level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR';
  text: string;
}

export interface SystemState {
  uptime: number; // in seconds
  cpuLoad: number; // percentage
  memoryUsage: number; // GB
  consensusScore: number; // F1 or accuracy (e.g. 0.9942)
  integrityStatus: 'NOMINAL' | 'DEGRADED' | 'REPAIRING' | 'MUTATED';
  activePayloadId: string;
  systemInvariants: {
    I: boolean;
    I_system_S: boolean;
    H_lex: boolean;
    G_lex: boolean;
    I_lexicon: boolean;
  };
}

export interface LexiconPayload {
  id: string;
  name: string;
  rawText: string;
  timestamp: string;
  metrics: {
    tokenCount: number;
    entropy: number;
    latencyMs: number;
    contradictionsCount: number;
  };
  classificationChain: {
    node: string;
    value: string;
    confidence: number;
    status: 'passed' | 'warning' | 'failed';
  }[];
}

export interface BiologicalSequence {
  id: string;
  geneName: string;
  rawSequence: string;
  mutatedSequence: string;
  divergenceFactor: number;
  alignmentScore: number;
  validationStatus: 'NOMINAL' | 'ALERT' | 'RESOLVED';
}
