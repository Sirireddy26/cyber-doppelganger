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
    <header className="border-b border-[#CDBEE7] bg-[#E8DEF6] sticky top-0 z-50 shadow-xs">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-[#D7C4F2] border border-[#BFABEB] flex items-center justify-center text-[#593CA5]">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-[#1E2638]">
                Cyber Doppelgänger
              </span>
              <span className="text-[11px] font-bold tracking-wide px-2.5 py-0.5 rounded-full bg-[#D7C4F2] text-[#431E8C] border border-[#BFABEB]">
                Research Lab
              </span>
            </div>
            <p className="text-xs text-[#505E75]">Continuous Behavioural Verification &amp; Safe Adaptation</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Backend Status */}
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium"
            style={{
              backgroundColor: backendOnline === true ? '#CCEBD4' : backendOnline === false ? '#F5CCD7' : '#E0D4F5',
              borderColor: backendOnline === true ? '#9EDAA9' : backendOnline === false ? '#EAAAB9' : '#C4B2E5',
              color: backendOnline === true ? '#0F5132' : backendOnline === false ? '#881337' : '#4A5568'
            }}>
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                backendOnline === true
                  ? 'bg-[#15803D]'
                  : backendOnline === false
                  ? 'bg-[#E11D48]'
                  : 'bg-[#D97706] animate-pulse'
              }`}
            />
            <span>
              API: {backendOnline === true ? 'ONLINE' : backendOnline === false ? 'OFFLINE' : 'CONNECTING'}
            </span>
          </div>

          {/* DB Status */}
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium"
            style={{
              backgroundColor: dbOnline === true ? '#D8E7F7' : dbOnline === false ? '#F5CCD7' : '#E0D4F5',
              borderColor: dbOnline === true ? '#ADC9EE' : dbOnline === false ? '#EAAAB9' : '#C4B2E5',
              color: dbOnline === true ? '#0A3B7B' : dbOnline === false ? '#881337' : '#4A5568'
            }}>
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                dbOnline === true
                  ? 'bg-[#1D4ED8]'
                  : dbOnline === false
                  ? 'bg-[#E11D48]'
                  : 'bg-[#94A3B8]'
              }`}
            />
            <span>
              DB: {dbOnline === true ? 'CONNECTED' : dbOnline === false ? 'DOWN' : 'N/A'}
            </span>
          </div>

          {/* ML Status */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium"
            style={{
              backgroundColor: mlOnline === true ? '#DDD0F2' : mlOnline === false ? '#F5CCD7' : '#E0D4F5',
              borderColor: mlOnline === true ? '#BFA9E4' : mlOnline === false ? '#EAAAB9' : '#C4B2E5',
              color: mlOnline === true ? '#431E8C' : mlOnline === false ? '#881337' : '#4A5568'
            }}>
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                mlOnline === true
                  ? 'bg-[#7C3AED]'
                  : mlOnline === false
                  ? 'bg-[#E11D48]'
                  : 'bg-[#94A3B8]'
              }`}
            />
            <span>
              ML: {mlOnline === true ? 'READY' : mlOnline === false ? 'OFFLINE' : 'N/A'}
            </span>
          </div>

          {/* Profile Status */}
          {profileStatus && (
            <div className="hidden xl:flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#DDD0F2] border border-[#BFA9E4] text-xs font-mono text-[#431E8C] font-medium">
              <span>Profile: {profileStatus}</span>
            </div>
          )}

          {/* Adaptation Status */}
          {adaptationFrozen !== undefined && adaptationFrozen !== null && (
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-xl border text-xs font-mono font-medium"
              style={{
                backgroundColor: adaptationFrozen ? '#F5CCD7' : '#DDD0F2',
                borderColor: adaptationFrozen ? '#EAAAB9' : '#BFA9E4',
                color: adaptationFrozen ? '#881337' : '#431E8C'
              }}>
              <span className={`w-2.5 h-2.5 rounded-full ${adaptationFrozen ? 'bg-[#E11D48]' : 'bg-[#7C3AED]'}`} />
              <span>{adaptationFrozen ? 'FROZEN' : 'ACTIVE'}</span>
            </div>
          )}

          {/* Refresh Action */}
          <button
            onClick={onRefresh}
            disabled={loading}
            title="Refresh system diagnostics"
            aria-label="Refresh diagnostics"
            className="p-2 rounded-xl bg-[#D7C4F2] border border-[#BFABEB] hover:bg-[#CBB4ED] text-[#1E2638] transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 text-[#431E8C] ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
