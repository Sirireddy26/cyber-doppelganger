export interface HealthResponse {
  status: string;
  service: string;
  database?: string;
  database_type?: string;
}

export interface ApiError {
  message: string;
  timestamp: string;
}

export interface AdaptationStatus {
  engine_status: string;
  active_version: string;
  is_frozen: boolean;
  freeze_reason?: string | null;
  frozen_at?: string | null;
  suspicious_streak: number;
  sample_count: number;
  candidate_buffer?: {
    current_size?: number;
    max_capacity?: number;
    min_required?: number;
    is_full?: boolean;
    mean_drift?: number;
    mean_velocity?: number;
    stability_score?: number;
    error?: string;
  };
  policy_config?: {
    min_observations?: number;
    max_drift_magnitude?: number;
    max_velocity?: number;
    min_stability?: number;
    max_suspicious_streak?: number;
    cooldown_seconds?: number;
    policy_version?: string;
  };
  versions_summary?: Array<{
    version_tag: string;
    parent_version_tag?: string | null;
    sample_count: number;
    status: string;
    reason: string;
    created_at: string;
  }>;
}

export interface AdaptationEvent {
  id: number;
  snapshot_id?: number | null;
  verification_result_id?: number | null;
  device_id: string;
  decision_state: string;
  prior_profile_version: string;
  new_profile_version?: string | null;
  drift_magnitude?: number | null;
  velocity?: number | null;
  stability_score?: number | null;
  candidate_count: number;
  suspicious_streak: number;
  is_profile_frozen: boolean;
  decision_reason: string;
  policy_version: string;
  created_at: string;
}

export interface AdaptationHistoryPage {
  content: AdaptationEvent[];
  page?: {
    totalElements: number;
    totalPages: number;
    size: number;
    number: number;
  };
  totalElements?: number;
  totalPages?: number;
}

export interface ModelStatusResponse {
  status: string;
  active_model_type: string;
  isolation_forest?: {
    available: boolean;
    version: string;
    threshold: number;
    sample_count: number;
  };
  random_forest?: {
    available: boolean;
    version?: string;
  };
}

export interface VerificationResult {
  id?: number;
  status: string;
  decision: string;
  confidence_score: number;
  anomaly_score: number;
  raw_score: number;
  threshold: number;
  model_type: string;
  model_version: string;
  reason: string;
  device_id?: string;
  snapshot_id?: number | null;
  created_at?: string;
}

export interface VerificationHistoryPage {
  content: VerificationResult[];
  page?: {
    totalElements: number;
    totalPages: number;
    size: number;
    number: number;
  };
}

export interface BehaviourSnapshot {
  id: number;
  timestamp: string;
  deviceId: string;
  windowDurationSeconds: number;
  userId?: string | null;
  createdAt?: string;
  keyboard?: {
    mean_dwell_time_ms?: number;
    mean_flight_time_ms?: number;
    typing_speed_wpm?: number;
    backspace_rate?: number;
    keystroke_count?: number;
  };
  mouse?: {
    mean_speed_pixels_per_second?: number;
    mean_acceleration?: number;
    jitter_metric?: number;
    movement_efficiency?: number;
    click_count?: number;
  };
}

export interface BehaviourHistoryPage {
  content: BehaviourSnapshot[];
  page?: {
    totalElements: number;
    totalPages: number;
    size: number;
    number: number;
  };
}

export interface KinematicsMetrics {
  dwellTimeMs: number;
  flightTimeMs: number;
  typingSpeedWpm: number;
  backspaceRate: number;
  keystrokeCount: number;
  mouseSpeedPps: number;
  mouseAcceleration: number;
  mouseJitter: number;
  movementEfficiency: number;
  mouseClickCount: number;
  mouseDistancePx: number;
}

export interface SystemDiagnostics {
  timestamp: string;
  backend: {
    status: string;
    service: string;
    version: string;
  };
  database: {
    status: string;
    database_type: string;
    connected: boolean;
  };
  ml_service: {
    status: string;
    service_status: string;
    active_model_type: string;
  };
  model_readiness: {
    ready: boolean;
    status: string;
    model_type: string;
    model_version: string;
  };
  trusted_profile: {
    ready: boolean;
    status: string;
    total_versions: number;
    active_version: string;
    device_id: string;
  };
  adaptation_engine: {
    ready: boolean;
    engine_status: string;
    is_frozen: boolean;
    adaptation_permitted: boolean;
    suspicious_streak: number;
  };
  agent_telemetry: {
    status: string;
    last_captured_at: string | null;
    last_device_id: string | null;
  };
  system_summary: {
    verification_ready: boolean;
    adaptation_ready: boolean;
    all_systems_operational: boolean;
  };
}

