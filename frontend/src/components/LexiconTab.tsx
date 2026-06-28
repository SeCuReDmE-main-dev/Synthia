import React, { useState, useEffect } from 'react';
import { LexiconPayload } from '../types';
import { Terminal, Cpu, Play, HelpCircle, Save, AlertTriangle, Layers, TrendingUp } from 'lucide-react';

interface LexiconTabProps {
  onAddLog: (category: 'SYS' | 'I_LEX' | 'PHYLO' | 'REPAIR', level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR', text: string) => void;
  onUpdateConsensus: (score: number) => void;
}

const DEFAULT_PAYLOADS: LexiconPayload[] = [
  {
    id: 'pay-001',
    name: 'STX-NOMINAL-TAXON_A',
    rawText: `{
  "sequence_id": "STX-9821-NOMINAL",
  "strain_type": "Plithogenic Variant Delta",
  "genetic_markers": ["ATGCTAA", "GCGCTAC", "TAATATA"],
  "validation_hash": "0x9dfd24ef289a74",
  "system_check": {
    "invariant_equality": true,
    "redundancy_count": 4
  }
}`,
    timestamp: '14:25:01',
    metrics: { tokenCount: 38, entropy: 4.85, latencyMs: 24, contradictionsCount: 0 },
    classificationChain: [
      { node: 'Local System Cache', value: 'CACHE_HIT', confidence: 0.999, status: 'passed' },
      { node: 'Semantic Lexer', value: 'NOMINAL', confidence: 0.985, status: 'passed' },
      { node: 'Plithogenic Sieve', value: '0_CONTRAD', confidence: 0.992, status: 'passed' },
      { node: 'Invariant Guard', value: 'STRICT_PASS', confidence: 1.000, status: 'passed' }
    ]
  },
  {
    id: 'pay-002',
    name: 'STX-MUTATED-BETA_3',
    rawText: `{
  "sequence_id": "STX-8412-MUTATED",
  "strain_type": "Divergent Beta 3 Strain",
  "genetic_markers": ["ATGCTAA", "GCGCGAC", "TAATATA"],
  "validation_hash": "0x3af420ef118c22",
  "system_check": {
    "invariant_equality": false,
    "redundancy_count": 2
  }
}`,
    timestamp: '15:10:32',
    metrics: { tokenCount: 40, entropy: 5.12, latencyMs: 65, contradictionsCount: 1 },
    classificationChain: [
      { node: 'Local System Cache', value: 'CACHE_MISS', confidence: 0.000, status: 'warning' },
      { node: 'Semantic Lexer', value: 'ENTROPY_HIGH', confidence: 0.912, status: 'passed' },
      { node: 'Plithogenic Sieve', value: '1_CONTRAD_FOUND', confidence: 0.895, status: 'warning' },
      { node: 'Invariant Guard', value: 'RECONCILED', confidence: 0.978, status: 'passed' }
    ]
  },
  {
    id: 'pay-003',
    name: 'STX-CRITICAL-FLIP',
    rawText: `{
  "sequence_id": "STX-0010-CRITICAL",
  "strain_type": "Bitflip Contradictory Strain",
  "genetic_markers": ["GTTTTTT", "XXXXXXX", "NULL_PTR"],
  "validation_hash": "0x00000000000000",
  "system_check": {
    "invariant_equality": false,
    "redundancy_count": 0
  }
}`,
    timestamp: '16:01:45',
    metrics: { tokenCount: 35, entropy: 3.42, latencyMs: 142, contradictionsCount: 3 },
    classificationChain: [
      { node: 'Local System Cache', value: 'ERR_SOCKET', confidence: 0.000, status: 'failed' },
      { node: 'Semantic Lexer', value: 'INVALID_LEX', confidence: 0.640, status: 'failed' },
      { node: 'Plithogenic Sieve', value: 'CRITICAL_DRIFT', confidence: 0.450, status: 'failed' },
      { node: 'Invariant Guard', value: 'FAIL_HALT', confidence: 0.000, status: 'failed' }
    ]
  }
];

export const LexiconTab: React.FC<LexiconTabProps> = ({ onAddLog, onUpdateConsensus }) => {
  const [payloads, setPayloads] = useState<LexiconPayload[]>(DEFAULT_PAYLOADS);
  const [selectedPayloadId, setSelectedPayloadId] = useState<string>('pay-001');
  const [editorText, setEditorText] = useState<string>(DEFAULT_PAYLOADS[0].rawText);
  const [activePayload, setActivePayload] = useState<LexiconPayload>(DEFAULT_PAYLOADS[0]);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);

