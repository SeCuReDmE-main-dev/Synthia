import React, { useState, useEffect } from 'react';
import { SystemState, LogMessage } from '../types';
import { Check, ShieldCheck, HelpCircle, Users, Activity, FileCode } from 'lucide-react';

interface SideNavBarProps {
  systemState: SystemState;
  logs: LogMessage[];
  systemStatus: string;
}

export const SideNavBar: React.FC<SideNavBarProps> = ({
  systemState,
  logs,
  systemStatus,
}) => {
  const [cpu, setCpu] = useState(systemState.cpuLoad);
  const [mem, setMem] = useState(systemState.memoryUsage);

  useEffect(() => {
    // Generate small fluctuations to simulate active computation
    const interval = setInterval(() => {
      setCpu((prev) => {
        const delta = (Math.random() - 0.5) * 4;
        const next = Math.max(12, Math.min(95, prev + delta));
        return parseFloat(next.toFixed(1));
      });
      setMem((prev) => {
        const delta = (Math.random() - 0.5) * 0.02;
        const next = Math.max(2.1, Math.min(2.8, prev + delta));
        return parseFloat(next.toFixed(3));
      });
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="w-full xl:w-[360px] glass rounded-3xl font-mono p-5 flex flex-col space-y-6 shrink-0 relative overflow-hidden transition-all-smooth z-10">
      
      {/* Telemetry Display */}
      <div className="border border-white/5 bg-white/2 rounded-2xl p-4 relative overflow-hidden transition-all-smooth">
        <div className="absolute top-0 right-0 bg-white/5 text-[9px] text-gray-500 px-2 py-0.5 border-b border-l border-white/10 rounded-bl-xl">
          LIVE_TELEMETRY
        </div>
        <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center">
          <Activity className="w-3.5 h-3.5 text-[#D9DADC] mr-2 animate-pulse" />
          SYSTEM LOADMETRIC
        </h3>
        
        <div className="space-y-4 text-xs">
          <div>
            <div className="flex justify-between mb-1.5 text-[11px]">
              <span className="text-gray-400">CPU CORE COMPUTE</span>
              <span className="text-[#5AA7A3] font-bold glow-text">{cpu}%</span>
            </div>
            <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] transition-all duration-300 rounded-full" style={{ width: `${cpu}%` }} />
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1.5 text-[11px]">
              <span className="text-gray-400">TAXONOMIC MEMORY</span>
              <span className="text-gray-200 font-bold">{mem} GB / 8.00 GB</span>
            </div>
            <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-white/30 transition-all duration-300 rounded-full" style={{ width: `${(mem / 8) * 100}%` }} />
            </div>
          </div>

          <div className="pt-3 border-t border-white/5 flex justify-between text-[11px]">
            <span className="text-gray-400">F1 CONSENSUS SCORE</span>
            <span className="text-[#5AA7A3] font-bold">{(systemState.consensusScore * 100).toFixed(4)}%</span>
          </div>

          <div className="flex justify-between text-[11px]">
            <span className="text-gray-400">INTEGRITY MONITOR</span>
            <span className={`font-bold tracking-wider ${systemStatus === 'NOMINAL' ? 'text-[#5AA7A3] glow-text' : 'text-amber-400'}`}>
              {systemStatus}
            </span>
          </div>
        </div>
      </div>

      {/* Mathematical System Invariants */}
      <div className="border border-white/5 p-4 bg-white/2 rounded-2xl transition-all-smooth">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center justify-between">
          <span className="flex items-center">
            <ShieldCheck className="w-3.5 h-3.5 text-[#5AA7A3] mr-2" />
            INVARIANT EQUALITY GUARD
          </span>
          <span className="text-[10px] text-gray-500 font-semibold">(STRICT_0x)</span>
        </h3>
        
        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-between p-2.5 bg-black/45 border border-white/5 rounded-xl hover:border-[#5AA7A3]/30 transition-all duration-200">
            <div className="flex flex-col">
              <span className="font-bold text-gray-200">Invariant I</span>
              <span className="text-[9px] text-gray-500">I = s_i in S</span>
            </div>
            <div className="flex items-center text-[#5AA7A3] text-[10px] font-bold tracking-wider bg-[#5AA7A3]/10 px-2 py-0.5 rounded-full">
              <Check className="w-3 h-3 mr-1" /> PASSED
            </div>
          </div>

          <div className="flex items-center justify-between p-2.5 bg-black/45 border border-white/5 rounded-xl hover:border-[#5AA7A3]/30 transition-all duration-200">
            <div className="flex flex-col">
              <span className="font-bold text-gray-200">System S_inv</span>
              <span className="text-[9px] text-gray-500">I_system^S = True</span>
            </div>
            <div className="flex items-center text-[#5AA7A3] text-[10px] font-bold tracking-wider bg-[#5AA7A3]/10 px-2 py-0.5 rounded-full">
              <Check className="w-3 h-3 mr-1" /> PASSED
            </div>
          </div>

          <div className="flex items-center justify-between p-2.5 bg-black/45 border border-white/5 rounded-xl hover:border-[#5AA7A3]/30 transition-all duration-200">
            <div className="flex flex-col">
              <span className="font-bold text-gray-200">H_lex Identity</span>
              <span className="text-[9px] text-gray-500">H_lex = f(G_lex)</span>
            </div>
            <div className="flex items-center text-[#5AA7A3] text-[10px] font-bold tracking-wider bg-[#5AA7A3]/10 px-2 py-0.5 rounded-full">
              <Check className="w-3 h-3 mr-1" /> PASSED
            </div>
          </div>

          <div className="flex items-center justify-between p-2.5 bg-black/45 border border-white/5 rounded-xl hover:border-[#5AA7A3]/30 transition-all duration-200">
            <div className="flex flex-col">
              <span className="font-bold text-gray-200">G_lex Generator</span>
              <span className="text-[9px] text-gray-500">G_lex(I_lexicon)</span>
            </div>
            <div className="flex items-center text-[#5AA7A3] text-[10px] font-bold tracking-wider bg-[#5AA7A3]/10 px-2 py-0.5 rounded-full">
              <Check className="w-3 h-3 mr-1" /> PASSED
            </div>
          </div>

          <div className="flex items-center justify-between p-2.5 bg-black/45 border border-white/5 rounded-xl hover:border-[#5AA7A3]/30 transition-all duration-200">
            <div className="flex flex-col">
              <span className="font-bold text-gray-200">I_lexicon Resolution</span>
              <span className="text-[9px] text-gray-500">I_lexicon is complete</span>
            </div>
            <div className="flex items-center text-[#5AA7A3] text-[10px] font-bold tracking-wider bg-[#5AA7A3]/10 px-2 py-0.5 rounded-full">
              <Check className="w-3 h-3 mr-1" /> PASSED
            </div>
          </div>
        </div>
      </div>

      {/* Key Developers & Credits */}
      <div className="border border-white/5 p-4 bg-white/2 rounded-2xl transition-all-smooth">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center">
          <Users className="w-3.5 h-3.5 text-[#5AA7A3] mr-2" />
          RESEARCH COLLABORATORS
        </h3>
        <p className="text-[10px] text-gray-400 mb-4 leading-relaxed font-sans">
          Synthia is developed as an open research framework for deterministic biological taxonomy and memory integrity.
        </p>
        
        <div className="space-y-3.5 text-xs">
          <div className="border-l-2 border-[#5AA7A3] pl-3">
            <div className="font-bold text-white">Jean-Sebastien Beaulieu</div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider font-semibold">Lead Architect & Systems Engineer</div>
          </div>

          <div className="border-l-2 border-[#5AA7A3] pl-3">
            <div className="font-bold text-white">Prof. Hector Fernando Aguilar</div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider font-semibold">Co-Inventor, Senior Biological Taxonomist</div>
          </div>

          <div className="border-l-2 border-white/10 pl-3">
            <div className="font-bold text-gray-300">SecuredMe Corp</div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider font-semibold">Educational Platform Integration</div>
          </div>
        </div>
      </div>

      {/* Terminal Mini-Log Feed */}
      <div className="flex-1 min-h-[160px] border border-white/5 bg-black/40 rounded-2xl p-4 text-[11px] flex flex-col justify-between overflow-hidden transition-all-smooth">
        <div className="flex justify-between items-center text-[9px] text-gray-500 border-b border-white/5 pb-2 mb-2.5 uppercase tracking-wider">
          <span>DIAGNOSTIC_LOGGER</span>
          <span>LIVE FEED</span>
        </div>
        
        <div className="flex-1 overflow-y-auto space-y-2 font-mono scrollbar-thin">
          {logs.slice(-6).map((log) => {
            const levelColor = 
              log.level === 'SUCCESS' ? 'text-[#5AA7A3]' :
              log.level === 'WARN' ? 'text-amber-400' :
              log.level === 'ERROR' ? 'text-red-400 font-bold' : 'text-gray-500';
            
            return (
              <div key={log.id} className="leading-tight flex flex-col">
                <div className="flex items-center space-x-1">
                  <span className="text-gray-600">[{log.timestamp}]</span>
                  <span className={`${levelColor} font-semibold text-[10px]`}>[{log.category}/{log.level}]</span>
                </div>
                <div className="text-gray-300 pl-2 text-[10px] break-words">{log.text}</div>
              </div>
            );
          })}
        </div>

        <div className="border-t border-white/5 pt-2 mt-2.5 flex justify-between items-center text-[9px] text-gray-600">
          <span>TOTAL LOGS: {logs.length}</span>
          <span className="flex items-center text-[#5AA7A3] font-semibold animate-pulse">
            <Activity className="w-2.5 h-2.5 mr-1" /> SECURE_LINK
          </span>
        </div>
      </div>

    </aside>
  );
};
