import React from "react";

interface PipelineStep {
  number: number;
  title: string;
  description: string;
  status: "DONE" | "ACTIVE" | "PENDING";
  icon: React.ReactNode;
}

export default function PipelineStepCard({ step }: { step: PipelineStep }) {
  const isDone = step.status === "DONE";
  const isActive = step.status === "ACTIVE";
  
  return (
    <div className={`p-5 rounded-xl border transition-all duration-300 relative ${
      isActive 
        ? "bg-blue-50 dark:bg-[#161a2b] active" 
        : isDone 
          ? "bg-white/80 dark:bg-[#12141c]/80 border-gray-200 dark:border-white/5 opacity-80" 
          : "bg-gray-50 dark:bg-[#12141c]/50 border-transparent opacity-60"
    }`}>
      <div className="flex justify-between items-start mb-6">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isActive ? "bg-blue-500/10 text-blue-500 dark:bg-blue-500/20 dark:text-blue-400" : isDone ? "bg-gray-100 dark:bg-white/10 text-gray-600 dark:text-gray-300" : "bg-gray-100 dark:bg-white/5 text-gray-500"
        }`}>
          {step.icon}
        </div>
        
        <div className={`px-2 py-1 space-x-1 text-[9px] font-bold tracking-widest rounded uppercase ${
          isActive ? "bg-blue-500 text-white shadow-sm" : isDone ? "bg-gray-100 dark:bg-white/10 text-gray-500 dark:text-gray-400" : "bg-gray-100 dark:bg-white/5 text-gray-500"
        }`}>
          {step.status}
        </div>
      </div>
      
      <div className="flex flex-col gap-1.5">
        <h3 className={`font-semibold text-[15px] ${isActive ? "text-blue-900 dark:text-white" : isDone ? "text-gray-800 dark:text-gray-200" : "text-gray-500 dark:text-gray-400"}`}>
          {step.number}. {step.title}
        </h3>
        <p className="text-xs text-gray-600 dark:text-gray-500 font-medium">
          {step.description}
        </p>
      </div>
    </div>
  );
}
