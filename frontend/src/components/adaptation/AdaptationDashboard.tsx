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
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#1C142E] text-[#C4B5FD] border border-[#382759]">
            <CheckCircle className="w-3 h-3 text-[#A78BFA]" />
            <span>ADAPTED</span>
          </span>
        );
      case 'PROFILE_FROZEN':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#2D1226] text-[#F472B6] border border-[#5E1E49]">
            <Lock className="w-3 h-3 text-[#F472B6]" />
            <span>FROZEN</span>
          </span>
        );
      case 'SUSPICIOUS_CHANGE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#26152B] text-[#E879F9] border border-[#521D5E]">
            <ShieldAlert className="w-3 h-3 text-[#E879F9]" />
            <span>SUSPICIOUS</span>
          </span>
        );
      case 'NORMAL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#1C142E] text-[#C4B5FD] border border-[#382759]">
            <ShieldCheck className="w-3 h-3 text-[#A78BFA]" />
            <span>NORMAL</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#181228] text-[#9D8EB9] border border-[#271C3D]">
            <Clock className="w-3 h-3 text-[#7C3AED]" />
            <span>{state}</span>
          </span>
        );
    }
  };

  return (
    <section className="bg-[#120D1F] border border-[#271C3D] rounded-2xl p-6 md:p-8 space-y-6 shadow-xl">
      {/* Header and Live Status Pill */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#271C3D] pb-5">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#1C142E] text-[#C4B5FD] border border-[#382759] text-xs font-semibold">
            <GitBranch className="w-3.5 h-3.5 text-[#8B5CF6]" />
            <span>Safe Adaptation Engine &bull; Reference Profile Protection</span>
          </div>
          <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
            Continuous Behavioural Profile Evolution
          </h2>
          <p className="text-xs md:text-sm text-[#9D8EB9] max-w-2xl leading-relaxed">
            Accommodates gradual user behavioural drift safely while preventing profile poisoning attacks. A candidate isolation buffer ensures suspicious observations cannot contaminate the reference model.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start md:self-auto">
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 rounded-xl bg-[#181228] border border-[#382759] hover:bg-[#251A3E] text-[#EDE9FE] transition-colors cursor-pointer"
            title="Refresh Adaptation Telemetry"
          >
            <RefreshCw className={`w-4 h-4 text-[#8B5CF6] ${loading ? 'animate-spin' : ''}`} />
          </button>

          {status?.is_frozen ? (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#2D1226] border border-[#5E1E49] text-[#F472B6] text-xs font-bold">
              <Lock className="w-3.5 h-3.5 text-[#F472B6]" />
              <span>PROFILE UPDATES FROZEN</span>
            </div>
          ) : status?.engine_status === 'ACTIVE' ? (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#1C142E] border border-[#382759] text-[#C4B5FD] text-xs font-bold">
              <ShieldCheck className="w-3.5 h-3.5 text-[#8B5CF6]" />
              <span>ACTIVE &bull; BOUNDED ADAPTATION</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#181228] border border-[#271C3D] text-[#9D8EB9] text-xs font-bold">
              <Activity className="w-3.5 h-3.5 text-[#8B5CF6]" />
              <span>{status?.engine_status || 'CONNECTING...'}</span>
            </div>
          )}
        </div>
      </div>

      {/* Explanatory Safety Note */}
      <div className="bg-[#161026] border border-[#271C3D] rounded-xl px-4 py-3 flex items-start gap-2.5 text-xs text-[#C4B5FD]">
        <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#8B5CF6]" />
        <span className="leading-relaxed">
          <strong className="text-white">Safety Architecture Clarification:</strong> Freezing profile adaptation halts background machine-learning updates to defend reference traits from poisoning attacks; it does not lock the operating system or terminate user access.
        </span>
      </div>

      {actionMessage && (
        <div className={`p-4 rounded-xl text-xs flex items-center justify-between border font-bold ${
          actionMessage.type === 'success' 
            ? 'bg-[#1C142E] border-[#382759] text-[#C4B5FD]' 
            : 'bg-[#2D1226] border-[#5E1E49] text-[#F472B6]'
        }`}>
          <span>{actionMessage.text}</span>
          <button onClick={() => setActionMessage(null)} className="text-[#9D8EB9] hover:text-white cursor-pointer">✕</button>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-[#2D1226] border border-[#5E1E49] text-xs text-[#F472B6] font-bold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-[#F472B6] shrink-0" />
          <span>{error}. Verify backend (port 8080) and ML service (port 5001) are operational.</span>
        </div>
      )}

      {/* Primary Status Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Version Card */}
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-[#9D8EB9] text-xs font-semibold">
            <span>Active Trusted Profile</span>
            <GitBranch className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-white">
            {status?.active_version || 'v1.0.0'}
          </div>
          <div className="text-xs text-[#9D8EB9]">
            Baseline Samples: <span className="text-white font-bold font-mono">{status?.sample_count ?? 435}</span>
          </div>
        </div>

        {/* Candidate Buffer Card */}
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-[#9D8EB9] text-xs font-semibold">
            <span>Candidate Observation Buffer</span>
            <Activity className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-white">
            {status?.candidate_buffer?.current_size ?? 0} / {status?.policy_config?.min_observations ?? 5}
          </div>
          {/* Progress bar */}
          <div className="w-full bg-[#0E0A18] h-2 rounded-full overflow-hidden border border-[#271C3D]">
            <div 
              className="bg-[#7C3AED] h-full rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(100, (((status?.candidate_buffer?.current_size ?? 0) / (status?.policy_config?.min_observations ?? 5)) * 100))}%`
              }}
            />
          </div>
          <div className="text-[11px] text-[#9D8EB9]">
            Isolated from reference profile until accepted
          </div>
        </div>

        {/* Suspicious Streak Card */}
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-[#9D8EB9] text-xs font-semibold">
            <span>Suspicious Anomaly Streak</span>
            <ShieldAlert className="w-4 h-4 text-[#E879F9]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-[#E879F9]">
            {status?.suspicious_streak ?? 0} / {status?.policy_config?.max_suspicious_streak ?? 3}
          </div>
          <div className="text-xs text-[#9D8EB9]">
            Auto-freezes at 3 to prevent profile poisoning
          </div>
        </div>

        {/* Policy Readiness Card */}
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-[#9D8EB9] text-xs font-semibold">
            <span>Safety Constraints &amp; Policy</span>
            <Lock className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="text-sm font-extrabold font-mono text-[#C4B5FD]">
            Policy v{status?.policy_config?.policy_version || '1.0.0'}
          </div>
          <div className="text-xs text-[#9D8EB9] truncate">
            Max Drift: <span className="font-mono font-bold text-white">{status?.policy_config?.max_drift_magnitude || 1.8}&sigma;</span> &bull; Velocity: <span className="font-mono font-bold text-white">{status?.policy_config?.max_velocity || 2.5}</span>
          </div>
        </div>
      </div>

      {/* Security Action Controls */}
      <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div className="space-y-0.5">
          <div className="text-xs font-bold text-white uppercase tracking-wider">
            Operational Security Controls
          </div>
          <p className="text-xs text-[#9D8EB9]">
            Enforce defensive safeguards, administrative recovery, or version rollback.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {status?.is_frozen ? (
            <button
              onClick={() => setShowUnfreezeModal(true)}
              disabled={actionLoading}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white border border-[#8B5CF6] text-xs font-bold transition-colors cursor-pointer shadow-lg shadow-violet-900/30"
            >
              <Unlock className="w-4 h-4" />
              <span>Authorize Unfreeze Recovery</span>
            </button>
          ) : (
            <button
              onClick={() => setShowFreezeModal(true)}
              disabled={actionLoading}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2D1226] hover:bg-[#3E1834] text-[#F472B6] border border-[#5E1E49] text-xs font-bold transition-colors cursor-pointer"
            >
              <Lock className="w-4 h-4 text-[#F472B6]" />
              <span>Freeze Profile Updates</span>
            </button>
          )}

          <div className="flex items-center gap-2 bg-[#0E0A18] border border-[#382759] rounded-xl px-3 py-1.5">
            <RotateCcw className="w-4 h-4 text-[#8B5CF6]" />
            <select
              value={rollbackVersion}
              onChange={(e) => setRollbackVersion(e.target.value)}
              className="bg-transparent text-xs text-[#EDE9FE] font-mono outline-none cursor-pointer font-bold"
            >
              {status?.versions_summary && status.versions_summary.length > 0 ? (
                status.versions_summary.map((v) => (
                  <option key={v.version_tag} value={v.version_tag} className="bg-[#120D1F] text-white">
                    {v.version_tag} ({v.sample_count} samples)
                  </option>
                ))
              ) : (
                <option value="v1.0.0" className="bg-[#120D1F] text-white">v1.0.0 (baseline)</option>
              )}
            </select>
            <button
              onClick={() => setShowRollbackModal(true)}
              disabled={actionLoading}
              className="text-xs text-white font-bold px-3 py-1 rounded-lg bg-[#7C3AED] hover:bg-[#6D28D9] transition-colors cursor-pointer"
            >
              Rollback...
            </button>
          </div>
        </div>
      </div>

      {/* Freeze Confirmation Modal */}
      {showFreezeModal && (
        <div className="p-5 rounded-2xl bg-[#1C1224] border border-[#5E1E49] space-y-3">
          <div className="text-xs font-bold text-[#F472B6] flex items-center gap-2">
            <Lock className="w-4 h-4 text-[#F472B6]" /> Confirm Profile Adaptation Freeze
          </div>
          <p className="text-xs text-[#EDE9FE]">
            Freezing stops all adaptation updates immediately. Observations will be rejected from candidate accumulation.
          </p>
          <div className="space-y-1">
            <label className="text-xs text-[#C4B5FD] font-semibold">Freeze Reason:</label>
            <input
              type="text"
              value={freezeReason}
              onChange={(e) => setFreezeReason(e.target.value)}
              className="w-full bg-[#0B0813] border border-[#382759] rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-[#7C3AED]"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleFreeze}
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-[#2D1226] hover:bg-[#3D1834] text-[#F472B6] border border-[#5E1E49] text-xs font-bold cursor-pointer"
            >
              {actionLoading ? 'Executing...' : 'Confirm Freeze'}
            </button>
            <button
              onClick={() => setShowFreezeModal(false)}
              className="px-4 py-2 rounded-xl bg-[#181228] border border-[#271C3D] text-[#9D8EB9] hover:text-white text-xs font-bold cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Unfreeze Confirmation Modal */}
      {showUnfreezeModal && (
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#382759] space-y-3">
          <div className="text-xs font-bold text-[#C4B5FD] flex items-center gap-2">
            <Unlock className="w-4 h-4 text-[#8B5CF6]" /> Authorize Administrative Unfreeze Recovery
          </div>
          <p className="text-xs text-[#9D8EB9]">
            Unfreezing resets the suspicious streak counter and reactivates continuous candidate buffering.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs text-[#C4B5FD] font-semibold">Authorized Operator:</label>
              <input
                type="text"
                value={unfreezeAuth}
                onChange={(e) => setUnfreezeAuth(e.target.value)}
                className="w-full bg-[#0B0813] border border-[#382759] rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-[#7C3AED]"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-[#C4B5FD] font-semibold">Unfreeze Justification:</label>
              <input
                type="text"
                value={unfreezeReason}
                onChange={(e) => setUnfreezeReason(e.target.value)}
                className="w-full bg-[#0B0813] border border-[#382759] rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-[#7C3AED]"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleUnfreeze}
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white text-xs font-bold cursor-pointer"
            >
              {actionLoading ? 'Executing...' : 'Authorize Recovery'}
            </button>
            <button
              onClick={() => setShowUnfreezeModal(false)}
              className="px-4 py-2 rounded-xl bg-[#181228] border border-[#271C3D] text-[#9D8EB9] hover:text-white text-xs font-bold cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Rollback Confirmation Modal */}
      {showRollbackModal && (
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#382759] space-y-3">
          <div className="text-xs font-bold text-[#C4B5FD] flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-[#8B5CF6]" /> Confirm Profile Version Rollback
          </div>
          <p className="text-xs text-[#9D8EB9]">
            Reverts behavioural identity to an earlier trusted reference version (<span className="text-white font-mono font-bold">{rollbackVersion}</span>). This clears candidate accumulation buffers, resets suspicious streaks, and reactivates continuous verification against baseline traits.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1">
              <label className="text-xs text-[#C4B5FD] font-semibold">Target Profile Version:</label>
              <select
                value={rollbackVersion}
                onChange={(e) => setRollbackVersion(e.target.value)}
                className="w-full bg-[#0B0813] border border-[#382759] rounded-xl p-2.5 text-xs text-white font-mono font-bold"
              >
                {status?.versions_summary && status.versions_summary.length > 0 ? (
                  status.versions_summary.map((v) => (
                    <option key={v.version_tag} value={v.version_tag} className="bg-[#120D1F] text-white">
                      {v.version_tag} ({v.sample_count} samples) - {v.status}
                    </option>
                  ))
                ) : (
                  <option value="v1.0.0" className="bg-[#120D1F] text-white">v1.0.0 (baseline)</option>
                )}
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs text-[#C4B5FD] font-semibold">Authorized Operator:</label>
              <input
                type="text"
                value={rollbackAuth}
                onChange={(e) => setRollbackAuth(e.target.value)}
                className="w-full bg-[#0B0813] border border-[#382759] rounded-xl p-2.5 text-xs text-white"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-[#C4B5FD] font-semibold">Rollback Justification:</label>
              <input
                type="text"
                value={rollbackReason}
                onChange={(e) => setRollbackReason(e.target.value)}
                className="w-full bg-[#0B0813] border border-[#382759] rounded-xl p-2.5 text-xs text-white"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleRollback}
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white text-xs font-bold cursor-pointer"
            >
              {actionLoading ? 'Executing...' : 'Confirm Rollback'}
            </button>
            <button
              onClick={() => setShowRollbackModal(false)}
              className="px-4 py-2 rounded-xl bg-[#181228] border border-[#271C3D] text-[#9D8EB9] hover:text-white text-xs font-bold cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Live Adaptation History Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-[#8B5CF6]">
            <History className="w-4 h-4" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Recent Adaptation Decisions &amp; Audit Trail
            </h3>
          </div>
          <span className="text-xs text-[#9D8EB9] font-mono">
            {history.length} events logged
          </span>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-[#271C3D]">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#181228] text-[11px] text-[#C4B5FD] uppercase font-bold border-b border-[#271C3D]">
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
            <tbody className="divide-y divide-[#271C3D] bg-[#0E0A18] font-mono text-[11px]">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-[#9D8EB9] font-sans text-xs">
                    No adaptation events recorded yet. Stream snapshots or run scenarios to observe continuous verification decisions.
                  </td>
                </tr>
              ) : (
                history.map((evt) => (
                  <tr key={evt.id} className="hover:bg-[#181228] transition-colors">
                    <td className="py-2.5 px-3 text-[#9D8EB9] whitespace-nowrap">
                      {new Date(evt.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap">
                      {getDecisionBadge(evt.decision_state)}
                    </td>
                    <td className="py-2.5 px-3 whitespace-nowrap text-white font-bold">
                      {evt.prior_profile_version}
                      {evt.new_profile_version && (
                        <span className="text-[#C4B5FD] font-bold"> &rarr; {evt.new_profile_version}</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-white">
                      {evt.drift_magnitude != null ? `${evt.drift_magnitude.toFixed(2)}σ` : '--'}
                    </td>
                    <td className="py-2.5 px-3 text-white">
                      {evt.velocity != null ? evt.velocity.toFixed(2) : '--'}
                    </td>
                    <td className="py-2.5 px-3 text-[#9D8EB9]">
                      {evt.candidate_count}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={evt.suspicious_streak > 0 ? 'text-[#E879F9] font-extrabold' : 'text-[#9D8EB9]'}>
                        {evt.suspicious_streak}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[#9D8EB9] font-sans text-xs max-w-xs truncate" title={evt.decision_reason}>
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
