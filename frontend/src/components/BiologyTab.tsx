import React, { useState, useEffect } from 'react';
import { BiologicalSequence } from '../types';
import { Dna, ShieldCheck, Play, HelpCircle, AlertTriangle, RefreshCw, Layers } from 'lucide-react';

interface BiologyTabProps {
  onAddLog: (category: 'SYS' | 'I_LEX' | 'PHYLO' | 'REPAIR', level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR', text: string) => void;
}

const PRESET_STRAINS: BiologicalSequence[] = [
  {
    id: 'seq-01',
    geneName: 'INFLUENZA_A_S_INV',
    rawSequence: 'ATGCGTACTAGCTAGCTAGCTAGC',
    mutatedSequence: 'ATGCGTACTAGCTAGCTAGCTAGC', // Nominal
    divergenceFactor: 0.00,
    alignmentScore: 100,
    validationStatus: 'NOMINAL'
  },
  {
    id: 'seq-02',
    geneName: 'COV_SPIKE_PLITHOGENIC',
    rawSequence: 'ATGCGTACTAGCTAGCTAGCTAGC',
    mutatedSequence: 'ATGCGTACTAGCAAGCTAGCTAGC', // point mutation at index 13 ('T' -> 'A')
    divergenceFactor: 4.17,
    alignmentScore: 95.8,
    validationStatus: 'ALERT'
  },
  {
    id: 'seq-03',
    geneName: 'ECOLI_PLASMID_ALPHA',
    rawSequence: 'ATGCGTACTAGCTAGCTAGCTAGC',
    mutatedSequence: 'ACGCGTACTAGCTAACTAGCTAGC', // point mutations at index 1 ('T' -> 'C') and index 14 ('G' -> 'A')
    divergenceFactor: 8.33,
    alignmentScore: 91.7,
    validationStatus: 'ALERT'
  }
];

export const BiologyTab: React.FC<BiologyTabProps> = ({ onAddLog }) => {
  const [strains, setStrains] = useState<BiologicalSequence[]>(PRESET_STRAINS);
  const [selectedStrainId, setSelectedStrainId] = useState<string>('seq-02');
  const [sourceSeq, setSourceSeq] = useState('ATGCGTACTAGCTAGCTAGCTAGC');
  const [mutatedSeq, setMutatedSeq] = useState('ATGCGTACTAGCAAGCTAGCTAGC');
  const [isAligning, setIsAligning] = useState(false);
  const [alignmentResult, setAlignmentResult] = useState<{
    divergence: number;
    score: number;
    matches: string;
    diffCount: number;
    status: 'NOMINAL' | 'ALERT';
  } | null>(null);

  useEffect(() => {
    const strain = strains.find(s => s.id === selectedStrainId);
    if (strain) {
      setSourceSeq(strain.rawSequence);
      setMutatedSeq(strain.mutatedSequence);
      setAlignmentResult(null);
    }
  }, [selectedStrainId, strains]);

  // Real client-side biological aligner (computes character mutations & matching visual strings)
  const runSequenceAlignment = () => {
    setIsAligning(true);
    onAddLog('PHYLO', 'INFO', `Running multi-attribute alignment on source sequence...`);

    setTimeout(() => {
      const len = Math.max(sourceSeq.length, mutatedSeq.length);
      let matchStr = '';
      let diffs = 0;

      for (let i = 0; i < len; i++) {
        const charA = sourceSeq[i] || '-';
        const charB = mutatedSeq[i] || '-';

        if (charA === charB) {
          matchStr += '|'; // Match symbol
        } else {
          matchStr += 'X'; // Mismatch symbol
          diffs++;
        }
      }

      const divergence = parseFloat(((diffs / len) * 100).toFixed(2));
      const score = parseFloat((100 - divergence).toFixed(1));
      const status = divergence > 0 ? 'ALERT' : 'NOMINAL';

      setAlignmentResult({
        divergence,
        score,
        matches: matchStr,
        diffCount: diffs,
        status
      });

      // Update the active list item
      setStrains(prev => prev.map(s => {
        if (s.id === selectedStrainId) {
          return {
            ...s,
            rawSequence: sourceSeq,
            mutatedSequence: mutatedSeq,
            divergenceFactor: divergence,
            alignmentScore: score,
            validationStatus: status === 'NOMINAL' ? 'NOMINAL' : 'ALERT'
          };
        }
        return s;
      }));

      setIsAligning(false);

      if (diffs > 0) {
        onAddLog('PHYLO', 'WARN', `Alignment completed. Point mutations identified: ${diffs} nucleotides divergent. Plithogenic guardrails ACTIVE.`);
      } else {
        onAddLog('PHYLO', 'SUCCESS', `Alignment completed. Full sequence alignment achieved. Divergence level: 0.00%.`);
      }
    }, 600);
  };

  const handleForceSynthesis = () => {
    onAddLog('PHYLO', 'INFO', `Invoking phylo-plithogenic consensus synthesis...`);
    setIsAligning(true);

    setTimeout(() => {
      // Force mutated sequence back to match source sequence
      setMutatedSeq(sourceSeq);
      
      const len = sourceSeq.length;
      const matchStr = '|'.repeat(len);

      setAlignmentResult({
        divergence: 0.00,
        score: 100,
        matches: matchStr,
        diffCount: 0,
        status: 'NOMINAL'
      });

      setStrains(prev => prev.map(s => {
        if (s.id === selectedStrainId) {
          return {
            ...s,
            mutatedSequence: sourceSeq,
            divergenceFactor: 0.00,
            alignmentScore: 100,
            validationStatus: 'NOMINAL'
          };
        }
        return s;
      }));

      setIsAligning(false);
      onAddLog('PHYLO', 'SUCCESS', `Consensus synthesis complete. DNA Invariant I established. Validation status: NOMINAL.`);
    }, 800);
  };

  const handleRandomMutation = () => {
    const bases = ['A', 'T', 'G', 'C'];
    const seqArray = sourceSeq.split('');
    const randomIndex = Math.floor(Math.random() * seqArray.length);
    const currentBase = seqArray[randomIndex];
    const pool = bases.filter(b => b !== currentBase);
    const newBase = pool[Math.floor(Math.random() * pool.length)];
    seqArray[randomIndex] = newBase;
    
    setMutatedSeq(seqArray.join(''));
    setAlignmentResult(null);
    onAddLog('PHYLO', 'INFO', `Injected arbitrary point mutation at nucleotide index ${randomIndex} (${currentBase} -> ${newBase})`);
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="glass rounded-3xl p-6 relative overflow-hidden transition-all-smooth">
        <div className="absolute top-0 right-0 bg-[#5AA7A3]/10 text-[#5AA7A3] text-[10px] font-mono px-3 py-1 border-b border-l border-white/10 rounded-bl-xl font-bold">
          3_BIOLOGY_PHYLO
        </div>
        <h2 className="text-xl font-bold tracking-wider text-white mb-2 font-sans">
          Phylo-plithogenic Sequence Alignment & Review
        </h2>
        <p className="text-xs text-gray-400 max-w-4xl leading-relaxed font-sans">
          Phylo-plithogenic review packets test taxonomic integrity across evolutionary boundaries. This sandbox executes local multi-attribute alignment to identify point mutation anomalies and resolve consensus drift inside biological sequence arrays.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Screen: Sequence Input Controls */}
        <div className="lg:col-span-6 space-y-6">
          <div className="glass rounded-3xl p-5 transition-all-smooth">
            <div className="flex justify-between items-center border-b border-white/5 pb-3 mb-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                <Dna className="w-4 h-4 text-[#5AA7A3] mr-2 animate-pulse" />
                SEQUENCE COMPARISON CONFIG
              </h3>
              
              <select
                value={selectedStrainId}
                onChange={(e) => setSelectedStrainId(e.target.value)}
                className="bg-black/50 text-white font-mono text-xs p-2 border border-white/10 focus:border-[#5AA7A3] focus:outline-none rounded-xl"
              >
                {strains.map(s => (
                  <option key={s.id} value={s.id}>{s.geneName} ({s.validationStatus})</option>
                ))}
              </select>
            </div>

            <div className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-gray-400 mb-1.5 uppercase tracking-wide font-sans font-semibold">A_SOURCE NUCLEOTIDE CHAIN (REFERENCE):</label>
                <input 
                  type="text"
                  value={sourceSeq}
                  onChange={(e) => {
                    setSourceSeq(e.target.value.toUpperCase());
                    setAlignmentResult(null);
                  }}
                  className="w-full bg-black/40 text-gray-200 p-3 border border-white/5 focus:border-[#5AA7A3]/40 focus:outline-none tracking-widest font-black uppercase rounded-xl"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="block text-gray-400 uppercase tracking-wide font-sans font-semibold">B_MUTATED NUCLEOTIDE CHAIN:</label>
                  <button 
                    onClick={handleRandomMutation}
                    className="text-[10px] text-[#5AA7A3] font-bold hover:underline hover:text-white cursor-pointer"
                  >
                    + INJECT POINT MUTATION
                  </button>
                </div>
                <input 
                  type="text"
                  value={mutatedSeq}
                  onChange={(e) => {
                    setMutatedSeq(e.target.value.toUpperCase());
                    setAlignmentResult(null);
                  }}
                  className="w-full bg-black/40 text-gray-200 p-3 border border-white/5 focus:border-[#5AA7A3]/40 focus:outline-none tracking-widest font-black uppercase rounded-xl"
                />
              </div>

              <div className="pt-4 border-t border-white/5 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
                <button
                  onClick={runSequenceAlignment}
                  disabled={isAligning}
                  className={`flex-1 py-2.5 font-sans font-extrabold uppercase text-xs tracking-wider border transition-all duration-300 rounded-full cursor-pointer ${
                    isAligning
                      ? 'bg-white/5 text-amber-400 border-white/5 cursor-wait'
                      : 'bg-white text-black border-none hover:opacity-90'
                  }`}
                >
                  RUN ALIGNMENT SEQUENCE
                </button>

                <button
                  onClick={handleForceSynthesis}
                  disabled={isAligning}
                  className={`flex-1 py-2.5 font-sans font-extrabold uppercase text-xs tracking-wider border transition-all duration-300 rounded-full cursor-pointer ${
                    isAligning
                      ? 'bg-white/5 text-amber-400 border-white/5 cursor-wait'
                      : 'bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] text-black border-none hover:opacity-95 shadow-[0_0_15px_rgba(0,242,255,0.25)]'
                  }`}
                >
                  FORCE SYNTHESIS CONSENSUS
                </button>
              </div>
            </div>
          </div>

          {/* Mutation Warning / Info */}
          <div className="glass rounded-3xl p-5 text-xs transition-all-smooth">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center">
              <AlertTriangle className="w-4 h-4 text-amber-400 mr-2" />
              PLITHOGENIC ALIGNMENT GUARD
            </h4>
            <p className="text-gray-400 leading-relaxed font-sans">
              Educational research strains shouldn't drift more than 15% divergence to respect core mathematical parameters. Run alignment checks, analyze mismatch indexes, and execute consensus synthesis to align system memory.
            </p>
          </div>
        </div>

        {/* Right Screen: Sequence Diff Viewer & Summary */}
        <div className="lg:col-span-6 space-y-6">
          <div className="glass rounded-3xl p-5 flex flex-col justify-between min-h-[380px] font-mono transition-all-smooth">
            <div>
              <div className="flex justify-between items-center text-xs text-gray-500 border-b border-white/5 pb-2.5 mb-4 uppercase tracking-wider">
                <span>MUTATION CHAIN INSPECTOR</span>
                <span className="font-bold">STATE: {alignmentResult ? alignmentResult.status : 'AWAITING RUN'}</span>
              </div>

              {alignmentResult ? (
                <div className="space-y-6 text-xs font-mono">
                  
                  {/* Sequence Comparison Alignment Display */}
                  <div className="p-4 bg-black/40 border border-white/5 overflow-x-auto rounded-2xl">
                    <div className="grid grid-cols-12 gap-x-2 text-center select-none font-bold">
                      <div className="col-span-3 text-left text-gray-500 uppercase text-[10px]">Reference:</div>
                      <div className="col-span-9 text-gray-300 tracking-[0.55em] text-xs font-semibold break-all text-left uppercase">
                        {sourceSeq}
                      </div>
                    </div>

                    <div className="grid grid-cols-12 gap-x-2 text-center select-none py-1.5">
                      <div className="col-span-3 text-left text-gray-500 uppercase text-[10px]">Alignment:</div>
                      <div className="col-span-9 text-[#5AA7A3] tracking-[0.55em] text-xs font-bold text-left break-all animate-pulse glow-text">
                        {alignmentResult.matches}
                      </div>
                    </div>

                    <div className="grid grid-cols-12 gap-x-2 text-center select-none font-bold">
                      <div className="col-span-3 text-left text-gray-500 uppercase text-[10px]">Mutation:</div>
                      <div className="col-span-9 text-white tracking-[0.55em] text-xs font-semibold break-all text-left uppercase">
                        {mutatedSeq}
                      </div>
                    </div>
                  </div>

                  {/* Scientific Summary Statistics */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3.5 bg-white/2 border border-white/5 rounded-xl">
                      <div className="text-[10px] text-gray-500 uppercase font-semibold">MUTATION COUNT</div>
                      <div className="text-xl font-bold text-white mt-1">
                        {alignmentResult.diffCount} <span className="text-[11px] font-normal text-gray-500 font-sans">nucleotides</span>
                      </div>
                    </div>

                    <div className="p-3.5 bg-white/2 border border-white/5 rounded-xl">
                      <div className="text-[10px] text-gray-500 uppercase font-semibold">SEQUENCE INTEGRITY</div>
                      <div className="text-xl font-bold text-[#5AA7A3] glow-text mt-1 font-mono">
                        {alignmentResult.score}%
                      </div>
                    </div>

                    <div className="p-3.5 bg-white/2 border border-white/5 rounded-xl">
                      <div className="text-[10px] text-gray-500 uppercase font-semibold">DIVERGENCE FACTOR</div>
                      <div className="text-xl font-bold text-white mt-1">
                        {alignmentResult.divergence}%
                      </div>
                    </div>

                    <div className="p-3.5 bg-white/2 border border-white/5 rounded-xl">
                      <div className="text-[10px] text-gray-500 uppercase font-semibold">ALIGNMENT INDEXES</div>
                      <div className="text-xl font-bold text-white mt-1">
                        0 .. {Math.max(sourceSeq.length, mutatedSeq.length) - 1}
                      </div>
                    </div>
                  </div>

                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                  <Layers className="w-10 h-10 mb-3 text-white/5 animate-pulse" />
                  <p className="text-xs font-semibold">AWAITING COMPARATIVE CONFORMANCE RUN</p>
                  <p className="text-[10px] text-gray-600 mt-1 uppercase">Click "RUN ALIGNMENT SEQUENCE" above to execute alignment</p>
                </div>
              )}
            </div>

            <div className="border-t border-white/5 pt-3 mt-4 flex justify-between items-center text-xs text-gray-500">
              <span>BLAST CLUSTERING MODEL: MULTI-ATTRIBUTE</span>
              <span className="flex items-center text-[#5AA7A3] font-semibold glow-text">
                <ShieldCheck className="w-4 h-4 mr-1.5" />
                CONFORMANCE ACTIVE
              </span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
