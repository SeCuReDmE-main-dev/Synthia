import React, { useState, useEffect } from 'react';
import { ActiveTab } from '../types';
import { Terminal, Cpu, Dna, FileText, Activity, ShieldCheck } from 'lucide-react';

interface TopNavBarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  systemStatus: string;
  onTriggerSweep: () => void;
  isSweeping: boolean;
}

export const TopNavBar: React.FC<TopNavBarProps> = ({
  activeTab,
  setActiveTab,
  systemStatus,
  onTriggerSweep,
  isSweeping,
}) => {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems: { id: ActiveTab; label: string; icon: React.ReactNode; desc: string }[] = [
    {
      id: 'model',
      label: '1_MODEL_REPAIR',
      icon: <Cpu className="w-4 h-4" />,
      desc: 'Taxonomic Memory & Invariants',
    },
    {
      id: 'lexicon',
      label: '2_I_LEXICON',
      icon: <Terminal className="w-4 h-4" />,
      desc: 'Entropy Parsing & Payload',
    },
    {
      id: 'biology',
      label: '3_BIOLOGY_PHYLO',
      icon: <Dna className="w-4 h-4" />,
      desc: 'Phylo-plithogenic Guardrails',
    },
    {
      id: 'docs',
      label: '4_SYSTEM_DOCS',
      icon: <FileText className="w-4 h-4" />,
      desc: 'Initialization & pytest Logs',
    },
  ];

  return (
    <header className="w-full bg-black/60 backdrop-blur-md border-b border-white/10 font-mono sticky top-0 z-50 transition-all-smooth">
      {/* Top Banner and Status Info */}
      <div className="max-w-[1600px] mx-auto px-4 py-2 flex flex-col md:flex-row justify-between items-center text-xs text-gray-400 border-b border-white/5">
        <div className="flex items-center space-x-4 mb-2 md:mb-0">
          <span className="flex items-center text-[#5AA7A3] font-bold tracking-wider">
            <ShieldCheck className="w-4 h-4 mr-1.5 text-[#5AA7A3] animate-pulse" />
            SYNTHIA SYSTEM PROTOCOL v4.2.1-RESEARCH
          </span>
          <span className="hidden sm:inline text-white/10">|</span>
          <span className="hidden sm:inline">SECURITY LEVEL: EDUCATIONAL RESEARCH</span>
          <span className="hidden sm:inline text-white/10">|</span>
          <span className="text-gray-300 flex items-center">
            <span className={`w-2 h-2 mr-1.5 rounded-full ${systemStatus === 'NOMINAL' ? 'bg-[#5AA7A3] glow-brand' : 'bg-amber-400 animate-pulse'} inline-block`} />
            CORE STATE: <strong className={`ml-1 ${systemStatus === 'NOMINAL' ? 'text-[#5AA7A3]' : 'text-amber-400'}`}>{systemStatus}</strong>
          </span>
        </div>
        <div className="flex items-center space-x-6 text-xs text-gray-400">
          <span>HOST: <strong className="text-gray-200">synthia.securedme.ca</strong></span>
          <span className="hidden sm:inline text-white/10">|</span>
          <span className="text-[#5AA7A3] tracking-widest font-mono select-none glow-text">{timeStr}</span>
        </div>
      </div>

      {/* Main Nav Bar */}
      <div className="max-w-[1600px] mx-auto px-4 flex flex-col lg:flex-row justify-between items-stretch">
        <div className="flex items-center py-4 border-b lg:border-b-0 border-white/5 lg:mr-8 cursor-pointer" onClick={() => setActiveTab('model')}>
          <div className="flex items-center space-x-3">
            <div className="p-2 border border-[#5AA7A3]/30 bg-white/5 text-[#5AA7A3] rounded-xl relative group">
              <span className="absolute inset-0 bg-[#5AA7A3]/10 scale-0 group-hover:scale-100 transition-transform duration-200 rounded-xl" />
              <Activity className="w-6 h-6 animate-pulse text-[#5AA7A3]" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-wider font-sans flex items-baseline">
                <span className="gradient-text font-black tracking-widest">SYNTHIA</span>
                <span className="text-[#5AA7A3] text-xs font-mono ml-1.5 tracking-widest font-semibold glow-text">[I_LEX]</span>
              </h1>
              <p className="text-[10px] uppercase text-gray-500 tracking-wider leading-none">Context-Preserving Taxonomic Engine</p>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex flex-1 flex-wrap items-stretch">
          {navItems.map((item) => {
            const isSelected = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex-1 min-w-[140px] px-4 py-4 text-left border-r border-white/5 transition-all duration-150 flex flex-col justify-between relative overflow-hidden group border-b lg:border-b-0 ${
                  isSelected 
                    ? 'bg-white/5 text-white border-b-2 border-b-[#5AA7A3]' 
                    : 'text-gray-400 hover:text-white hover:bg-white/2'
                }`}
              >
                {/* Active indicator bar */}
                {isSelected && (
                  <span className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] glow-brand" />
                )}
                
                <div className="flex justify-between items-start w-full">
                  <span className={`text-[11px] font-mono tracking-widest ${isSelected ? 'text-[#5AA7A3] font-bold' : 'text-gray-500 group-hover:text-gray-300'}`}>
                    {item.label}
                  </span>
                  <span className={isSelected ? 'text-[#5AA7A3] glow-text' : 'text-gray-600 group-hover:text-gray-400'}>
                    {item.icon}
                  </span>
                </div>
                
                <div className="mt-2">
                  <span className="text-xs font-sans font-semibold tracking-tight">{item.desc}</span>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Global Action Sweep Trigger */}
        <div className="flex items-center py-4 lg:py-0 border-t lg:border-t-0 border-white/5 lg:pl-6">
          <button
            onClick={onTriggerSweep}
            disabled={isSweeping}
            className={`w-full lg:w-auto px-5 py-2.5 font-sans font-extrabold text-xs uppercase tracking-wider transition-all duration-300 flex items-center justify-center rounded-full border ${
              isSweeping
                ? 'bg-white/5 text-amber-400 border-amber-400 animate-pulse cursor-not-allowed'
                : 'bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] text-black border-none hover:opacity-90 hover:scale-[1.02] shadow-[0_0_15px_rgba(0,242,255,0.25)] active:translate-y-px cursor-pointer'
            }`}
          >
            {isSweeping ? (
              <>
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping mr-2" />
                SWEEP IN PROGRESS...
              </>
            ) : (
              <>
                <Cpu className="w-4 h-4 mr-2" />
                RUN SYSTEM SWEEP
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
