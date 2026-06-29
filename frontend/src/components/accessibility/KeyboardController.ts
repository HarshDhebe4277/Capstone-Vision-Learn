import { commandBus, AccessibilityCommandType } from "./CommandBus";

export const DEFAULT_KEY_MAP: Record<string, AccessibilityCommandType> = {
  "ArrowDown": "FOCUS_NEXT",
  "ArrowUp": "FOCUS_PREVIOUS",
  "Enter": "ACTIVATE",
  "Backspace": "GO_BACK",
  " ": "GO_HOME", // Space
  "ArrowRight": "NEXT_SECTION",
  "ArrowLeft": "PREVIOUS_SECTION",
  "Escape": "STOP",
};

class KeyboardController {
  private keyMap: Record<string, AccessibilityCommandType> = { ...DEFAULT_KEY_MAP };
  private active = false;

  constructor() {
    // Registered once when initialized
  }

  public activate() {
    if (this.active) return;
    this.active = true;
    window.addEventListener("keydown", this.handleKeyDown, true); // Capture phase to intercept first
  }

  public deactivate() {
    if (!this.active) return;
    this.active = false;
    window.removeEventListener("keydown", this.handleKeyDown, true);
  }

  private isInsideInput(el: HTMLElement | null): boolean {
    if (!el) return false;
    const tagName = el.tagName.toLowerCase();
    if (tagName === "textarea") return true;
    if (tagName === "input") {
      const type = (el as HTMLInputElement).type.toLowerCase();
      const textTypes = ["text", "search", "url", "email", "password", "number", "tel"];
      return textTypes.includes(type);
    }
    return el.isContentEditable;
  }

  private isSlider(el: HTMLElement | null): boolean {
    if (!el) return false;
    if (el.tagName.toLowerCase() === "input" && (el as HTMLInputElement).type.toLowerCase() === "range") {
      return true;
    }
    return el.getAttribute("role") === "slider";
  }

  private handleKeyDown = (e: KeyboardEvent) => {
    // Ignore key repeat events while key is held down
    if (e.repeat) return;

    const command = this.keyMap[e.key];
    if (!command) return;

    const activeEl = document.activeElement as HTMLElement | null;

    // Inside a text input: only Escape should be intercepted, others should proceed normally
    if (this.isInsideInput(activeEl)) {
      if (e.key === "Escape") {
        e.preventDefault();
        commandBus.dispatch({ type: command, source: "keyboard" });
      }
      return;
    }

    // Slider controls: ignore Left / Right arrow navigation so slider value can be adjusted
    if (this.isSlider(activeEl)) {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        return;
      }
    }

    // Intercept event and dispatch command
    e.preventDefault();
    e.stopPropagation();
    
    commandBus.dispatch({
      type: command,
      source: "keyboard",
    });
  };
}

export const keyboardController = new KeyboardController();
