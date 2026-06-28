import React from 'react';
import { Github, Globe, Shield, Scale } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-black/60 backdrop-blur-md border-t border-white/5 font-mono py-10 mt-16">
      <div className="max-w-[1600px] mx-auto px-6">
        
        {/* Compliance and Ethical Banner */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pb-8 border-b border-white/5 text-xs text-gray-400">
          <div className="flex items-start space-x-3.5">
            <Shield className="w-5 h-5 text-[#5AA7A3] shrink-0 mt-0.5 animate-pulse glow-text" />
            <div>
              <h4 className="font-bold text-white uppercase mb-1.5 tracking-wider">Taxonomic Consistency Policy</h4>
              <p className="font-sans text-[11px] leading-relaxed text-gray-400">
                SYNTHIA demonstrates mathematical isomorphy during taxonomic modeling. The framework prevents arbitrary database drift, ensuring that computed outputs remain completely context-preserving across evolution trees.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3.5">
            <Scale className="w-5 h-5 text-[#5AA7A3] shrink-0 mt-0.5 animate-pulse glow-text" />
            <div>
              <h4 className="font-bold text-white uppercase mb-1.5 tracking-wider">Academic & Open Source Licensing</h4>
              <p className="font-sans text-[11px] leading-relaxed text-gray-400">
                Developed as open source core intellectual property for educational use. Contributions by leading taxonomists and systems architects.
              </p>
            </div>
          </div>
        </div>

        {/* Brand and Links Section */}
        <div className="pt-8 flex flex-col md:flex-row justify-between items-center text-xs space-y-5 md:space-y-0">
          
          <div className="flex flex-col text-center md:text-left space-y-1.5">
            <div className="font-bold text-white font-sans text-sm tracking-wide">
              SYNTHIA [I_LEX] <span className="text-[#5AA7A3] font-mono text-[10px] ml-2 font-black glow-text">[RESEARCH v4.2.1]</span>
            </div>
            <div className="text-gray-500 text-[10px] uppercase tracking-wider font-semibold">
              Designed & Co-Invented by <strong className="text-gray-300 font-sans">Jean-Sebastien Beaulieu</strong> & <strong className="text-gray-300 font-sans">Prof. Hector Fernando Aguilar</strong>
            </div>
          </div>

          {/* Social Links */}
          <div className="flex flex-wrap justify-center gap-4 text-gray-400">
            <a 
              href="https://github.com/SeCuReDmE-main-dev/Synthia" 
              target="_blank" 
              rel="noreferrer"
              className="flex items-center space-x-2 px-4 py-2 border border-white/5 bg-white/5 hover:border-[#5AA7A3]/40 hover:bg-white/10 text-gray-300 hover:text-white rounded-xl transition-all duration-300 group cursor-pointer"
            >
              <Github className="w-4 h-4 text-[#5AA7A3] group-hover:scale-110 transition-all duration-300" />
              <span className="font-bold tracking-wider text-[10px]">GITHUB_REPOSITORY</span>
            </a>

            <a 
              href="https://synthia.securedme.ca" 
              target="_blank" 
              rel="noreferrer"
              className="flex items-center space-x-2 px-4 py-2 border border-white/5 bg-white/5 hover:border-[#5AA7A3]/40 hover:bg-white/10 text-gray-300 hover:text-white rounded-xl transition-all duration-300 group cursor-pointer"
            >
              <Globe className="w-4 h-4 text-[#5AA7A3] group-hover:scale-110 transition-all duration-300" />
              <span className="font-bold tracking-wider text-[10px]">OFFICIAL_LANDING</span>
            </a>
          </div>

        </div>

        {/* Copyright notice */}
        <div className="text-center text-[10px] text-gray-600 pt-8 uppercase tracking-widest font-bold">
          © {new Date().getFullYear()} SECUREDME CORP. ALL RIGHTS RESERVED. EDUCATIONAL SYSTEM DEMONSTRATOR.
        </div>

      </div>
    </footer>
  );
};
