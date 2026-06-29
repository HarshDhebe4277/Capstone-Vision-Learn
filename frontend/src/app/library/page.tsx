"use client";

import React, { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import LibrarySidebar from "@/components/LibrarySidebar";
import MediaPlayer from "@/components/MediaPlayer";
import ScriptPanel from "@/components/ScriptPanel";
import ChaptersPanel from "@/components/ChaptersPanel";

export default function LibraryPage() {
  // This holds the currently clicked lecture!
  const [selectedLecture, setSelectedLecture] = useState<any>(null);

  return (
    <div data-page-name="Library" className="min-h-screen flex flex-col relative font-sans">
      <div className="absolute inset-0 bg-dot-pattern z-0 opacity-100 pointer-events-none"></div>

      <div className="z-10 flex flex-col min-h-screen flex-grow">
        <Navbar
          activePage="Library"
          customTabs={["Dashboard", "Library", "Learning Paths", "Analytics"]}
        />

        <main className="flex-grow flex gap-8 w-full mx-auto px-6 md:px-12 pt-8 pb-28 relative max-w-[1600px] lg:flex-row flex-col">

          {/* Pass the state and the updater function to the Sidebar */}
          <LibrarySidebar
            selectedLecture={selectedLecture}
            onSelectLecture={setSelectedLecture}
          />

          <div 
            data-nav-section="player"
            data-nav-order="3"
            data-nav-name="Media and Insights"
            className="flex-grow flex flex-col gap-6 min-w-[300px] max-w-4xl mx-auto w-full border-x border-gray-200 dark:border-white/5 px-4 lg:px-8"
          >
            <div className="flex-shrink-0">
              {/* Pass the selected lecture data to the Player */}
              <MediaPlayer selectedLecture={selectedLecture} />
            </div>
            <ScriptPanel selectedLecture={selectedLecture} />
          </div>

          <ChaptersPanel />

        </main>

        <div 
          data-nav-section="footer"
          data-nav-order="5"
          data-nav-name="Footer Links"
          className="w-full mx-auto px-6 md:px-12 pb-4 z-20 absolute bottom-0 bg-white/80 dark:bg-[#0d0f14]/80 backdrop-blur-sm pt-4 border-t border-gray-200 dark:border-white/5"
        >
          <Footer />
        </div>
      </div>
    </div>
  );
}