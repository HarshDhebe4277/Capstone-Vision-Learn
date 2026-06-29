export type AccessibilityEventType =
  | "FOCUS_CHANGED"
  | "SECTION_CHANGED"
  | "ACTION_EXECUTED"
  | "PAGE_CHANGED";

type EventCallback = (payload: any) => void;

class AccessibilityEvents {
  private listeners: Map<AccessibilityEventType, Set<EventCallback>> = new Map();

  public on(event: AccessibilityEventType, callback: EventCallback): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
    return () => this.off(event, callback);
  }

  public off(event: AccessibilityEventType, callback: EventCallback) {
    const set = this.listeners.get(event);
    if (set) {
      set.delete(callback);
    }
  }

  public emit(event: AccessibilityEventType, payload: any) {
    const set = this.listeners.get(event);
    if (set) {
      set.forEach((callback) => {
        try {
          callback(payload);
        } catch (err) {
          console.error(`Error in AccessibilityEvents listener for event ${event}:`, err);
        }
      });
    }
  }
}

export const accessibilityEvents = new AccessibilityEvents();
