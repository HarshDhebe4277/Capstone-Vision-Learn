"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { keyboardController } from "./KeyboardController";
import { focusManager } from "./FocusManager";
import { navigationManager } from "./NavigationManager";
import { actionManager } from "./ActionManager";
import { accessibilityEvents } from "./AccessibilityEvents";
import { pageRegistry } from "./PageRegistry";

export default function KeyboardNavigation() {
  const router = useRouter();
  const pathname = usePathname();
  const [announcement, setAnnouncement] = useState("");

  // 1. Initialize input controllers & set router references
  useEffect(() => {
    navigationManager.setRouter(router);
    actionManager.setRouter(router);
    keyboardController.activate();

    return () => {
      keyboardController.deactivate();
      focusManager.destroy();
    };
  }, [router]);

  // 2. Handle page changes & restore focus
  useEffect(() => {
    if (pathname) {
      focusManager.handlePageTransition(pathname);

      const config = pageRegistry.getPageConfig(pathname);
      if (config) {
        accessibilityEvents.emit("PAGE_CHANGED", { name: config.name });
      }
    }
  }, [pathname]);

  // 3. Listen to accessibility events to update aria-live announcer
  useEffect(() => {
    const handleFocusChanged = (payload: { label?: string; description?: string }) => {
      const text = [payload.label, payload.description].filter(Boolean).join(". ");
      setAnnouncement(text);
    };

    const handleSectionChanged = (payload: { name: string }) => {
      setAnnouncement(`Section ${payload.name}`);
    };

    const handlePageChanged = (payload: { name: string }) => {
      setAnnouncement(`${payload.name} page loaded`);
    };

    const handleActionExecuted = (payload: { details?: string; actionName?: string }) => {
      if (payload.details) {
        setAnnouncement(payload.details);
      }
    };

    const unsubFocus = accessibilityEvents.on("FOCUS_CHANGED", handleFocusChanged);
    const unsubSection = accessibilityEvents.on("SECTION_CHANGED", handleSectionChanged);
    const unsubPage = accessibilityEvents.on("PAGE_CHANGED", handlePageChanged);
    const unsubAction = accessibilityEvents.on("ACTION_EXECUTED", handleActionExecuted);

    return () => {
      unsubFocus();
      unsubSection();
      unsubPage();
      unsubAction();
    };
  }, []);

  return (
    <div className="sr-only" aria-live="assertive" aria-atomic="true">
      {announcement}
    </div>
  );
}
