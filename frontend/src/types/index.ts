/**
 * Frontend types for Chimera
 */

export interface AgentRequest {
  goal: string;
  target?: string;
  budget: number;
  constraints?: Record<string, any>;
  config?: Record<string, any>;
}

export interface AgentResponse {
  run_id: string;
  status: string;
  phase: string;
  message: string;
  budget_remaining: number;
  molecules_generated: number;
  molecules_passed: number;
  logs: string[];
  results?: any;
}

export interface Molecule {
  id: string;
  name: string;
  smiles: string;
  status: string;
  properties: MoleculeProperties;
  visualization_url?: string;
  cost_incurred?: number;
  rejection_reason?: string;
}

export interface MoleculeProperties {
  toxicity_score?: number;
  efficacy_score?: number;
  molecular_weight?: number;
  logp?: number;
  h_bond_donors?: number;
  h_bond_acceptors?: number;
  drug_likeness?: number;
  predicted_activity?: string;
  additional_properties?: Record<string, any>;
}

export interface RunSummary {
  run_id: string;
  goal: string;
  phase: string;
  molecules: number;
  start_time: string;
  budget_spent: number;
}

export interface DiscoveryResult {
  response: AgentResponse;
  final_report?: any;
  molecules?: Molecule[];
}
