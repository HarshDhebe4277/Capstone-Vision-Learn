import React from "react";

export default function FeatureCard({ title, icon, children }: { title: string, icon: React.ReactNode, children: React.ReactNode }) {
  return (
    <div className="bg-white/80 dark:bg-[#12141c]/60 backdrop-blur-md border border-gray-200 dark:border-white/5 rounded-[24px] p-8 shadow-2xl flex flex-col hover:border-blue-500/30 dark:hover:border-blue-500/30 hover:shadow-[0_0_50px_-20px_rgba(59,130,246,0.15)] dark:hover:shadow-[0_0_50px_-20px_rgba(59,130,246,0.25)] transition-all duration-500 group relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-blue-500/10 dark:via-white/10 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
      
      <div className="flex items-center gap-5 mb-8 z-10">
        <div className="w-12 h-12 rounded-xl bg-gray-50 dark:bg-[#1e2029] border border-gray-200 dark:border-white/5 flex items-center justify-center text-blue-500 dark:text-blue-400 shadow-[inset_0_2px_10px_rgba(0,0,0,0.05)] dark:shadow-[inset_0_2px_10px_rgba(0,0,0,0.5),_0_2px_10px_rgba(59,130,246,0.1)] group-hover:text-blue-600 dark:group-hover:text-blue-300 group-hover:bg-blue-50 dark:group-hover:bg-[#252836] transition-all">
          {icon}
        </div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white tracking-wide">{title}</h2>
      </div>
      <div className="flex flex-col flex-grow z-10">
        {children}
      </div>
    </div>
  );
}
