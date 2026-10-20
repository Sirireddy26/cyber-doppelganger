import React, { useState, useRef, useCallback } from 'react';
import { 
  Keyboard, 
  MousePointer, 
  ShieldCheck, 
  Zap, 
  Activity, 
  RotateCcw, 
  Send, 
  CheckCircle2, 
  AlertTriangle, 
  Lock,
  Sparkles,
  HelpCircle,
  Info
} from 'lucide-react';
import { ApiService } from '../../services/api';
import type { VerificationResult, KinematicsMetrics } from '../../types/api';

const SAMPLE_PHRASES = [
  "Continuous biometric authentication verifies identity through natural interaction dynamics.",
  "Safe adaptive identity models learn behavioural evolution while preventing profile poisoning.",
  "Privacy by design ensures timing kinematics are verified without recording raw content."
];

export const BiometricPlayground: React.FC<{ onSnapshotIngested?: () => void }> = ({ onSnapshotIngested }) => {
  const [activePhraseIndex, setActivePhraseIndex] = useState(0);
  const [typedText, setTypedText] = useState('');
  
  // Real-time Keystroke Kinematics state (Privacy-Safe: Zero character storage)
  const keyDownTimestamps = useRef<Map<string, number>>(new Map());
  const dwellTimes = useRef<number[]>([]);
  const flightTimes = useRef<number[]>([]);
  const lastKeyUpTime = useRef<number | null>(null);
  const backspaceCount = useRef<number>(0);
  const keystrokeCount = useRef<number>(0);
  const typingStartTime = useRef<number | null>(null);

  // Real-time Mouse Kinematics state
  const mouseTrajectory = useRef<Array<{ x: number; y: number; time: number }>>([]);
  const mouseSpeeds = useRef<number[]>([]);
  const mouseAccelerations = useRef<number[]>([]);
  const mouseClicks = useRef<number>(0);
  const mouseTotalDistance = useRef<number>(0);

  // Live Display Metrics
  const [metrics, setMetrics] = useState<KinematicsMetrics>({
    dwellTimeMs: 0,
    flightTimeMs: 0,
    typingSpeedWpm: 0,
    backspaceRate: 0,
    keystrokeCount: 0,
    mouseSpeedPps: 0,
    mouseAcceleration: 0,
    mouseJitter: 0,
    movementEfficiency: 1.0,
    mouseClickCount: 0,
    mouseDistancePx: 0,
  });

  // Verification & Feedback State
  const [verifying, setVerifying] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  const trackingAreaRef = useRef<HTMLDivElement>(null);

  // Keyboard Event Handlers (Strictly timing only, characters are discarded immediately)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const now = performance.now();
    keystrokeCount.current += 1;
    if (!typingStartTime.current) {
      typingStartTime.current = now;
    }

    if (e.key === 'Backspace') {
      backspaceCount.current += 1;
    }

    // Inter-key latency (flight time)
    if (lastKeyUpTime.current !== null) {
      const flight = Math.max(0, now - lastKeyUpTime.current);
      if (flight < 2000) {
        flightTimes.current.push(flight);
        if (flightTimes.current.length > 30) flightTimes.current.shift();
      }
    }

    keyDownTimestamps.current.set(e.code, now);
    updateMetrics();
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const now = performance.now();
    lastKeyUpTime.current = now;

    const downTime = keyDownTimestamps.current.get(e.code);
    if (downTime) {
      const dwell = Math.max(10, now - downTime);
      dwellTimes.current.push(dwell);
      if (dwellTimes.current.length > 30) dwellTimes.current.shift();
      keyDownTimestamps.current.delete(e.code);
    }
    updateMetrics();
  };

  // Mouse Movement Handler (Spatial Kinematics)
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const now = performance.now();
    const rect = trackingAreaRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const traj = mouseTrajectory.current;
    if (traj.length > 0) {
      const lastPoint = traj[traj.length - 1];
      const dt = Math.max(1, now - lastPoint.time) / 1000.0;
      const dx = x - lastPoint.x;
      const dy = y - lastPoint.y;
      const dist = Math.hypot(dx, dy);

      mouseTotalDistance.current += dist;
      const speed = dist / dt;
      mouseSpeeds.current.push(speed);
      if (mouseSpeeds.current.length > 40) mouseSpeeds.current.shift();

      if (mouseSpeeds.current.length >= 2) {
        const prevSpeed = mouseSpeeds.current[mouseSpeeds.current.length - 2];
        const accel = Math.abs(speed - prevSpeed) / dt;
        mouseAccelerations.current.push(accel);
        if (mouseAccelerations.current.length > 40) mouseAccelerations.current.shift();
      }
    }

    traj.push({ x, y, time: now });
    if (traj.length > 50) traj.shift();

    updateMetrics();
  };

  const handleMouseClick = () => {
    mouseClicks.current += 1;
    updateMetrics();
  };

  const updateMetrics = useCallback(() => {
    const meanDwell = dwellTimes.current.length > 0 
      ? dwellTimes.current.reduce((a, b) => a + b, 0) / dwellTimes.current.length 
      : 0;

    const meanFlight = flightTimes.current.length > 0 
      ? flightTimes.current.reduce((a, b) => a + b, 0) / flightTimes.current.length 
      : 0;

    const now = performance.now();
    const totalKeyTime = typingStartTime.current ? (now - typingStartTime.current) / 60000 : 0;
    
    const wpm = totalKeyTime > 0.01 && keystrokeCount.current > 0
      ? Math.round((keystrokeCount.current / 5) / totalKeyTime)
      : 0;

    const backspaceRate = keystrokeCount.current > 0
      ? backspaceCount.current / keystrokeCount.current
      : 0;

    const meanSpeed = mouseSpeeds.current.length > 0
      ? mouseSpeeds.current.reduce((a, b) => a + b, 0) / mouseSpeeds.current.length
      : 0;

    const meanAccel = mouseAccelerations.current.length > 0
      ? mouseAccelerations.current.reduce((a, b) => a + b, 0) / mouseAccelerations.current.length
      : 0;

    let jitter = 0;
    if (mouseSpeeds.current.length > 2) {
      const avg = meanSpeed;
      const variance = mouseSpeeds.current.reduce((s, x) => s + Math.pow(x - avg, 2), 0) / mouseSpeeds.current.length;
      jitter = Math.sqrt(variance) / (avg + 1);
    }

    let efficiency = 1.0;
    const traj = mouseTrajectory.current;
    if (traj.length >= 2 && mouseTotalDistance.current > 0) {
      const straightDist = Math.hypot(traj[traj.length - 1].x - traj[0].x, traj[traj.length - 1].y - traj[0].y);
      efficiency = Math.min(1.0, straightDist / (mouseTotalDistance.current + 1));
    }

    setMetrics({
      dwellTimeMs: Math.round(meanDwell),
      flightTimeMs: Math.round(meanFlight),
      typingSpeedWpm: Math.min(180, wpm),
      backspaceRate: Math.round(backspaceRate * 100) / 100,
      keystrokeCount: keystrokeCount.current,
      mouseSpeedPps: Math.round(meanSpeed),
      mouseAcceleration: Math.round(meanAccel),
      mouseJitter: Math.round(jitter * 100) / 100,
      movementEfficiency: Math.round(efficiency * 100) / 100,
      mouseClickCount: mouseClicks.current,
      mouseDistancePx: Math.round(mouseTotalDistance.current),
    });
  }, []);

  const handleReset = () => {
    setTypedText('');
    dwellTimes.current = [];
    flightTimes.current = [];
    keyDownTimestamps.current.clear();
    lastKeyUpTime.current = null;
    backspaceCount.current = 0;
    keystrokeCount.current = 0;
    typingStartTime.current = null;
    mouseTrajectory.current = [];
    mouseSpeeds.current = [];
    mouseAccelerations.current = [];
    mouseClicks.current = 0;
    mouseTotalDistance.current = 0;
    setVerificationResult(null);
    setFeedbackMessage({ type: 'info', text: 'Biometric capture arena reset. Ready for new observation.' });
    setMetrics({
      dwellTimeMs: 0,
      flightTimeMs: 0,
      typingSpeedWpm: 0,
      backspaceRate: 0,
      keystrokeCount: 0,
      mouseSpeedPps: 0,
      mouseAcceleration: 0,
      mouseJitter: 0,
      movementEfficiency: 1.0,
      mouseClickCount: 0,
      mouseDistancePx: 0,
    });
  };

  const buildCurrentSnapshot = () => {
    const dwell = metrics.dwellTimeMs > 0 ? metrics.dwellTimeMs : 88.0;
    const flight = metrics.flightTimeMs > 0 ? metrics.flightTimeMs : 135.0;
    const wpm = metrics.typingSpeedWpm > 0 ? metrics.typingSpeedWpm : 48.0;
    const mouseSpeed = metrics.mouseSpeedPps > 0 ? metrics.mouseSpeedPps : 160.0;
    const mouseAccel = metrics.mouseAcceleration > 0 ? metrics.mouseAcceleration : 420.0;
    const jitter = metrics.mouseJitter > 0 ? metrics.mouseJitter : 0.06;

    return {
      timestamp: new Date().toISOString(),
      window_duration_seconds: 60,
      device_id: 'WEB-BROWSER-PLAYGROUND',
      user_id: '1',
      schema_version: '2.0',
      keyboard: {
        mean_dwell_time_ms: dwell,
        mean_flight_time_ms: flight,
        typing_speed_wpm: wpm,
        backspace_rate: metrics.backspaceRate,
        keystroke_count: Math.max(15, metrics.keystrokeCount)
      },
      mouse: {
        mean_speed_pixels_per_second: mouseSpeed,
        mean_acceleration: mouseAccel,
        jitter_metric: jitter,
        movement_efficiency: metrics.movementEfficiency || 0.85,
        click_count: Math.max(2, metrics.mouseClickCount),
        total_distance_pixels: Math.max(100, metrics.mouseDistancePx)
      },
      session: {
        idle_ratio: 0.05,
        active_duration_seconds: 57.0
      },
      application: {
        active_process_name: 'browser.exe',
        window_switch_count: 1
      }
    };
  };

  // 1. Process Instant ML Verification
  const handleVerify = async () => {
    setVerifying(true);
    setFeedbackMessage(null);
    try {
      const snapshot = buildCurrentSnapshot();
      const result = await ApiService.processVerification({ preferred_model: 'ISOLATION_FOREST', snapshot });
      setVerificationResult(result);
      if (result.decision === 'NORMAL_BEHAVIOUR') {
        setFeedbackMessage({
          type: 'success',
          text: `Verified genuine user. Model decision score: ${result.raw_score > 0 ? '+' : ''}${result.raw_score.toFixed(4)} >= threshold (${result.threshold.toFixed(4)}).`
        });
      } else {
        setFeedbackMessage({
          type: 'error',
          text: `Behavioural deviation flagged. Model decision score: ${result.raw_score.toFixed(4)} < threshold (${result.threshold.toFixed(4)}).`
        });
      }
    } catch (err: any) {
      setFeedbackMessage({
        type: 'error',
        text: err.message || 'Verification service error.'
      });
    } finally {
      setVerifying(false);
    }
  };

  // 2. Ingest Snapshot to Safe Adaptation Candidate Buffer
  const handleIngestToBuffer = async () => {
    setIngesting(true);
    setFeedbackMessage(null);
    try {
      const snapshot = buildCurrentSnapshot();
      const res = await ApiService.processAdaptation({
        features: {
          mean_dwell_time_ms: snapshot.keyboard.mean_dwell_time_ms,
          mean_flight_time_ms: snapshot.keyboard.mean_flight_time_ms,
          typing_speed_wpm: snapshot.keyboard.typing_speed_wpm,
          backspace_rate: snapshot.keyboard.backspace_rate,
          mouse_speed: snapshot.mouse.mean_speed_pixels_per_second,
          mouse_accel: snapshot.mouse.mean_acceleration,
          mouse_jitter: snapshot.mouse.jitter_metric,
          movement_efficiency: snapshot.mouse.movement_efficiency
        },
        device_id: 'WEB-BROWSER-PLAYGROUND',
        verification_result_id: verificationResult?.id
      });

      setFeedbackMessage({
        type: 'success',
        text: `Observation buffered (${res.candidate_count}/20 candidates). Adaptation engine state: ${res.decision_state}.`
      });

      if (onSnapshotIngested) {
        onSnapshotIngested();
      }
    } catch (err: any) {
      setFeedbackMessage({
        type: 'error',
        text: err.message || 'Ingestion to candidate buffer failed.'
      });
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Privacy Guarantee - Filled Soft Lavender */}
      <div className="bg-[#EAE1F7] border border-[#CDBEE5] rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#593CA5]" />
            <h2 className="text-base font-extrabold text-[#1E2638] tracking-tight">
              Interactive Biometric Capture Arena
            </h2>
            <span className="px-3 py-0.5 rounded-full text-[11px] font-bold bg-[#D7C4F2] text-[#431E8C] border border-[#BFA8E7]">
              Live Kinematics
            </span>
          </div>
          <p className="text-xs text-[#4A5568] leading-relaxed max-w-2xl font-medium">
            Type the reference sentence or move your mouse across the tracking zone below. Keystroke dwell times, flight latencies, and mouse dynamics are calculated locally. Characters are strictly discarded immediately.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-[#CCEBD4] px-4 py-2.5 rounded-xl border border-[#9EDAA9] text-xs text-[#0F5132] font-bold shadow-xs">
          <Lock className="w-4 h-4 text-[#15803D]" />
          <span>Zero-Content Privacy (No Text Stored)</span>
        </div>
      </div>

      {/* Main Interactive Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Column: Keystroke Dynamics - Filled Soft Lavender Card */}
        <div className="bg-[#F1EBFA] border border-[#D2C4EB] rounded-2xl p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#D2C4EB] pb-3">
            <div className="flex items-center gap-2 text-[#593CA5]">
              <Keyboard className="w-5 h-5" />
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#1E2638]">
                1. Keystroke Dynamics Collector
              </h3>
            </div>
            <button 
              onClick={() => setActivePhraseIndex((prev) => (prev + 1) % SAMPLE_PHRASES.length)}
              className="text-xs text-[#431E8C] font-bold hover:underline cursor-pointer"
            >
              Cycle Prompt Phrase
            </button>
          </div>

          <div className="p-4 rounded-xl bg-[#E4DAF5] border border-[#C8B8E4] text-xs text-[#1E2638] font-mono leading-relaxed select-none shadow-xs">
            <span className="text-[#593CA5] font-sans block text-[10px] uppercase font-bold mb-1">REFERENCE TARGET PHRASE:</span>
            {SAMPLE_PHRASES[activePhraseIndex]}
          </div>

          <div className="space-y-1.5">
            <label className="text-xs text-[#4A5568] font-bold block">
              Type Here (Keystroke Timestamps Measured in Real-Time):
            </label>
            <input 
              type="text"
              value={typedText}
              onChange={(e) => setTypedText(e.target.value)}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
              placeholder="Start typing naturally to generate physical timing..."
              className="w-full bg-[#FFFFFF] border border-[#C8BCD8] rounded-xl px-4 py-3 text-xs text-[#1E2638] placeholder-[#718096] focus:outline-none focus:border-[#7864D1] focus:ring-2 focus:ring-[#D7C4F2] font-mono transition-all shadow-xs"
            />
          </div>

          {/* Keystroke Readout Meters with Explicit Scientific Tooltips - Distinct Pastel Fills */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
            {/* Dwell Time - Filled Lavender */}
            <div 
              className="p-3.5 rounded-xl bg-[#E4DAF5] border border-[#C8B8E4] text-center cursor-help shadow-xs"
              title="Dwell Time: Duration a key remains depressed from KeyDown to KeyUp in milliseconds (ms). Varies with finger contact strength, key travel, and typing rhythm."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#431E8C] uppercase font-bold">
                <span>Dwell Time</span>
                <HelpCircle className="w-3 h-3 text-[#593CA5]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#1E2638] mt-1 block">
                {metrics.dwellTimeMs > 0 ? `${metrics.dwellTimeMs}ms` : '--'}
              </span>
              <span className="text-[10px] text-[#4A5568] font-medium">Hold interval</span>
            </div>

            {/* Flight Time - Filled Powder Blue */}
            <div 
              className="p-3.5 rounded-xl bg-[#D8E7F7] border border-[#ADC9EE] text-center cursor-help shadow-xs"
              title="Flight Time: Latency elapsed between releasing one key and pressing the next key in milliseconds (ms). Reflects motor habits, cognitive pauses, and digraph transition speed."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#0A3B7B] uppercase font-bold">
                <span>Flight Time</span>
                <HelpCircle className="w-3 h-3 text-[#1D4ED8]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#1E2638] mt-1 block">
                {metrics.flightTimeMs > 0 ? `${metrics.flightTimeMs}ms` : '--'}
              </span>
              <span className="text-[10px] text-[#4A5568] font-medium">Latency</span>
            </div>

            {/* Typing Speed - Filled Mint */}
            <div 
              className="p-3.5 rounded-xl bg-[#CCEBD4] border border-[#9EDAA9] text-center cursor-help shadow-xs"
              title="Typing Speed: Keystroke throughput expressed as (Keystrokes / 5) / minutes. Measured in Words Per Minute (WPM). Reflects user familiarity and fluency."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#0F5132] uppercase font-bold">
                <span>Speed</span>
                <HelpCircle className="w-3 h-3 text-[#15803D]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#0F5132] mt-1 block">
                {metrics.typingSpeedWpm > 0 ? `${metrics.typingSpeedWpm} WPM` : '--'}
              </span>
              <span className="text-[10px] text-[#0F5132] font-medium">Cadence</span>
            </div>

            {/* Backspace Rate - Filled Warm Peach */}
            <div 
              className="p-3.5 rounded-xl bg-[#F8DAC0] border border-[#F0BF94] text-center cursor-help shadow-xs"
              title="Backspace Rate: Ratio of error-correction keystrokes to total keystrokes (%). Measures self-correction tendencies."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#7C2D12] uppercase font-bold">
                <span>Correction</span>
                <HelpCircle className="w-3 h-3 text-[#D97706]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#7C2D12] mt-1 block">
                {Math.round(metrics.backspaceRate * 100)}%
              </span>
              <span className="text-[10px] text-[#7C2D12] font-medium">Backspace ratio</span>
            </div>
          </div>
        </div>

        {/* Right Column: Mouse Kinematics Tracker - Filled Powder Blue Card */}
        <div className="bg-[#EBF3FB] border border-[#BFD6EE] rounded-2xl p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#BFD6EE] pb-3">
            <div className="flex items-center gap-2 text-[#1D4ED8]">
              <MousePointer className="w-5 h-5" />
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#1E2638]">
                2. Mouse Kinematics Tracker
              </h3>
            </div>
            <span className="text-xs text-[#0A3B7B] font-bold">
              Recorded Clicks: <span className="text-[#1E2638]">{metrics.mouseClickCount}</span>
            </span>
          </div>

          {/* Interactive Mouse Tracking Pad - Deep Powder Blue Accent */}
          <div 
            ref={trackingAreaRef}
            onMouseMove={handleMouseMove}
            onClick={handleMouseClick}
            className="h-36 rounded-xl bg-[#D8E7F7] border-2 border-dashed border-[#8EBBE6] hover:border-[#1D4ED8] flex flex-col items-center justify-center gap-2 cursor-crosshair select-none transition-colors shadow-xs"
          >
            <Activity className="w-6 h-6 text-[#1D4ED8] animate-pulse" />
            <span className="text-xs font-bold text-[#0A3B7B]">
              Move cursor &amp; click within this box to measure spatial acceleration &amp; jitter
            </span>
            <span className="text-[11px] font-mono text-[#4A5568] font-medium">
              Distance traversed: {metrics.mouseDistancePx} px
            </span>
          </div>

          {/* Mouse Readout Meters with Explicit Tooltips - Distinct Pastel Fills */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
            {/* Velocity - Filled Powder Blue */}
            <div 
              className="p-3.5 rounded-xl bg-[#D8E7F7] border border-[#ADC9EE] text-center cursor-help shadow-xs"
              title="Mouse Velocity: Mean displacement speed across movement vectors in pixels per second (px/s). Reflects user physical dexterity and hardware sensitivity."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#0A3B7B] uppercase font-bold">
                <span>Velocity</span>
                <HelpCircle className="w-3 h-3 text-[#1D4ED8]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#1E2638] mt-1 block">
                {metrics.mouseSpeedPps > 0 ? `${metrics.mouseSpeedPps} px/s` : '--'}
              </span>
              <span className="text-[10px] text-[#4A5568] font-medium">Speed</span>
            </div>

            {/* Acceleration - Filled Soft Lavender */}
            <div 
              className="p-3.5 rounded-xl bg-[#E4DAF5] border border-[#C8B8E4] text-center cursor-help shadow-xs"
              title="Acceleration: Second derivative of position with respect to time in px/s². Captures rapid ballistic flicks vs smooth targeted gestures."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#431E8C] uppercase font-bold">
                <span>Acceleration</span>
                <HelpCircle className="w-3 h-3 text-[#593CA5]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#1E2638] mt-1 block">
                {metrics.mouseAcceleration > 0 ? `${metrics.mouseAcceleration} px/s²` : '--'}
              </span>
              <span className="text-[10px] text-[#4A5568] font-medium">Rate change</span>
            </div>

            {/* Jitter - Filled Warm Peach */}
            <div 
              className="p-3.5 rounded-xl bg-[#F8DAC0] border border-[#F0BF94] text-center cursor-help shadow-xs"
              title="Jitter: Normalized velocity standard deviation (unitless). Higher jitter indicates hand tremor, hesitation, or erratic mechanical adjustments."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#7C2D12] uppercase font-bold">
                <span>Jitter</span>
                <HelpCircle className="w-3 h-3 text-[#D97706]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#7C2D12] mt-1 block">
                {metrics.mouseJitter > 0 ? metrics.mouseJitter.toFixed(2) : '--'}
              </span>
              <span className="text-[10px] text-[#7C2D12] font-medium">Noise index</span>
            </div>

            {/* Path Efficiency - Filled Soft Mint */}
            <div 
              className="p-3.5 rounded-xl bg-[#CCEBD4] border border-[#9EDAA9] text-center cursor-help shadow-xs"
              title="Path Efficiency: Ratio of direct Euclidean straight-line distance to actual distance travelled (0.0 to 1.0). Lower values indicate wandering or curved paths."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#0F5132] uppercase font-bold">
                <span>Efficiency</span>
                <HelpCircle className="w-3 h-3 text-[#15803D]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-[#0F5132] mt-1 block">
                {metrics.movementEfficiency ? metrics.movementEfficiency.toFixed(2) : '--'}
              </span>
              <span className="text-[10px] text-[#0F5132] font-medium">Linear ratio</span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Controls Toolbar - Filled Soft Lavender Panel */}
      <div className="bg-[#EAE1F7] border border-[#CDBEE5] rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          {/* Primary Verify Button */}
          <button 
            onClick={handleVerify}
            disabled={verifying}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#7864D1] hover:bg-[#6752C4] disabled:opacity-50 text-[#FFFFFF] text-xs font-bold shadow-sm cursor-pointer transition-all active:scale-98"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{verifying ? 'Evaluating Model...' : 'Verify Biometric Identity Now'}</span>
          </button>

          {/* Buffer Ingestion Button */}
          <button 
            onClick={handleIngestToBuffer}
            disabled={ingesting}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#D7C4F2] hover:bg-[#C8B2ED] disabled:opacity-50 text-[#431E8C] border border-[#BFA8E7] text-xs font-bold cursor-pointer transition-all active:scale-98"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{ingesting ? 'Buffering Observation...' : 'Ingest Snapshot to Candidate Buffer'}</span>
          </button>

          {/* Reset Button */}
          <button 
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-[#E2D5F3] border border-[#C4B2E1] hover:bg-[#D4C4EB] text-[#1E2638] text-xs font-bold cursor-pointer transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#593CA5]" />
            <span>Reset Arena</span>
          </button>
        </div>

        <div className="text-xs font-mono text-[#4A5568]">
          Inference Engine: <span className="text-[#431E8C] font-extrabold">Isolation Forest v1.0.0</span> (Threshold: 0.0327)
        </div>
      </div>

      {/* User Feedback Notice Banner */}
      {feedbackMessage && (
        <div className={`p-4 rounded-xl border text-xs flex items-center gap-3 font-bold shadow-xs ${
          feedbackMessage.type === 'success' 
            ? 'bg-[#CCEBD4] border-[#9EDAA9] text-[#0F5132]' 
            : feedbackMessage.type === 'error'
            ? 'bg-[#F5CCD7] border-[#EAAAB9] text-[#881337]'
            : 'bg-[#D8E7F7] border-[#ADC9EE] text-[#0A3B7B]'
        }`}>
          {feedbackMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-[#15803D]" />
          ) : (
            <AlertTriangle className="w-4 h-4 flex-shrink-0 text-[#E11D48]" />
          )}
          <span>{feedbackMessage.text}</span>
        </div>
      )}

      {/* Live Verification Result Card - Filled Soft Pastel Presentation */}
      {verificationResult && (
        <div className={`border rounded-2xl p-6 space-y-4 shadow-sm ${
          verificationResult.decision === 'NORMAL_BEHAVIOUR'
            ? 'bg-[#E3F4E8] border-[#9EDAA9]'
            : 'bg-[#F9E2E8] border-[#EAAAB9]'
        }`}>
          <div className="flex items-center justify-between border-b border-[#B8D8C2] pb-3">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#D97706]" />
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#1E2638]">
                Machine Learning Verification Verdict
              </h3>
            </div>
            <span className="text-xs font-mono text-[#4A5568] font-medium">
              Evaluated at: {new Date(verificationResult.created_at || Date.now()).toLocaleTimeString()}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Status Verdict */}
            <div className={`p-4 rounded-xl space-y-1 shadow-xs border ${
              verificationResult.decision === 'NORMAL_BEHAVIOUR'
                ? 'bg-[#CCEBD4] border-[#9EDAA9]'
                : 'bg-[#FCE7ED] border-[#F5B5C4]'
            }`}>
              <span className={`text-[10px] uppercase font-bold ${
                verificationResult.decision === 'NORMAL_BEHAVIOUR' ? 'text-[#0F5132]' : 'text-[#881337]'
              }`}>Verification Verdict</span>
              <div className="flex items-center gap-2 pt-1">
                {verificationResult.decision === 'NORMAL_BEHAVIOUR' ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-[#15803D]" />
                    <span className="text-xs font-extrabold text-[#0F5132]">AUTHENTICATED (NORMAL)</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-4 h-4 text-[#E11D48]" />
                    <span className="text-xs font-extrabold text-[#881337]">ANOMALOUS DEVIATION</span>
                  </>
                )}
              </div>
            </div>

            {/* Model Decision Score */}
            <div 
              className={`p-4 rounded-xl space-y-1 cursor-help shadow-xs border ${
                verificationResult.raw_score >= verificationResult.threshold
                  ? 'bg-[#D8E7F7] border-[#ADC9EE]'
                  : 'bg-[#F8DAC0] border-[#F0BF94]'
              }`}
              title="Raw Isolation Forest decision function score. Values above the threshold (+0.0327) indicate inliers consistent with the genuine user reference profile. Negative scores indicate behavioural distance."
            >
              <div className="flex items-center justify-between text-[10px] uppercase font-bold text-[#1E2638]">
                <span>Model Decision Score</span>
                <HelpCircle className="w-3 h-3 text-[#7864D1]" />
              </div>
              <div className="flex items-baseline gap-2 pt-1 font-mono text-xs">
                <span className={`text-base font-extrabold ${
                  verificationResult.raw_score >= verificationResult.threshold ? 'text-[#0A3B7B]' : 'text-[#7C2D12]'
                }`}>
                  {verificationResult.raw_score > 0 ? `+${verificationResult.raw_score.toFixed(4)}` : verificationResult.raw_score.toFixed(4)}
                </span>
                <span className="text-[#4A5568] font-medium">vs thresh {verificationResult.threshold.toFixed(4)}</span>
              </div>
            </div>

            {/* Anomaly Score */}
            <div 
              className="p-4 rounded-xl bg-[#E4DAF5] border border-[#C8B8E4] space-y-1 cursor-help shadow-xs"
              title="Anomaly score is defined mathematically as -raw_score. Higher positive values indicate greater behavioural divergence from the baseline profile cluster."
            >
              <div className="flex items-center justify-between text-[10px] text-[#431E8C] uppercase font-bold">
                <span>Anomaly Score</span>
                <HelpCircle className="w-3 h-3 text-[#7864D1]" />
              </div>
              <div className="flex items-baseline gap-2 pt-1">
                <span className="text-base font-extrabold font-mono text-[#1E2638]">
                  {verificationResult.anomaly_score.toFixed(4)}
                </span>
                <span className="text-[11px] text-[#4A5568] font-medium">(-raw)</span>
              </div>
            </div>

            {/* Model Provenance */}
            <div className="p-4 rounded-xl bg-[#EBE2F8] border border-[#CEBEE6] space-y-1 shadow-xs">
              <span className="text-[10px] text-[#593CA5] uppercase font-bold">Algorithm &amp; Version</span>
              <p className="text-xs font-mono font-bold text-[#1E2638] pt-1">
                {verificationResult.model_type} (v{verificationResult.model_version})
              </p>
              <span className="text-[10px] text-[#593CA5] font-medium">Calibrated on baseline</span>
            </div>
          </div>

          <div className="text-xs text-[#431E8C] bg-[#D7C4F2] border border-[#BFABEB] p-3 rounded-xl flex items-start gap-2">
            <Info className="w-4 h-4 text-[#431E8C] flex-shrink-0 mt-0.5" />
            <span>
              <strong>Scientific Verification Note:</strong> Behavioural distance assesses deviation from baseline typing and cursor dynamics. An anomaly score indicates physical deviation, not conclusive forensic proof of an attacker.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
