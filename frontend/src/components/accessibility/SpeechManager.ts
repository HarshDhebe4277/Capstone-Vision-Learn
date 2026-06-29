import { accessibilityEvents } from "./AccessibilityEvents";
import { accessibilityStore } from "./AccessibilityStore";

export type SpeechPriority = "LOW" | "NORMAL" | "HIGH" | "CRITICAL";

interface SpeechItem {
  text: string;
  priority: SpeechPriority;
}

class SpeechManager {
  private queue: SpeechItem[] = [];
  private activeUtterance: SpeechSynthesisUtterance | null = null;
  
  constructor() {
    this.initEventListeners();
  }

  private initEventListeners() {
    // When focus changes, announce the focused element label/description
    accessibilityEvents.on("FOCUS_CHANGED", (payload: { label?: string; description?: string }) => {
      const state = accessibilityStore.getState();
      if (!state.speechEnabled) return;

      const parts: string[] = [];
      if (payload.label) parts.push(payload.label);
      if (payload.description) parts.push(payload.description);

      if (parts.length > 0) {
        this.speak(parts.join(". "), "LOW");
      }
    });

    // When section changes, announce the section name
    accessibilityEvents.on("SECTION_CHANGED", (payload: { name: string }) => {
      const state = accessibilityStore.getState();
      if (!state.speechEnabled) return;
      this.speak(`Section ${payload.name}`, "NORMAL");
    });

    // When page changes, announce the page name
    accessibilityEvents.on("PAGE_CHANGED", (payload: { name: string }) => {
      const state = accessibilityStore.getState();
      if (!state.speechEnabled) return;
      this.speak(`${payload.name} page`, "NORMAL");
    });

    // When action is executed
    accessibilityEvents.on("ACTION_EXECUTED", (payload: { actionName: string; details?: string }) => {
      const state = accessibilityStore.getState();
      if (!state.speechEnabled) return;
      
      const message = payload.details || `Activated ${payload.actionName}`;
      this.speak(message, "HIGH");
    });
  }

  public speak(text: string, priority: SpeechPriority = "NORMAL") {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }

    // Stop and clear queue for high-priority interrupts
    if (priority === "HIGH" || priority === "CRITICAL") {
      this.stop();
    }

    this.queue.push({ text, priority });
    this.processQueue();
  }

  public announce(text: string, priority: SpeechPriority = "NORMAL") {
    this.speak(text, priority);
  }

  public stop() {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    this.queue = [];
    this.activeUtterance = null;
    accessibilityStore.setState({ isSpeaking: false });
  }

  public isSpeaking(): boolean {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return false;
    }
    return window.speechSynthesis.speaking;
  }

  private processQueue() {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }

    if (window.speechSynthesis.speaking) {
      // The browser is already synthesizing speech. It will call onend which calls processQueue.
      return;
    }

    const nextItem = this.queue.shift();
    if (!nextItem) {
      accessibilityStore.setState({ isSpeaking: false });
      return;
    }

    accessibilityStore.setState({ isSpeaking: true });
    
    // Announce via aria-live wrapper if needed (KeyboardNavigation handles this)
    const utterance = new SpeechSynthesisUtterance(nextItem.text);
    this.activeUtterance = utterance;

    const resumeOnEnd = () => {
      this.activeUtterance = null;
      this.processQueue();
    };

    utterance.onend = resumeOnEnd;
    utterance.onerror = resumeOnEnd;

    window.speechSynthesis.speak(utterance);
  }
}

export const speechManager = new SpeechManager();
