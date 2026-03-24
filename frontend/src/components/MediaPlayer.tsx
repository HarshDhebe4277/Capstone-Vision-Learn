import React from "react";
import { Play, Pause, RotateCcw, RotateCw, Volume2, Settings2 } from "lucide-react";

export default function MediaPlayer() {
  return (
    <div className="bg-white/80 dark:bg-[#12141c]/80 backdrop-blur-md rounded-[24px] p-8 border border-gray-200 dark:border-white/5 flex flex-col gap-10 shadow-xl overflow-hidden relative group">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-500/10 blur-[80px] pointer-events-none rounded-full"></div>
      
      <div className="flex justify-between items-start z-10 relative">
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Now Generating Insights</span>
          <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight leading-tight max-w-[300px]">Quantum Computing Fundamentals</h2>
        </div>
        
        <div className="flex items-center gap-6">
          <button className="flex items-center gap-2 bg-gray-100 dark:bg-white/5 hover:bg-gray-200 dark:hover:bg-white/10 border border-gray-200 dark:border-white/10 rounded-full px-4 py-2 text-xs font-semibold text-gray-600 dark:text-gray-300 transition-colors">
            <Settings2 className="w-3.5 h-3.5" />
            1.25x
          </button>
          
          <div className="flex items-center gap-3">
            <Volume2 className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <div className="w-20 h-1 bg-gray-200 dark:bg-white/10 rounded-full overflow-hidden">
              <div className="w-3/4 h-full bg-blue-500 dark:bg-blue-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="flex flex-col gap-8 z-10 relative">
        <div className="flex items-center justify-center gap-8 text-center pt-2">
          <button suppressHydrationWarning className="text-gray-400 hover:text-gray-600 dark:hover:text-white transition-colors hover:scale-110 transform duration-200">
            <RotateCcw className="w-6 h-6" />
          </button>
          
          <button suppressHydrationWarning className="w-20 h-20 rounded-3xl bg-blue-500 text-white flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.3)] dark:shadow-[0_0_30px_rgba(59,130,246,0.5)] hover:bg-blue-600 dark:hover:bg-blue-400 transition-all transform hover:scale-105">
            <Pause className="w-8 h-8 fill-current" />
          </button>
          
          <button suppressHydrationWarning className="text-gray-400 hover:text-gray-600 dark:hover:text-white transition-colors hover:scale-110 transform duration-200">
            <RotateCw className="w-6 h-6" />
          </button>
        </div>
        
        <div className="flex flex-col gap-2">
          <div className="w-full h-2 bg-gray-200 dark:bg-white/10 rounded-full cursor-pointer relative overflow-hidden group">
            <div className="absolute top-0 left-0 h-full w-[25%] bg-gradient-to-r from-blue-400 to-blue-600 dark:from-blue-300 dark:to-blue-500 rounded-full"></div>
            <div className="absolute top-1/2 left-[25%] -translate-y-1/2 -ml-1.5 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 shadow-sm transition-opacity"></div>
          </div>
          <div className="flex justify-between text-gray-500 dark:text-[#8e95b3] text-xs font-medium">
            <span>2:30</span>
            <span>15:00</span>
          </div>
        </div>
      </div>
    </div>
  );
}
