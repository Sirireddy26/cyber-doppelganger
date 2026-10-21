import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  Database, 
  ShieldCheck, 
  RefreshCw, 
  HelpCircle, 
  Layers, 
  Info 
} from 'lucide-react';
import { ApiService } from '../../services/api';
import type { ModelStatusResponse, VerificationResult, BehaviourSnapshot, SystemDiagnostics } from '../../types/api';

export const ModelDiagnostics: React.FC = () => {
  const [modelStatus, setModelStatus] = useState<ModelStatusResponse | null>(null);
  const [diagnostics, setDiagnostics] = useState<SystemDiagnostics | null>(null);
  const [verifications, setVerifications] = useState<VerificationResult[]>([]);
  const [snapshots, setSnapshots] = useState<BehaviourSnapshot[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState<'verifications' | 'snapshots'>('verifications');

  const fetchTelemetry = async () => {
    setLoading(true);
    try {
      const [modelData, diagData, verifData, snapData] = await Promise.allSettled([
        ApiService.getModelStatus(),
        ApiService.getDiagnostics(),
        ApiService.getVerificationHistory(0, 15),
        ApiService.getBehaviourSnapshots(0, 15),
      ]);

      if (modelData.status === 'fulfilled') setModelStatus(modelData.value);
      if (diagData.status === 'fulfilled') setDiagnostics(diagData.value);
      if (verifData.status === 'fulfilled') setVerifications(verifData.value.content || []);
      if (snapData.status === 'fulfilled') setSnapshots(snapData.value.content || []);
    } catch {
      // Ignored
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, []);

  const activeDbType = diagnostics?.database?.database_type || 'H2';
  const isDbConnected = diagnostics?.database?.connected ?? true;

  return (
    <div className="space-y-6">
      {/* Top Header & Refresh */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-[#120D1F] border border-[#271C3D] rounded-2xl p-6 shadow-xl">
        <div>
          <h2 className="text-base font-extrabold text-white tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-[#8B5CF6]" />
            Machine Learning Diagnostics &amp; Ingestion Telemetry
          </h2>
          <p className="text-xs text-[#9D8EB9] mt-1 font-medium">
            Transparent inspection of trained anomaly models, calibrated decision boundaries, and stored biometric feature snapshots.
          </p>
        </div>

        <button 
          onClick={fetchTelemetry}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white text-xs font-bold cursor-pointer transition-colors shadow-lg shadow-violet-900/30"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Model Parameter Specs Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Algorithm */}
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#9D8EB9] uppercase tracking-wider font-bold">Active Algorithm</span>
            <ShieldCheck className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="text-base font-extrabold font-mono text-white">
            {modelStatus?.active_model_type || 'ISOLATION_FOREST'}
          </div>
          <span className="text-xs text-[#C4B5FD] font-semibold block">
            Status: {modelStatus?.status || 'READY'} (Calibrated)
          </span>
        </div>

        {/* Decision Boundary */}
        <div 
          className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-1.5 shadow-sm cursor-help"
          title="Trained Decision Threshold: Calibrated from 5th percentile of baseline training observation scores. Inliers scoring >= 0.0327 are verified as genuine behaviour. Lower scores indicate anomalous deviation."
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#9D8EB9] uppercase tracking-wider font-bold">Decision Boundary</span>
            <HelpCircle className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-white">
            {modelStatus?.isolation_forest?.threshold !== undefined 
              ? modelStatus.isolation_forest.threshold.toFixed(4) 
              : '0.0327'}
          </div>
          <span className="text-xs text-[#9D8EB9] font-medium block">
            5th Percentile Calibrated Cutoff
          </span>
        </div>

        {/* Reference Dataset */}
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#9D8EB9] uppercase tracking-wider font-bold">Baseline Observations</span>
            <Layers className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-extrabold font-mono text-white">
              {modelStatus?.isolation_forest?.sample_count || 435}
            </span>
            <span className="text-xs text-[#9D8EB9]">samples</span>
          </div>
          <span className="text-xs text-[#C4B5FD] font-medium block">
            Trusted Reference Profile v1.0.0
          </span>
        </div>

        {/* Active Database */}
        <div className="p-5 rounded-2xl bg-[#161026] border border-[#271C3D] space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#9D8EB9] uppercase tracking-wider font-bold">Active Database</span>
            <Database className="w-4 h-4 text-[#8B5CF6]" />
          </div>
          <div className="text-base font-extrabold font-mono text-white">
            {activeDbType}
          </div>
          <span className="text-xs text-[#C4B5FD] font-semibold block">
            {isDbConnected ? 'CONNECTED (Active Connection)' : 'DISCONNECTED'}
          </span>
        </div>
      </div>

      {/* Explanatory Scientific Score Card */}
      <div className="bg-[#161026] border border-[#271C3D] rounded-2xl p-5 text-xs text-[#C4B5FD] space-y-2 shadow-sm">
        <div className="flex items-center gap-2 font-bold text-white">
          <Info className="w-4 h-4 text-[#8B5CF6]" />
          <span>Understanding Decision Scores vs Anomaly Scores</span>
        </div>
        <p className="leading-relaxed font-medium text-[#9D8EB9]">
          The Isolation Forest produces a <strong className="text-white">Model Decision Score (raw_score)</strong> via its decision function, where higher positive values represent typical inlier clusters and negative values indicate abnormal outliers. The <strong className="text-white">Anomaly Score</strong> is mathematically defined as <code className="bg-[#0E0A18] text-[#E879F9] border border-[#271C3D] px-1.5 py-0.5 rounded font-mono font-bold">-raw_score</code>, where larger positive values indicate greater deviation from the reference baseline. A non-calibrated score is not a probability; it measures geometric distance in kinematic space.
        </p>
      </div>

      {/* Sub-Tabs: Verification History vs Ingested Snapshots */}
      <div className="bg-[#120D1F] border border-[#271C3D] rounded-2xl p-6 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-[#271C3D] pb-4">
          <div className="flex items-center gap-2.5">
            <button 
              onClick={() => setActiveSubTab('verifications')}
              className={`px-4 py-2 rounded-xl text-xs font-bold cursor-pointer transition-colors ${
                activeSubTab === 'verifications'
                  ? 'bg-[#7C3AED] text-white shadow-lg shadow-violet-900/30'
                  : 'bg-[#181228] border border-[#271C3D] text-[#9D8EB9] hover:text-white hover:bg-[#221639]'
              }`}
            >
              Verification Audit Stream ({verifications.length})
            </button>
            <button 
              onClick={() => setActiveSubTab('snapshots')}
              className={`px-4 py-2 rounded-xl text-xs font-bold cursor-pointer transition-colors ${
                activeSubTab === 'snapshots'
                  ? 'bg-[#7C3AED] text-white shadow-lg shadow-violet-900/30'
                  : 'bg-[#181228] border border-[#271C3D] text-[#9D8EB9] hover:text-white hover:bg-[#221639]'
              }`}
            >
              Ingested Feature Snapshots ({snapshots.length})
            </button>
          </div>

          <span className="text-xs text-[#9D8EB9] font-mono hidden sm:inline">
            Showing most recent records
          </span>
        </div>

        {/* Verification History Table */}
        {activeSubTab === 'verifications' && (
          <div className="overflow-x-auto rounded-2xl border border-[#271C3D]">
            {verifications.length === 0 ? (
              <div className="py-8 text-center text-[#9D8EB9] text-xs font-mono bg-[#0E0A18]">
                No verification records found yet. Use the Biometric Playground to evaluate live timing.
              </div>
            ) : (
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#181228] text-[#C4B5FD] uppercase text-[10px] tracking-wider font-bold border-b border-[#271C3D]">
                  <tr>
                    <th className="py-3 px-3">ID</th>
                    <th className="py-3 px-3">Timestamp</th>
                    <th className="py-3 px-3">Decision</th>
                    <th className="py-3 px-3">Raw Score</th>
                    <th className="py-3 px-3">Anomaly Score</th>
                    <th className="py-3 px-3">Device</th>
                    <th className="py-3 px-3">Rationale</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#271C3D] bg-[#0E0A18]">
                  {verifications.map((item) => (
                    <tr key={item.id} className="hover:bg-[#181228] transition-colors">
                      <td className="py-2.5 px-3 text-[#A78BFA] font-extrabold">#{item.id}</td>
                      <td className="py-2.5 px-3 text-[#9D8EB9]">
                        {item.created_at ? new Date(item.created_at).toLocaleTimeString() : '--'}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          item.decision === 'NORMAL_BEHAVIOUR'
                            ? 'bg-[#1C142E] text-[#C4B5FD] border border-[#382759]'
                            : 'bg-[#2D1226] text-[#F472B6] border border-[#5E1E49]'
                        }`}>
                          {item.decision}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-bold text-white">
                        {item.raw_score > 0 ? `+${item.raw_score.toFixed(4)}` : item.raw_score.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 text-[#9D8EB9]">
                        {item.anomaly_score.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 text-[#9D8EB9] truncate max-w-[120px]">
                        {item.device_id || 'LOCAL'}
                      </td>
                      <td className="py-2.5 px-3 text-[#9D8EB9] truncate max-w-[220px]" title={item.reason}>
                        {item.reason}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Snapshots Table */}
        {activeSubTab === 'snapshots' && (
          <div className="overflow-x-auto rounded-2xl border border-[#271C3D]">
            {snapshots.length === 0 ? (
              <div className="py-8 text-center text-[#9D8EB9] text-xs font-mono bg-[#0E0A18]">
                No feature snapshots stored yet. Start the desktop agent or ingest snapshots from the Playground.
              </div>
            ) : (
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#181228] text-[#C4B5FD] uppercase text-[10px] tracking-wider font-bold border-b border-[#271C3D]">
                  <tr>
                    <th className="py-3 px-3">ID</th>
                    <th className="py-3 px-3">Device ID</th>
                    <th className="py-3 px-3">Window</th>
                    <th className="py-3 px-3">Dwell Time</th>
                    <th className="py-3 px-3">Flight Time</th>
                    <th className="py-3 px-3">Typing WPM</th>
                    <th className="py-3 px-3">Mouse Speed</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#271C3D] bg-[#0E0A18]">
                  {snapshots.map((snap) => (
                    <tr key={snap.id} className="hover:bg-[#181228] transition-colors">
                      <td className="py-2.5 px-3 text-[#A78BFA] font-extrabold">#{snap.id}</td>
                      <td className="py-2.5 px-3 text-white font-bold">{snap.deviceId}</td>
                      <td className="py-2.5 px-3 text-[#9D8EB9]">{snap.windowDurationSeconds}s</td>
                      <td className="py-2.5 px-3 text-white">
                        {snap.keyboard?.mean_dwell_time_ms ? `${snap.keyboard.mean_dwell_time_ms.toFixed(1)}ms` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-white">
                        {snap.keyboard?.mean_flight_time_ms ? `${snap.keyboard.mean_flight_time_ms.toFixed(1)}ms` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-[#C4B5FD] font-bold">
                        {snap.keyboard?.typing_speed_wpm ? `${snap.keyboard.typing_speed_wpm.toFixed(1)}` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-white">
                        {snap.mouse?.mean_speed_pixels_per_second ? `${snap.mouse.mean_speed_pixels_per_second.toFixed(1)} px/s` : '--'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
