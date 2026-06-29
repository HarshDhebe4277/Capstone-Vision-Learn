import React from "react";
import { Bookmark, Settings } from "lucide-react";

export default function ChaptersPanel() {
  const chapters = [
    { time: "00:00", title: "Introduction", active: false },
    { time: "02:10", title: "Key Concepts", active: true },
    { time: "05:45", title: "Analogy: The Stack", active: false },
    { time: "10:20", title: "Algorithmic Advantage", active: false },
    { time: "14:00", title: "Summary", active: false },
  ];

  return (
    <aside 
      data-nav-section="chapters"
      data-nav-order="4"
      data-nav-name="Lecture Chapters"
      className="w-full lg:w-72 flex-shrink-0 flex flex-col gap-6"
    >
      <div className="flex items-center gap-2 text-gray-800 dark:text-gray-300">
        <Bookmark className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h3 className="text-xl font-bold tracking-wide">Chapters</h3>
      </div>
      
      <div className="flex flex-col gap-2">
        {chapters.map((chap, i) => (
          <div 
            key={i} 
            tabIndex={0}
            role="button"
            data-a11y-id={`chapter-${i}`}
            data-a11y-label={`Chapter: ${chap.title}`}
            data-a11y-description={`Starts at timestamp ${chap.time}. ${chap.active ? "Currently active chapter." : ""}`}
            onClick={() => alert(`Selected chapter: ${chap.title}`)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                alert(`Selected chapter: ${chap.title}`);
              }
            }}
            className={`flex items-center gap-4 p-3 rounded-xl cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              chap.active 
                ? "bg-white dark:bg-white/10 border border-gray-200 dark:border-white/10 shadow-sm dark:shadow-none" 
                : "bg-gray-50 dark:bg-[#181a24] hover:bg-white dark:hover:bg-white/5 border border-transparent dark:border-white/5"
            }`}
          >
            <span className="text-xs font-bold text-gray-400 dark:text-[#8e95b3] w-10">{chap.time}</span>
            <span className={`text-sm font-semibold truncate ${chap.active ? "text-blue-600 dark:text-blue-300" : "text-gray-700 dark:text-gray-300"}`}>{chap.title}</span>
          </div>
        ))}
      </div>
      
      {/* AI Insight Box */}
      <div 
        tabIndex={0}
        role="region"
        aria-label="AI Insight"
        data-a11y-id="ai-insight-box"
        data-a11y-label="AI Insight Box"
        data-a11y-description="This session highlights 3 key areas you struggled with previously. Focus on the Superposition chapter."
        className="mt-8 bg-gradient-to-br from-blue-50 to-white dark:from-[#1b1f33] dark:to-[#12141c] rounded-2xl p-6 border border-blue-100 dark:border-white/5 shadow-xl relative overflow-hidden group hover:border-blue-300 dark:hover:border-blue-500/20 transition-all cursor-crosshair focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <div className="absolute right-[-10px] bottom-[-10px] opacity-10 dark:opacity-10 group-hover:opacity-20 transition-opacity">
          <Settings className="w-24 h-24 text-blue-500 dark:text-white" />
        </div>
        <h4 className="text-sm font-bold text-gray-900 dark:text-white mb-2 relative z-10">AI Insight</h4>
        <p className="text-xs text-gray-600 dark:text-[#8e95b3] leading-relaxed relative z-10 font-medium">
          This session highlights 3 key areas you've struggled with previously. Focus on the "Superposition" chapter.
        </p>
      </div>
    </aside>
  );
}
