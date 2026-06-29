import { commandBus } from "./CommandBus";
import { accessibilityStore } from "./AccessibilityStore";
import { accessibilityEvents } from "./AccessibilityEvents";
import { pageRegistry } from "./PageRegistry";

function isVisible(el: HTMLElement): boolean {
  if (!el) return false;
  const style = window.getComputedStyle(el);
  if (style.display === "none" || style.visibility === "hidden" || parseFloat(style.opacity) === 0) {
    return false;
  }
  if (el.offsetWidth === 0 && el.offsetHeight === 0) {
    const rects = el.getClientRects();
    if (rects.length === 0) return false;
  }
  let parent = el.parentElement;
  while (parent) {
    const pStyle = window.getComputedStyle(parent);
    if (pStyle.display === "none" || pStyle.visibility === "hidden") {
      return false;
    }
    if (parent.getAttribute("aria-hidden") === "true") {
      return false;
    }
    parent = parent.parentElement;
  }
  return true;
}

class FocusManager {
  private cachedElements: HTMLElement[] = [];
  private observers: MutationObserver[] = [];
  private routeSavedIndices: Record<string, number> = {};
  private currentPathname: string = "";

  constructor() {
    this.init();
  }

  private init() {
    if (typeof window === "undefined") return;

    // Register handlers on Command Bus
    commandBus.registerHandler("FOCUS_NEXT", () => this.moveFocus(1));
    commandBus.registerHandler("FOCUS_PREVIOUS", () => this.moveFocus(-1));

    // Listen to focus changes
    document.addEventListener("focusin", this.handleFocusIn);
    document.addEventListener("focusout", this.handleFocusOut);
    window.addEventListener("mousedown", this.handleMouseDown);
    window.addEventListener("keydown", this.handleKeyDown);
  }

  public handlePageTransition(pathname: string) {
    // Save focus index of current page before leaving
    if (this.currentPathname && typeof document !== "undefined") {
      const activeEl = document.activeElement as HTMLElement | null;
      if (activeEl && this.cachedElements.includes(activeEl)) {
        this.routeSavedIndices[this.currentPathname] = this.cachedElements.indexOf(activeEl);
      }
    }

    this.currentPathname = pathname;
    this.cleanupObservers();

    // Scan page and cache focusable elements
    this.updateCache();

    // Set up MutationObservers on containers for performance
    const config = pageRegistry.getPageConfig(pathname);
    const containers: HTMLElement[] = [];

    if (config) {
      config.sections.forEach((sec) => {
        const el = document.querySelector(`[data-nav-section="${sec.id}"], #${sec.id}`) as HTMLElement | null;
        if (el) containers.push(el);
      });
    } else {
      const main = document.querySelector("main") || document.body;
      containers.push(main);
    }

    containers.forEach((container) => {
      const obs = new MutationObserver(() => {
        this.updateCache();
      });
      try {
        obs.observe(container, { childList: true, subtree: true });
        this.observers.push(obs);
      } catch (e) {
        console.error("MutationObserver error on container:", e);
      }
    });

    // Restore index or focus first element
    const savedIndex = this.routeSavedIndices[pathname];
    setTimeout(() => {
      if (savedIndex !== undefined && savedIndex >= 0 && savedIndex < this.cachedElements.length) {
        const el = this.cachedElements[savedIndex];
        if (el && isVisible(el)) {
          el.focus();
          return;
        }
      }
      
      // Fallback: focus first element
      if (this.cachedElements.length > 0) {
        this.cachedElements[0].focus();
      }
    }, 150);
  }

  private cleanupObservers() {
    this.observers.forEach((obs) => obs.disconnect());
    this.observers = [];
  }

