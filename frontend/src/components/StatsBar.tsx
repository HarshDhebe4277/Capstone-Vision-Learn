export default function StatsBar() {
  return (
    <div className="w-full bg-white/60 dark:bg-[#12141c]/60 border border-gray-200 dark:border-white/5 rounded-2xl p-8 backdrop-blur-md grid grid-cols-1 md:grid-cols-3 gap-8 shadow-xl dark:shadow-2xl text-gray-900 dark:text-white">
      {/* Metric 1 */}
      <div className="flex flex-col gap-3 relative">
        <div className="text-[10px] font-bold tracking-widest text-gray-500 uppercase">Transcription Accuracy</div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white drop-shadow-sm">99.4</span>
          <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">%</span>
        </div>
        <div className="w-full h-1 bg-gray-200 dark:bg-[#1e2029] rounded-full mt-3 overflow-hidden relative">
          <div className="absolute top-0 left-0 h-full w-[99.4%] bg-gradient-to-r from-blue-500 to-indigo-400 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.8)]"></div>
        </div>
      </div>
      
      {/* Metric 2 */}
      <div className="flex flex-col gap-3 relative">
        <div className="text-[10px] font-bold tracking-widest text-gray-500 uppercase">Processing Latency</div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white drop-shadow-sm">1.2</span>
          <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">s/min</span>
        </div>
        <div className="w-full h-1 bg-gray-200 dark:bg-[#1e2029] rounded-full mt-3 overflow-hidden relative">
          <div className="absolute top-0 left-0 h-full w-[15%] bg-gradient-to-r from-indigo-400 to-blue-500 rounded-full shadow-[0_0_10px_rgba(99,102,241,0.8)]"></div>
        </div>
      </div>
      
      {/* Metric 3 */}
      <div className="flex flex-col gap-3">
        <div className="text-[10px] font-bold tracking-widest text-gray-500 uppercase">Neural Connections</div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white drop-shadow-sm">14.2</span>
          <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">M</span>
        </div>
        <div className="w-full h-1 bg-gray-200 dark:bg-[#1e2029] rounded-full mt-3 overflow-hidden relative">
          <div className="absolute top-0 left-0 h-full w-[75%] bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.8)]"></div>
        </div>
      </div>
    </div>
  );
}
