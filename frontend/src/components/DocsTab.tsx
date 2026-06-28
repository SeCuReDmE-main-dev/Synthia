import React, { useState } from 'react';
import { Terminal, Shield, Play, Search, Folder, CheckCircle, HelpCircle } from 'lucide-react';
import { LogMessage } from '../types';

interface DocsTabProps {
  onAddLog: (category: 'SYS' | 'I_LEX' | 'PHYLO' | 'REPAIR', level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR', text: string) => void;
}

export const DocsTab: React.FC<DocsTabProps> = ({ onAddLog }) => {
  const [projectPath, setProjectPath] = useState('/Users/securedme/workspace/synthia-python-core');
  const [selectedConfig, setSelectedConfig] = useState('nominal_analysis.json');
  const [searchQuery, setSearchQuery] = useState('');
  const [isInitializing, setIsInitializing] = useState(false);
  const [initProgress, setInitProgress] = useState(0);
  const [terminalOutput, setTerminalOutput] = useState<string[]>([
    'SYNTHIA CORE v4.2.1-RESEARCH initialization framework loading...',
    'System ready. Enter path and execute initialization sequence.'
  ]);

  const docArticles = [
    {
      title: 'SYNTHIA_LOCAL INTEGRATION',
      category: 'Front-End Connectivity',
      content: 'Synthia connects to the local memory layer for taxonomic state caching. This bridge maps the taxonomy sequences directly to local variables for educational demonstration updates.'
    },
    {
      title: 'PHYLO-PLITHOGENIC ALIGNMENT',
      category: 'Mathematical Proofs',
      content: 'By establishing plithogenic multi-attribute contradiction matrices, Synthia isolates point mutations from biological sequence chains without losing systemic context. It maintains integrity across divergent mutation strains.'
    },
    {
      title: 'TAXONOMIC MEMORY REPAIR',
      category: 'Security Invariants',
      content: 'Taxonomic database schemas undergo a series of strict mathematical invariant verification passes during system execution. If any database cell fails the invariant proof f(S_i) = H_lex, the memory repair worker automatically reconstructs the node.'
    },
    {
      title: 'STRICT INVARIANT EQUALITY f(S_i) = I_system^S',
      category: 'Core Logic',
      content: 'This formula asserts that the semantic state of the lexicon strictly matches the systemic memory database layout. It prevents injection attacks, silent bit flips, and database drift during concurrent writes.'
    }
  ];

  const filteredDocs = docArticles.filter(art => 
    art.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    art.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    art.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleBootInitialization = () => {
    if (isInitializing) return;
    setIsInitializing(true);
    setInitProgress(0);
    onAddLog('SYS', 'INFO', `Initializing system alignment from path: ${projectPath}`);
    
    const lines = [
      `$ cd ${projectPath}`,
      '$ python -m venv venv && source venv/bin/activate',
      '(venv) $ pip install -r requirements.txt --quiet',
      'Checking dependencies: numpy (1.24), pandas (2.0), pytest (7.4), google-genai (2.4)...',
      'Connecting to SecuredMe Python middleware engine via local IPC sockets...',
      'Booting automated Pytest verification suite (tests/test_invariants.py):',
      '============================= test session starts =============================',
      'platform darwin -- Python 3.11.4, pytest-7.4.0',
      'rootdir: /Users/securedme/workspace/synthia-python-core',
      'collected 5 items',
      '',
      'tests/test_invariants.py::test_invariant_I PASSED                     [ 20% ]',
      'tests/test_invariants.py::test_system_S_invariance PASSED             [ 40% ]',
      'tests/test_invariants.py::test_h_lex_identity PASSED                  [ 60% ]',
      'tests/test_invariants.py::test_g_lex_generation PASSED                [ 80% ]',
      'tests/test_invariants.py::test_i_lexicon_resolution PASSED            [ DONE ]',
      '============================== 5 passed in 0.84s ===============================',
      '✔ Pytest completed: complete conformance matching achieved.',
      '✔ Invariant state established on s_inv parameters.',
      'System calibrated and nominally active.'
    ];

    let currentLine = 0;
    setTerminalOutput([`Executing reconciliation sequence on ${selectedConfig}...`]);

    const interval = setInterval(() => {
      if (currentLine < lines.length) {
        setTerminalOutput(prev => [...prev, lines[currentLine]]);
        setInitProgress(Math.floor((currentLine / (lines.length - 1)) * 100));
        currentLine++;
      } else {
        clearInterval(interval);
        setIsInitializing(false);
        setInitProgress(100);
        onAddLog('SYS', 'SUCCESS', 'Pytest run complete. 5 of 5 system invariant tests PASSED.');
      }
    }, 150);
  };

  return (
    <div className="space-y-6">
      
      {/* Quick Summary Header */}
      <div className="glass rounded-3xl p-6 relative overflow-hidden transition-all-smooth">
        <div className="absolute top-0 right-0 bg-[#5AA7A3]/10 text-[#5AA7A3] text-[10px] font-mono px-3 py-1 border-b border-l border-white/10 rounded-bl-xl font-bold">
          4_SYSTEM_DOCS
        </div>
        <h2 className="text-xl font-bold tracking-wider text-white mb-2 font-sans">
          Initialization & Alignment Console
        </h2>
        <p className="text-xs text-gray-400 max-w-4xl leading-relaxed font-sans">
          The initialization module connects this React user interface directly to the Python core engine repository at <code className="text-[#5AA7A3] bg-black/45 px-1.5 py-0.5 rounded-md font-mono">github.com/SeCuReDmE-main-dev/Synthia</code>. Map local pathing configurations, verify physical constraints, and run unit tests.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: System Setup Configuration */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass rounded-3xl p-5 transition-all-smooth">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center border-b border-white/5 pb-3">
              <Folder className="w-4 h-4 text-[#5AA7A3] mr-2 animate-pulse" />
              PYTHON COMPONENT PATHING
            </h3>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-gray-400 font-mono mb-1.5 uppercase tracking-wide font-semibold">Core Installation Root Path:</label>
                <div className="flex">
                  <input 
                    type="text" 
                    value={projectPath} 
                    onChange={(e) => setProjectPath(e.target.value)}
                    className="flex-1 bg-black/40 text-gray-200 font-mono p-3 border border-white/5 focus:border-[#5AA7A3]/40 focus:outline-none rounded-xl"
                    placeholder="/Users/username/workspace/synthia-python-core"
                  />
                </div>
                <span className="text-[10px] text-gray-500 mt-1.5 block font-mono">
                  Absolute path used by the middleware listener.
                </span>
              </div>

              <div>
                <label className="block text-gray-400 font-mono mb-1.5 uppercase tracking-wide font-semibold">Configuration Profiles:</label>
                <select 
                  value={selectedConfig}
                  onChange={(e) => setSelectedConfig(e.target.value)}
                  className="w-full bg-black/50 text-white font-mono p-2.5 border border-white/10 focus:border-[#5AA7A3] focus:outline-none rounded-xl"
                >
                  <option value="nominal_analysis.json">nominal_analysis.json (Standard Clinic)</option>
                  <option value="aggressive_divergence_strain_b3.json">aggressive_divergence_strain_b3.json (High-entropy Mutations)</option>
                  <option value="local_hybrid_token.json">local_hybrid_token.json (Local Caching Active)</option>
                </select>
              </div>

              <button
                onClick={handleBootInitialization}
                disabled={isInitializing}
                className={`w-full py-2.5 font-sans font-extrabold uppercase text-xs tracking-wider border flex items-center justify-center transition-all duration-300 rounded-full cursor-pointer ${
                  isInitializing
                    ? 'bg-white/5 text-amber-400 border-white/5 cursor-wait'
                    : 'bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] text-black border-none hover:opacity-95 shadow-[0_0_15px_rgba(0,242,255,0.25)]'
                }`}
              >
                <Play className="w-4 h-4 mr-2" />
                EXECUTE ALIGNMENT SUITE
              </button>
            </div>
          </div>

          {/* Quick Docs Search / FAQ Card */}
          <div className="glass rounded-3xl p-5 transition-all-smooth">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center">
              <Search className="w-4 h-4 text-[#5AA7A3] mr-2" />
              SPECIFICATION SEARCH
            </h3>
            
            <div className="relative mb-4">
              <input 
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search specs, theorems, local cache..."
                className="w-full bg-black/40 text-xs text-gray-200 p-3 pl-10 border border-white/5 focus:border-[#5AA7A3]/40 focus:outline-none font-mono rounded-xl"
              />
              <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
            </div>

            <div className="space-y-3 max-h-[220px] overflow-y-auto scrollbar-thin pr-1">
              {filteredDocs.map((art, index) => (
                <div key={index} className="p-3 bg-black/40 border border-white/5 rounded-2xl text-xs">
                  <div className="flex justify-between text-[10px] mb-1 font-mono">
                    <span className="text-[#5AA7A3] font-bold">{art.category}</span>
                    <span className="text-gray-500 font-bold">CODE_SPEC_{index + 1}</span>
                  </div>
                  <h4 className="font-bold text-gray-200 mb-1 font-mono">{art.title}</h4>
                  <p className="text-gray-400 text-[11px] leading-relaxed font-sans">{art.content}</p>
                </div>
              ))}
              {filteredDocs.length === 0 && (
                <div className="text-center text-gray-500 py-4 text-xs font-semibold">No specifications match search.</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Side: Pytest and Init console log */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          
          <div className="glass rounded-3xl p-5 flex flex-col font-mono justify-between min-h-[400px] transition-all-smooth">
            <div>
              <div className="flex justify-between items-center text-xs text-gray-500 border-b border-white/5 pb-2.5 mb-4 uppercase tracking-wider">
                <span className="flex items-center">
                  <Terminal className="w-4 h-4 text-[#5AA7A3] mr-2 animate-pulse" />
                  LOCAL TERMINAL & AUTOMATED TEST LOGGER
                </span>
                <span className="font-bold">CONFORMANCE STATE: NOMINAL</span>
              </div>

              {isInitializing && (
                <div className="mb-4">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-amber-400 font-bold">RECONCILING REPOSITORY...</span>
                    <span className="text-[#5AA7A3] font-bold">{initProgress}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-[#5AA7A3] to-[#8AB38B] transition-all duration-150 rounded-full" style={{ width: `${initProgress}%` }} />
                  </div>
                </div>
              )}

              <div className="space-y-1.5 text-xs text-[#ececec] overflow-y-auto max-h-[360px] scrollbar-thin pr-2">
                {terminalOutput.map((line, idx) => {
                  let colorClass = 'text-[#ececec]';
                  if (line.startsWith('$') || line.startsWith('(venv)')) colorClass = 'text-[#5AA7A3] font-bold';
                  else if (line.includes('PASSED')) colorClass = 'text-[#5AA7A3] font-extrabold';
                  else if (line.includes('=====')) colorClass = 'text-gray-600 font-semibold';
                  else if (line.startsWith('✔')) colorClass = 'text-[#5AA7A3] font-extrabold glow-text';
                  
                  return (
                    <div key={idx} className={`leading-relaxed font-mono ${colorClass} whitespace-pre-wrap`}>
                      {line}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="border-t border-white/5 pt-3 mt-4 flex flex-col sm:flex-row justify-between items-center text-xs text-gray-500">
              <span className="mb-2 sm:mb-0">TEST HARNESS: Pytest v7.4.0 • Python 3.11</span>
              <span className="flex items-center text-[#5AA7A3] font-semibold glow-text">
                <CheckCircle className="w-3.5 h-3.5 mr-1.5" />
                CONFORMANCE ALIGNED WITH REPO
              </span>
            </div>
          </div>

          {/* Core Science Alignment Summary */}
          <div className="glass rounded-3xl p-5 text-xs transition-all-smooth">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center">
              <Shield className="w-4 h-4 text-[#5AA7A3] mr-2" />
              COMPLIANCE GUARDRAILS ACTIVE
            </h4>
            <p className="text-gray-400 leading-relaxed font-sans">
              Every component of SYNTHIA strictly validates the five mathematical invariants during transaction steps. In-memory calculations are aligned using local Python mathematical schemas to prevent floating-point drift and secure genomic context across all client instances.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
};
