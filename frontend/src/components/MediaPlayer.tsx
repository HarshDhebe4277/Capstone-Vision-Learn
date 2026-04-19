"use client";

import React, { useState, useRef, useEffect } from "react";
import { Play, Pause, RotateCcw, RotateCw, Volume2, Settings2 } from "lucide-react";

export default function MediaPlayer({ selectedLecture }: { selectedLecture: any }) {
  // --- Audio Engine State ---
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState("0:00");
  const [duration, setDuration] = useState("0:00");
  const [playbackRate, setPlaybackRate] = useState(1);

  useEffect(() => {
    if (audioRef.current && selectedLecture) {
      setProgress(0);
      setCurrentTime("0:00");

      audioRef.current.play()
        .then(() => setIsPlaying(true))
        .catch((err) => console.log("Browser blocked autoplay. User must click play.", err));
    }
  }, [selectedLecture]);

  // Helper to format seconds into M:SS
  const formatTime = (timeInSeconds: number) => {
    if (isNaN(timeInSeconds)) return "0:00";
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  if (!selectedLecture) {
    return (
      <div className="bg-white/80 dark:bg-[#12141c]/80 backdrop-blur-md rounded-[24px] p-8 border border-gray-200 dark:border-white/5 flex items-center justify-center min-h-[200px] shadow-xl">
        <p className="text-gray-500 font-bold">Select a lecture from the library to start listening.</p>
      </div>
    );
  }

  const audioUrl = `${apiUrl}/api/audio/${selectedLecture.id}/narration`;

  // --- Audio Event Handlers ---
  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const skip = (amount: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime += amount;
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      const current = audioRef.current.currentTime;
      const total = audioRef.current.duration;
      setProgress((current / total) * 100);
      setCurrentTime(formatTime(current));
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(formatTime(audioRef.current.duration));
    }
  };

  const toggleSpeed = () => {
    if (audioRef.current) {
      const speedOptions = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2];
      const currentIndex = speedOptions.findIndex((speed) => speed === playbackRate);
      const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % speedOptions.length;
      const newRate = speedOptions[nextIndex];
      audioRef.current.playbackRate = newRate;
      setPlaybackRate(newRate);
    }
  };

  return (
    <div className="bg-white/80 dark:bg-[#12141c]/80 backdrop-blur-md rounded-[24px] p-8 border border-gray-200 dark:border-white/5 flex flex-col gap-10 shadow-xl overflow-hidden relative group">

      {/* THE HIDDEN AUDIO ENGINE */}
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
        // Note: We will replace this src with the actual backend URL in the next step!
        src={audioUrl}
        preload="metadata"
        autoPlay
      />

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-500/10 blur-[80px] pointer-events-none rounded-full"></div>

      <div className="flex justify-between items-start z-10 relative">
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-bold tracking-widest text-gray-500 dark:text-[#6c7293] uppercase">Now Generating Insights</span>
          <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight leading-tight max-w-[300px]">
            {selectedLecture.title || "Processing Audio..."}
          </h2>
        </div>

        <div className="flex items-center gap-6">
          <button
            onClick={toggleSpeed}
            className="flex items-center gap-2 bg-gray-100 dark:bg-white/5 hover:bg-gray-200 dark:hover:bg-white/10 border border-gray-200 dark:border-white/10 rounded-full px-4 py-2 text-xs font-semibold text-gray-600 dark:text-gray-300 transition-colors"
          >
            <Settings2 className="w-3.5 h-3.5" />
            {playbackRate}x
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
          <button onClick={() => skip(-10)} aria-label="Skip backward 10 seconds" className="text-gray-400 hover:text-gray-600 dark:hover:text-white transition-colors hover:scale-110 transform duration-200">
            <RotateCcw className="w-6 h-6" />
          </button>

          <button
            onClick={togglePlay}
            aria-label={isPlaying ? "Pause" : "Play"}
            className="w-20 h-20 rounded-3xl bg-blue-500 text-white flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.3)] dark:shadow-[0_0_30px_rgba(59,130,246,0.5)] hover:bg-blue-600 dark:hover:bg-blue-400 transition-all transform hover:scale-105"
          >
            {isPlaying ? <Pause className="w-8 h-8 fill-current" /> : <Play className="w-8 h-8 fill-current ml-1" />}
          </button>

          <button onClick={() => skip(10)} aria-label="Skip forward 10 seconds" className="text-gray-400 hover:text-gray-600 dark:hover:text-white transition-colors hover:scale-110 transform duration-200">
            <RotateCw className="w-6 h-6" />
          </button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="w-full h-2 bg-gray-200 dark:bg-white/10 rounded-full relative overflow-hidden group">
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-400 to-blue-600 dark:from-blue-300 dark:to-blue-500 rounded-full transition-all duration-100"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-gray-500 dark:text-[#8e95b3] text-xs font-medium">
            <span>{currentTime}</span>
            <span>{duration}</span>
          </div>
        </div>
      </div>
    </div>
  );
}