  public updateCache() {
    if (typeof window === "undefined") return;

    // Check if modal / dialog is open
    const modalSelectors = ["dialog[open]", '[role="dialog"]', '[role="alertdialog"]', ".modal"];
    let activeModal: HTMLElement | null = null;
    for (const mSel of modalSelectors) {
      const modals = Array.from(document.querySelectorAll(mSel)) as HTMLElement[];
      const visibleModal = modals.find((m) => isVisible(m));
      if (visibleModal) {
        activeModal = visibleModal;
        break;
      }
    }

    const focusableSelector =
      'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"], [role="tab"], [role="menuitem"]';

    if (activeModal) {
      const elements = Array.from(activeModal.querySelectorAll(focusableSelector)) as HTMLElement[];
      this.cachedElements = elements.filter((el) => isVisible(el));
      return;
    }

    const config = pageRegistry.getPageConfig(this.currentPathname);
    if (!config) {
      const elements = Array.from(document.body.querySelectorAll(focusableSelector)) as HTMLElement[];
      this.cachedElements = elements.filter((el) => isVisible(el));
      return;
    }

    // Dynamic Visual Sorting by section order
    const sortedSections = [...config.sections].sort((a, b) => a.order - b.order);
    const elementsList: HTMLElement[] = [];

    sortedSections.forEach((secConfig) => {
      const secEl = document.querySelector(`[data-nav-section="${secConfig.id}"], #${secConfig.id}`) as HTMLElement | null;
      if (secEl && isVisible(secEl)) {
        const secElements = Array.from(secEl.querySelectorAll(focusableSelector)) as HTMLElement[];
        secElements.forEach((el) => {
          if (isVisible(el) && !elementsList.includes(el)) {
            elementsList.push(el);
          }
        });
      }
    });

    // Capture non-section items (like floaters, top-level tags, footers without sections)
    const allElements = Array.from(document.body.querySelectorAll(focusableSelector)) as HTMLElement[];
    allElements.forEach((el) => {
      if (isVisible(el) && !elementsList.includes(el)) {
        let inSection = false;
        for (const secConfig of config.sections) {
          const secEl = document.querySelector(`[data-nav-section="${secConfig.id}"], #${secConfig.id}`);
          if (secEl && secEl.contains(el)) {
            inSection = true;
            break;
          }
        }
        if (!inSection) {
          elementsList.push(el);
        }
      }
    });

    this.cachedElements = elementsList;
  }

  private moveFocus(direction: number) {
    this.updateCache();
    if (this.cachedElements.length === 0) return;

    // Enable keyboard focus rings
    accessibilityStore.setState({ keyboardMode: true });

    const activeEl = document.activeElement as HTMLElement | null;
    let index = -1;
    if (activeEl) {
      index = this.cachedElements.indexOf(activeEl);
    }

    let nextIndex = 0;
    if (index !== -1) {
      nextIndex = (index + direction + this.cachedElements.length) % this.cachedElements.length;
    } else if (direction < 0) {
      nextIndex = this.cachedElements.length - 1;
    }

    const nextEl = this.cachedElements[nextIndex];
    if (nextEl) {
      nextEl.focus();
    }
  }

  private handleFocusIn = (e: FocusEvent) => {
    const target = e.target as HTMLElement | null;
    if (!target) return;

    accessibilityStore.setState({ currentFocus: target });

    // Apply high-contrast keyboard focus styling if keyboardMode is active
    const state = accessibilityStore.getState();
    if (state.keyboardMode) {
      target.classList.add("kb-focus");
    }

    // Trigger focus change event
    const label = target.getAttribute("data-a11y-label") || target.innerText || target.getAttribute("aria-label") || target.getAttribute("placeholder") || "";
    const description = target.getAttribute("data-a11y-description") || target.title || "";
    
    accessibilityEvents.emit("FOCUS_CHANGED", {
      element: target,
      label,
      description,
    });
  };

  private handleFocusOut = (e: FocusEvent) => {
    const target = e.target as HTMLElement | null;
    if (target) {
      target.classList.remove("kb-focus");
    }
    accessibilityStore.setState({ currentFocus: null });
  };

  private handleMouseDown = () => {
    // Disable keyboard focus outline mode when user clicks
    accessibilityStore.setState({ keyboardMode: false });
    
    // Clean up focus indicator class from whatever has it
    const kbFocused = document.querySelectorAll(".kb-focus");
    kbFocused.forEach((el) => el.classList.remove("kb-focus"));
  };

  private handleKeyDown = (e: KeyboardEvent) => {
    // Enable keyboard focus outline mode on keyboard interaction
    if (["ArrowUp", "ArrowDown", "Tab", "ArrowLeft", "ArrowRight"].includes(e.key)) {
      accessibilityStore.setState({ keyboardMode: true });
    }
  };

  public destroy() {
    this.cleanupObservers();
    if (typeof window !== "undefined") {
      document.removeEventListener("focusin", this.handleFocusIn);
      document.removeEventListener("focusout", this.handleFocusOut);
      window.removeEventListener("mousedown", this.handleMouseDown);
      window.removeEventListener("keydown", this.handleKeyDown);
    }
  }
}

export const focusManager = new FocusManager();
