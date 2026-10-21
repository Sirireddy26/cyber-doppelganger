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
      {/* Top Banner / Privacy Guarantee - Executive Dark Violet Card */}
      <div className="bg-[#120D1F] border border-[#271C3D] rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#8B5CF6]" />
            <h2 className="text-base font-extrabold text-white tracking-tight">
              Interactive Biometric Capture Arena
            </h2>
            <span className="px-3 py-0.5 rounded-full text-[11px] font-bold bg-[#1E1436] text-[#C4B5FD] border border-[#3E296A]">
              Live Kinematics
            </span>
          </div>
          <p className="text-xs text-[#9D8EB9] leading-relaxed max-w-2xl font-medium">
            Type the reference sentence or move your mouse across the tracking zone below. Keystroke dwell times, flight latencies, and mouse dynamics are calculated locally. Raw characters are strictly discarded.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-[#1A1230] px-4 py-2.5 rounded-xl border border-[#3E296A] text-xs text-[#C4B5FD] font-bold shadow-xs">
          <Lock className="w-4 h-4 text-[#8B5CF6]" />
          <span>Zero-Content Privacy (No Text Stored)</span>
        </div>
      </div>

      {/* Main Interactive Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Column: Keystroke Dynamics */}
        <div className="bg-[#120D1F] border border-[#271C3D] rounded-2xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-[#271C3D] pb-3">
            <div className="flex items-center gap-2 text-[#8B5CF6]">
              <Keyboard className="w-5 h-5" />
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-white">
                1. Keystroke Dynamics Collector
              </h3>
            </div>
            <button 
              onClick={() => setActivePhraseIndex((prev) => (prev + 1) % SAMPLE_PHRASES.length)}
              className="text-xs text-[#A78BFA] font-bold hover:text-white cursor-pointer transition-colors"
            >
              Cycle Prompt Phrase
            </button>
          </div>

          <div className="p-4 rounded-xl bg-[#181228] border border-[#382759] text-xs text-white font-mono leading-relaxed select-none shadow-xs">
            <span className="text-[#8B5CF6] font-sans block text-[10px] uppercase font-bold mb-1">REFERENCE TARGET PHRASE:</span>
            {SAMPLE_PHRASES[activePhraseIndex]}
          </div>

          <div className="space-y-1.5">
            <label className="text-xs text-[#9D8EB9] font-bold block">
              Type Here (Keystroke Timestamps Measured in Real-Time):
            </label>
            <input 
              type="text"
              value={typedText}
              onChange={(e) => setTypedText(e.target.value)}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
              placeholder="Start typing naturally to generate physical timing..."
              className="w-full bg-[#0B0813] border border-[#382759] rounded-xl px-4 py-3 text-xs text-white placeholder-[#6B5D88] focus:outline-none focus:border-[#8B5CF6] focus:ring-2 focus:ring-[#8B5CF6]/25 font-mono transition-all shadow-inner"
            />
          </div>

          {/* Keystroke Readout Meters - Dark Obsidian with Violet Accents */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
            {/* Dwell Time */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Dwell Time: Duration a key remains depressed from KeyDown to KeyUp in milliseconds (ms)."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Dwell Time</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {metrics.dwellTimeMs > 0 ? `${metrics.dwellTimeMs}ms` : '--'}
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Hold interval</span>
            </div>

            {/* Flight Time */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Flight Time: Latency elapsed between releasing one key and pressing the next key in milliseconds (ms)."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Flight Time</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {metrics.flightTimeMs > 0 ? `${metrics.flightTimeMs}ms` : '--'}
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Latency</span>
            </div>

            {/* Typing Speed */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Typing Speed: Keystroke throughput expressed as Words Per Minute (WPM)."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Speed</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {metrics.typingSpeedWpm > 0 ? `${metrics.typingSpeedWpm} WPM` : '--'}
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Cadence</span>
            </div>

            {/* Backspace Rate */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Backspace Rate: Ratio of error-correction keystrokes to total keystrokes (%)."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Correction</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {Math.round(metrics.backspaceRate * 100)}%
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Backspace ratio</span>
            </div>
          </div>
        </div>

        {/* Right Column: Mouse Kinematics Tracker */}
        <div className="bg-[#120D1F] border border-[#271C3D] rounded-2xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-[#271C3D] pb-3">
            <div className="flex items-center gap-2 text-[#8B5CF6]">
              <MousePointer className="w-5 h-5" />
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-white">
                2. Mouse Kinematics Tracker
              </h3>
            </div>
            <span className="text-xs text-[#C4B5FD] font-bold">
              Recorded Clicks: <span className="text-white font-mono">{metrics.mouseClickCount}</span>
            </span>
          </div>

          {/* Interactive Mouse Tracking Pad */}
          <div 
            ref={trackingAreaRef}
            onMouseMove={handleMouseMove}
            onClick={handleMouseClick}
            className="h-36 rounded-xl bg-[#0E0A1A] border-2 border-dashed border-[#382759] hover:border-[#8B5CF6] flex flex-col items-center justify-center gap-2 cursor-crosshair select-none transition-colors shadow-inner"
          >
            <Activity className="w-6 h-6 text-[#8B5CF6] animate-pulse" />
            <span className="text-xs font-bold text-white">
              Move cursor &amp; click within this box to measure spatial acceleration &amp; velocity
            </span>
            <span className="text-[11px] font-mono text-[#8E7FA8] font-medium">
              Distance traversed: <span className="text-[#C4B5FD]">{metrics.mouseDistancePx} px</span>
            </span>
          </div>

          {/* Mouse Readout Meters */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
            {/* Velocity */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Mouse Velocity: Mean displacement speed across movement vectors in pixels per second (px/s)."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Velocity</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {metrics.mouseSpeedPps > 0 ? `${metrics.mouseSpeedPps} px/s` : '--'}
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Speed</span>
            </div>

            {/* Acceleration */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Acceleration: Second derivative of position with respect to time in px/s²."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Acceleration</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {metrics.mouseAcceleration > 0 ? `${metrics.mouseAcceleration} px/s²` : '--'}
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Rate change</span>
            </div>

            {/* Jitter */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Jitter: Normalized velocity standard deviation (unitless)."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Jitter</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {metrics.mouseJitter > 0 ? metrics.mouseJitter.toFixed(2) : '--'}
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Noise index</span>
            </div>

            {/* Path Efficiency */}
            <div 
              className="p-3.5 rounded-xl bg-[#161026] border border-[#2D214C] text-center cursor-help shadow-xs"
              title="Path Efficiency: Ratio of direct Euclidean straight-line distance to actual distance travelled (0.0 to 1.0)."
            >
              <div className="flex items-center justify-center gap-1 text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Efficiency</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <span className="text-sm font-extrabold font-mono text-white mt-1 block">
                {metrics.movementEfficiency ? metrics.movementEfficiency.toFixed(2) : '--'}
              </span>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Linear ratio</span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Controls Toolbar */}
      <div className="bg-[#120D1F] border border-[#271C3D] rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
        <div className="flex flex-wrap items-center gap-3">
          {/* Primary Verify Button */}
          <button 
            onClick={handleVerify}
            disabled={verifying}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] disabled:opacity-50 text-white text-xs font-bold shadow-[0_0_16px_rgba(124,58,237,0.35)] cursor-pointer transition-all active:scale-98"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{verifying ? 'Evaluating Model...' : 'Verify Biometric Identity Now'}</span>
          </button>

          {/* Buffer Ingestion Button */}
          <button 
            onClick={handleIngestToBuffer}
            disabled={ingesting}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#1E1436] hover:bg-[#2B1B4D] disabled:opacity-50 text-[#C4B5FD] border border-[#432C73] text-xs font-bold cursor-pointer transition-all active:scale-98"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{ingesting ? 'Buffering Observation...' : 'Ingest Snapshot to Candidate Buffer'}</span>
          </button>

          {/* Reset Button */}
          <button 
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-[#161026] border border-[#382759] hover:bg-[#22163B] text-[#9D8EB9] hover:text-white text-xs font-bold cursor-pointer transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#8B5CF6]" />
            <span>Reset Arena</span>
          </button>
        </div>

        <div className="text-xs font-mono text-[#8E7FA8]">
          Inference Engine: <span className="text-[#C4B5FD] font-extrabold">Isolation Forest v1.0.0</span> (Threshold: +0.0327)
        </div>
      </div>

      {/* User Feedback Notice Banner */}
      {feedbackMessage && (
        <div className={`p-4 rounded-xl border text-xs flex items-center gap-3 font-bold shadow-md ${
          feedbackMessage.type === 'success' 
            ? 'bg-[#121E19] border-[#224A35] text-[#34D399]' 
            : feedbackMessage.type === 'error'
            ? 'bg-[#291122] border-[#5A1D46] text-[#F472B6]'
            : 'bg-[#181228] border-[#382759] text-[#C4B5FD]'
        }`}>
          {feedbackMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-[#34D399]" />
          ) : (
            <AlertTriangle className="w-4 h-4 flex-shrink-0 text-[#F472B6]" />
          )}
          <span>{feedbackMessage.text}</span>
        </div>
      )}

      {/* Live Verification Result Card */}
      {verificationResult && (
        <div className={`border rounded-2xl p-6 space-y-4 shadow-xl ${
          verificationResult.decision === 'NORMAL_BEHAVIOUR'
            ? 'bg-[#101915] border-[#1E432A]'
            : 'bg-[#1F0E1B] border-[#4A1837]'
        }`}>
          <div className="flex items-center justify-between border-b border-[#2C1D42] pb-3">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#8B5CF6]" />
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-white">
                Machine Learning Verification Verdict
              </h3>
            </div>
            <span className="text-xs font-mono text-[#8E7FA8] font-medium">
              Evaluated at: {new Date(verificationResult.created_at || Date.now()).toLocaleTimeString()}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Status Verdict */}
            <div className={`p-4 rounded-xl space-y-1 shadow-xs border ${
              verificationResult.decision === 'NORMAL_BEHAVIOUR'
                ? 'bg-[#13231B] border-[#1F4930]'
                : 'bg-[#2D1226] border-[#5E1E49]'
            }`}>
              <span className={`text-[10px] uppercase font-bold ${
                verificationResult.decision === 'NORMAL_BEHAVIOUR' ? 'text-[#34D399]' : 'text-[#F472B6]'
              }`}>Verification Verdict</span>
              <div className="flex items-center gap-2 pt-1">
                {verificationResult.decision === 'NORMAL_BEHAVIOUR' ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-[#34D399]" />
                    <span className="text-xs font-extrabold text-[#34D399]">AUTHENTICATED (NORMAL)</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-4 h-4 text-[#F472B6]" />
                    <span className="text-xs font-extrabold text-[#F472B6]">ANOMALOUS DEVIATION</span>
                  </>
                )}
              </div>
            </div>

            {/* Model Decision Score */}
            <div 
              className="p-4 rounded-xl space-y-1 cursor-help shadow-xs border bg-[#161026] border-[#2D214C]"
              title="Raw Isolation Forest decision function score. Values above the threshold (+0.0327) indicate inliers consistent with the genuine user reference profile."
            >
              <div className="flex items-center justify-between text-[10px] uppercase font-bold text-[#A78BFA]">
                <span>Model Decision Score</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <div className="flex items-baseline gap-2 pt-1 font-mono text-xs">
                <span className={`text-base font-extrabold ${
                  verificationResult.raw_score >= verificationResult.threshold ? 'text-[#34D399]' : 'text-[#F472B6]'
                }`}>
                  {verificationResult.raw_score > 0 ? `+${verificationResult.raw_score.toFixed(4)}` : verificationResult.raw_score.toFixed(4)}
                </span>
                <span className="text-[#8E7FA8] font-medium">vs thresh {verificationResult.threshold.toFixed(4)}</span>
              </div>
            </div>

            {/* Anomaly Score */}
            <div 
              className="p-4 rounded-xl bg-[#161026] border border-[#2D214C] space-y-1 cursor-help shadow-xs"
              title="Anomaly score is defined mathematically as -raw_score."
            >
              <div className="flex items-center justify-between text-[10px] text-[#A78BFA] uppercase font-bold">
                <span>Anomaly Score</span>
                <HelpCircle className="w-3 h-3 text-[#8B5CF6]" />
              </div>
              <div className="flex items-baseline gap-2 pt-1">
                <span className="text-base font-extrabold font-mono text-white">
                  {verificationResult.anomaly_score.toFixed(4)}
                </span>
                <span className="text-[11px] text-[#8E7FA8] font-medium">(-raw)</span>
              </div>
            </div>

            {/* Model Provenance */}
            <div className="p-4 rounded-xl bg-[#161026] border border-[#2D214C] space-y-1 shadow-xs">
              <span className="text-[10px] text-[#8E7FA8] uppercase font-bold">Algorithm &amp; Version</span>
              <p className="text-xs font-mono font-bold text-white pt-1">
                {verificationResult.model_type} (v{verificationResult.model_version})
              </p>
              <span className="text-[10px] text-[#8E7FA8] font-medium">Calibrated baseline</span>
            </div>
          </div>

          <div className="text-xs text-[#C4B5FD] bg-[#161026] border border-[#382759] p-3 rounded-xl flex items-start gap-2">
            <Info className="w-4 h-4 text-[#8B5CF6] flex-shrink-0 mt-0.5" />
            <span>
              <strong>Scientific Verification Note:</strong> Behavioural distance assesses deviation from baseline typing and cursor dynamics. An anomaly score indicates physical deviation, not conclusive forensic proof of an attacker.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
