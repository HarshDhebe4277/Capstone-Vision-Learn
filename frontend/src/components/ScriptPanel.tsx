"use client";

import React, { useState, useEffect } from "react";
import { FileText, AlignLeft, Loader2 } from "lucide-react";

export default function ScriptPanel({ selectedLecture }: { selectedLecture: any }) {
  const [scriptText, setScriptText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Fetch the script whenever a new lecture is clicked
  useEffect(() => {
    if (!selectedLecture) {
      setScriptText("");
      return;
    }

    const fetchScript = async () => {
      setIsLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        // Call your backend endpoint from the Swagger docs
        const response = await fetch(`${apiUrl}/api/audio/${selectedLecture.id}/script`);

        if (response.ok) {
          const data = await response.json();
          setScriptText(data.script);
        } else {
          setScriptText("No script found for this narration.");
        }
      } catch (error) {
        console.error("Failed to fetch script:", error);
        setScriptText("Failed to load script. Please check your connection.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchScript();
  }, [selectedLecture]);

  return (
    <div className="flex flex-col flex-grow gap-6 h-full min-h-[400px]">
      <div className="flex items-center gap-2 text-gray-800 dark:text-gray-300">
        <FileText className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h3 className="text-xl font-bold tracking-wide">Narration Script</h3>
      </div>

      <div className="bg-white/80 dark:bg-[#12141c]/60 backdrop-blur-md rounded-2xl p-6 md:p-8 flex flex-col gap-6 flex-grow border border-gray-200 dark:border-white/5 shadow-lg relative overflow-hidden">

        {/* State 1: Nothing Selected */}
        {!selectedLecture ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 gap-3 opacity-60 mt-10">
            <AlignLeft className="w-12 h-12" />
            <p className="font-semibold">Select a lecture to view its script.</p>
          </div>
        ) :

          /* State 2: Loading */
          isLoading ? (
            <div className="flex flex-col items-center justify-center h-full text-blue-500 gap-3 mt-10">
              <Loader2 className="w-8 h-8 animate-spin" />
              <p className="text-sm font-bold text-gray-500 animate-pulse">Loading AI insights...</p>
            </div>
          ) :

            /* State 3: Show the Script */
            (
              <div className="flex-grow overflow-y-auto pr-4 flex flex-col gap-5 custom-scrollbar text-gray-700 dark:text-gray-300 text-[15px] leading-relaxed">
                {/* Split the text by newlines so it formats nicely into paragraphs instead of a giant wall of text */}
                {scriptText.split('\n').filter(p => p.trim() !== '').map((paragraph, idx) => {

                  // Formatting trick: If the AI puts tags like [SCENE 1] or [PAUSE], make them look like cool UI badges!
                  if (paragraph.startsWith('[') && paragraph.endsWith(']')) {
                    return (
                      <div key={idx} className="flex items-center gap-3 my-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                        <span className="font-bold text-gray-900 dark:text-white tracking-widest uppercase text-xs">
                          {paragraph}
                        </span>
                      </div>
                    );
                  }

                  // Regular text
                  return (
                    <div key={idx}>
                      <span className="text-gray-600 dark:text-gray-400">{paragraph}</span>
                    </div>
                  );
                })}
              </div>
            )}
      </div>
    </div>
  );
}