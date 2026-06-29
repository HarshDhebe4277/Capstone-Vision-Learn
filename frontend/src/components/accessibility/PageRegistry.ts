export interface NavSection {
  id: string;
  name: string;
  order: number;
}

export interface PageConfig {
  name: string;
  route: string;
  sections: NavSection[];
}

class PageRegistry {
  private pages: Map<string, PageConfig> = new Map();

  constructor() {
    this.registerDefaults();
  }

  private registerDefaults() {
    // 1. Home / Dashboard Page
    this.registerPage({
      name: "Home",
      route: "/",
      sections: [
        { id: "navbar", name: "Navbar Navigation", order: 1 },
        { id: "video-card", name: "Video Narration", order: 2 },
        { id: "notes-card", name: "Notes Narration", order: 3 },
        { id: "stats-bar", name: "System Metrics", order: 4 },
        { id: "footer", name: "Footer Links", order: 5 },
      ],
    });

    // 2. Library Page
    this.registerPage({
      name: "Library",
      route: "/library",
      sections: [
        { id: "navbar", name: "Navbar Navigation", order: 1 },
        { id: "sidebar", name: "Narration Library", order: 2 },
        { id: "player", name: "Media and Insights", order: 3 },
        { id: "chapters", name: "Lecture Chapters", order: 4 },
        { id: "footer", name: "Footer Links", order: 5 },
      ],
    });

    // 3. Processing Page
    this.registerPage({
      name: "Processing",
      route: "/processing",
      sections: [
        { id: "navbar", name: "Navbar Navigation", order: 1 },
        { id: "progress", name: "Overall Progress", order: 2 },
        { id: "steps", name: "Pipeline Steps", order: 3 },
        { id: "cancel", name: "Control Actions", order: 4 },
        { id: "footer", name: "Footer Links", order: 5 },
      ],
    });
  }

  public registerPage(config: PageConfig) {
    this.pages.set(config.route, config);
  }

  public getPageConfig(route: string): PageConfig | null {
    // Exact match
    if (this.pages.has(route)) {
      return this.pages.get(route)!;
    }
    
    // Normalize path by stripping query params
    const cleanRoute = route.split("?")[0];
    if (this.pages.has(cleanRoute)) {
      return this.pages.get(cleanRoute)!;
    }

    // Try fuzzy match (e.g. dynamic routes)
    for (const key of Array.from(this.pages.keys())) {
      if (cleanRoute.startsWith(key) && key !== "/") {
        return this.pages.get(key)!;
      }
    }

    return null;
  }
}

export const pageRegistry = new PageRegistry();
