"use client";

import React, { useState, useEffect } from "react";
import { Search, Play, AudioLines, Inbox } from "lucide-react";

// This defines the shape of the data coming from your PostgreSQL database
interface Lecture {
  id: string;
  title: string;
  source_type: string;
  status: string;
  created_at?: string;
}

export default function LibrarySidebar({ selectedLecture, onSelectLecture }: { selectedLecture: any, onSelectLecture: (lecture: any) => void }) {
  const [items, setItems] = useState<Lecture[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch data from the backend when the component loads
  useEffect(() => {
    const fetchLibrary = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        // Assuming your friend's endpoint to get all lectures is /api/lectures
        const response = await fetch(`${apiUrl}/api/lectures`);

        if (response.ok) {
          const data = await response.json();
          setItems(data);

          if (data.length > 0 && !selectedLecture) {
            onSelectLecture(data[0]);
          }
        } else {
          console.error("Failed to fetch library data");
        }
      } catch (error) {
        console.error("Error connecting to backend:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLibrary();
  }, []);

  return (
    <aside className="w-full lg:w-80 flex-shrink-0 flex flex-col gap-6">
      <h2 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">My Library</h2>

      {/* Search Bar */}
      <div className="relative group">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-400 transition-colors" />
        <input
          type="text"
          placeholder="Filter courses..."
          className="w-full bg-white dark:bg-[#1a1c23]/60 border border-gray-200 dark:border-white/5 rounded-xl py-3 pl-10 pr-4 text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-gray-500 dark:placeholder:text-[#6c7293] shadow-inner"
        />
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 dark:border-white/5 pb-4">
        <button className="px-4 py-1.5 rounded-full bg-gray-200 dark:bg-white/10 text-gray-800 dark:text-white text-xs font-semibold tracking-wide">All</button>
        <button className="px-4 py-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white transition-colors text-xs font-medium tracking-wide">Video</button>
        <button className="px-4 py-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white transition-colors text-xs font-medium tracking-wide">Notes</button>
      </div>

      {/* List / Empty State */}
      <div className="flex flex-col gap-3 overflow-y-auto pr-2 pb-10">
        {isLoading ? (
          <div className="text-center py-10 text-gray-500 dark:text-gray-400 text-sm font-bold animate-pulse">
            Loading your knowledge base...
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed border-gray-200 dark:border-white/5 rounded-xl">
            <Inbox className="w-10 h-10 text-gray-400 dark:text-gray-600 mb-3" />
            <h3 className="text-gray-800 dark:text-gray-300 font-bold mb-1">Your library is empty</h3>
            <p className="text-xs text-gray-500 dark:text-gray-500 max-w-[200px]">Go to the dashboard to process your first lecture or PDF.</p>
          </div>
        ) : (
          items.map((item, i) => (
            <div
              key={item.id || i}
              onClick={() => onSelectLecture(item)}
              className={`flex items-stretch gap-4 p-4 rounded-xl cursor-pointer transition-all ${selectedLecture?.id === item.id
                ? "bg-blue-500 text-white shadow-lg"
                : "bg-white dark:bg-[#181a24] hover:bg-gray-50 dark:hover:bg-[#1e2029] border border-gray-100 dark:border-white/5"
                }`}
            >
              <div className="w-12 flex-shrink-0 rounded-lg flex items-center justify-center bg-gray-100 dark:bg-[#252836] text-gray-500 dark:text-gray-400">
                {item.source_type === "notes" ? <AudioLines className="w-5 h-5" /> : <Play className="w-5 h-5 ml-1" />}
              </div>

              <div className="flex flex-col justify-center flex-grow py-0.5">
                <h4 className="text-sm font-semibold leading-tight mb-1 content-start text-gray-800 dark:text-gray-200">
                  {item.title || "Untitled Narration"}
                </h4>
                <span className="text-[11px] font-medium text-gray-500 uppercase">
                  {item.source_type || "Media"} • {item.status || "Ready"}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}