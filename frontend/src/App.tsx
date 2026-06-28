/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { ActiveTab, SystemState, LogMessage } from './types';
import { TopNavBar } from './components/TopNavBar';
import { SideNavBar } from './components/SideNavBar';
import { ModelTab } from './components/ModelTab';
import { LexiconTab } from './components/LexiconTab';
import { BiologyTab } from './components/BiologyTab';
import { DocsTab } from './components/DocsTab';
import { Footer } from './components/Footer';
import { Terminal, ShieldCheck, Activity } from 'lucide-react';

const INITIAL_LOGS: LogMessage[] = [
  { id: '1', timestamp: '12:00:00', category: 'SYS', level: 'INFO', text: 'SYNTHIA core local system loaded.' },
  { id: '2', timestamp: '12:00:01', category: 'SYS', level: 'SUCCESS', text: 'Local memory cache synced: 2,408 indices nominal.' },
  { id: '3', timestamp: '12:00:03', category: 'I_LEX', level: 'INFO', text: 'Pre-caching lexicon mapping schemas.' },
  { id: '4', timestamp: '12:00:05', category: 'REPAIR', level: 'SUCCESS', text: 'Verification pass: Invariant I through I_lexicon verified true.' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('model');
  const [systemStatus, setSystemStatus] = useState<'NOMINAL' | 'DEGRADED' | 'REPAIRING' | 'MUTATED'>('NOMINAL');
  const [isSweeping, setIsSweeping] = useState(false);
  const [sweepProgress, setSweepProgress] = useState(0);
  const [sweepLogs, setSweepLogs] = useState<string[]>([]);
  
  const [systemState, setSystemState] = useState<SystemState>({
    uptime: 0,
    cpuLoad: 32.4,
    memoryUsage: 2.345,
    consensusScore: 0.9942,
    integrityStatus: 'NOMINAL',
    activePayloadId: 'pay-001',
    systemInvariants: {
      I: true,
      I_system_S: true,
      H_lex: true,
      G_lex: true,
      I_lexicon: true,
    }
  });

  const [logs, setLogs] = useState<LogMessage[]>(INITIAL_LOGS);

  // Uptime ticker
  useEffect(() => {
    const timer = setInterval(() => {
      setSystemState((prev) => ({
        ...prev,
        uptime: prev.uptime + 1,
      }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const addLog = (
    category: 'SYS' | 'I_LEX' | 'PHYLO' | 'REPAIR',
    level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR',
    text: string
  ) => {
    const timestamp = new Date().toTimeString().split(' ')[0];
    const newLog: LogMessage = {
      id: Math.random().toString(),
      timestamp,
      category,
      level,
      text,
    };
    setLogs((prev) => [...prev, newLog]);
  };

  const handleUpdateConsensus = (score: number) => {
    setSystemState((prev) => ({
      ...prev,
      consensusScore: score,
    }));
  };

  const handleUpdateStatus = (status: 'NOMINAL' | 'DEGRADED' | 'REPAIRING' | 'MUTATED') => {
    setSystemStatus(status);
    setSystemState((prev) => ({
      ...prev,
      integrityStatus: status,
    }));
  };

  const handleTriggerSweep = () => {
    if (isSweeping) return;
    setIsSweeping(true);
    setSweepProgress(0);
    setSweepLogs(['INITIALIZING SYSTEM-WIDE CALIBRATION SWEEP...']);
    addLog('SYS', 'INFO', 'Calibration sweep initiated on virtual sectors...');

    const sweepSteps = [
      'Scanning cell sector ranges 0x00 through 0xFF...',
      'Verifying internal cache integrity sockets...',
      'Validating invariant equality constraint f(S_i) = I_system^S...',
      'Inspecting biological sequences for plithogenic mutations...',
      'Resetting cellular contradiction thresholds to strict zero...',
      'Rebuilding divergent hash links inside H_lex table...',
      'Calibrating CPU load allocations and memory constraints...',
      'Recalculating global Shannon Entropy curves...',
      'SWEEP RECONCILIATION COMPLETE. ALL SECTORS NOMINAL.'
    ];

    let currentStep = 0;
    const interval = setInterval(() => {
      if (currentStep < sweepSteps.length) {
        setSweepLogs((prev) => [...prev, `[Sweep Log]: ${sweepSteps[currentStep]}`]);
        setSweepProgress((currentStep + 1) * 11);
        currentStep++;
      } else {
        clearInterval(interval);
        setTimeout(() => {
          setIsSweeping(false);
          setSystemStatus('NOMINAL');
          setSystemState(prev => ({
            ...prev,
            consensusScore: 0.9942,
            integrityStatus: 'NOMINAL'
          }));
          addLog('SYS', 'SUCCESS', 'Calibration sweep complete. Uptime clock synced. Core indicators returned to NOMINAL.');
        }, 500);
      }
    }, 300);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-[#2B2F33] text-[#D9DADC] select-none relative scanlines transition-all-smooth">
      
      {/* Background Atmosphere Ambient Glows */}
      <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-[#5AA7A3] opacity-[0.04] blur-[120px] rounded-full pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-[#8AB38B] opacity-[0.06] blur-[120px] rounded-full pointer-events-none z-0" />

      {/* Dynamic Calibration Sweep Animation Overlay */}
      {isSweeping && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-[9999] flex flex-col justify-center items-center font-mono p-4">
          <div className="w-full max-w-2xl glass rounded-3xl p-6 relative overflow-hidden glow-cyan">
            
            {/* Pulsing horizontal laser scanner sweep */}
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] animate-bounce glow-brand" />
            
            <div className="flex justify-between items-center text-xs text-[#737373] border-b border-white/10 pb-3 mb-4">
              <span className="flex items-center text-[#5AA7A3] font-bold tracking-wider">
                <Activity className="w-4 h-4 mr-2 animate-pulse text-[#5AA7A3]" />
                ACTIVE SYSTEM CALIBRATION SWEEP
              </span>
              <span className="text-[#5AA7A3] font-bold">PROGRESS: {sweepProgress}%</span>
            </div>

            <div className="w-full bg-white/5 h-2.5 mb-6 border border-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] transition-all duration-300 rounded-full" style={{ width: `${sweepProgress}%` }} />
            </div>

            <div className="h-[200px] overflow-y-auto bg-black/50 border border-white/5 p-3 text-xs space-y-1.5 text-[#D9DADC] scrollbar-thin rounded-xl">
              {sweepLogs.map((log, idx) => (
                <div key={idx} className="leading-tight text-[11px] font-mono flex items-center">
                  <span className="text-[#5AA7A3] mr-2">✔</span>
                  <span className="text-gray-300">{log}</span>
                </div>
              ))}
            </div>

            <div className="text-center text-[10px] text-gray-500 mt-4 uppercase tracking-widest font-sans">
              DO NOT CLOSE BROWSER PANEL • COGNITIVE ENGINES SUSPENDED
            </div>
          </div>
        </div>
      )}

      {/* Main Layout Header */}
      <TopNavBar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={systemStatus}
        onTriggerSweep={handleTriggerSweep}
        isSweeping={isSweeping}
      />

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 py-6 flex flex-col xl:flex-row gap-6">
        
        {/* Left/Right Column sidebar */}
        <SideNavBar
          systemState={systemState}
          logs={logs}
          systemStatus={systemStatus}
        />

        {/* Primary Screen Area switching active view */}
        <div className="flex-1 min-w-0">
          {activeTab === 'model' && (
            <ModelTab
              systemState={systemState}
              onAddLog={addLog}
              onUpdateStatus={handleUpdateStatus}
            />
          )}

          {activeTab === 'lexicon' && (
            <LexiconTab
              onAddLog={addLog}
              onUpdateConsensus={handleUpdateConsensus}
            />
          )}

          {activeTab === 'biology' && (
            <BiologyTab
              onAddLog={addLog}
            />
          )}

          {activeTab === 'docs' && (
            <DocsTab
              onAddLog={addLog}
            />
          )}
        </div>

      </main>

      {/* Shared Footer and Licensing Credits */}
      <Footer />

    </div>
  );
}

