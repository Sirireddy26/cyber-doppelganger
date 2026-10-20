import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[#CDBEE7] bg-[#E8DEF6] py-6 px-6 mt-auto">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-[#505E75] gap-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-[#1E2638]">Cyber Doppelgänger</span>
          <span>&bull;</span>
          <span>Safe Adaptive Behavioural Identity &amp; Continuous Verification</span>
        </div>
        <div className="font-mono text-[11px] text-[#505E75]">
          CSE Final-Year Research Project &bull; Soft Research Lab
        </div>
      </div>
    </footer>
  );
};
