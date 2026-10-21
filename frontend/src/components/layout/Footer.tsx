import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[#221738] bg-[#0A0713] py-6 px-6 mt-auto">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-[#8E7FA8] gap-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-white">Cyber Doppelgänger</span>
          <span className="text-[#4C337D]">&bull;</span>
          <span>Safe Adaptive Behavioural Identity &amp; Continuous Verification</span>
        </div>
        <div className="font-mono text-[11px] text-[#71618C]">
          CSE Final-Year Research Project &bull; Zero-Content Architecture
        </div>
      </div>
    </footer>
  );
};
