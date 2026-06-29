export interface AccessibilityState {
  currentFocus: HTMLElement | null;
  currentSection: string | null;
  currentPage: string;
  keyboardMode: boolean;
  voiceMode: boolean;
  speechEnabled: boolean;
  lastCommand: string | null;
  isListening: boolean;
  isSpeaking: boolean;
}

type Listener = (state: AccessibilityState) => void;

class AccessibilityStore {
  private state: AccessibilityState = {
    currentFocus: null,
    currentSection: null,
    currentPage: "",
    keyboardMode: false,
    voiceMode: false,
    speechEnabled: true,
    lastCommand: null,
    isListening: false,
    isSpeaking: false,
  };

  private listeners: Set<Listener> = new Set();

  public getState(): AccessibilityState {
    return this.state;
  }

  public setState(partial: Partial<AccessibilityState>) {
    this.state = { ...this.state, ...partial };
    this.listeners.forEach((listener) => {
      try {
        listener(this.state);
      } catch (err) {
        console.error("Error in accessibility store listener:", err);
      }
    });
  }

  public subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }
}

export const accessibilityStore = new AccessibilityStore();
