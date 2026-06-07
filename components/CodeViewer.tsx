'use client';
import { useState } from 'react';
import { Folder, FileCode, FileText, Check, Copy, HardDrive } from 'lucide-react';

export default function CodeViewer({ files }: { files: any[] }) {
  const [activeFile, setActiveFile] = useState(files[0]?.path || '');
  const [copied, setCopied] = useState(false);

  const file = files.find(f => f.path === activeFile);

  const handleCopy = () => {
     if (!file) return;
     navigator.clipboard.writeText(file.content);
     setCopied(true);
     setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#0A0A0A] font-sans">
       {/* Sidebar */}
       <div className="w-72 border-r border-white/10 bg-[#141414] flex flex-col shadow-xl z-10">
          <div className="p-4 border-b border-white/10 flex items-center gap-3">
             <div className="p-2 bg-blue-500/10 rounded-lg">
                <HardDrive className="w-5 h-5 text-blue-400" />
             </div>
             <div>
                <div className="font-bold text-[13px] tracking-wide text-white">STORE BOT SOURCE</div>
                <div className="text-[11px] text-zinc-500 font-medium">Ready for deployment</div>
             </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-1">
             <div className="flex items-center gap-2 text-[10px] text-zinc-500 mb-3 px-2 uppercase tracking-[0.15em] font-semibold">
                Workspace Files
             </div>
             {files.map(f => (
               <button 
                 key={f.path}
                 onClick={() => setActiveFile(f.path)}
                 className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-left transition-all duration-200 ${
                   activeFile === f.path 
                    ? 'bg-blue-500/15 text-blue-400 ring-1 ring-blue-500/30' 
                    : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200'
                 }`}
               >
                  {f.name.endsWith('.md') || f.name.endsWith('.txt') 
                    ? <FileText className="w-4 h-4 opacity-80" /> 
                    : <FileCode className="w-4 h-4 opacity-80" />
                  }
                  <span className="truncate font-medium">{f.name}</span>
               </button>
             ))}
          </div>
       </div>

       {/* Editor Panel */}
       <div className="flex-1 flex flex-col min-w-0 bg-[#0E1117] relative">
         <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0E1117] sticky top-0 z-10">
            <div className="flex items-center gap-2">
               <div className="text-[13px] font-mono text-zinc-400 flex items-center gap-2">
                  <span className="text-zinc-500">storebot /</span> 
                  <span className="text-zinc-200 font-medium">{file?.name}</span>
               </div>
            </div>
            <button
               onClick={handleCopy}
               className="flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-semibold bg-[#1C1C1C] text-zinc-200 hover:bg-[#2A2A2A] hover:text-white transition-all ring-1 ring-white/5 shadow-sm"
            >
               {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
               {copied ? 'Copied to Clipboard' : 'Copy Source Code'}
            </button>
         </div>
         <div className="flex-1 overflow-auto p-6 md:p-8 custom-scrollbar">
            <pre className="font-mono text-[13.5px] leading-[1.65] text-zinc-300 whitespace-pre-wrap outline-none selection:bg-blue-500/30">
               <code>{file?.content}</code>
            </pre>
         </div>
       </div>
    </div>
  )
}
