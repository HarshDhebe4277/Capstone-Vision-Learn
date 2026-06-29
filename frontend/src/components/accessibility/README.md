# Accessibility Navigation Engine (Part 1 - Keyboard-First Navigation)

This package contains a decoupled, event-driven accessibility system for keyboard-only web operation and is designed as the structural foundation for Voice Navigation (Part 2).

## Architecture Overview

Instead of coupling input controls to execution behaviors, this architecture uses a centralized **Command Bus** and **State Store** to route inputs and track page accessibility state. 

```
  [Input Sources]
  Keyboard Controller   Voice Controller (Part 2)
         │                         │
         └───────────┬─────────────┘
                     ▼
          Accessibility Command Bus
                     │
                     ▼
            Accessibility Store  ◄─────────┐
                     │                     │
                     ├─────────────────────┼─────────────────────┐
                     ▼                     ▼                     ▼
               FocusManager        NavigationManager       ActionManager
                     │                     │                     │
                     └─────────────────────┼─────────────────────┘
                                           ▼
                                  Accessibility Events
                                           │
                                           ▼
                                     SpeechManager
                                           │
                                           ▼
                                   Browser TTS Engine
```

---

## 1. Core Modules

| Module | Filename | Description |
| :--- | :--- | :--- |
| **Store** | `AccessibilityStore.ts` | Global store tracking focus, current sections, page route names, and active modes. |
| **Command Bus** | `CommandBus.ts` | Dispatches payload-based command messages (`type`, `source`, `payload`) such as `FOCUS_NEXT`, `ACTIVATE`, etc. |
| **Events** | `AccessibilityEvents.ts` | An event emitter (`on`, `off`, `emit`) notifying listeners of states like `FOCUS_CHANGED`. |
| **Speech Manager** | `SpeechManager.ts` | Basic TTS wrapper with a sequential queue and priority tiers (`LOW` to `CRITICAL`) to avoid audio overlaps. |
| **Page Registry** | `PageRegistry.ts` | Maps page routes to order-based section collections for deterministic page section flow. |
| **Focus Manager** | `FocusManager.ts` | Caches focusable elements dynamically via MutationObservers, moves focus (`FOCUS_NEXT`, `FOCUS_PREVIOUS`), and restores focus indexes on routing. |
| **Navigation Manager** | `NavigationManager.ts` | Executes section transitions (`NEXT_SECTION`, `PREVIOUS_SECTION`) using registry metadata. |
| **Action Manager** | `ActionManager.ts` | Handles custom confirmed click triggers (`ACTIVATE`), history back (`GO_BACK`), Escape cancel (`STOP`), and double-space home triggers (`GO_HOME`). |
| **Keyboard Controller** | `KeyboardController.ts` | Captures key events and dispatches commands to the bus, ignoring inputs when typing in forms/sliders. |

---

## 2. Command Flow Example

When the user navigates:

1. **User presses `ArrowDown`**:
   - `KeyboardController` catches the key event.
   - It checks that focus is not inside an active text input or textarea.
   - It dispatches: `commandBus.dispatch({ type: "FOCUS_NEXT", source: "keyboard" })`.
2. **Command Bus routes to FocusManager**:
   - `FocusManager` updates current focus state: `accessibilityStore.setState({ keyboardMode: true })`.
   - Focus is shifted to the next element: `nextElement.focus()`.
   - Element focus attributes are evaluated and `FOCUS_CHANGED` is emitted: `accessibilityEvents.emit("FOCUS_CHANGED", { label: "...", description: "..." })`.
3. **Event triggers announcement**:
   - `SpeechManager` catches `FOCUS_CHANGED`.
   - It pushes the announcement into the speech queue.
   - Browser speaks the element's label and description to the user.

---

## 3. How Voice Navigation (Part 2) Integrates

Because all logic is decoupled:

- **No Navigation Rewrite**: To add Voice Navigation, Part 2 only needs to instantiate a voice recognition listener.
- **Direct Dispatching**: If the user says *"Next"*, the voice listener translates it and calls:
  ```typescript
  commandBus.dispatch({ type: "FOCUS_NEXT", source: "voice" });
  ```
- **Direct Action Execution**: If the user says *"Confirm"* or *"Open"*, it dispatches:
  ```typescript
  commandBus.dispatch({ type: "ACTIVATE", source: "voice" });
  ```
- **Speaking State Sync**: Voice Mode can enable or disable TTS by calling:
  ```typescript
  accessibilityStore.setState({ voiceMode: true, speechEnabled: true });
  ```
- **Unified Testing**: Core navigation/activation logic remains unchanged and is shared across all inputs.
