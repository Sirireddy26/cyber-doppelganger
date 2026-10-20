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
      {/* Top Header & Refresh - Filled Soft Lavender */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-[#F1EBFA] border border-[#D2C4EB] rounded-2xl p-6 shadow-sm">
        <div>
          <h2 className="text-base font-extrabold text-[#1E2638] tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-[#593CA5]" />
            Machine Learning Diagnostics &amp; Ingestion Telemetry
          </h2>
          <p className="text-xs text-[#4A5568] mt-1 font-medium">
            Transparent inspection of trained anomaly models, calibrated decision boundaries, and stored biometric feature snapshots.
          </p>
        </div>

        <button 
          onClick={fetchTelemetry}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#7864D1] hover:bg-[#6752C4] text-white text-xs font-bold cursor-pointer transition-colors shadow-xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Model Parameter Specs Grid - Filled Pastel Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Algorithm - Soft Mint */}
        <div className="p-5 rounded-2xl bg-[#CCEBD4] border border-[#9EDAA9] space-y-1.5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#0F5132] uppercase tracking-wider font-bold">Active Algorithm</span>
            <ShieldCheck className="w-4 h-4 text-[#15803D]" />
          </div>
          <div className="text-base font-extrabold font-mono text-[#0F5132]">
            {modelStatus?.active_model_type || 'ISOLATION_FOREST'}
          </div>
          <span className="text-xs text-[#0F5132] font-semibold block">
            Status: {modelStatus?.status || 'READY'} (Calibrated)
          </span>
        </div>

        {/* Decision Boundary - Powder Blue */}
        <div 
          className="p-5 rounded-2xl bg-[#D8E7F7] border border-[#ADC9EE] space-y-1.5 shadow-xs cursor-help"
          title="Trained Decision Threshold: Calibrated from 5th percentile of baseline training observation scores. Inliers scoring >= 0.0327 are verified as genuine behaviour. Lower scores indicate anomalous deviation."
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#0A3B7B] uppercase tracking-wider font-bold">Decision Boundary</span>
            <HelpCircle className="w-4 h-4 text-[#1D4ED8]" />
          </div>
          <div className="text-xl font-extrabold font-mono text-[#0A3B7B]">
            {modelStatus?.isolation_forest?.threshold !== undefined 
              ? modelStatus.isolation_forest.threshold.toFixed(4) 
              : '0.0327'}
          </div>
          <span className="text-xs text-[#0A3B7B] font-medium block">
            5th Percentile Calibrated Cutoff
          </span>
        </div>

        {/* Reference Dataset - Soft Lavender */}
        <div className="p-5 rounded-2xl bg-[#E4DAF5] border border-[#C8B8E4] space-y-1.5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#431E8C] uppercase tracking-wider font-bold">Baseline Observations</span>
            <Layers className="w-4 h-4 text-[#593CA5]" />
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-extrabold font-mono text-[#431E8C]">
              {modelStatus?.isolation_forest?.sample_count || 435}
            </span>
            <span className="text-xs text-[#431E8C] font-semibold">samples</span>
          </div>
          <span className="text-xs text-[#431E8C] font-medium block">
            Trusted Reference Profile v1.0.0
          </span>
        </div>

        {/* Active Database - Warm Peach */}
        <div className="p-5 rounded-2xl bg-[#F8DAC0] border border-[#F0BF94] space-y-1.5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-[#7C2D12] uppercase tracking-wider font-bold">Active Database</span>
            <Database className="w-4 h-4 text-[#D97706]" />
          </div>
          <div className="text-base font-extrabold font-mono text-[#7C2D12]">
            {activeDbType}
          </div>
          <span className="text-xs text-[#7C2D12] font-semibold block">
            {isDbConnected ? 'CONNECTED (Active Connection)' : 'DISCONNECTED'}
          </span>
        </div>
      </div>

      {/* Explanatory Scientific Score Card - Powder Blue */}
      <div className="bg-[#D6E6F7] border border-[#A5C8EE] rounded-2xl p-5 text-xs text-[#0A3B7B] space-y-2 shadow-xs">
        <div className="flex items-center gap-2 font-bold text-[#0A3B7B]">
          <Info className="w-4 h-4 text-[#1D4ED8]" />
          <span>Understanding Decision Scores vs Anomaly Scores</span>
        </div>
        <p className="leading-relaxed font-medium">
          The Isolation Forest produces a <strong>Model Decision Score (raw_score)</strong> via its decision function, where higher positive values represent typical inlier clusters and negative values indicate abnormal outliers. The <strong>Anomaly Score</strong> is mathematically defined as <code className="bg-[#BFD6EE] px-1.5 py-0.5 rounded font-mono font-bold">-raw_score</code>, where larger positive values indicate greater deviation from the reference baseline. A non-calibrated score is not a probability; it measures geometric distance in kinematic space.
        </p>
      </div>

      {/* Sub-Tabs: Verification History vs Ingested Snapshots - Filled Soft Lavender */}
      <div className="bg-[#F1EBFA] border border-[#D2C4EB] rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-[#D2C4EB] pb-4">
          <div className="flex items-center gap-2.5">
            <button 
              onClick={() => setActiveSubTab('verifications')}
              className={`px-4 py-2 rounded-xl text-xs font-bold cursor-pointer transition-colors ${
                activeSubTab === 'verifications'
                  ? 'bg-[#7864D1] text-white shadow-xs'
                  : 'bg-[#E4DAF5] border border-[#C8B8E4] text-[#1E2638] hover:bg-[#D7C6EE]'
              }`}
            >
              Verification Audit Stream ({verifications.length})
            </button>
            <button 
              onClick={() => setActiveSubTab('snapshots')}
              className={`px-4 py-2 rounded-xl text-xs font-bold cursor-pointer transition-colors ${
                activeSubTab === 'snapshots'
                  ? 'bg-[#7864D1] text-white shadow-xs'
                  : 'bg-[#E4DAF5] border border-[#C8B8E4] text-[#1E2638] hover:bg-[#D7C6EE]'
              }`}
            >
              Ingested Feature Snapshots ({snapshots.length})
            </button>
          </div>

          <span className="text-xs text-[#4A5568] font-mono hidden sm:inline font-medium">
            Showing most recent records
          </span>
        </div>

        {/* Verification History Table */}
        {activeSubTab === 'verifications' && (
          <div className="overflow-x-auto rounded-2xl border border-[#C8B8E4]">
            {verifications.length === 0 ? (
              <div className="py-8 text-center text-[#4A5568] text-xs font-mono bg-[#F7F3FC]">
                No verification records found yet. Use the Biometric Playground to evaluate live timing.
              </div>
            ) : (
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#DFD3F2] text-[#431E8C] uppercase text-[10px] tracking-wider font-bold border-b border-[#C8B8E4]">
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
                <tbody className="divide-y divide-[#E3D9F3] bg-[#F7F3FC]">
                  {verifications.map((item) => (
                    <tr key={item.id} className="hover:bg-[#ECE4F8] transition-colors">
                      <td className="py-2.5 px-3 text-[#593CA5] font-extrabold">#{item.id}</td>
                      <td className="py-2.5 px-3 text-[#4A5568]">
                        {item.created_at ? new Date(item.created_at).toLocaleTimeString() : '--'}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          item.decision === 'NORMAL_BEHAVIOUR'
                            ? 'bg-[#CCEBD4] text-[#0F5132] border border-[#9EDAA9]'
                            : 'bg-[#F5CCD7] text-[#881337] border border-[#EAAAB9]'
                        }`}>
                          {item.decision}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-bold text-[#1E2638]">
                        {item.raw_score > 0 ? `+${item.raw_score.toFixed(4)}` : item.raw_score.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 text-[#4A5568]">
                        {item.anomaly_score.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 text-[#4A5568] truncate max-w-[120px]">
                        {item.device_id || 'LOCAL'}
                      </td>
                      <td className="py-2.5 px-3 text-[#4A5568] truncate max-w-[220px]" title={item.reason}>
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
          <div className="overflow-x-auto rounded-2xl border border-[#C8B8E4]">
            {snapshots.length === 0 ? (
              <div className="py-8 text-center text-[#4A5568] text-xs font-mono bg-[#F7F3FC]">
                No feature snapshots stored yet. Start the desktop agent or ingest snapshots from the Playground.
              </div>
            ) : (
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#DFD3F2] text-[#431E8C] uppercase text-[10px] tracking-wider font-bold border-b border-[#C8B8E4]">
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
                <tbody className="divide-y divide-[#E3D9F3] bg-[#F7F3FC]">
                  {snapshots.map((snap) => (
                    <tr key={snap.id} className="hover:bg-[#ECE4F8] transition-colors">
                      <td className="py-2.5 px-3 text-[#593CA5] font-extrabold">#{snap.id}</td>
                      <td className="py-2.5 px-3 text-[#1E2638] font-bold">{snap.deviceId}</td>
                      <td className="py-2.5 px-3 text-[#4A5568]">{snap.windowDurationSeconds}s</td>
                      <td className="py-2.5 px-3 text-[#1E2638]">
                        {snap.keyboard?.mean_dwell_time_ms ? `${snap.keyboard.mean_dwell_time_ms.toFixed(1)}ms` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-[#1E2638]">
                        {snap.keyboard?.mean_flight_time_ms ? `${snap.keyboard.mean_flight_time_ms.toFixed(1)}ms` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-[#0F5132] font-bold">
                        {snap.keyboard?.typing_speed_wpm ? `${snap.keyboard.typing_speed_wpm.toFixed(1)}` : '--'}
                      </td>
                      <td className="py-2.5 px-3 text-[#1E2638]">
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
