import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Layers, 
  FileText,
  Lock,
  Cpu,
  Sparkles,
  TrendingUp,
  Activity,
  Info
} from 'lucide-react';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { AdaptationDashboard } from './components/adaptation/AdaptationDashboard';
import { BiometricPlayground } from './components/biometrics/BiometricPlayground';
import { ResearchSimulators } from './components/research/ResearchSimulators';
import { ModelDiagnostics } from './components/telemetry/ModelDiagnostics';
import { ApiService } from './services/api';
import type { HealthResponse, SystemDiagnostics } from './types/api';

type DashboardTab = 'playground' | 'adaptation' | 'simulators' | 'telemetry';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DashboardTab>('playground');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [diagnostics, setDiagnostics] = useState<SystemDiagnostics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const [hData, dData] = await Promise.allSettled([
        ApiService.getHealth(),
        ApiService.getDiagnostics()
      ]);

      if (hData.status === 'fulfilled') {
        setHealth(hData.value);
      } else {
        setHealth(null);
        setError('Backend API is unreachable');
      }

      if (dData.status === 'fulfilled') {
        setDiagnostics(dData.value);
      } else {
        setDiagnostics(null);
      }

      setLastChecked(new Date().toLocaleTimeString());
    } catch (err: any) {
      setHealth(null);
      setDiagnostics(null);
      setError(err.message || 'Backend API is unreachable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleDataRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
    fetchHealth();
  };

  const isMlUp = diagnostics?.ml_service?.status === 'UP';
  const isDbUp = diagnostics?.database?.connected ?? (health ? true : false);
  const dbType = diagnostics?.database?.database_type || health?.database_type || 'H2';
  const isProfileInit = diagnostics?.trusted_profile?.ready ?? false;
  const profileVersion = diagnostics?.trusted_profile?.active_version || 'v1.0.0';
  const profileStatus = diagnostics?.trusted_profile?.status || 'INITIALIZED';
  const isAdaptFrozen = diagnostics?.adaptation_engine?.is_frozen ?? false;
  const isAgentActive = diagnostics?.agent_telemetry?.status === 'ACTIVE';

  return (
    <div className="min-h-screen bg-[#09070F] text-[#EDE9FE] flex flex-col font-sans selection:bg-[#7C3AED] selection:text-white">
      <Navbar 
        backendOnline={health ? true : error ? false : null} 
        mlOnline={diagnostics ? isMlUp : null}
        dbOnline={diagnostics ? isDbUp : null}
        profileStatus={isProfileInit ? `${profileVersion} (${profileStatus})` : null}
        adaptationFrozen={diagnostics ? isAdaptFrozen : null}
        loading={loading} 
        onRefresh={fetchHealth} 
      />

      <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 py-8 w-full space-y-6">
        {/* Project Header Banner - Executive Dark Violet Card */}
        <section className="bg-[#120D1F] border border-[#271C3D] rounded-2xl p-6 md:p-8 space-y-4 shadow-xl relative overflow-hidden">
          {/* Subtle Ambient Glow */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#7C3AED]/10 rounded-full blur-3xl -z-0 pointer-events-none" />

          <div className="relative z-10 inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#1F1538] text-[#C4B5FD] border border-[#3E296A] text-xs font-bold shadow-xs">
            <ShieldCheck className="w-4 h-4 text-[#8B5CF6]" />
            <span>Cyber Doppelgänger &bull; Behavioural Identity &amp; Safe Continuous Verification</span>
          </div>

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
                Continuous Behavioural Identity &amp; Safe Adaptation
              </h1>
              <p className="text-[#9D8EB9] text-xs md:text-sm max-w-3xl leading-relaxed mt-1.5 font-medium">
                Autonomous verification platform analyzing keystroke cadence and mouse kinematics in real time. Adapts to natural behavioural drift while actively preventing reference profile poisoning.
              </p>
            </div>

            {/* Overall Health Summary Badge */}
            <div className="flex items-center gap-3.5 p-3.5 rounded-xl bg-[#181228] border border-[#382759] self-start md:self-auto flex-shrink-0 shadow-md">
              <div className={`w-3.5 h-3.5 rounded-full flex-shrink-0 ${health ? 'bg-[#8B5CF6] shadow-[0_0_10px_#8B5CF6]' : 'bg-[#E11D48] shadow-[0_0_10px_#E11D48]'}`} />
              <div className="text-left">
                <div className="text-[10px] text-[#8E7FA8] uppercase font-bold tracking-wider">
                  System Health {lastChecked ? `(${lastChecked})` : ''}
                </div>
                <div className="text-xs font-extrabold text-white">
                  {loading ? 'CHECKING...' : health ? 'OPERATIONAL (200 OK)' : 'OFFLINE'}
                </div>
              </div>
            </div>
          </div>

          {/* Granular Subsystem Diagnostics - Unified Dark Violet Cards */}
          <div className="relative z-10 pt-3 border-t border-[#271C3D] grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
            {/* 1. Backend */}
            <div className="p-3 rounded-xl bg-[#161026] border border-[#2D214C] flex flex-col justify-between shadow-xs">
              <span className="text-[10px] text-[#8E7FA8] uppercase font-bold">Backend API</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className={`w-2.5 h-2.5 rounded-full ${health ? 'bg-[#8B5CF6]' : 'bg-[#E11D48]'}`} />
                <span className={`font-bold ${health ? 'text-white' : 'text-[#F472B6]'}`}>
                  {health ? 'Port 8080' : 'OFFLINE'}
                </span>
              </div>
              <span className="text-[10px] text-[#9D8EB9] mt-0.5 font-medium">Spring Boot 3.4</span>
            </div>

            {/* 2. Database */}
            <div className="p-3 rounded-xl bg-[#161026] border border-[#2D214C] flex flex-col justify-between shadow-xs">
              <span className="text-[10px] text-[#8E7FA8] uppercase font-bold">Active Database</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className={`w-2.5 h-2.5 rounded-full ${isDbUp ? 'bg-[#8B5CF6]' : 'bg-[#E11D48]'}`} />
                <span className={`font-bold ${isDbUp ? 'text-white' : 'text-[#F472B6]'}`}>
                  {dbType}
                </span>
              </div>
              <span className="text-[10px] text-[#9D8EB9] mt-0.5 font-medium">
                {dbType === 'H2' ? 'In-Memory Dev DB' : 'PostgreSQL Prod'}
              </span>
            </div>

            {/* 3. ML Model */}
            <div className="p-3 rounded-xl bg-[#161026] border border-[#2D214C] flex flex-col justify-between shadow-xs">
              <span className="text-[10px] text-[#8E7FA8] uppercase font-bold">ML Detector</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className={`w-2.5 h-2.5 rounded-full ${isMlUp ? 'bg-[#8B5CF6]' : 'bg-[#D97706]'}`} />
                <span className={`font-bold ${isMlUp ? 'text-white' : 'text-[#F472B6]'}`}>
                  {isMlUp ? 'Isolation Forest' : 'Port 5001'}
                </span>
              </div>
              <span className="text-[10px] text-[#9D8EB9] mt-0.5 font-medium">Trained Threshold</span>
            </div>

            {/* 4. Trusted Profile */}
            <div className="p-3 rounded-xl bg-[#161026] border border-[#2D214C] flex flex-col justify-between shadow-xs">
              <span className="text-[10px] text-[#8E7FA8] uppercase font-bold">Trusted Profile</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className={`w-2.5 h-2.5 rounded-full ${isProfileInit ? 'bg-[#8B5CF6]' : 'bg-[#6B5D88]'}`} />
                <span className="font-bold text-white">
                  {isProfileInit ? profileVersion : 'None'}
                </span>
              </div>
              <span className="text-[10px] text-[#9D8EB9] mt-0.5 font-medium">
                {isAdaptFrozen ? 'Frozen Status' : 'Active Profile'}
              </span>
            </div>

            {/* 5. Safe Adaptation */}
            <div className={`p-3 rounded-xl border flex flex-col justify-between shadow-xs ${
              isAdaptFrozen ? 'bg-[#2D1226] border-[#5E1E49]' : 'bg-[#161026] border-[#2D214C]'
            }`}>
              <span className={`text-[10px] uppercase font-bold ${
                isAdaptFrozen ? 'text-[#F472B6]' : 'text-[#8E7FA8]'
              }`}>Safe Adaptation</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className={`w-2.5 h-2.5 rounded-full ${isAdaptFrozen ? 'bg-[#E11D48]' : 'bg-[#8B5CF6]'}`} />
                <span className={`font-bold ${isAdaptFrozen ? 'text-[#F472B6]' : 'text-white'}`}>
                  {isAdaptFrozen ? 'FROZEN' : 'ACTIVE'}
                </span>
              </div>
              <span className={`text-[10px] mt-0.5 font-medium ${
                isAdaptFrozen ? 'text-[#F472B6]' : 'text-[#9D8EB9]'
              }`}>
                {isAdaptFrozen ? 'Updates Blocked' : 'Bounded Updates'}
              </span>
            </div>

            {/* 6. Telemetry Agent */}
            <div className="p-3 rounded-xl bg-[#161026] border border-[#2D214C] flex flex-col justify-between shadow-xs">
              <span className="text-[10px] text-[#8E7FA8] uppercase font-bold">Telemetry Agent</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className={`w-2.5 h-2.5 rounded-full ${isAgentActive ? 'bg-[#8B5CF6]' : 'bg-[#6B5D88]'}`} />
                <span className={`font-bold ${isAgentActive ? 'text-white' : 'text-[#8E7FA8]'}`}>
                  {isAgentActive ? 'LISTENING' : 'IDLE'}
                </span>
              </div>
              <span className="text-[10px] text-[#9D8EB9] mt-0.5 font-medium">Zero-Content Feed</span>
            </div>
          </div>
        </section>

        {/* Navigation Tabs - Cohesive Black & Violet Bar */}
        <div className="bg-[#100B1C] border border-[#271C3D] rounded-2xl p-2 flex flex-wrap gap-2 shadow-md">
          <button
            onClick={() => setActiveTab('playground')}
            className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition-all ${
              activeTab === 'playground'
                ? 'bg-[#7C3AED] text-white shadow-[0_0_16px_rgba(124,58,237,0.4)]'
                : 'bg-[#161026] border border-[#271C3D] text-[#C4B5FD] hover:bg-[#21163B] hover:border-[#43306B]'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>1. Biometric Playground</span>
          </button>

          <button
            onClick={() => setActiveTab('adaptation')}
            className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition-all ${
              activeTab === 'adaptation'
                ? 'bg-[#7C3AED] text-white shadow-[0_0_16px_rgba(124,58,237,0.4)]'
                : 'bg-[#161026] border border-[#271C3D] text-[#C4B5FD] hover:bg-[#21163B] hover:border-[#43306B]'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>2. Safe Adaptation Engine</span>
          </button>

          <button
            onClick={() => setActiveTab('simulators')}
            className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition-all ${
              activeTab === 'simulators'
                ? 'bg-[#7C3AED] text-white shadow-[0_0_16px_rgba(124,58,237,0.4)]'
                : 'bg-[#161026] border border-[#271C3D] text-[#C4B5FD] hover:bg-[#21163B] hover:border-[#43306B]'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span>3. Research Simulators</span>
          </button>

          <button
            onClick={() => setActiveTab('telemetry')}
            className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold cursor-pointer transition-all ${
              activeTab === 'telemetry'
                ? 'bg-[#7C3AED] text-white shadow-[0_0_16px_rgba(124,58,237,0.4)]'
                : 'bg-[#161026] border border-[#271C3D] text-[#C4B5FD] hover:bg-[#21163B] hover:border-[#43306B]'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>4. ML Models &amp; Telemetry</span>
          </button>
        </div>

        {/* Section Beginner Guide Note */}
        <div className="bg-[#140F24] border border-[#322352] rounded-2xl px-5 py-3.5 flex items-start gap-3 text-xs text-[#C4B5FD] shadow-xs">
          <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#8B5CF6]" />
          <div>
            <span className="font-extrabold text-white">
              {activeTab === 'playground' && 'About the Biometric Playground: '}
              {activeTab === 'adaptation' && 'About the Safe Adaptation Engine: '}
              {activeTab === 'simulators' && 'About the Research Simulators: '}
              {activeTab === 'telemetry' && 'About ML Models & Telemetry: '}
            </span>
            <span className="font-medium text-[#A79BC4]">
              {activeTab === 'playground' && 'Type in the box or move your mouse to capture privacy-preserving physical timing kinematics. Verify your behaviour against the trusted baseline without recording any characters.'}
              {activeTab === 'adaptation' && 'Inspect candidate observations, drift magnitude, and streak protection. Observe how legitimate changes adapt v1.0.0 while suspicious observations are rejected and frozen.'}
              {activeTab === 'simulators' && 'Run controlled synthetic benchmark simulations to demonstrate gradual legitimate drift adaptation, sudden takeover freeze, and slow stealth poisoning defense.'}
              {activeTab === 'telemetry' && 'Inspect calibrated Isolation Forest decision boundaries, mathematically explainable anomaly scores, and historical verification records.'}
            </span>
          </div>
        </div>

        {/* Tab Content Panels */}
        <div className="space-y-6">
          {activeTab === 'playground' && (
            <BiometricPlayground onSnapshotIngested={handleDataRefresh} />
          )}

          {activeTab === 'adaptation' && (
            <AdaptationDashboard key={refreshTrigger} />
          )}

          {activeTab === 'simulators' && (
            <ResearchSimulators onScenarioComplete={handleDataRefresh} />
          )}

          {activeTab === 'telemetry' && (
            <ModelDiagnostics key={refreshTrigger} />
          )}
        </div>

        {/* Foundation Architecture Cards - Dark Violet Panels */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="p-5 rounded-2xl border border-[#271C3D] bg-[#120D1F] space-y-2 shadow-xs">
            <div className="flex items-center space-x-2 text-[#8B5CF6]">
              <Cpu className="w-4 h-4" />
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">Desktop Agent</h3>
            </div>
            <p className="text-xs text-[#9D8EB9] leading-relaxed font-medium">
              Modular Python background collector tracking keystroke timing, mouse kinematics, and idle boundaries via OS hooks without recording characters.
            </p>
          </div>

          <div className="p-5 rounded-2xl border border-[#271C3D] bg-[#120D1F] space-y-2 shadow-xs">
            <div className="flex items-center space-x-2 text-[#8B5CF6]">
              <Layers className="w-4 h-4" />
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">ML Pipeline</h3>
            </div>
            <p className="text-xs text-[#9D8EB9] leading-relaxed font-medium">
              Scikit-learn Isolation Forest scoring kinematic feature vectors with bounded contamination, 5th-percentile calibration, and explainable decision scores.
            </p>
          </div>

          <div className="p-5 rounded-2xl border border-[#271C3D] bg-[#120D1F] space-y-2 shadow-xs">
            <div className="flex items-center space-x-2 text-[#8B5CF6]">
              <Lock className="w-4 h-4" />
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">Privacy Guardrails</h3>
            </div>
            <p className="text-xs text-[#9D8EB9] leading-relaxed font-medium">
              Strict non-surveillance boundary. Zero character retention, zero clipboard logging, zero screen scraping. Pure physical dynamics only.
            </p>
          </div>
        </section>

        {/* Privacy Principles Box */}
        <section className="border border-[#382759] rounded-2xl bg-[#140F24] p-5 space-y-2 shadow-xs">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-[#8B5CF6]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">
              Research Privacy Specification
            </h3>
          </div>
          <p className="text-xs text-[#A79BC4] leading-relaxed font-medium">
            In accordance with ethical CS research standards, Cyber Doppelgänger operates under an immutable zero-content policy. The system strictly discards raw characters and window contents, utilizing only timing durations (dwell/flight intervals) and physical motion kinematics.
          </p>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default App;
