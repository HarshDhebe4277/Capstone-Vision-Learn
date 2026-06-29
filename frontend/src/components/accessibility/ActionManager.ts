import { commandBus } from "./CommandBus";
import { accessibilityStore } from "./AccessibilityStore";
import { accessibilityEvents } from "./AccessibilityEvents";
import { speechManager } from "./SpeechManager";

class ActionManager {
  private router: any = null;
  private lastSpaceTime: number = 0;
  private spaceTimer: any = null;

  constructor() {
    this.init();
  }

  private init() {
    if (typeof window === "undefined") return;

    commandBus.registerHandler("ACTIVATE", () => this.handleActivate());
    commandBus.registerHandler("GO_BACK", () => this.handleGoBack());
    commandBus.registerHandler("GO_HOME", () => this.handleGoHome());
    commandBus.registerHandler("STOP", () => this.handleStop());
  }

  public setRouter(router: any) {
    this.router = router;
  }

  private handleActivate() {
    if (typeof window === "undefined") return;

    const activeEl = document.activeElement as HTMLElement | null;
    if (!activeEl) return;

    // Trigger standard click event
    activeEl.click();

    const label =
      activeEl.getAttribute("data-a11y-label") ||
      activeEl.innerText ||
      activeEl.getAttribute("aria-label") ||
      "element";

    accessibilityEvents.emit("ACTION_EXECUTED", {
      actionName: "Confirm",
      details: `Selected ${label}`,
    });
  }

  private handleGoBack() {
    if (typeof window === "undefined") return;

    accessibilityEvents.emit("ACTION_EXECUTED", {
      actionName: "Navigate Back",
      details: "Going to previous page",
    });

    window.history.back();
  }

  private handleGoHome() {
    if (typeof window === "undefined") return;

    const now = Date.now();
    
    // Double tap Space within 3 seconds
    if (now - this.lastSpaceTime <= 3000) {
      this.lastSpaceTime = 0;
      if (this.spaceTimer) {
        clearTimeout(this.spaceTimer);
        this.spaceTimer = null;
      }

      if (this.router) {
        accessibilityEvents.emit("ACTION_EXECUTED", {
          actionName: "Go Home",
          details: "Arrived at Home page",
        });
        this.router.push("/");
      }
    } else {
      this.lastSpaceTime = now;
      
      // Announce first space press
      accessibilityEvents.emit("ACTION_EXECUTED", {
        actionName: "Home Request",
        details: "Home",
      });

      if (this.spaceTimer) clearTimeout(this.spaceTimer);
      this.spaceTimer = setTimeout(() => {
        this.lastSpaceTime = 0;
      }, 3000);
    }
  }

  private isVisible(el: HTMLElement): boolean {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    return style.display !== "none" && style.visibility !== "hidden" && parseFloat(style.opacity) !== 0;
  }

  private handleStop() {
    if (typeof window === "undefined") return;

    // 1. Stop Speech Synthesis
    speechManager.stop();

    // Reset space timer
    this.lastSpaceTime = 0;
    if (this.spaceTimer) {
      clearTimeout(this.spaceTimer);
      this.spaceTimer = null;
    }

    // 2. Close native open dialogs
    const openDialogs = Array.from(document.querySelectorAll("dialog[open]")) as HTMLDialogElement[];
    openDialogs.forEach((dialog) => {
      try {
        dialog.close();
      } catch (err) {
        console.error("Failed to close native dialog:", err);
      }
    });

    // 3. Close custom modals
    const modalSelectors = ['[role="dialog"]', '[role="alertdialog"]', ".modal"];
    modalSelectors.forEach((mSel) => {
      const modals = Array.from(document.querySelectorAll(mSel)) as HTMLElement[];
      modals.forEach((modal) => {
        if (this.isVisible(modal)) {
          // Find close button inside custom modal and click it
          const closeBtn = modal.querySelector(
            'button[aria-label*="close" i], button[aria-label*="cancel" i], .close-button, [class*="close" i]'
          ) as HTMLElement | null;
          if (closeBtn) {
            closeBtn.click();
          }
        }
      });
    });

    // 4. Close menus / dropdowns (if applicable, remove focus or reset state)
    // Custom dropdown selectors can go here

    accessibilityEvents.emit("ACTION_EXECUTED", {
      actionName: "Stop",
      details: "Speech stopped, dialogs closed",
    });
  }
}

export const actionManager = new ActionManager();
