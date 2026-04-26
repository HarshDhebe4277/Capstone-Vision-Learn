"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import PipelineStepCard from "@/components/PipelineStepCard";
import { CheckCircle2, RefreshCw, MoreHorizontal, FileText, Mic, Save, Activity, TriangleAlert, Grid2X2 } from "lucide-react";

export default function ProcessingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const jobId = searchParams.get("jobId");

  const [currentStep, setCurrentStep] = useState(1);
  const [progress, setProgress] = useState(0);
  const [pollMessage, setPollMessage] = useState<string>("Waiting for job status...");
  const hasRedirectedRef = useRef(false);

  useEffect(() => {
    if (!jobId) {
      setPollMessage("No job id found. Start a new processing run from the home page.");
      return;
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    let stopped = false;

    const pollStatus = async () => {
      if (stopped) {
        return;
      }

      try {
        const res = await fetch(`${apiUrl}/api/pipeline/status/${encodeURIComponent(jobId)}`, { cache: "no-store" });
        if (res.status === 404) {
          setPollMessage("Status endpoint not found on backend. Check API routes and server restart.");
          return;
        }
        if (!res.ok) {
          throw new Error(`Status request failed (${res.status})`);
        }

        const data = await res.json();
        const nextStep = Number(data.current_step ?? 1);
        const nextProgress = Number(data.progress ?? 0);

        setCurrentStep(Math.min(8, Math.max(1, nextStep)));
        setProgress(Math.min(100, Math.max(0, nextProgress)));
        setPollMessage("Live pipeline status connected.");
      } catch (error) {
        console.error("Polling error", error);
        setPollMessage("Waiting for backend status...");
      }
    };

    pollStatus();
    const interval = setInterval(async () => {
      await pollStatus();
    }, 1200);

    return () => {
      stopped = true;
      clearInterval(interval);
    };
  }, [jobId]);

  useEffect(() => {
    if (progress < 100 || hasRedirectedRef.current) {
      return;
    }

    hasRedirectedRef.current = true;
    setPollMessage("Processing complete. Redirecting to library...");

    const timeout = setTimeout(() => {
      router.push("/library");
    }, 900);

    return () => clearTimeout(timeout);
  }, [progress, router]);

  const pipelineSteps = [
    { title: "Fetch & Download", description: "Source media verified and ingested.", icon: <CheckCircle2 className="w-4 h-4" /> },
    { title: "Split Audio", description: "Acoustic segmentation completed.", icon: <CheckCircle2 className="w-4 h-4" /> },
    { title: "Parallel Transcription", description: "Neural engine processing 12 concurrent streams.", icon: <RefreshCw className="w-4 h-4 animate-spin-slow" /> },
    { title: "Timestamp Selection", description: "Waiting for data sequences.", icon: <MoreHorizontal className="w-4 h-4" /> },
    { title: "Frame Extraction", description: "Visual keyframing logic queued.", icon: <Grid2X2 className="w-4 h-4" /> },
    { title: "Script Generation", description: "Narrative LLM synthesis.", icon: <FileText className="w-4 h-4" /> },
    { title: "TTS Synthesis", description: "Cloning selected voice profile.", icon: <Mic className="w-4 h-4" /> },
    { title: "Persistence", description: "Final asset assembly and storage.", icon: <Save className="w-4 h-4" /> },
  ];

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
              Processing...
            </h1>
            <div className="flex items-center gap-2 text-gray-500 dark:text-[#8e95b3] font-medium text-sm">
              <RefreshCw className="w-4 h-4 animate-spin-slow text-blue-500 dark:text-blue-400" />
              Step {currentStep} of 8: {pipelineSteps[Math.min(currentStep - 1, 7)]?.title}...
            </div>
            <div className="text-xs text-gray-500 dark:text-[#8e95b3]">{pollMessage}</div>
          </section>

          <section className="w-full bg-white/80 dark:bg-[#12141c]/80 backdrop-blur-md rounded-[20px] p-8 border border-gray-200 dark:border-white/5 shadow-xl flex flex-col gap-5">
            <div className="flex justify-between items-baseline">
              <span className="text-sm font-semibold text-gray-500 dark:text-gray-400 tracking-wide">Global Progress</span>
              <span className="text-2xl font-bold text-gray-900 dark:text-white tracking-widest pl-2">{progress}<span className="text-base text-gray-500">%</span></span>
            </div>
            <div className="w-full h-2.5 bg-gray-200 dark:bg-white/5 rounded-full overflow-hidden shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 dark:from-blue-600 dark:to-indigo-400 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.3)] dark:shadow-[0_0_15px_rgba(59,130,246,0.6)] relative"
                style={{ width: `${progress}%` }}
              >
                <div className="absolute top-0 right-0 bottom-0 left-0 bg-gradient-to-r from-white/0 via-white/40 dark:via-white/20 to-white/0 w-1/2 -rotate-12 transform scale-150 animate-shimmer"></div>
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/80 dark:bg-[#12141c]/60 border-y border-r border-gray-200 dark:border-white/5 rounded-xl px-7 py-5 shadow-lg flex flex-col gap-1.5 hover:border-blue-500/20 transition-all border-l-4 border-l-blue-500">
              <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Elapsed Time</span>
              <span className="text-2xl font-bold text-gray-900 dark:text-white tracking-wide">2m 45s</span>
            </div>
            <div className="bg-white/80 dark:bg-[#12141c]/60 border border-gray-200 dark:border-white/5 rounded-xl px-7 py-5 shadow-lg flex flex-col gap-1.5 dark:hover:border-blue-500/20 transition-all">
              <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Estimated Remaining</span>
              <span className="text-2xl font-bold text-gray-800 dark:text-gray-200 tracking-wide">4m 15s</span>
            </div>
            <div className="bg-white/80 dark:bg-[#12141c]/60 border border-gray-200 dark:border-white/5 rounded-xl px-7 py-5 shadow-lg flex flex-col gap-1.5 dark:hover:border-blue-500/20 transition-all">
              <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Current Speed</span>
              <span className="text-2xl font-bold text-gray-800 dark:text-gray-200 tracking-wide">1.2<span className="text-[13px] text-gray-500 font-semibold align-bottom pb-1">s/min</span></span>
            </div>
          </section>

          <section className="flex flex-col gap-6 mt-4">
            <div className="flex items-center gap-3">
              <Activity className="w-5 h-5 text-gray-500 dark:text-gray-300" />
              <h2 className="text-xl font-bold text-gray-900 dark:text-white tracking-wide">Vision-to-Narration Pipeline</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {pipelineSteps.map((step, index) => {
                const stepNumber = index + 1;
                let status: "PENDING" | "ACTIVE" | "DONE" = "PENDING";
                
                if (stepNumber < currentStep) status = "DONE";
                else if (stepNumber === currentStep) status = "ACTIVE";
                else status = "PENDING";

                return <PipelineStepCard key={stepNumber} step={{ ...step, number: stepNumber, status }} />;
              })}
            </div>
          </section>

          <section className="mt-8 flex justify-center pb-8">
            <div className="bg-red-50/80 dark:bg-[#151214]/60 border border-red-200 dark:border-red-500/10 rounded-2xl md:min-w-[500px] p-6 flex flex-col items-center gap-6 shadow-sm dark:shadow-[0_0_80px_-20px_rgba(239,68,68,0.1)]">
              <div className="flex items-center gap-3 text-red-600 dark:text-red-400">
                <TriangleAlert className="w-4 h-4" />
                <span className="text-[12px] font-bold tracking-wide">Cancelling will lose all currently unsaved progress.</span>
              </div>
              <button className="bg-red-600 dark:bg-[#aa1e1e] hover:bg-red-700 text-white text-xs font-bold px-6 py-2.5 rounded shadow-sm hover:shadow-[0_0_15px_rgba(220,38,38,0.2)] dark:hover:shadow-[0_0_15px_rgba(220,38,38,0.3)] transition-all flex items-center gap-2 tracking-wide uppercase">
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
