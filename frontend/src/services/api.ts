/**
 * API service for communicating with Chimera backend
 */
import axios from 'axios';
import type { AgentRequest, AgentResponse, RunSummary, DiscoveryResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chimeraApi = {
  /**
   * Start a synchronous discovery run (waits for completion)
   */
  async discover(request: AgentRequest): Promise<DiscoveryResult> {
    const response = await api.post<DiscoveryResult>('/discover/sync', request);
    return response.data;
  },

  /**
   * Start an asynchronous discovery run (returns immediately)
   */
  async discoverAsync(request: AgentRequest): Promise<AgentResponse> {
    const response = await api.post<AgentResponse>('/discover', request);
    return response.data;
  },

  /**
   * Get status of a specific run
   */
  async getRunStatus(runId: string): Promise<any> {
    const response = await api.get(`/runs/${runId}`);
    return response.data;
  },

  /**
   * List all runs
   */
  async listRuns(): Promise<{ runs: RunSummary[] }> {
    const response = await api.get('/runs');
    return response.data;
  },

  /**
   * Delete a run
   */
  async deleteRun(runId: string): Promise<void> {
    await api.delete(`/runs/${runId}`);
  },

  /**
   * Get agent configuration
   */
  async getConfig(): Promise<{ config: Record<string, any> }> {
    const response = await api.get('/config');
    return response.data;
  },

  /**
   * Update agent configuration
   */
  async updateConfig(config: Record<string, any>): Promise<{ config: Record<string, any> }> {
    const response = await api.post('/config', config);
    return response.data;
  },
};

export default chimeraApi;
