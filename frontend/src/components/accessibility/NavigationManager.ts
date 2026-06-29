import { commandBus } from "./CommandBus";
import { accessibilityStore } from "./AccessibilityStore";
import { accessibilityEvents } from "./AccessibilityEvents";
import { pageRegistry, NavSection } from "./PageRegistry";

class NavigationManager {
  private router: any = null;

  constructor() {
    this.init();
  }

  private init() {
    if (typeof window === "undefined") return;

    commandBus.registerHandler("NEXT_SECTION", () => this.moveSection(1));
    commandBus.registerHandler("PREVIOUS_SECTION", () => this.moveSection(-1));
  }

  public setRouter(router: any) {
    this.router = router;
  }

  private getFocusableSelector(): string {
    return 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"], [role="tab"], [role="menuitem"]';
  }

  private isVisible(el: HTMLElement): boolean {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    return style.display !== "none" && style.visibility !== "hidden" && parseFloat(style.opacity) !== 0;
  }

  private getElementSectionId(el: HTMLElement | null, sections: NavSection[]): string | null {
    let parent: HTMLElement | null = el;
    while (parent) {
      const currentParent = parent;
      const secId = currentParent.getAttribute("data-nav-section");
      if (secId && sections.some((s) => s.id === secId)) {
        return secId;
      }
      if (currentParent.id && sections.some((s) => s.id === currentParent.id)) {
        return currentParent.id;
      }
      parent = currentParent.parentElement;
    }
    return null;
  }

  private moveSection(direction: number) {
    if (typeof window === "undefined") return;

    const route = window.location.pathname;
    const config = pageRegistry.getPageConfig(route);
    if (!config || config.sections.length === 0) return;

    const sortedSections = [...config.sections].sort((a, b) => a.order - b.order);
    const activeEl = document.activeElement as HTMLElement | null;
    const currentSectionId = this.getElementSectionId(activeEl, sortedSections);

    let currentIndex = -1;
    if (currentSectionId) {
      currentIndex = sortedSections.findIndex((s) => s.id === currentSectionId);
    }

    let nextIndex = 0;
    if (currentIndex !== -1) {
      nextIndex = currentIndex + direction;
    } else if (direction < 0) {
      nextIndex = sortedSections.length - 1;
    }

    // Handle out-of-bounds page transitions (page boundary navigation)
    if (nextIndex < 0) {
      if (route === "/library" && this.router) {
        accessibilityEvents.emit("ACTION_EXECUTED", { actionName: "Navigate Home", details: "Navigating to Home" });
        this.router.push("/");
      }
      return;
    }

    if (nextIndex >= sortedSections.length) {
      if (route === "/" && this.router) {
        accessibilityEvents.emit("ACTION_EXECUTED", { actionName: "Navigate Library", details: "Navigating to Library" });
        this.router.push("/library");
      }
      return;
    }

    // Try to focus the first element in the next section
    const targetSection = sortedSections[nextIndex];
    const sectionEl = document.querySelector(`[data-nav-section="${targetSection.id}"], #${targetSection.id}`) as HTMLElement | null;

    if (sectionEl) {
      const focusables = Array.from(sectionEl.querySelectorAll(this.getFocusableSelector())) as HTMLElement[];
      const visibleElements = focusables.filter((el) => this.isVisible(el));

      if (visibleElements.length > 0) {
        // Toggle keyboard mode so focus rings show
        accessibilityStore.setState({ keyboardMode: true, currentSection: targetSection.id });
        visibleElements[0].focus();
        
        accessibilityEvents.emit("SECTION_CHANGED", {
          id: targetSection.id,
          name: targetSection.name,
        });
      } else {
        // If section is empty, jump past it
        const currentActive = document.activeElement;
        this.moveSection(direction > 0 ? direction + 1 : direction - 1);
        
        // Prevent infinite loops if all sections are empty
        if (document.activeElement === currentActive) {
          return;
        }
      }
    }
  }
}

export const navigationManager = new NavigationManager();
