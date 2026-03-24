import React from "react";
import { Search, Play, AudioLines } from "lucide-react";

export default function LibrarySidebar() {
  const items = [
    { title: "Quantum Computing Fundamentals", active: true, type: "audio", date: "Oct 24", length: "15:00" },
    { title: "Neural Network Architecture", active: false, type: "video", date: "Oct 22", length: "42:15" },
    { title: "Advanced Linear Algebra for ML", active: false, type: "video", date: "Oct 20", length: "28:40" },
    { title: "Ethics in Generative AI Models", active: false, type: "video", date: "Oct 18", length: "12:05" },
    { title: "Distributed Systems 101", active: false, type: "video", date: "Oct 15", length: "55:30" },
  ];

  return (
    <aside className="w-full lg:w-80 flex-shrink-0 flex flex-col gap-6">
      <h2 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">My Library</h2>
      
      {/* Search Bar */}
      <div className="relative group">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-400 transition-colors" />
        <input 
          type="text" 
          placeholder="Filter courses..." 
          className="w-full bg-white dark:bg-[#1a1c23]/60 border border-gray-200 dark:border-white/5 rounded-xl py-3 pl-10 pr-4 text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-gray-500 dark:placeholder:text-[#6c7293] shadow-inner"
        />
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 dark:border-white/5 pb-4">
        <button className="px-4 py-1.5 rounded-full bg-gray-200 dark:bg-white/10 text-gray-800 dark:text-white text-xs font-semibold tracking-wide">All</button>
        <button className="px-4 py-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white transition-colors text-xs font-medium tracking-wide">Video</button>
        <button className="px-4 py-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white transition-colors text-xs font-medium tracking-wide">Notes</button>
      </div>

      {/* List */}
      <div className="flex flex-col gap-3 overflow-y-auto pr-2 pb-10">
        {items.map((item, i) => (
          <div 
            key={i} 
            className={`flex items-stretch gap-4 p-4 rounded-xl cursor-pointer transition-all ${
              item.active 
                ? "bg-blue-500 text-white shadow-[0_4px_20px_rgba(59,130,246,0.2)]" 
                : "bg-white dark:bg-[#181a24] hover:bg-gray-50 dark:hover:bg-[#1e2029] border border-gray-100 dark:border-white/5"
            }`}
          >
            <div className={`w-12 flex-shrink-0 rounded-lg flex items-center justify-center ${
              item.active ? "bg-black/10 text-white" : "bg-gray-100 dark:bg-[#252836] text-gray-500 dark:text-gray-400"
            }`}>
              {item.type === "audio" && item.active ? <AudioLines className="w-5 h-5" /> : <Play className="w-5 h-5 ml-1" />}
            </div>
            
            <div className="flex flex-col justify-center flex-grow py-0.5">
              {item.active && <span className="text-[9px] font-bold tracking-widest uppercase text-blue-100 mb-1">Currently Playing</span>}
              <h4 className={`text-sm font-semibold leading-tight mb-1 content-start ${item.active ? "text-white" : "text-gray-800 dark:text-gray-200"}`}>{item.title}</h4>
              <span className={`text-[11px] font-medium ${item.active ? "text-blue-100/80" : "text-gray-500"}`}>
                {item.date} • {item.length}
              </span>
            </div>
            
            {item.active && (
              <div className="flex items-start">
                <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse mt-1"></div>
              </div>
            )}
          </div>
        ))}
      </div>
    </aside>
  );
}
