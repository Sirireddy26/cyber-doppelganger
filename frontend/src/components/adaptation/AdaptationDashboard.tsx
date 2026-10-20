import React, { useState, useEffect } from 'react';
import { 
  GitBranch, 
  ShieldAlert, 
  ShieldCheck, 
  RotateCcw, 
  Lock, 
  Unlock, 
  RefreshCw, 
  Activity, 
  AlertTriangle,
  History,
  CheckCircle,
  Clock,
  Info
} from 'lucide-react';
import { ApiService } from '../../services/api';
import type { AdaptationStatus, AdaptationEvent } from '../../types/api';

export const AdaptationDashboard: React.FC = () => {
  const [status, setStatus] = useState<AdaptationStatus | null>(null);
  const [history, setHistory] = useState<AdaptationEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Modal / Form state for actions
  const [showFreezeModal, setShowFreezeModal] = useState<boolean>(false);
  const [freezeReason, setFreezeReason] = useState<string>('Suspicious behavioural anomaly detected by analyst');
  const [showUnfreezeModal, setShowUnfreezeModal] = useState<boolean>(false);
  const [unfreezeAuth, setUnfreezeAuth] = useState<string>('sec-ops-admin');
  const [unfreezeReason, setUnfreezeReason] = useState<string>('Identity re-verified via secondary authentication');
  const [showRollbackModal, setShowRollbackModal] = useState<boolean>(false);
  const [rollbackAuth, setRollbackAuth] = useState<string>('sec-ops-admin');
  const [rollbackReason, setRollbackReason] = useState<string>('Administrative recovery to trusted baseline profile');
  const [rollbackVersion, setRollbackVersion] = useState<string>('v1.0.0');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusData, historyData] = await Promise.all([
        ApiService.getAdaptationStatus(),
        ApiService.getAdaptationHistory(0, 15),
      ]);
      setStatus(statusData);
      setHistory(historyData.content || []);
    } catch (err: any) {
      setError(err.message || 'Unable to fetch adaptation engine state');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleFreeze = async () => {
    setActionLoading(true);
    setActionMessage(null);
    try {
      await ApiService.freezeProfile(freezeReason);
      setActionMessage({ type: 'success', text: 'Profile adaptation successfully FROZEN.' });
      setShowFreezeModal(false);
      await fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to freeze profile' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnfreeze = async () => {
    setActionLoading(true);
    setActionMessage(null);
    try {
      await ApiService.unfreezeProfile(unfreezeAuth, unfreezeReason);
      setActionMessage({ type: 'success', text: 'Profile adaptation successfully UNFROZEN.' });
      setShowUnfreezeModal(false);
      await fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to unfreeze profile' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleRollback = async () => {
    setActionLoading(true);
    setActionMessage(null);
    try {
      const res = await ApiService.rollbackProfile(rollbackVersion, rollbackReason, rollbackAuth);
      setActionMessage({
        type: 'success',
        text: res?.message || `Profile successfully rolled back to ${rollbackVersion}. Adaptation un-frozen and reset.`
      });
      setShowRollbackModal(false);
      await fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to rollback profile' });
    } finally {
      setActionLoading(false);
    }
  };

  const getDecisionBadge = (state: string) => {
    switch (state) {
      case 'SAFE_ADAPTATION':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#CCEBD4] text-[#0F5132] border border-[#9EDAA9]">
            <CheckCircle className="w-3 h-3 text-[#15803D]" />
            <span>ADAPTED</span>
          </span>
        );
      case 'PROFILE_FROZEN':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#F5CCD7] text-[#881337] border border-[#EAAAB9]">
            <Lock className="w-3 h-3 text-[#E11D48]" />
            <span>FROZEN</span>
          </span>
        );
      case 'SUSPICIOUS_CHANGE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#F8DAC0] text-[#7C2D12] border border-[#F0BF94]">
            <ShieldAlert className="w-3 h-3 text-[#D97706]" />
            <span>SUSPICIOUS</span>
          </span>
        );
      case 'NORMAL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#CCEBD4] text-[#0F5132] border border-[#9EDAA9]">
            <ShieldCheck className="w-3 h-3 text-[#15803D]" />
            <span>NORMAL</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#E4DAF5] text-[#431E8C] border border-[#C8B8E4]">
            <Clock className="w-3 h-3 text-[#593CA5]" />
            <span>{state}</span>
          </span>
        );
    }
  };

  return (
    <section className="bg-[#F1EBFA] border border-[#D2C4EB] rounded-2xl p-6 md:p-8 space-y-6 shadow-sm">
      {/* Header and Live Status Pill */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#D2C4EB] pb-5">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-[#E2D5F3] text-[#431E8C] border border-[#C5B3E3] text-xs font-bold">
            <GitBranch className="w-3.5 h-3.5" />
            <span>Safe Adaptation Engine &bull; Reference Profile Protection</span>
          </div>
          <h2 className="text-xl md:text-2xl font-extrabold text-[#1E2638] tracking-tight">
            Continuous Behavioural Profile Evolution
          </h2>
          <p className="text-xs md:text-sm text-[#4A5568] max-w-2xl leading-relaxed font-medium">
            Accommodates gradual user behavioural drift safely while preventing profile poisoning attacks. A candidate isolation buffer ensures suspicious observations cannot contaminate the reference model.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start md:self-auto">
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 rounded-xl bg-[#E4DAF5] border border-[#C8B8E4] hover:bg-[#D5C6F0] text-[#1E2638] transition-colors cursor-pointer"
            title="Refresh Adaptation Telemetry"
          >
            <RefreshCw className={`w-4 h-4 text-[#593CA5] ${loading ? 'animate-spin' : ''}`} />
          </button>

          {status?.is_frozen ? (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#F5CCD7] border border-[#EAAAB9] text-[#881337] text-xs font-bold">
              <Lock className="w-3.5 h-3.5 text-[#E11D48]" />
              <span>PROFILE UPDATES FROZEN</span>
            </div>
          ) : status?.engine_status === 'ACTIVE' ? (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#CCEBD4] border border-[#9EDAA9] text-[#0F5132] text-xs font-bold">
              <ShieldCheck className="w-3.5 h-3.5 text-[#15803D]" />
              <span>ACTIVE &bull; BOUNDED ADAPTATION</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#E4DAF5] border border-[#C8B8E4] text-[#431E8C] text-xs font-bold">
              <Activity className="w-3.5 h-3.5" />
              <span>{status?.engine_status || 'CONNECTING...'}</span>
            </div>
          )}
        </div>
      </div>

      {/* Explanatory Safety Note - Filled Lavender */}
      <div className="bg-[#E4DAF5] border border-[#C8B8E4] rounded-xl px-4 py-3 flex items-start gap-2.5 text-xs text-[#431E8C]">
        <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#593CA5]" />
        <span>
          <strong>Safety Architecture Clarification:</strong> Freezing profile adaptation halts background machine-learning updates to defend reference traits from poisoning attacks; it does not lock the operating system or terminate user access.
        </span>
      </div>

      {actionMessage && (
        <div className={`p-4 rounded-xl text-xs flex items-center justify-between border font-bold ${
          actionMessage.type === 'success' 
            ? 'bg-[#CCEBD4] border-[#9EDAA9] text-[#0F5132]' 
            : 'bg-[#F5CCD7] border-[#EAAAB9] text-[#881337]'
        }`}>
          <span>{actionMessage.text}</span>
          <button onClick={() => setActionMessage(null)} className="text-[#4A5568] hover:text-[#1E2638] cursor-pointer">✕</button>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-[#F5CCD7] border border-[#EAAAB9] text-xs text-[#881337] font-bold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-[#E11D48] shrink-0" />
          <span>{error}. Verify backend (port 8080) and ML service (port 5001) are operational.</span>
        </div>
      )}

      {/* Primary Status Metric Cards - Rich Pastel Fills */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Version Card - Soft Lavender */}
        <div className="p-5 rounded-2xl bg-[#E4DAF5] border border-[#C8B8E4] space-y-1.5 shadow-xs">
          <div className="flex items-center justify-between text-[#431E8C] text-xs font-bold">
            <span>Active Trusted Profile</span>
            <GitBranch className="w-4 h-4 text-[#593CA5]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-[#1E2638]">
            {status?.active_version || 'v1.0.0'}
          </div>
          <div className="text-xs text-[#4A5568]">
            Baseline Samples: <span className="text-[#1E2638] font-bold font-mono">{status?.sample_count ?? 435}</span>
          </div>
        </div>

        {/* Candidate Buffer Card - Powder Blue */}
        <div className="p-5 rounded-2xl bg-[#D8E7F7] border border-[#ADC9EE] space-y-2 shadow-xs">
          <div className="flex items-center justify-between text-[#0A3B7B] text-xs font-bold">
            <span>Candidate Observation Buffer</span>
            <Activity className="w-4 h-4 text-[#1D4ED8]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-[#0A3B7B]">
            {status?.candidate_buffer?.current_size ?? 0} / {status?.policy_config?.min_observations ?? 5}
          </div>
          {/* Progress bar */}
          <div className="w-full bg-[#BFD6EE] h-2.5 rounded-full overflow-hidden">
            <div 
              className="bg-[#1D4ED8] h-full rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(100, (((status?.candidate_buffer?.current_size ?? 0) / (status?.policy_config?.min_observations ?? 5)) * 100))}%`
              }}
            />
          </div>
          <div className="text-[11px] text-[#0A3B7B] font-medium">
            Isolated from reference profile until accepted
          </div>
        </div>

        {/* Suspicious Streak Card - Warm Peach */}
        <div className="p-5 rounded-2xl bg-[#F8DAC0] border border-[#F0BF94] space-y-1.5 shadow-xs">
          <div className="flex items-center justify-between text-[#7C2D12] text-xs font-bold">
            <span>Suspicious Anomaly Streak</span>
            <ShieldAlert className="w-4 h-4 text-[#D97706]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-[#7C2D12]">
            {status?.suspicious_streak ?? 0} / {status?.policy_config?.max_suspicious_streak ?? 3}
          </div>
          <div className="text-xs text-[#7C2D12] font-medium">
            Auto-freezes at 3 to prevent profile poisoning
          </div>
        </div>

        {/* Policy Readiness Card - Soft Mint */}
        <div className="p-5 rounded-2xl bg-[#CCEBD4] border border-[#9EDAA9] space-y-1.5 shadow-xs">
          <div className="flex items-center justify-between text-[#0F5132] text-xs font-bold">
            <span>Safety Constraints &amp; Policy</span>
            <Lock className="w-4 h-4 text-[#15803D]" />
          </div>
          <div className="text-sm font-extrabold font-mono text-[#0F5132]">
            Policy v{status?.policy_config?.policy_version || '1.0.0'}
          </div>
          <div className="text-xs text-[#0F5132] truncate font-medium">
            Max Drift: <span className="font-mono font-bold text-[#0F5132]">{status?.policy_config?.max_drift_magnitude || 1.8}&sigma;</span> &bull; Velocity: <span className="font-mono font-bold text-[#0F5132]">{status?.policy_config?.max_velocity || 2.5}</span>
          </div>
        </div>
      </div>

      {/* Security Action Controls - Filled Soft Lavender Bar */}
      <div className="p-5 rounded-2xl bg-[#EAE0F7] border border-[#CDBEE5] flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <div className="space-y-0.5">
          <div className="text-xs font-extrabold text-[#1E2638] uppercase tracking-wider">
            Operational Security Controls
          </div>
          <p className="text-xs text-[#4A5568] font-medium">
            Enforce defensive safeguards, administrative recovery, or version rollback.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {status?.is_frozen ? (
            <button
              onClick={() => setShowUnfreezeModal(true)}
              disabled={actionLoading}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#CCEBD4] hover:bg-[#BCE3C5] text-[#0F5132] border border-[#9EDAA9] text-xs font-bold transition-colors cursor-pointer"
            >
              <Unlock className="w-4 h-4 text-[#15803D]" />
              <span>Authorize Unfreeze Recovery</span>
            </button>
          ) : (
            <button
              onClick={() => setShowFreezeModal(true)}
              disabled={actionLoading}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#F5CCD7] hover:bg-[#EAAAB9] text-[#881337] border border-[#EAAAB9] text-xs font-bold transition-colors cursor-pointer"
            >
              <Lock className="w-4 h-4 text-[#E11D48]" />
              <span>Freeze Profile Updates</span>
            </button>
          )}

          <div className="flex items-center gap-2 bg-[#E4DAF5] border border-[#C8B8E4] rounded-xl px-3 py-1.5">
            <RotateCcw className="w-4 h-4 text-[#593CA5]" />
            <select
              value={rollbackVersion}
              onChange={(e) => setRollbackVersion(e.target.value)}
              className="bg-transparent text-xs text-[#1E2638] font-mono outline-none cursor-pointer font-bold"
            >
              {status?.versions_summary && status.versions_summary.length > 0 ? (
                status.versions_summary.map((v) => (
                  <option key={v.version_tag} value={v.version_tag} className="bg-[#E4DAF5] text-[#1E2638]">
                    {v.version_tag} ({v.sample_count} samples)
                  </option>
                ))
              ) : (
                <option value="v1.0.0" className="bg-[#E4DAF5] text-[#1E2638]">v1.0.0 (baseline)</option>
              )}
            </select>
            <button
              onClick={() => setShowRollbackModal(true)}
              disabled={actionLoading}
              className="text-xs text-[#7C2D12] font-bold px-3 py-1 rounded-lg bg-[#F8DAC0] border border-[#F0BF94] hover:bg-[#F2CCA8] transition-colors cursor-pointer"
            >
              Rollback...
            </button>
          </div>
        </div>
      </div>

      {/* Freeze Confirmation Modal */}
      {showFreezeModal && (
        <div className="p-5 rounded-2xl bg-[#FCE7ED] border border-[#F5B5C4] space-y-3">
          <div className="text-xs font-bold text-[#881337] flex items-center gap-2">
            <Lock className="w-4 h-4 text-[#E11D48]" /> Confirm Profile Adaptation Freeze
          </div>
          <p className="text-xs text-[#4C0519] font-medium">
            Freezing stops all adaptation updates immediately. Observations will be rejected from candidate accumulation.
          </p>
          <div className="space-y-1">
            <label className="text-xs text-[#881337] font-bold">Freeze Reason:</label>
            <input
              type="text"
              value={freezeReason}
              onChange={(e) => setFreezeReason(e.target.value)}
              className="w-full bg-[#FDF2F4] border border-[#F5B5C4] rounded-xl p-2.5 text-xs text-[#1E2638] focus:outline-none focus:ring-2 focus:ring-[#E11D48]"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleFreeze}
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-[#E11D48] hover:bg-[#BE123C] text-white text-xs font-bold cursor-pointer"
            >
              {actionLoading ? 'Executing...' : 'Confirm Freeze'}
            </button>
            <button
              onClick={() => setShowFreezeModal(false)}
              className="px-4 py-2 rounded-xl bg-[#FDF2F4] border border-[#F5B5C4] text-[#881337] text-xs font-bold cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Unfreeze Confirmation Modal */}
      {showUnfreezeModal && (
        <div className="p-5 rounded-2xl bg-[#DDF3E4] border border-[#B1E5C0] space-y-3">
          <div className="text-xs font-bold text-[#0F5132] flex items-center gap-2">
            <Unlock className="w-4 h-4 text-[#15803D]" /> Authorize Administrative Unfreeze Recovery
          </div>
          <p className="text-xs text-[#0F5132] font-medium">
            Unfreezing resets the suspicious streak counter and reactivates continuous candidate buffering.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs text-[#0F5132] font-bold">Authorized Operator:</label>
              <input
                type="text"
                value={unfreezeAuth}
                onChange={(e) => setUnfreezeAuth(e.target.value)}
                className="w-full bg-[#EBF8EF] border border-[#B1E5C0] rounded-xl p-2.5 text-xs text-[#1E2638] focus:outline-none focus:ring-2 focus:ring-[#15803D]"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-[#0F5132] font-bold">Unfreeze Justification:</label>
              <input
                type="text"
                value={unfreezeReason}
                onChange={(e) => setUnfreezeReason(e.target.value)}
                className="w-full bg-[#EBF8EF] border border-[#B1E5C0] rounded-xl p-2.5 text-xs text-[#1E2638] focus:outline-none focus:ring-2 focus:ring-[#15803D]"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleUnfreeze}
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-[#15803D] hover:bg-[#166534] text-white text-xs font-bold cursor-pointer"
            >
              {actionLoading ? 'Executing...' : 'Authorize Recovery'}
            </button>
            <button
              onClick={() => setShowUnfreezeModal(false)}
              className="px-4 py-2 rounded-xl bg-[#EBF8EF] border border-[#B1E5C0] text-[#0F5132] text-xs font-bold cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Rollback Confirmation Modal */}
      {showRollbackModal && (
        <div className="p-5 rounded-2xl bg-[#FEF0E0] border border-[#FCD4AF] space-y-3">
          <div className="text-xs font-bold text-[#7C2D12] flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-[#D97706]" /> Confirm Profile Version Rollback
          </div>
          <p className="text-xs text-[#7C2D12] font-medium">
            Reverts behavioural identity to an earlier trusted reference version (<span className="text-[#B45309] font-mono font-bold">{rollbackVersion}</span>). This clears candidate accumulation buffers, resets suspicious streaks, and reactivates continuous verification against baseline traits.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1">
              <label className="text-xs text-[#7C2D12] font-bold">Target Profile Version:</label>
              <select
                value={rollbackVersion}
                onChange={(e) => setRollbackVersion(e.target.value)}
                className="w-full bg-[#FFF6ED] border border-[#FCD4AF] rounded-xl p-2.5 text-xs text-[#1E2638] font-mono font-bold"
              >
                {status?.versions_summary && status.versions_summary.length > 0 ? (
                  status.versions_summary.map((v) => (
                    <option key={v.version_tag} value={v.version_tag}>
                      {v.version_tag} ({v.sample_count} samples) - {v.status}
                    </option>
                  ))
                ) : (
                  <option value="v1.0.0">v1.0.0 (baseline)</option>
                )}
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs text-[#7C2D12] font-bold">Authorized Operator:</label>
              <input
                type="text"
                value={rollbackAuth}
                onChange={(e) => setRollbackAuth(e.target.value)}
                className="w-full bg-[#FFF6ED] border border-[#FCD4AF] rounded-xl p-2.5 text-xs text-[#1E2638]"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-[#7C2D12] font-bold">Rollback Justification:</label>
              <input
                type="text"
                value={rollbackReason}
                onChange={(e) => setRollbackReason(e.target.value)}
                className="w-full bg-[#FFF6ED] border border-[#FCD4AF] rounded-xl p-2.5 text-xs text-[#1E2638]"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleRollback}
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-[#D97706] hover:bg-[#B45309] text-white text-xs font-bold cursor-pointer"
            >
              {actionLoading ? 'Executing...' : 'Confirm Rollback'}
            </button>
            <button
              onClick={() => setShowRollbackModal(false)}
              className="px-4 py-2 rounded-xl bg-[#FFF6ED] border border-[#FCD4AF] text-[#7C2D12] text-xs font-bold cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Live Adaptation History Table - Filled Soft Lavender Presentation */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-[#593CA5]">
            <History className="w-4 h-4" />
            <h3 className="text-xs font-bold text-[#1E2638] uppercase tracking-wider">
              Recent Adaptation Decisions &amp; Audit Trail
            </h3>
          </div>
          <span className="text-xs text-[#4A5568] font-mono font-medium">
            {history.length} events logged
          </span>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-[#C8B8E4]">
          <table className="w-full text-left text-xs text-[#1E2638]">
            <thead className="bg-[#DFD3F2] text-[11px] text-[#431E8C] uppercase font-bold border-b border-[#C8B8E4]">
              <tr>
                <th className="py-3 px-3">Timestamp</th>
                <th className="py-3 px-3">Decision State</th>
                <th className="py-3 px-3">Version Lineage</th>
                <th className="py-3 px-3">Drift (&sigma;)</th>
                <th className="py-3 px-3">Velocity</th>
                <th className="py-3 px-3">Candidates</th>
                <th className="py-3 px-3">Streak</th>
                <th className="py-3 px-3">Decision Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E3D9F3] bg-[#F7F3FC] font-mono text-[11px]">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-[#4A5568] font-sans text-xs">
                    No adaptation events recorded yet. Stream snapshots or run scenarios to observe continuous verification decisions.
                  </td>
                </tr>
              ) : (
                history.map((evt) => (
                  <tr key={evt.id} className="hover:bg-[#ECE4F8] transition-colors">
                    <td className="py-2.5 px-3 text-[#4A5568] whitespace-nowrap">
                      {new Date(evt.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      {getDecisionBadge(evt.decision_state)}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap text-[#1E2638] font-bold">
                      {evt.prior_profile_version}
                      {evt.new_profile_version && (
                        <span className="text-[#0F5132] font-bold"> &rarr; {evt.new_profile_version}</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-[#1E2638]">
                      {evt.drift_magnitude != null ? `${evt.drift_magnitude.toFixed(2)}σ` : '--'}
                    </td>
                    <td className="py-2.5 px-3 text-[#1E2638]">
                      {evt.velocity != null ? evt.velocity.toFixed(2) : '--'}
                    </td>
                    <td className="py-2.5 px-3 text-[#4A5568]">
                      {evt.candidate_count}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={evt.suspicious_streak > 0 ? 'text-[#D97706] font-extrabold' : 'text-[#4A5568]'}>
                        {evt.suspicious_streak}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[#4A5568] font-sans text-xs max-w-xs truncate" title={evt.decision_reason}>
                      {evt.decision_reason}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};
