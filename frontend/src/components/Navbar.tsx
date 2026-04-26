"use client";

import { Search, Bell, HelpCircle, Sun, Moon } from "lucide-react";
import { useTheme } from "next-themes";
import { useState, useEffect } from "react";

export default function Navbar({ activePage = "Dashboard", customTabs }: { activePage?: string, customTabs?: string[] }) {
  const tabs = customTabs || ["Dashboard", "Library", "Analytics", "Settings"];
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);
  
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-white/5 bg-white/80 dark:bg-[#0d0f14]/80 backdrop-blur-xl px-6 md:px-12 py-5 flex items-center justify-between transition-all">
      <div className="flex items-center gap-12">
        <h1 className="font-bold text-xl tracking-wide flex items-center gap-2 text-gray-900 dark:text-white">
          <div className="w-5 h-5 bg-gray-100 dark:bg-white/5 border border-gray-300 dark:border-white/10 rounded flex items-center justify-center shadow-inner">
            <div className="w-2 h-2 bg-blue-500 rounded-sm"></div>
          </div>
          Vision-Learn AI
        </h1>
        <ul className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-500 dark:text-gray-400">
          {tabs.map(tab => (
            <li 
              key={tab}
              className={`${activePage === tab ? "text-gray-900 dark:text-white border-b-2 border-blue-500 pb-1 -mb-[33px]" : "hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer pb-1 -mb-[33px]"}`}
            >
              <a href={tab === "Dashboard" ? "/" : `/${tab.toLowerCase()}`}>{tab}</a>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="relative hidden md:block group">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-400 transition-colors" />
          <input 
            type="text" 
            placeholder="Quick search..." 
            suppressHydrationWarning
            className="w-72 bg-gray-100/60 dark:bg-[#1a1c23]/60 border border-gray-200 dark:border-white/5 rounded-xl py-2.5 pl-10 pr-4 text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-gray-400 dark:placeholder:text-gray-600 shadow-inner"
          />
        </div>
        <div className="flex items-center gap-5 text-gray-500 dark:text-gray-400">
          
          {mounted && (
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
              aria-label="Toggle Dark Mode"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          )}

          <Bell className="w-5 h-5 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer" />
          <HelpCircle className="w-5 h-5 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer" />
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 p-[1px] cursor-pointer hover:shadow-[0_0_15px_rgba(59,130,246,0.5)] transition-all duration-300">
            <div className="w-full h-full rounded-full bg-white dark:bg-[#15171e] flex items-center justify-center overflow-hidden">
              <div className="w-full h-full bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-300 flex items-center justify-center text-xs font-bold font-mono">
                JS
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
