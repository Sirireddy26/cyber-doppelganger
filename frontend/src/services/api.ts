import type { 
  HealthResponse, 
  SystemDiagnostics,
  AdaptationStatus, 
  AdaptationEvent,
  AdaptationHistoryPage,
  ModelStatusResponse,
  VerificationResult,
  VerificationHistoryPage,
  BehaviourHistoryPage
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export class ApiService {
  private static baseUrl = API_BASE_URL.replace(/\/$/, '');

  public static async getHealth(): Promise<HealthResponse> {
    try {
      const res = await fetch(`${this.baseUrl}/api/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      return await res.json() as HealthResponse;
    } catch (err: any) {
      try {
        const fallbackRes = await fetch('/api/health');
        if (fallbackRes.ok) {
          return await fallbackRes.json() as HealthResponse;
        }
      } catch {
        // Ignore fallback error
      }
      throw new Error(err.message || 'Unable to connect to backend server');
    }
  }

  public static async getDiagnostics(): Promise<SystemDiagnostics> {
    try {
      const res = await fetch(`${this.baseUrl}/api/health/diagnostics`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      return await res.json() as SystemDiagnostics;
    } catch (err: any) {
      try {
        const fallbackRes = await fetch('/api/health/diagnostics');
        if (fallbackRes.ok) {
          return await fallbackRes.json() as SystemDiagnostics;
        }
      } catch {
        // Ignore fallback error
      }
      throw new Error(err.message || 'Unable to fetch system diagnostics');
    }
  }

  public static async getAdaptationStatus(): Promise<AdaptationStatus> {
    try {
      const res = await fetch(`${this.baseUrl}/api/adaptation/status`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json() as AdaptationStatus;
    } catch (err: any) {
      try {
        const fallbackRes = await fetch('/api/adaptation/status');
        if (fallbackRes.ok) {
          return await fallbackRes.json() as AdaptationStatus;
        }
      } catch {
        // Ignore fallback error
      }
      throw new Error(err.message || 'Failed to fetch adaptation status');
    }
  }

  public static async getAdaptationHistory(page = 0, size = 10): Promise<AdaptationHistoryPage> {
    try {
      const res = await fetch(`${this.baseUrl}/api/adaptation/history?page=${page}&size=${size}`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json() as AdaptationHistoryPage;
    } catch (err: any) {
      try {
        const fallbackRes = await fetch(`/api/adaptation/history?page=${page}&size=${size}`);
        if (fallbackRes.ok) {
          return await fallbackRes.json() as AdaptationHistoryPage;
        }
      } catch {
        // Ignore fallback error
      }
      throw new Error(err.message || 'Failed to fetch adaptation history');
    }
  }

  public static async freezeProfile(reason: string, authorizedBy = 'sec-ops-admin'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/adaptation/freeze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ reason, authorized_by: authorizedBy }),
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      throw new Error(errBody?.message || errBody?.error || `HTTP ${res.status}: Failed to freeze profile`);
    }
    return await res.json();
  }

  public static async unfreezeProfile(authorizedBy = 'sec-ops-admin', reason = 'Security recovery'): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/adaptation/unfreeze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ authorized_by: authorizedBy, reason }),
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      throw new Error(errBody?.message || errBody?.error || `HTTP ${res.status}: Failed to unfreeze profile`);
    }
    return await res.json();
  }

  public static async rollbackProfile(
    targetVersion: string,
    reason = 'Rollback to trusted version',
    authorizedBy = 'sec-ops-admin'
  ): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/adaptation/rollback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        target_version: targetVersion,
        reason,
        authorized_by: authorizedBy,
      }),
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      let msg = errBody?.message || errBody?.error || `HTTP ${res.status}: Failed to rollback profile`;
      try {
        const parsed = JSON.parse(msg);
        if (parsed?.message) msg = parsed.message;
      } catch {}
      throw new Error(msg);
    }
    return await res.json();
  }

  public static async processAdaptation(payload: {
    features: Record<string, any>;
    snapshot_id?: number | null;
    verification_result_id?: number | null;
    device_id?: string;
    user_id?: string;
    drift_magnitude?: number;
    velocity?: number;
    is_anomaly?: boolean;
  }): Promise<AdaptationEvent> {
    const res = await fetch(`${this.baseUrl}/api/adaptation/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.message || `HTTP ${res.status}: Failed to process adaptation`);
    }
    return await res.json() as AdaptationEvent;
  }

  public static async getModelStatus(): Promise<ModelStatusResponse> {
    try {
      const res = await fetch(`${this.baseUrl}/api/models/status`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json() as ModelStatusResponse;
    } catch (err: any) {
      try {
        const fallbackRes = await fetch('/api/models/status');
        if (fallbackRes.ok) {
          return await fallbackRes.json() as ModelStatusResponse;
        }
      } catch {
        // Ignore fallback error
      }
      throw new Error(err.message || 'Failed to fetch model status');
    }
  }

  public static async processVerification(payload: {
    preferred_model?: string;
    snapshot: any;
  }): Promise<VerificationResult> {
    const res = await fetch(`${this.baseUrl}/api/verification/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      throw new Error(errBody?.message || `HTTP ${res.status}: Failed to process verification`);
    }
    return await res.json() as VerificationResult;
  }

  public static async getVerificationHistory(page = 0, size = 10): Promise<VerificationHistoryPage> {
    try {
      const res = await fetch(`${this.baseUrl}/api/verification?page=${page}&size=${size}`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json() as VerificationHistoryPage;
    } catch (err: any) {
      try {
        const fallbackRes = await fetch(`/api/verification?page=${page}&size=${size}`);
        if (fallbackRes.ok) {
          return await fallbackRes.json() as VerificationHistoryPage;
        }
      } catch {
        // Ignore fallback error
      }
      throw new Error(err.message || 'Failed to fetch verification history');
    }
  }

  public static async getBehaviourSnapshots(page = 0, size = 10): Promise<BehaviourHistoryPage> {
    try {
      const res = await fetch(`${this.baseUrl}/api/behaviour?page=${page}&size=${size}`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json() as BehaviourHistoryPage;
    } catch (err: any) {
      try {
        const fallbackRes = await fetch(`/api/behaviour?page=${page}&size=${size}`);
        if (fallbackRes.ok) {
          return await fallbackRes.json() as BehaviourHistoryPage;
        }
      } catch {
        // Ignore fallback error
      }
      throw new Error(err.message || 'Failed to fetch behaviour snapshots');
    }
  }

  public static async ingestFeatures(snapshotPayload: any): Promise<any> {
    const res = await fetch(`${this.baseUrl}/api/agent/features`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(snapshotPayload),
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      throw new Error(errBody?.message || `HTTP ${res.status}: Failed to ingest features`);
    }
    return await res.json();
  }

  public static getBaseUrl(): string {
    return this.baseUrl;
  }
}

