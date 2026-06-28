import React, { useState, useEffect } from 'react';
import { SystemState } from '../types';
import { Cpu, ShieldAlert, Sparkles, Check, Play, HelpCircle, Activity, RotateCcw } from 'lucide-react';

interface ModelTabProps {
  systemState: SystemState;
  onAddLog: (category: 'SYS' | 'I_LEX' | 'PHYLO' | 'REPAIR', level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR', text: string) => void;
  onUpdateStatus: (status: 'NOMINAL' | 'DEGRADED' | 'REPAIRING' | 'MUTATED') => void;
}

interface InvariantNode {
  id: string;
  name: string;
  formula: string;
  description: string;
  pythonFile: string;
  verifiedVar: string;
}

const INVARIANT_STEPS: InvariantNode[] = [
  {
    id: 'I',
    name: '01_BIOLOGICAL_INPUT (I)',
    formula: 's_i ∈ S_taxonomic',
    description: 'Validates that the biological sequence input sequence conforms to the primary alphanumeric alphabet of nucleotides (A, T, G, C) and is mapped inside the valid search space S.',
    pythonFile: 'synthia/core/input_verifier.py',
    verifiedVar: 'seq_alphabet_matched = True'
  },
  {
    id: 'I_system_S',
    name: '02_SYSTEM_INTEGRITY (I_system^S)',
    formula: 'f(s_i) ≡ I_system^S',
    description: 'Asserts that the physical SQLite / relational state of the database conforms to structural schema layout constraints. Prevents illegal transactions or missing tables.',
    pythonFile: 'synthia/db/integrity_check.py',
    verifiedVar: 'db_structural_hash_verified = True'
  },
  {
    id: 'H_lex',
    name: '03_LEXICON_IDENTITY (H_lex)',
    formula: 'H_lex = Hash(G_lex)',
    description: 'Asserts semantic mapping uniqueness. Generates an immutable cryptographic hash of the generated plithogenic sieve structure to ensure context remains preserved without leakage.',
    pythonFile: 'synthia/lexicon/identity_mapping.py',
    verifiedVar: 'hash_identity_isomorphic = True'
  },
  {
    id: 'G_lex',
    name: '04_PLITHOGENIC_SIEVE (G_lex)',
    formula: 'G_lex(I_lexicon) = s_i',
    description: 'Constructs the generator function which reconstructs the original raw biological text sequence from the parsed lexicon categories. Enables high-fidelity semantic parsing.',
    pythonFile: 'synthia/lexicon/sieve_generator.py',
    verifiedVar: 'generator_roundtrip_conformance = 1.0'
  },
  {
    id: 'I_lexicon',
    name: '05_LEXICON_RESOLUTION (I_lexicon)',
    formula: 'I_lexicon is complete',
    description: 'Confirms that the resolved lexicon table is complete, containing all identified point mutations, classification weights, and associated taxonomic confidence score parameters.',
    pythonFile: 'synthia/core/resolver.py',
    verifiedVar: 'lexicon_conformance_complete = True'
  }
];

export const ModelTab: React.FC<ModelTabProps> = ({
  systemState,
  onAddLog,
  onUpdateStatus,
}) => {
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [isRepairing, setIsRepairing] = useState(false);
  const [repairProgress, setRepairProgress] = useState(0);
  const [isCorrupted, setIsCorrupted] = useState(true);
  const [memoryCells, setMemoryCells] = useState<string[]>([]);

  // Initialize simulated memory cells
  useEffect(() => {
    generateMemoryCells(isCorrupted);
  }, [isCorrupted]);

  const generateMemoryCells = (corrupt: boolean) => {
    const cells: string[] = [];
    const hexChars = '#2B2F336789ABCDEF';
    for (let i = 0; i < 64; i++) {
      let cellVal = '';
      for (let j = 0; j < 4; j++) {
        cellVal += hexChars[Math.floor(Math.random() * 16)];
      }
      cells.push(cellVal);
    }
    // Inject a corrupted red cell at cell index 42 if corrupt is true
    if (corrupt) {
      cells[42] = 'ERR0';
    }
    setMemoryCells(cells);
  };

  const handleNextStep = () => {
    setCurrentStepIdx((prev) => (prev + 1) % INVARIANT_STEPS.length);
    const node = INVARIANT_STEPS[(currentStepIdx + 1) % INVARIANT_STEPS.length];
    onAddLog('REPAIR', 'INFO', `Scanning ${node.name}: Checking formula ${node.formula}`);
  };

  const handleResetStep = () => {
    setCurrentStepIdx(0);
    onAddLog('REPAIR', 'INFO', 'Step sequencer reset to initial input state.');
  };

  const handleExecuteMemoryRepair = () => {
    if (isRepairing) return;
    setIsRepairing(true);
    onUpdateStatus('REPAIRING');
    onAddLog('REPAIR', 'WARN', 'CRITICAL DETECTED: Data divergence isolated in cellular block 0x2A (cell 42). Starting repair worker...');

    let progress = 0;
    const interval = setInterval(() => {
      progress += 5;
      setRepairProgress(progress);
      
      // Randomly change values of cells during sweep to simulate cellular scanning
      setMemoryCells(prev => prev.map((cell, idx) => {
        if (idx === 42 && progress < 90) return 'ERR0';
        if (idx === Math.floor((progress / 100) * 64)) {
          return 'SCAN';
        }
        return cell;
      }));

      if (progress >= 100) {
        clearInterval(interval);
        setIsRepairing(false);
        setIsCorrupted(false);
        onUpdateStatus('NOMINAL');
        onAddLog('REPAIR', 'SUCCESS', 'HIGH-PRECISION REPAIR SUCCEEDED: Point anomaly resolved. System memory restored to nominal database conformance.');
      }
    }, 100);
  };

  const handleInjectCorrupt = () => {
    setIsCorrupted(true);
    onUpdateStatus('DEGRADED');
    onAddLog('REPAIR', 'WARN', 'Anomalous point mutation injected. Database sector 0x2A reported cell divergence. System integrity state DEGRADED.');
  };

  const activeNode = INVARIANT_STEPS[currentStepIdx];

  return (
    <div className="space-y-6">
      
      {/* Page Description Banner */}
      <div className="glass rounded-3xl p-6 relative overflow-hidden transition-all-smooth">
        <div className="absolute top-0 right-0 bg-[#5AA7A3]/10 text-[#5AA7A3] text-[10px] font-mono px-3 py-1 border-b border-l border-white/10 rounded-bl-xl font-bold">
          1_MODEL_REPAIR
        </div>
        <h2 className="text-xl font-bold tracking-wider text-white mb-2 font-sans">
          High-Precision Taxonomic Memory Repair
        </h2>
        <p className="text-xs text-gray-400 max-w-4xl leading-relaxed font-sans">
          The SYNTHIA memory-repair layer acts as a semantic self-healing engine. It actively monitors the five fundamental mathematical invariants across the lexicon state. When cellular drift or bit-flips occur, the repair algorithm uses plithogenic equations to rebuild divergent database blocks.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Screen: Step-by-Step Invariant Stepper */}
        <div className="lg:col-span-7 space-y-6">
          <div className="glass rounded-3xl p-5 flex flex-col justify-between min-h-[480px] transition-all-smooth">
            <div>
              <div className="flex justify-between items-center border-b border-white/5 pb-3 mb-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                  <Cpu className="w-4 h-4 text-[#5AA7A3] mr-2 animate-pulse" />
                  INVARIANT PIPELINE STEPPER
                </h3>
                <div className="flex space-x-2">
                  <button 
                    onClick={handleResetStep}
                    className="p-1.5 border border-white/5 bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white rounded-lg transition-all duration-150"
                    title="Reset Sequencer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={handleNextStep}
                    className="px-4 py-1.5 border border-[#5AA7A3]/30 bg-[#5AA7A3]/10 text-[#5AA7A3] text-[10px] font-extrabold hover:bg-[#5AA7A3] hover:text-black uppercase rounded-full transition-all duration-150 cursor-pointer"
                  >
                    STEP PIPELINE →
                  </button>
                </div>
              </div>

              {/* Graphic Nodes representing Invariants */}
              <div className="grid grid-cols-5 gap-2.5 mb-6 font-mono text-center select-none">
                {INVARIANT_STEPS.map((step, idx) => {
                  const isActive = idx === currentStepIdx;
                  const isPassed = idx < currentStepIdx;
                  
                  return (
                    <div 
                      key={step.id}
                      onClick={() => {
                        setCurrentStepIdx(idx);
                        onAddLog('REPAIR', 'INFO', `Scanned ${step.name}: Checking formula ${step.formula}`);
                      }}
                      className={`p-3 border transition-all duration-300 cursor-pointer rounded-xl ${
                        isActive 
                          ? 'border-[#5AA7A3] bg-[#5AA7A3]/10 text-white shadow-[0_0_10px_rgba(0,242,255,0.15)] glow-border' 
                          : isPassed
                            ? 'border-[#8AB38B]/40 bg-[#8AB38B]/5 text-[#5AA7A3]'
                            : 'border-white/5 bg-white/2 text-gray-500 hover:border-white/20 hover:text-gray-300'
                      }`}
                    >
                      <div className="text-[9px] font-semibold mb-1 opacity-50">NODE</div>
                      <div className="text-sm font-bold tracking-wider">{step.id}</div>
                      <div className="text-[8px] mt-1.5 truncate max-w-full font-sans uppercase font-bold tracking-wider">
                        {isActive ? '● ACTIVE' : isPassed ? '✔ PASSED' : '○ READY'}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Active Step Details Pane */}
              <div className="p-4 bg-black/40 border border-white/5 rounded-2xl space-y-4">
                <div className="flex flex-col sm:flex-row justify-between sm:items-center border-b border-white/5 pb-2.5 text-xs">
                  <span className="font-bold text-gray-200 uppercase tracking-wider font-mono">{activeNode.name}</span>
                  <span className="text-[#5AA7A3] font-bold font-mono bg-[#5AA7A3]/10 px-2.5 py-0.5 rounded-full mt-1.5 sm:mt-0 border border-[#5AA7A3]/15">
                    FORMULA: {activeNode.formula}
                  </span>
                </div>

                <p className="text-gray-400 text-xs leading-relaxed font-sans">
                  {activeNode.description}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-[11px] font-mono">
                  <div className="p-3 bg-white/2 border border-white/5 rounded-xl">
                    <span className="text-gray-500 block uppercase text-[10px] font-semibold">VERIFIED_PYTHON_FILE:</span>
                    <span className="text-gray-200 mt-1 block break-all font-semibold">{activeNode.pythonFile}</span>
                  </div>

                  <div className="p-3 bg-white/2 border border-white/5 rounded-xl">
                    <span className="text-gray-500 block uppercase text-[10px] font-semibold">VERIFICATION_OUTCOME:</span>
                    <span className="text-[#5AA7A3] mt-1 block break-all font-bold glow-text">{activeNode.verifiedVar}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="border-t border-white/5 pt-3 mt-4 flex justify-between items-center text-xs text-gray-500 font-mono">
              <span>ACTIVE SCHEMA PASSED: NOMINAL_ALIGNED</span>
              <span className="flex items-center text-[#5AA7A3] font-semibold glow-text">
                <Check className="w-4 h-4 mr-1.5" />
                STRICT_INVARIANT = TRUE
              </span>
            </div>
          </div>
        </div>

        {/* Right Screen: High-Precision Cell Memory Matrix */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass rounded-3xl p-5 flex flex-col justify-between min-h-[480px] transition-all-smooth">
            <div>
              <div className="flex justify-between items-center border-b border-white/5 pb-3 mb-4 text-xs font-mono">
                <h3 className="font-bold text-white uppercase tracking-wider flex items-center">
                  <ShieldAlert className="w-4 h-4 text-[#5AA7A3] mr-2 animate-pulse" />
                  DATABASE SECTOR 0x2A GRID
                </h3>
                
                {isCorrupted ? (
                  <span className="text-amber-400 font-bold animate-pulse">● ANOMALY ISOLATED</span>
                ) : (
                  <span className="text-[#5AA7A3] font-bold glow-text">● NOMINAL STATE</span>
                )}
              </div>

              {isRepairing && (
                <div className="mb-4">
                  <div className="flex justify-between text-xs mb-1.5 font-mono">
                    <span className="text-amber-400 uppercase font-semibold">Sweeping memory sectors...</span>
                    <span className="text-[#5AA7A3] font-bold">{repairProgress}%</span>
                  </div>
                  <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-[#5AA7A3] transition-all duration-100 rounded-full" style={{ width: `${repairProgress}%` }} />
                  </div>
                </div>
              )}

              {/* Memory Hex Matrix Grid */}
              <div className="grid grid-cols-8 gap-1.5 font-mono text-[9px] leading-none mb-6">
                {memoryCells.map((cell, idx) => {
                  let cellBg = 'bg-black/30 text-gray-600 border-white/5 rounded-md';
                  
                  if (cell === 'ERR0') {
                    cellBg = 'bg-red-500/20 text-red-400 border-red-500/35 font-bold animate-pulse rounded-md shadow-[0_0_8px_rgba(239,68,68,0.2)]';
                  } else if (cell === 'SCAN') {
                    cellBg = 'bg-amber-400/20 text-amber-400 border-amber-400/30 rounded-md font-bold';
                  } else if (!isCorrupted) {
                    // Highlit restored state
                    if (idx === 42) {
                      cellBg = 'bg-[#5AA7A3]/20 text-[#5AA7A3] border-[#5AA7A3]/35 rounded-md font-bold glow-border';
                    }
                  }

                  return (
                    <div 
                      key={idx} 
                      className={`p-2 border text-center transition-all duration-150 relative group ${cellBg}`}
                      title={`Sector cell index ${idx}`}
                    >
                      <span>{cell}</span>
                    </div>
                  );
                })}
              </div>

              <div className="p-3 bg-black/40 border border-white/5 text-xs text-gray-400 leading-relaxed font-sans rounded-2xl">
                {isCorrupted ? (
                  <p>
                    Sector address <code className="text-amber-400 font-mono">0x2A</code> reported cellular corruption. The plithogenic checksum solver failed to match cell sequence hash <code className="text-amber-400 font-mono">ERR0</code> against reference formula. Click <strong className="text-white">"INITIATE MEMORY REPAIR"</strong> below.
                  </p>
                ) : (
                  <p className="text-[#5AA7A3]">
                    ✔ High-precision cell memory repair succeeded! Structural cell address <code className="text-[#5AA7A3] font-mono">0x2A</code> has been correctly reconstructed using plithogenic sibling matrix coefficients. Validation hash conformance checks passed.
                  </p>
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-white/5 flex space-x-2">
              {isCorrupted ? (
                <button
                  onClick={handleExecuteMemoryRepair}
                  disabled={isRepairing}
                  className={`w-full py-2.5 font-sans font-extrabold uppercase text-xs tracking-wider transition-all duration-300 rounded-full border ${
                    isRepairing
                      ? 'bg-white/5 text-amber-400 border-white/5 cursor-wait'
                      : 'bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] text-black border-none hover:opacity-95 shadow-[0_0_15px_rgba(0,242,255,0.25)] cursor-pointer'
                  }`}
                >
                  {isRepairing ? 'RECONCILING SECTOR...' : 'INITIATE MEMORY REPAIR'}
                </button>
              ) : (
                <button
                  onClick={handleInjectCorrupt}
                  className="w-full py-2.5 bg-black/40 hover:bg-red-500/10 text-gray-400 hover:text-red-400 border border-white/5 hover:border-red-500/20 rounded-full font-sans font-bold uppercase text-xs tracking-wider transition-all cursor-pointer"
                >
                  INJECT POINT ANOMALY
                </button>
              )}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
