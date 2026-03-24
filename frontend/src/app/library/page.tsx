import React from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import LibrarySidebar from "@/components/LibrarySidebar";
import MediaPlayer from "@/components/MediaPlayer";
import ScriptPanel from "@/components/ScriptPanel";
import ChaptersPanel from "@/components/ChaptersPanel";

export default function LibraryPage() {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden font-sans">
      <div className="absolute inset-0 bg-dot-pattern z-0 opacity-100 pointer-events-none"></div>

      <div className="z-10 flex flex-col min-h-screen flex-grow h-screen">
        <Navbar 
          activePage="Library" 
          customTabs={["Dashboard", "Library", "Learning Paths", "Analytics"]} 
        />
        
        <main className="flex-grow flex gap-8 w-full mx-auto px-6 md:px-12 py-8 relative max-w-[1600px] overflow-hidden h-[calc(100vh-140px)] lg:flex-row flex-col">
          
          <LibrarySidebar />

          <div className="flex-grow flex flex-col gap-6 overflow-hidden min-w-[300px] max-w-4xl mx-auto w-full border-x border-gray-200 dark:border-white/5 px-4 lg:px-8">
            <MediaPlayer />
            <ScriptPanel />
          </div>

          <ChaptersPanel />

        </main>
        
        <div className="w-full mx-auto px-6 md:px-12 pb-4 z-20 absolute bottom-0 bg-white/80 dark:bg-[#0d0f14]/80 backdrop-blur-sm pt-4 border-t border-gray-200 dark:border-white/5">
          <Footer />
        </div>
      </div>
    </div>
  );
}
