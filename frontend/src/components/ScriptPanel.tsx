import React from "react";
import { FileText } from "lucide-react";

export default function ScriptPanel() {
  return (
    <div className="flex flex-col flex-grow gap-6">
      <div className="flex items-center gap-2 text-gray-800 dark:text-gray-300">
        <FileText className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h3 className="text-xl font-bold tracking-wide">Narration Script</h3>
      </div>
      
      <div className="bg-white/80 dark:bg-[#12141c]/60 backdrop-blur-md rounded-2xl p-6 md:p-8 flex flex-col gap-6 flex-grow border border-gray-200 dark:border-white/5 h-full overflow-hidden shadow-lg">
        <div className="flex-grow overflow-y-auto pr-4 flex flex-col gap-6 custom-scrollbar text-gray-700 dark:text-gray-300 text-[15px] leading-relaxed">
          
          <div>
            <span className="inline-block bg-gray-100 dark:bg-white/10 text-gray-700 dark:text-gray-300 text-xs font-bold px-2 py-1 rounded-md mr-3 align-text-bottom">00:00</span>
            <span className="text-gray-600 dark:text-gray-400">Welcome to the fundamental shift in computational paradigms. To understand Quantum Computing, we must first look at the limitation of the classical bit. In your standard computer, information is binary—a switch is either ON or OFF.</span>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            <span className="font-bold text-gray-900 dark:text-white tracking-widest uppercase text-xs">[PAUSE: KEY CONCEPTS]</span>
          </div>
          
          <div>
            <span className="inline-block bg-blue-50 dark:bg-[#1e293b] text-blue-600 dark:text-blue-300 text-xs font-bold px-2 py-1 rounded-md mr-3 align-text-bottom shadow-sm">02:15</span>
            <span className="text-gray-800 dark:text-gray-200">
              Now, imagine a coin spinning on a table. While it's spinning, it isn't strictly heads or tails; it exists in a state of both. This is <span className="text-blue-500 dark:text-blue-400 border-b border-blue-200 dark:border-blue-400/50 cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-500/10 px-0.5">Superposition</span>. Quantum bits, or qubits, leverage this to perform complex calculations simultaneously.
            </span>
          </div>
          
          <div className="p-4 border-l-2 border-gray-200 dark:border-white/20 bg-gray-50 dark:bg-white/5 rounded-r-xl italic text-gray-500 dark:text-gray-400 text-sm mt-2">
            Analogy Check: The Library of Alexandria. A classical computer reads every book one by one. A quantum computer reads all of them at the same time.
          </div>

        </div>
      </div>
    </div>
  );
}
