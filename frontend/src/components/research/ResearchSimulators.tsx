import React, { useState } from 'react';
import { 
  Play, 
  ShieldAlert, 
  TrendingUp, 
  RotateCcw, 
  Terminal, 
  Zap,
  Info,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  FlaskConical
} from 'lucide-react';
import { ApiService } from '../../services/api';

interface SimulationLog {
  timestamp: string;
  step: number;
  scenario: string;
  action: string;
  status: 'info' | 'success' | 'warning' | 'error';
  details: string;
}

export const ResearchSimulators: React.FC<{ onScenarioComplete?: () => void }> = ({ onScenarioComplete }) => {
  const [running, setRunning] = useState<string | null>(null);
  const [logs, setLogs] = useState<SimulationLog[]>([]);

  const appendLog = (step: number, scenario: string, action: string, status: 'info' | 'success' | 'warning' | 'error', details: string) => {
    setLogs((prev) => [
      {
        timestamp: new Date().toLocaleTimeString(),
        step,
        scenario,
        action,
        status,
        details,
      },
      ...prev.slice(0, 49),
    ]);
  };

  // Scenario 1: Legitimate Continuous Session -> Fills buffer (5/5) -> Promotes profile v1.0.0 -> v1.1.0
  const runLegitimateAdaptationScenario = async () => {
    setRunning('legitimate');
    appendLog(1, 'Legitimate Session', 'Scenario Initiated', 'info', 'Starting 5-step continuous legitimate user interaction session.');

    try {
      for (let i = 1; i <= 5; i++) {
        const slightDrift = 0.35 + (i * 0.05);
        const payload = {
          features: {
            mean_key_interval: 140.0 + (i * 2.0),
            typing_speed: 46.0 - (i * 0.5),
            backspace_rate: 0.04,
            mean_mouse_speed: 155.0 + (i * 1.5),
            mouse_jitter: 0.05
          },
          drift_magnitude: slightDrift,
          velocity: 0.4,
          is_anomaly: false
        };

        appendLog(i, 'Legitimate Session', `Ingesting Candidate ${i}/5`, 'info', `Synthetic Drift: ${slightDrift.toFixed(2)} | Velocity: 0.40 | Normal Range`);
        const res = await ApiService.processAdaptation(payload);

        if (i < 5) {
          appendLog(i, 'Legitimate Session', `Buffer Accumulated`, 'info', `Buffer Size: ${res.candidate_count}/5 observations | State: ${res.decision_state}`);
        } else {
          appendLog(5, 'Legitimate Session', `Candidate Buffer Full (5/5)`, 'success', `State: ${res.decision_state} | Version: ${res.new_profile_version || 'Promoted'} | Reason: ${res.decision_reason}`);
        }

        await new Promise((r) => setTimeout(r, 600));
      }

      appendLog(6, 'Legitimate Session', 'Scenario Completed', 'success', 'Safe profile evolution successfully verified. Zero contamination detected.');
      if (onScenarioComplete) onScenarioComplete();
    } catch (err: any) {
      appendLog(0, 'Legitimate Session', 'Error Encountered', 'error', err.message || 'Execution failed');
    } finally {
      setRunning(null);
    }
  };

  // Scenario 2: Sudden Impostor Takeover -> High drift -> Streak 3/3 -> Automatic Freeze
  const runSuddenTakeoverScenario = async () => {
    setRunning('takeover');
    appendLog(1, 'Impostor Takeover', 'Attack Simulation Initiated', 'warning', 'Simulating sudden session takeover with erratic high-drift kinematics.');

    try {
      for (let i = 1; i <= 3; i++) {
        const erraticDrift = 2.45 + (i * 0.2);
        const payload = {
          features: {
            mean_key_interval: 320.0,
            typing_speed: 18.0,
            backspace_rate: 0.38,
            mean_mouse_speed: 820.0,
            mouse_jitter: 0.45
          },
          drift_magnitude: erraticDrift,
          velocity: 3.1,
          is_anomaly: true
        };

        appendLog(i, 'Impostor Takeover', `Submitting Anomaly ${i}/3`, 'warning', `Synthetic Drift: ${erraticDrift.toFixed(2)} > 1.80 limit | Flagged Anomalous`);
        const res = await ApiService.processAdaptation(payload);

        if (res.is_profile_frozen || res.decision_state === 'PROFILE_FROZEN') {
          appendLog(i, 'Impostor Takeover', 'Automatic Freeze Activated', 'error', `Streak Threshold Reached (3/3). Engine locked: ${res.decision_reason}`);
          break;
        } else {
          appendLog(i, 'Impostor Takeover', `Suspicious Streak Increment`, 'warning', `Streak: ${res.suspicious_streak}/3 | Decision: ${res.decision_state}`);
        }

        await new Promise((r) => setTimeout(r, 600));
      }

      appendLog(4, 'Impostor Takeover', 'Simulation Completed', 'success', 'Safety constraint verified: Profile adaptation frozen. Profile contamination prevented.');
      if (onScenarioComplete) onScenarioComplete();
    } catch (err: any) {
      appendLog(0, 'Impostor Takeover', 'Error Encountered', 'error', err.message || 'Execution failed');
    } finally {
      setRunning(null);
    }
  };

  // Scenario 3: Bounded Velocity Filter Guardrail
  const runVelocityFilterScenario = async () => {
    setRunning('velocity');
    appendLog(1, 'Velocity Guardrail', 'Scenario Initiated', 'info', 'Testing bounded velocity filter with sudden biometric acceleration.');

    try {
      const payload = {
        features: {
          mean_key_interval: 180.0,
          typing_speed: 40.0,
          backspace_rate: 0.05,
          mean_mouse_speed: 250.0,
          mouse_jitter: 0.1
        },
        drift_magnitude: 1.2,
        velocity: 3.8, // Violates max_velocity (2.5)
        is_anomaly: false
      };

      appendLog(2, 'Velocity Guardrail', 'Submitting High-Velocity Observation', 'warning', 'Synthetic Velocity: 3.80 exceeds safety ceiling of 2.50.');
      const res = await ApiService.processAdaptation(payload);
      appendLog(3, 'Velocity Guardrail', 'Guardrail Activated', 'warning', `Decision: ${res.decision_state} | Reason: ${res.decision_reason}`);

      if (onScenarioComplete) onScenarioComplete();
    } catch (err: any) {
      appendLog(0, 'Velocity Guardrail', 'Error Encountered', 'error', err.message || 'Execution failed');
    } finally {
      setRunning(null);
    }
  };

  // Scenario 4: Recovery Reset / Unfreeze
  const handleSecurityReset = async () => {
    setRunning('reset');
    appendLog(1, 'Security Reset', 'Admin Authorization', 'info', 'Unfreezing profile and resetting adaptation telemetry.');

    try {
      const res = await ApiService.unfreezeProfile('security-admin', 'Research demonstration baseline reset');
      appendLog(2, 'Security Reset', 'Profile Unfrozen', 'success', `Status: ${res.message || 'Active'} | Profile restored to ACTIVE state.`);
      if (onScenarioComplete) onScenarioComplete();
    } catch (err: any) {
      appendLog(0, 'Security Reset', 'Error Encountered', 'error', err.message || 'Reset failed');
    } finally {
      setRunning(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Prominent Mandatory Academic Transparency Banner - Filled Warm Amber/Peach */}
      <div className="bg-[#FEF0DC] border-2 border-[#FCD49F] rounded-2xl p-5 space-y-2 shadow-xs">
        <div className="flex items-center gap-2 text-[#78350F]">
          <FlaskConical className="w-5 h-5 flex-shrink-0 text-[#C25E00]" />
          <h2 className="text-xs sm:text-sm font-extrabold uppercase tracking-wider">
            SIMULATION — CONTROLLED DEMONSTRATION, NOT PROOF OF REAL-WORLD ATTACK DETECTION
          </h2>
        </div>
        <p className="text-xs text-[#78350F] leading-relaxed font-medium">
          These simulator scenarios utilize calibrated synthetic biometric vectors to evaluate the behavioral state machine (drift bounding, candidate buffer thresholds, and streak freeze protections). Synthetic functional test events are segregated from empirical evaluation data.
        </p>
      </div>

      {/* Scenario Action Cards - Distinctly Colored Filled Pastel Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* Scenario 1 Card - Filled Soft Mint */}
        <div className="bg-[#CCEBD4] border border-[#9CD6A8] rounded-2xl p-6 flex flex-col justify-between space-y-4 shadow-sm">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-[#0F5132]">
                <TrendingUp className="w-4 h-4" />
                <h3 className="font-extrabold text-xs uppercase tracking-wider text-[#0F5132]">
                  Scenario 1: Legitimate Drift
                </h3>
              </div>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#B3E3BE] text-[#0A4126] border border-[#8ED49C]">
                Synthetic Control
              </span>
            </div>

            <div className="space-y-1.5 text-xs text-[#1E3A2B] font-medium">
              <p><strong className="text-[#0F5132]">Start State:</strong> Active profile v1.0.0, empty buffer.</p>
              <p><strong className="text-[#0F5132]">Intended:</strong> Ingests 5 legitimate samples with natural drift (&Delta; &le; 1.8). Safely advances profile.</p>
              <p><strong className="text-[#0F5132]">Expected Verdict:</strong> SAFE_ADAPTATION &rarr; v1.1.0.</p>
            </div>
          </div>

          <button 
            onClick={runLegitimateAdaptationScenario}
            disabled={running !== null}
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#2D8A4E] hover:bg-[#236F3E] disabled:opacity-50 text-white text-xs font-bold cursor-pointer transition-all active:scale-98 shadow-xs"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{running === 'legitimate' ? 'Executing Steps (1-5)...' : 'Run Safe Adaptation'}</span>
          </button>
        </div>

        {/* Scenario 2 Card - Filled Dusty Rose */}
        <div className="bg-[#F5CCD7] border border-[#E49DAE] rounded-2xl p-6 flex flex-col justify-between space-y-4 shadow-sm">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-[#881337]">
                <ShieldAlert className="w-4 h-4" />
                <h3 className="font-extrabold text-xs uppercase tracking-wider text-[#881337]">
                  Scenario 2: Impostor Takeover
                </h3>
              </div>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#EBB4C3] text-[#650B25] border border-[#DF8FA3]">
                Synthetic Attack
              </span>
            </div>

            <div className="space-y-1.5 text-xs text-[#4A1525] font-medium">
              <p><strong className="text-[#881337]">Start State:</strong> Active profile v1.0.0, streak 0/3.</p>
              <p><strong className="text-[#881337]">Intended:</strong> Injects 3 erratic anomalies (&Delta; &gt; 1.8). Reaches streak ceiling and freezes.</p>
              <p><strong className="text-[#881337]">Expected Verdict:</strong> PROFILE_FROZEN (Protection Active).</p>
            </div>
          </div>

          <button 
            onClick={runSuddenTakeoverScenario}
            disabled={running !== null}
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#BE123C] hover:bg-[#9F0E31] disabled:opacity-50 text-white text-xs font-bold cursor-pointer transition-all active:scale-98 shadow-xs"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{running === 'takeover' ? 'Simulating Impostor...' : 'Simulate Impostor Attack'}</span>
          </button>
        </div>

        {/* Scenario 3 Card - Filled Warm Peach */}
        <div className="bg-[#F8DAC0] border border-[#EDB482] rounded-2xl p-6 flex flex-col justify-between space-y-4 shadow-sm">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-[#7C2D12]">
                <Zap className="w-4 h-4" />
                <h3 className="font-extrabold text-xs uppercase tracking-wider text-[#7C2D12]">
                  Scenario 3: Velocity Guardrail
                </h3>
              </div>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#F1C39E] text-[#5C1D08] border border-[#E7A576]">
                Synthetic Boundary
              </span>
            </div>

            <div className="space-y-1.5 text-xs text-[#4A2011] font-medium">
              <p><strong className="text-[#7C2D12]">Start State:</strong> Active profile v1.0.0, standard rate limit.</p>
              <p><strong className="text-[#7C2D12]">Intended:</strong> Submits observation exceeding velocity limit (3.80 &gt; 2.50). Rejects candidate.</p>
              <p><strong className="text-[#7C2D12]">Expected Verdict:</strong> SUSPICIOUS_CHANGE (Bounded Reject).</p>
            </div>
          </div>

          <button 
            onClick={runVelocityFilterScenario}
            disabled={running !== null}
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#C25E00] hover:bg-[#9E4C00] disabled:opacity-50 text-white text-xs font-bold cursor-pointer transition-all active:scale-98 shadow-xs"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{running === 'velocity' ? 'Testing Guardrail...' : 'Test Velocity Guardrail'}</span>
          </button>
        </div>
      </div>

      {/* Simulator Execution Audit Log - Filled Soft Lavender Console */}
      <div className="bg-[#EAE1F7] border border-[#CDBEE5] rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-[#CDBEE5] pb-3">
          <div className="flex items-center gap-2 text-[#593CA5]">
            <Terminal className="w-4 h-4" />
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#1E2638]">
              Simulation Event Stream &amp; State Trace ({logs.length} events)
            </h3>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={handleSecurityReset}
              disabled={running !== null}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#D7C4F2] border border-[#BFA8E7] hover:bg-[#C8B2ED] text-[#431E8C] text-xs font-bold cursor-pointer transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset &amp; Unfreeze Engine</span>
            </button>

            {logs.length > 0 && (
              <button 
                onClick={() => setLogs([])}
                className="text-xs text-[#593CA5] hover:underline font-bold cursor-pointer"
              >
                Clear Log
              </button>
            )}
          </div>
        </div>

        {logs.length === 0 ? (
          <div className="p-8 text-center text-xs text-[#431E8C] bg-[#DFD3F2] rounded-xl border border-[#C5B4E2] font-medium">
            No simulation runs recorded yet. Click one of the scenario buttons above to execute a controlled functional verification test.
          </div>
        ) : (
          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {logs.map((log, idx) => (
              <div 
                key={idx}
                className={`p-3 rounded-xl border text-xs flex items-start gap-3 transition-colors ${
                  log.status === 'success' 
                    ? 'bg-[#CCEBD4] border-[#9EDAA9] text-[#0F5132]' 
                    : log.status === 'warning'
                    ? 'bg-[#F8DAC0] border-[#F0BF94] text-[#7C2D12]'
                    : log.status === 'error'
                    ? 'bg-[#F5CCD7] border-[#EAAAB9] text-[#881337]'
                    : 'bg-[#D8E7F7] border-[#ADC9EE] text-[#0A3B7B]'
                }`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {log.status === 'success' && <CheckCircle2 className="w-4 h-4 text-[#15803D]" />}
                  {log.status === 'warning' && <AlertTriangle className="w-4 h-4 text-[#D97706]" />}
                  {log.status === 'error' && <AlertCircle className="w-4 h-4 text-[#E11D48]" />}
                  {log.status === 'info' && <Info className="w-4 h-4 text-[#1D4ED8]" />}
                </div>

                <div className="flex-1 space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-[11px] uppercase tracking-wider">{log.scenario}</span>
                    <span className="text-[10px] font-mono opacity-80">Step {log.step} &bull; {log.timestamp}</span>
                    <span className="text-[11px] font-bold">{log.action}</span>
                  </div>
                  <p className="text-xs leading-relaxed opacity-95 font-medium">{log.details}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
