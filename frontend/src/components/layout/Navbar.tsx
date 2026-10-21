import React from 'react';
import { Shield, RefreshCw } from 'lucide-react';

interface NavbarProps {
  backendOnline: boolean | null;
  mlOnline?: boolean | null;
  dbOnline?: boolean | null;
  profileStatus?: string | null;
  adaptationFrozen?: boolean | null;
  loading: boolean;
  onRefresh: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ 
  backendOnline, 
  mlOnline, 
  dbOnline, 
  profileStatus, 
  adaptationFrozen,
  loading, 
  onRefresh 
}) => {
  return (
    <header className="border-b border-[#271C3D] bg-[#0E0A1A]/95 backdrop-blur-md sticky top-0 z-50 shadow-md">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-[#1C1333] border border-[#3E296A] flex items-center justify-center text-[#A78BFA] shadow-xs">
            <Shield className="w-5 h-5 text-[#8B5CF6]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base tracking-tight text-white">
                Cyber Doppelgänger
              </span>
              <span className="text-[11px] font-bold tracking-wide px-2.5 py-0.5 rounded-full bg-[#20143B] text-[#C4B5FD] border border-[#432C73]">
                Security Operations
              </span>
            </div>
            <p className="text-xs text-[#8E7FA8]">Continuous Behavioural Biometrics &amp; Safe Adaptation</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Backend Status */}
          <div 
            className="flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium transition-all"
            style={{
              backgroundColor: backendOnline === true ? '#1A1230' : backendOnline === false ? '#2D1226' : '#140E24',
              borderColor: backendOnline === true ? '#432C73' : backendOnline === false ? '#5E1E49' : '#2A1D45',
              color: backendOnline === true ? '#C4B5FD' : backendOnline === false ? '#F472B6' : '#8E7FA8'
            }}
          >
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                backendOnline === true
                  ? 'bg-[#8B5CF6] shadow-[0_0_8px_#8B5CF6]'
                  : backendOnline === false
                  ? 'bg-[#E11D48] shadow-[0_0_8px_#E11D48]'
                  : 'bg-[#A855F7] animate-pulse'
              }`}
            />
            <span>
              API: {backendOnline === true ? 'ONLINE' : backendOnline === false ? 'OFFLINE' : 'CONNECTING'}
            </span>
          </div>

          {/* DB Status */}
          <div 
            className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium"
            style={{
              backgroundColor: dbOnline === true ? '#1A1230' : dbOnline === false ? '#2D1226' : '#140E24',
              borderColor: dbOnline === true ? '#432C73' : dbOnline === false ? '#5E1E49' : '#2A1D45',
              color: dbOnline === true ? '#C4B5FD' : dbOnline === false ? '#F472B6' : '#8E7FA8'
            }}
          >
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                dbOnline === true
                  ? 'bg-[#8B5CF6]'
                  : dbOnline === false
                  ? 'bg-[#E11D48]'
                  : 'bg-[#6B5D88]'
              }`}
            />
            <span>
              DB: {dbOnline === true ? 'CONNECTED' : dbOnline === false ? 'DOWN' : 'N/A'}
            </span>
          </div>

          {/* ML Status */}
          <div 
            className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium"
            style={{
              backgroundColor: mlOnline === true ? '#1A1230' : mlOnline === false ? '#2D1226' : '#140E24',
              borderColor: mlOnline === true ? '#432C73' : mlOnline === false ? '#5E1E49' : '#2A1D45',
              color: mlOnline === true ? '#C4B5FD' : mlOnline === false ? '#F472B6' : '#8E7FA8'
            }}
          >
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                mlOnline === true
                  ? 'bg-[#8B5CF6] shadow-[0_0_8px_#8B5CF6]'
                  : mlOnline === false
                  ? 'bg-[#E11D48]'
                  : 'bg-[#6B5D88]'
              }`}
            />
            <span>
              ML: {mlOnline === true ? 'READY' : mlOnline === false ? 'OFFLINE' : 'N/A'}
            </span>
          </div>

          {/* Profile Status */}
          {profileStatus && (
            <div className="hidden xl:flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#1A1230] border border-[#432C73] text-xs font-mono text-[#C4B5FD] font-medium">
              <span>Profile: {profileStatus}</span>
            </div>
          )}

          {/* Adaptation Status */}
          {adaptationFrozen !== undefined && adaptationFrozen !== null && (
            <div 
              className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium"
              style={{
                backgroundColor: adaptationFrozen ? '#2D1226' : '#1A1230',
                borderColor: adaptationFrozen ? '#5E1E49' : '#432C73',
                color: adaptationFrozen ? '#F472B6' : '#C4B5FD'
              }}
            >
              <span className={`w-2.5 h-2.5 rounded-full ${adaptationFrozen ? 'bg-[#E11D48]' : 'bg-[#8B5CF6]'}`} />
              <span>{adaptationFrozen ? 'FROZEN' : 'ACTIVE'}</span>
            </div>
          )}

          {/* Refresh Action */}
          <button
            onClick={onRefresh}
            disabled={loading}
            title="Refresh system diagnostics"
            aria-label="Refresh diagnostics"
            className="p-2 rounded-xl bg-[#1A1230] border border-[#3E296A] hover:bg-[#251A44] hover:border-[#8B5CF6] text-[#C4B5FD] transition-all cursor-pointer shadow-xs"
          >
            <RefreshCw className={`w-4 h-4 text-[#A78BFA] ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
