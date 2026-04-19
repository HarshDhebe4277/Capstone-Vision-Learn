"use client";

import React, { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import PipelineStepCard from "@/components/PipelineStepCard";
import { CheckCircle2, RefreshCw, MoreHorizontal, Maximize, FileText, Mic, Save, Activity, TriangleAlert, MoveDown, Grid2X2 } from "lucide-react";
import { useRouter } from "next/navigation";

interface ProcessingPageProps {
  jobId?: string;
}

export default function ProcessingPage({ jobId }: ProcessingPageProps) {
  const router = useRouter();
  const [progress, setProgress] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [statusMessage, setStatusMessage] = useState("Initializing pipeline...");

  useEffect(() => {
    const timer = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // If no jobId is provided, simply fallback to the simulated progress (for dev/presentation testing if wanted)
    if (!jobId) {
      const timer = setInterval(() => {
        setProgress((prev) => {
          const increment = Math.random() * 2 + 0.5;
          const next = Math.min(prev + increment, 100);
          if (next === 100) clearInterval(timer);
          return next;
        });
      }, 800);
      return () => clearInterval(timer);
    }

    // Polling logic when jobId is present
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`${apiUrl}/api/pipeline/status/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          // data format: { step: number, progress: number, message: string }
          if (data.progress !== undefined) {
             setProgress(data.progress);
          }
          if (data.message) {
             setStatusMessage(data.message);
          }
          if (data.progress >= 100) {
             clearInterval(pollInterval);
          }
        }
      } catch (err) {
        console.error("Failed to fetch pipeline status", err);
      }
    }, 1000);

    return () => clearInterval(pollInterval);
  }, [jobId]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}m ${s < 10 ? "0" : ""}${s}s`;
  };

  const getStepStatus = (stepIndex: number): "DONE" | "ACTIVE" | "PENDING" => {
    const thresholds = [15, 30, 45, 60, 75, 88, 98, 100];
    const prevThreshold = stepIndex === 0 ? 0 : thresholds[stepIndex - 1];
    const currThreshold = thresholds[stepIndex];
    
    if (progress >= currThreshold) return "DONE";
    if (progress >= prevThreshold && progress < currThreshold) return "ACTIVE";
    return "PENDING";
  };

  const getStepIcon = (status: "DONE" | "ACTIVE" | "PENDING", defaultIcon: React.ReactNode) => {
    if (status === "DONE") return <CheckCircle2 className="w-4 h-4" />;
    if (status === "ACTIVE") return <RefreshCw className="w-4 h-4 animate-spin-slow" />;
    return defaultIcon;
  };

  const getSubStatusStr = () => {
    if (jobId) return statusMessage;

    // Fallback simulated messages
    if (progress < 15) return "Step 1 of 8: Fetching and verifying media...";
    if (progress < 30) return "Step 2 of 8: Segmenting audio securely...";
    if (progress < 45) return "Step 3 of 8: Transcribing streams concurrently...";
    if (progress < 60) return "Step 4 of 8: Generating timestamps...";
    if (progress < 75) return "Step 5 of 8: Selecting visual keyframes...";
    if (progress < 88) return "Step 6 of 8: LLM synthesizing narrative...";
    if (progress < 98) return "Step 7 of 8: Voice TTS Cloning running...";
    if (progress < 100) return "Step 8 of 8: Finalizing and assembling output...";
    return "Complete: Output ready.";
  };

  const pipelineSteps = [
    { number: 1, title: "Fetch & Download", description: "Source media verified and ingested.", status: getStepStatus(0), icon: getStepIcon(getStepStatus(0), <MoreHorizontal className="w-4 h-4" />) },
    { number: 2, title: "Split Audio", description: "Acoustic segmentation completed.", status: getStepStatus(1), icon: getStepIcon(getStepStatus(1), <MoreHorizontal className="w-4 h-4" />) },
    { number: 3, title: "Parallel Transcription", description: "Neural engine processing 12 concurrent streams.", status: getStepStatus(2), icon: getStepIcon(getStepStatus(2), <MoreHorizontal className="w-4 h-4" />) },
    { number: 4, title: "Timestamp Selection", description: "Waiting for data sequences.", status: getStepStatus(3), icon: getStepIcon(getStepStatus(3), <MoreHorizontal className="w-4 h-4" />) },
    { number: 5, title: "Frame Extraction", description: "Visual keyframing logic queued.", status: getStepStatus(4), icon: getStepIcon(getStepStatus(4), <Grid2X2 className="w-4 h-4" />) },
    { number: 6, title: "Script Generation", description: "Narrative LLM synthesis.", status: getStepStatus(5), icon: getStepIcon(getStepStatus(5), <FileText className="w-4 h-4" />) },
    { number: 7, title: "TTS Synthesis", description: "Cloning selected voice profile.", status: getStepStatus(6), icon: getStepIcon(getStepStatus(6), <Mic className="w-4 h-4" />) },
    { number: 8, title: "Persistence", description: "Final asset assembly and storage.", status: getStepStatus(7), icon: getStepIcon(getStepStatus(7), <Save className="w-4 h-4" />) },
  ];

  const estTotalSeconds = progress > 0 ? (elapsed / progress) * 100 : 120;
  const remainingSeconds = progress >= 100 ? 0 : Math.max(0, estTotalSeconds - elapsed);
  const speed = progress > 0 ? (elapsed / progress).toFixed(1) : "0.0";

  return (
    <div className="min-h-screen flex flex-col relative overflow-x-hidden font-sans">
      <div className="absolute inset-0 bg-dot-pattern z-0 opacity-100 pointer-events-none"></div>
      <div className="absolute top-[20%] right-[-5%] w-[400px] h-[400px] bg-indigo-300/30 dark:bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none z-0"></div>

      <div className="z-10 flex flex-col min-h-screen flex-grow w-full h-full">
        <Navbar 
          activePage="Narrations" 
          customTabs={["Dashboard", "Narrations", "Voices", "Library"]} 
        />
        
        <main className="flex-grow flex flex-col max-w-[1100px] w-full mx-auto px-6 md:px-12 py-12 relative gap-10">
          
          <section className="flex flex-col gap-4">
            <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 dark:text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.1)] dark:drop-shadow-md">
              {progress >= 100 ? "Completed!" : "Processing..."}
            </h1>
            <div className="flex items-center gap-2 text-gray-500 dark:text-[#8e95b3] font-medium text-sm">
              {progress < 100 && <RefreshCw className="w-4 h-4 animate-spin-slow text-blue-500 dark:text-blue-400" />}
              {progress >= 100 && <CheckCircle2 className="w-4 h-4 text-green-500 dark:text-green-400" />}
              {getSubStatusStr()}
            </div>
          </section>

          <section className="w-full bg-white/80 dark:bg-[#12141c]/80 backdrop-blur-md rounded-[20px] p-8 border border-gray-200 dark:border-white/5 shadow-xl flex flex-col gap-5">
            <div className="flex justify-between items-baseline">
              <span className="text-sm font-semibold text-gray-500 dark:text-gray-400 tracking-wide">Global Progress</span>
              <span className="text-2xl font-bold text-gray-900 dark:text-white tracking-widest pl-2">
                {Math.floor(progress)}<span className="text-base text-gray-500">%</span>
              </span>
            </div>
            <div className="w-full h-2.5 bg-gray-200 dark:bg-white/5 rounded-full overflow-hidden shadow-inner">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 dark:from-blue-600 dark:to-indigo-400 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.3)] dark:shadow-[0_0_15px_rgba(59,130,246,0.6)] relative transition-all duration-75"
                style={{ width: `${progress}%` }}
              >
                <div className="absolute top-0 right-0 bottom-0 left-0 bg-gradient-to-r from-white/0 via-white/40 dark:via-white/20 to-white/0 w-1/2 -rotate-12 transform scale-150 animate-shimmer"></div>
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/80 dark:bg-[#12141c]/60 border-y border-r border-gray-200 dark:border-white/5 rounded-xl px-7 py-5 shadow-lg flex flex-col gap-1.5 hover:border-blue-500/20 transition-all border-l-4 border-l-blue-500">
              <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Elapsed Time</span>
              <span className="text-2xl font-bold text-gray-900 dark:text-white tracking-wide">{formatTime(elapsed)}</span>
            </div>
            <div className="bg-white/80 dark:bg-[#12141c]/60 border border-gray-200 dark:border-white/5 rounded-xl px-7 py-5 shadow-lg flex flex-col gap-1.5 dark:hover:border-blue-500/20 transition-all">
              <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Estimated Remaining</span>
              <span className="text-2xl font-bold text-gray-800 dark:text-gray-200 tracking-wide">{formatTime(remainingSeconds)}</span>
            </div>
            <div className="bg-white/80 dark:bg-[#12141c]/60 border border-gray-200 dark:border-white/5 rounded-xl px-7 py-5 shadow-lg flex flex-col gap-1.5 dark:hover:border-blue-500/20 transition-all">
              <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Current Speed</span>
              <span className="text-2xl font-bold text-gray-800 dark:text-gray-200 tracking-wide">{speed}<span className="text-[13px] text-gray-500 font-semibold align-bottom pb-1">s/1%</span></span>
            </div>
          </section>

          <section className="flex flex-col gap-6 mt-4">
            <div className="flex items-center gap-3">
              <Activity className="w-5 h-5 text-gray-500 dark:text-gray-300" />
              <h2 className="text-xl font-bold text-gray-900 dark:text-white tracking-wide">Vision-to-Narration Pipeline</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {pipelineSteps.map((step) => (
                <PipelineStepCard key={step.number} step={step} />
              ))}
            </div>
          </section>

          <section className="mt-8 flex justify-center pb-8">
            <div className="bg-red-50/80 dark:bg-[#151214]/60 border border-red-200 dark:border-red-500/10 rounded-2xl md:min-w-[500px] p-6 flex flex-col items-center gap-6 shadow-sm dark:shadow-[0_0_80px_-20px_rgba(239,68,68,0.1)]">
              <div className="flex items-center gap-3 text-red-600 dark:text-red-400">
                <TriangleAlert className="w-4 h-4" />
                <span className="text-[12px] font-bold tracking-wide">Cancelling will lose all currently unsaved progress.</span>
              </div>
              <button 
                onClick={() => router.push("/")}
                className="bg-red-600 dark:bg-[#aa1e1e] hover:bg-red-700 text-white text-xs font-bold px-6 py-2.5 rounded shadow-sm hover:shadow-[0_0_15px_rgba(220,38,38,0.2)] dark:hover:shadow-[0_0_15px_rgba(220,38,38,0.3)] transition-all flex items-center gap-2 tracking-wide uppercase"
              >
                <div className="w-4 h-4 bg-white/20 rounded-full flex items-center justify-center p-[2px]">
                  <div className="w-full h-full bg-white rounded-full flex items-center justify-center"><div className="w-1.5 h-1.5 bg-red-600 dark:bg-[#aa1e1e] rounded-sm"></div></div>
                </div>
                Cancel Processing
              </button>
            </div>
          </section>

        </main>
        
        <div className="max-w-[1100px] w-full mx-auto px-6 md:px-12 pb-6 z-20">
          <Footer />
        </div>
      </div>
    </div>
  );
}
