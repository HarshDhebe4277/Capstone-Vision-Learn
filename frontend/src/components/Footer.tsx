export default function Footer() {
  return (
    <footer className="w-full mt-auto py-8 border-t border-gray-200 dark:border-white/5 text-[11px] text-gray-500 flex flex-col md:flex-row items-center justify-between bg-transparent">
      <div className="flex flex-col md:flex-row gap-2 md:gap-4 items-center mb-6 md:mb-0">
        <div className="font-bold text-gray-800 dark:text-gray-300">Vision-Learn AI</div>
        <div className="hidden md:block w-1 h-1 rounded-full bg-gray-400 dark:bg-gray-600"></div>
        <div className="tracking-wide uppercase text-gray-500">© 2024 VISION-LEARN AI. THE LUMINOUS AUTHORITY.</div>
      </div>
      <div className="flex flex-wrap justify-center gap-6 uppercase font-bold tracking-wider text-[10px]">
        <a href="#" className="hover:text-blue-500 dark:hover:text-blue-400 transition-colors">Accessibility Statement</a>
        <a href="#" className="hover:text-blue-500 dark:hover:text-blue-400 transition-colors">Privacy Policy</a>
        <a href="#" className="hover:text-blue-500 dark:hover:text-blue-400 transition-colors">Terms of Service</a>
        <a href="#" className="hover:text-blue-500 dark:hover:text-blue-400 transition-colors">Support</a>
      </div>
    </footer>
  );
}