  useEffect(() => {
    const found = payloads.find(p => p.id === selectedPayloadId);
    if (found) {
      setEditorText(found.rawText);
      setActivePayload(found);
    }
  }, [selectedPayloadId, payloads]);

  // Real client-side Shannon Entropy Calculator
  const calculateShannonEntropy = (str: string): number => {
    if (!str) return 0;
    const freqs: { [key: string]: number } = {};
    for (let i = 0; i < str.length; i++) {
      const char = str[i];
      freqs[char] = (freqs[char] || 0) + 1;
    }
    let entropy = 0;
    const len = str.length;
    for (const char in freqs) {
      const p = freqs[char] / len;
      entropy -= p * Math.log2(p);
    }
    return parseFloat(entropy.toFixed(3));
  };

  const handleRunEntropyAnalysis = () => {
    setIsCalculating(true);
    onAddLog('I_LEX', 'INFO', `Parsing raw payload text for entropy analysis...`);

    setTimeout(() => {
      // Calculate token length roughly
      const tokenCount = editorText.trim().split(/\s+/).filter(Boolean).length;
      const shannonEntropy = calculateShannonEntropy(editorText);
      
      // Determine contradictions based on keywords
      let contradictionCount = 0;
      if (editorText.toLowerCase().includes('"invariant_equality": false')) contradictionCount += 1;
      if (editorText.toLowerCase().includes('"redundancy_count": 0') || editorText.includes('NULL')) contradictionCount += 1;
      if (editorText.toLowerCase().includes('xxxx')) contradictionCount += 1;

      // Simulate classification chain
      let cacheStatus: 'passed' | 'warning' | 'failed' = 'passed';
      let cacheVal = 'CACHE_HIT';
      let sieveStatus: 'passed' | 'warning' | 'failed' = 'passed';
      let sieveVal = '0_CONTRAD';
      let guardStatus: 'passed' | 'warning' | 'failed' = 'passed';
      let guardVal = 'STRICT_PASS';

      if (shannonEntropy > 5.0) {
        cacheStatus = 'warning';
        cacheVal = 'CACHE_MISS';
      }
      if (contradictionCount === 1) {
        sieveStatus = 'warning';
        sieveVal = '1_CONTRAD_FOUND';
        guardVal = 'RECONCILED';
      } else if (contradictionCount > 1) {
        cacheStatus = 'failed';
        cacheVal = 'ERR_SOCKET';
        sieveStatus = 'failed';
        sieveVal = 'CRITICAL_DRIFT';
        guardStatus = 'failed';
        guardVal = 'FAIL_HALT';
      }

      const calculatedPayload: LexiconPayload = {
        id: `pay-user-${Date.now().toString().slice(-4)}`,
        name: `USER-ANALYZED-${Date.now().toString().slice(-3)}`,
        rawText: editorText,
        timestamp: new Date().toLocaleTimeString(),
        metrics: {
          tokenCount,
          entropy: shannonEntropy,
          latencyMs: Math.floor(15 + Math.random() * 45 + contradictionCount * 30),
          contradictionsCount: contradictionCount
        },
        classificationChain: [
          { node: 'Local System Cache', value: cacheVal, confidence: cacheStatus === 'passed' ? 0.999 : 0.000, status: cacheStatus },
          { node: 'Semantic Lexer', value: shannonEntropy > 4.8 ? 'ENTROPY_HIGH' : 'NOMINAL', confidence: 0.945, status: 'passed' },
          { node: 'Plithogenic Sieve', value: sieveVal, confidence: sieveStatus === 'passed' ? 0.995 : 0.760, status: sieveStatus },
          { node: 'Invariant Guard', value: guardVal, confidence: guardStatus === 'passed' ? 1.000 : 0.000, status: guardStatus }
        ]
      };

      // Add to list, select it
      setPayloads(prev => [calculatedPayload, ...prev.filter(p => !p.id.startsWith('pay-user'))]);
      setActivePayload(calculatedPayload);
      setIsCalculating(false);

      // Adjust overall system consensus score based on entropy quality
      const nextConsensus = Math.max(0.724, Math.min(0.999, 0.9942 - (contradictionCount * 0.08)));
      onUpdateConsensus(nextConsensus);

      if (contradictionCount > 0) {
        onAddLog('I_LEX', 'WARN', `Entropy analysis complete. Warning: ${contradictionCount} semantic contradictions isolated in strain.`);
      } else {
        onAddLog('I_LEX', 'SUCCESS', `Entropy analysis complete. Shannon Entropy: ${shannonEntropy} sh. Complete semantic validation PASSED.`);
      }

    }, 800);
  };

