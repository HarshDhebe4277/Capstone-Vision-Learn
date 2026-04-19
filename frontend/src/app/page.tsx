"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import FeatureCard from "@/components/FeatureCard";
import StatsBar from "@/components/StatsBar";
import Footer from "@/components/Footer";
import { UploadCloud, FileText, Image as ImageIcon, Clapperboard, ScanText, Languages } from "lucide-react";
import ProcessingPage from "./processing/page"

const generateUID = () => Math.random().toString(36).substring(2, 15);

export default function Home() {
  const router = useRouter();

  // State to hold our inputs
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [notesFile, setNotesFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | undefined>(undefined);

  // --- API Connection Logic ---
  const handleProcessVideo = async () => {
    if (!youtubeUrl && !videoFile) {
      alert("Please provide a YouTube URL or a video file.");
      return;
    }

    const jobId = generateUID();
    setCurrentJobId(jobId);
    setIsProcessing(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      if (youtubeUrl) {
        // Hit the YouTube Endpoint
        await fetch(`${apiUrl}/api/pipeline/process`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ youtube_url: youtubeUrl, lecture_id: jobId }),
        });
      } else if (videoFile) {
        // Hit the Local Video Upload Endpoint
        const formData = new FormData();
        formData.append("file", videoFile);
        formData.append("lecture_id", jobId);
        await fetch(`${apiUrl}/api/pipeline/upload`, {
          method: "POST",
          body: formData,
        });
      }

      router.push("/library");

    } catch (error) {
      console.error("Error starting video pipeline:", error);
      alert("Failed to connect to the backend server.");
      setIsProcessing(false);
      setCurrentJobId(undefined);
    }
  };

  const handleProcessNotes = async () => {
    if (!notesFile) {
      alert("Please upload a PDF or Image file.");
      return;
    }

    const jobId = generateUID();
    setCurrentJobId(jobId);
    setIsProcessing(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const formData = new FormData();
      formData.append("file", notesFile);
      formData.append("lecture_id", jobId);

      // Hit the Notes Endpoint
      await fetch(`${apiUrl}/api/notes/process`, {
        method: "POST",
        body: formData,
      });

      // Send the user to the processing screen
      router.push("/library");

    } catch (error) {
      console.error("Error starting notes pipeline:", error);
      alert("Failed to connect to the backend server.");
      setIsProcessing(false);
      setCurrentJobId(undefined);
    }
  };

  if (isProcessing) {
    return <ProcessingPage jobId={currentJobId} />;
  }

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden font-sans">
      <div className="absolute inset-0 bg-dot-pattern z-0 pointer-events-none"></div>

      <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-blue-300/20 dark:bg-blue-600/10 rounded-full blur-[120px] pointer-events-none z-0"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[700px] h-[700px] bg-purple-300/20 dark:bg-purple-600/10 rounded-full blur-[150px] pointer-events-none z-0"></div>
      <div className="absolute top-[40%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-200/20 dark:bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none z-0"></div>

      <div className="z-10 flex flex-col min-h-screen flex-grow">
        <Navbar />

        <main className="flex-grow flex flex-col max-w-[1200px] w-full mx-auto px-6 md:px-12 py-16 md:py-24 relative gap-16">

          <section className="flex flex-col gap-6 max-w-2xl">
            <h1 className="text-5xl md:text-[64px] font-extrabold tracking-tight text-gray-900 dark:text-white leading-tight drop-shadow-sm dark:drop-shadow-md">
              Intelligence. <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">Amplified.</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 leading-relaxed font-medium">
              Synthesize knowledge from any source. Our luminous engine processes visual and textual data into structured narrative insights.
            </p>
          </section>

          <section className="grid justify-center md:grid-cols-2 gap-8 w-full z-20">
            {/* VIDEO NARRATION CARD */}
            <FeatureCard title="Video Narration" icon={<Clapperboard className="w-6 h-6" />}>
              <div className="flex flex-col gap-8 h-full">
                <div className="flex flex-col gap-3">
                  <label className="text-[10px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Source Link</label>
                  <input
                    type="url"
                    value={youtubeUrl}
                    onChange={(e) => {
                      setYoutubeUrl(e.target.value);
                      setVideoFile(null); // Clear file if URL is typed
                    }}
                    placeholder="https://youtube.com/watch?v=..."
                    className="w-full bg-gray-50 dark:bg-[#1e2029]/50 border border-gray-200 dark:border-white/5 shadow-inner rounded-xl px-4 py-3.5 text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-gray-400 dark:placeholder:text-[#555970]"
                  />
                </div>

                <div className="flex flex-col gap-3 flex-grow">
                  <label className="text-[10px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Local Capture</label>
                  {/* Invisible file input wrapped in the dropzone styling */}
                  <div className="relative h-full min-h-[140px] border border-dashed border-gray-200 dark:border-white/10 rounded-xl bg-gray-50 dark:bg-[#1e2029]/30 hover:bg-white dark:hover:bg-[#1e2029]/60 hover:border-blue-300 dark:hover:border-blue-500/40 transition-all cursor-pointer group flex flex-col items-center justify-center py-8 gap-4 shadow-sm overflow-hidden">
                    <input
                      type="file"
                      accept="video/*,audio/*"
                      onChange={(e) => {
                        setVideoFile(e.target.files?.[0] || null);
                        setYoutubeUrl(""); // Clear URL if file is chosen
                      }}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    />
                    <div className="bg-white dark:bg-[#242735] p-3 rounded-full group-hover:bg-gray-50 dark:group-hover:bg-[#2b2e3d] group-hover:scale-105 transition-all text-gray-400 group-hover:text-blue-500 dark:group-hover:text-blue-400 shadow-sm border border-gray-100 dark:border-white/5">
                      <FileText className="w-5 h-5" />
                    </div>
                    <span className="text-sm font-semibold text-gray-500 dark:text-[#8e95b3] group-hover:text-gray-700 dark:group-hover:text-gray-200 z-0 text-center px-4">
                      {videoFile ? videoFile.name : "Drop MP4/MOV or Click to Browse"}
                    </span>
                  </div>
                </div>

                <div className="mt-2 text-center w-full">
                  <button
                    onClick={handleProcessVideo}
                    disabled={isProcessing}
                    className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 hover:from-blue-500 hover:to-indigo-500 dark:hover:from-blue-400 dark:hover:to-indigo-400 text-white font-bold tracking-wide shadow-[0_4px_15px_rgba(59,130,246,0.2)] dark:shadow-[0_4px_20px_rgba(59,130,246,0.3)] hover:shadow-[0_8px_20px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_8px_25px_rgba(59,130,246,0.5)] transition-all transform hover:-translate-y-1 active:translate-y-0 text-sm disabled:opacity-50"
                  >
                    {isProcessing ? "STARTING PIPELINE..." : "PROCESS VIDEO"}
                  </button>
                </div>
              </div>
            </FeatureCard>

            {/* NOTES NARRATION CARD */}
            <FeatureCard title="Notes Narration" icon={<ImageIcon className="w-6 h-6" />}>
              <div className="flex flex-col gap-8 h-full">
                <div className="flex flex-col gap-3 flex-grow">
                  <label className="text-[10px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Document Upload</label>
                  {/* Invisible file input wrapped in the dropzone styling */}
                  <div className="relative h-full min-h-[180px] border border-dashed border-gray-200 dark:border-white/10 rounded-xl bg-gray-50 dark:bg-[#1e2029]/30 hover:bg-white dark:hover:bg-[#1e2029]/60 hover:border-blue-300 dark:hover:border-blue-500/40 transition-all cursor-pointer group flex flex-col items-center justify-center py-8 gap-4 shadow-sm overflow-hidden">
                    <input
                      type="file"
                      accept=".pdf,image/png,image/jpeg"
                      onChange={(e) => setNotesFile(e.target.files?.[0] || null)}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    />
                    <div className="bg-white dark:bg-[#242735] p-3 rounded-full group-hover:bg-gray-50 dark:group-hover:bg-[#2b2e3d] group-hover:scale-105 transition-all text-gray-400 group-hover:text-blue-500 dark:group-hover:text-blue-400 shadow-sm border border-gray-100 dark:border-white/5">
                      <UploadCloud className="w-5 h-5" />
                    </div>
                    <span className="text-sm font-semibold text-gray-500 dark:text-[#8e95b3] group-hover:text-gray-700 dark:group-hover:text-gray-200 z-0 text-center px-4">
                      {notesFile ? notesFile.name : "Drop PDF, PNG or JPG here"}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-4 bg-gray-50 dark:bg-[#1e2029]/60 border border-gray-200 dark:border-white/5 rounded-xl px-5 py-3.5 flex-1 shadow-inner hover:border-gray-300 dark:hover:border-white/10 transition-colors">
                    <ScanText className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                    <div className="flex flex-col">
                      <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Feature</span>
                      <span className="text-sm font-bold text-gray-800 dark:text-gray-300">OCR Enabled</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 bg-gray-50 dark:bg-[#1e2029]/60 border border-gray-200 dark:border-white/5 rounded-xl px-5 py-3.5 flex-1 shadow-inner hover:border-gray-300 dark:hover:border-white/10 transition-colors">
                    <Languages className="w-5 h-5 text-blue-500 dark:text-blue-400" />
                    <div className="flex flex-col">
                      <span className="text-[9px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Feature</span>
                      <span className="text-sm font-bold text-gray-800 dark:text-gray-300">Multilingual</span>
                    </div>
                  </div>
                </div>

                <div className="mt-2 text-center w-full">
                  <button
                    onClick={handleProcessNotes}
                    disabled={isProcessing}
                    className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-500 dark:to-indigo-500 hover:from-blue-500 hover:to-indigo-500 dark:hover:from-blue-400 dark:hover:to-indigo-400 text-white font-bold tracking-wide shadow-[0_4px_15px_rgba(59,130,246,0.2)] dark:shadow-[0_4px_20px_rgba(59,130,246,0.3)] hover:shadow-[0_8px_20px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_8px_25px_rgba(59,130,246,0.5)] transition-all transform hover:-translate-y-1 active:translate-y-0 text-sm disabled:opacity-50"
                  >
                    {isProcessing ? "STARTING PIPELINE..." : "PROCESS NOTES"}
                  </button>
                </div>
              </div>
            </FeatureCard>
          </section>

          <section className="w-full pt-4 z-20">
            <StatsBar />
          </section>
        </main>

        <div className="max-w-[1200px] w-full mx-auto px-6 md:px-12 pb-8 z-20">
          <Footer />
        </div>
      </div>
    </div>
  );
}