  const handleSaveAsSample = () => {
    const newSampleName = `STX-SAVED-${Date.now().toString().slice(-4)}`;
    const newSample: LexiconPayload = {
      ...activePayload,
      id: `pay-user-${Date.now().toString().slice(-4)}`,
      name: newSampleName,
      rawText: editorText
    };
    setPayloads(prev => [newSample, ...prev]);
    setSelectedPayloadId(newSample.id);
    onAddLog('I_LEX', 'SUCCESS', `Saved current payload configuration as: ${newSampleName}`);
  };

  return (
    <div className="space-y-6">
      
      {/* Tab Header Card */}
      <div className="glass rounded-3xl p-6 relative overflow-hidden transition-all-smooth">
        <div className="absolute top-0 right-0 bg-[#5AA7A3]/10 text-[#5AA7A3] text-[10px] font-mono px-3 py-1 border-b border-l border-white/10 rounded-bl-xl font-bold">
          2_I_LEXICON
        </div>
        <h2 className="text-xl font-bold tracking-wider text-white mb-2 font-sans">
          Dynamic Lexicon & Entropy Parsing Engine
        </h2>
        <p className="text-xs text-gray-400 max-w-4xl leading-relaxed font-sans">
          The <code className="text-[#5AA7A3] font-mono font-bold">I_lexicon</code> processing layer isolates semantic divergence and calculates exact token-level Shannon entropy across raw input payloads. It maps strings through a deterministic sequence pipeline to satisfy mathematical invariant checks.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Grid: Payload Select and Code Editor */}
        <div className="lg:col-span-7 space-y-6">
          <div className="glass rounded-3xl p-5 flex flex-col justify-between h-full min-h-[500px] transition-all-smooth">
            <div>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/5 pb-3 mb-4 space-y-2 sm:space-y-0">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                  <Terminal className="w-4 h-4 text-[#5AA7A3] mr-2 animate-pulse" />
                  PAYLOAD SOURCE EDITOR
                </h3>
                
                <div className="flex space-x-2 w-full sm:w-auto">
                  <select 
                    value={selectedPayloadId}
                    onChange={(e) => setSelectedPayloadId(e.target.value)}
                    className="bg-black/50 text-white font-mono text-xs p-2 border border-white/10 focus:border-[#5AA7A3] focus:outline-none rounded-xl"
                  >
                    {payloads.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                  <button
                    onClick={handleSaveAsSample}
                    className="p-2 bg-white/5 hover:bg-white/10 text-gray-400 hover:text-[#5AA7A3] border border-white/5 rounded-xl transition cursor-pointer"
                    title="Save current payload as new template"
                  >
                    <Save className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Editable area */}
              <div className="relative font-mono">
                <textarea
                  value={editorText}
                  onChange={(e) => setEditorText(e.target.value)}
                  className="w-full h-[320px] bg-black/40 text-xs text-gray-200 p-3.5 border border-white/5 focus:border-[#5AA7A3]/40 focus:outline-none focus:ring-0 leading-relaxed font-mono resize-none rounded-2xl"
                  placeholder="Paste JSON or biological sequences here..."
                />
                <div className="absolute bottom-3 right-3 text-[9px] text-gray-500 uppercase select-none font-bold">
                  L:{editorText.split('\n').length} | C:{editorText.length}
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center border-t border-white/5 pt-3 mt-4">
              <span className="text-[10px] text-gray-500 font-mono font-semibold uppercase tracking-wider">
                COMPUTE LAYER: DETERMINISTIC ENTROPY SOLVER
              </span>
              <button
                onClick={handleRunEntropyAnalysis}
                disabled={isCalculating}
                className={`px-6 py-2.5 font-sans font-extrabold uppercase text-xs tracking-wider transition-all duration-300 rounded-full border ${
                  isCalculating
                    ? 'bg-white/5 text-amber-400 border-white/5 cursor-wait animate-pulse'
                    : 'bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] text-black border-none hover:opacity-95 shadow-[0_0_15px_rgba(0,242,255,0.25)] cursor-pointer'
                }`}
              >
                {isCalculating ? 'COMPUTING ENTROPY...' : 'RUN PARSE ENTROPY'}
              </button>
            </div>
          </div>
        </div>

        {/* Right Grid: Metrics Dashboard & Node diagram */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Active Payload Real-time Metrics */}
          <div className="glass rounded-3xl p-5 transition-all-smooth">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center">
              <TrendingUp className="w-4 h-4 text-[#5AA7A3] mr-2 animate-pulse" />
              SOLVER REAL-TIME METRICS
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-black/40 border border-white/5 rounded-2xl">
                <div className="text-[10px] text-gray-500 font-mono font-bold tracking-wider">SHANNON ENTROPY (H)</div>
                <div className="text-2xl font-black text-[#5AA7A3] glow-text font-mono mt-1">
                  {activePayload.metrics.entropy} <span className="text-xs font-normal text-gray-500 font-sans">sh</span>
                </div>
              </div>

              <div className="p-4 bg-black/40 border border-white/5 rounded-2xl">
                <div className="text-[10px] text-gray-500 font-mono font-bold tracking-wider">PARSE LATENCY (t)</div>
                <div className="text-2xl font-black text-gray-200 font-mono mt-1">
                  {activePayload.metrics.latencyMs} <span className="text-xs font-normal text-gray-500 font-sans">ms</span>
                </div>
              </div>

              <div className="p-4 bg-black/40 border border-white/5 rounded-2xl">
                <div className="text-[10px] text-gray-500 font-mono font-bold tracking-wider">ISOLATED DRIFTS</div>
                <div className={`text-2xl font-black font-mono mt-1 ${activePayload.metrics.contradictionsCount > 0 ? 'text-amber-400' : 'text-[#5AA7A3] glow-text'}`}>
                  {activePayload.metrics.contradictionsCount}
                </div>
              </div>

              <div className="p-4 bg-black/40 border border-white/5 rounded-2xl">
                <div className="text-[10px] text-gray-500 font-mono font-bold tracking-wider">TOKEN LENGTH</div>
                <div className="text-2xl font-black text-gray-200 font-mono mt-1">
                  {activePayload.metrics.tokenCount} <span className="text-xs font-normal text-gray-500 font-sans">tokens</span>
                </div>
              </div>
            </div>
          </div>

          {/* Graphical Node Schematic of Classification Chain */}
          <div className="glass rounded-3xl p-5 relative overflow-hidden transition-all-smooth">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center">
              <Layers className="w-4 h-4 text-[#5AA7A3] mr-2" />
              CLASSIFICATION CHAIN SCHEMA
            </h3>

            <div className="space-y-3 relative font-mono text-xs">
              {activePayload.classificationChain.map((chain, index) => {
                let statusBg = 'border-white/5 bg-black/20 rounded-2xl';
                let valueColor = 'text-gray-400';

                if (chain.status === 'passed') {
                  statusBg = 'border-[#5AA7A3]/30 bg-[#5AA7A3]/5 rounded-2xl';
                  valueColor = 'text-[#5AA7A3]';
                } else if (chain.status === 'warning') {
                  statusBg = 'border-amber-500/25 bg-amber-500/5 rounded-2xl';
                  valueColor = 'text-amber-400';
                } else if (chain.status === 'failed') {
                  statusBg = 'border-red-500/25 bg-red-500/5 rounded-2xl';
                  valueColor = 'text-red-400 font-bold';
                }

                return (
                  <div key={index} className="relative">
                    {/* Visual linking line */}
                    {index < activePayload.classificationChain.length - 1 && (
                      <div className="absolute left-[20px] top-[28px] bottom-[-24px] w-0.5 bg-white/5" />
                    )}

                    <div className={`p-3.5 border transition-all duration-300 flex justify-between items-center ${statusBg}`}>
                      <div className="flex items-center space-x-3.5">
                        {/* Number Indicator */}
                        <div className={`w-7 h-7 border border-current text-xs font-extrabold flex items-center justify-center rounded-full ${valueColor}`}>
                          {index + 1}
                        </div>
                        <div>
                          <div className="font-bold text-gray-200 text-[11px] uppercase tracking-wider">{chain.node}</div>
                          <div className="text-[9px] text-gray-500 font-bold mt-0.5">
                            CONFIDENCE: {(chain.confidence * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <span className={`text-[9px] font-extrabold px-2.5 py-0.5 border border-current uppercase rounded-full tracking-wider ${valueColor}`}>
                          {chain.value}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
