export type AccessibilityCommandType =
  | "FOCUS_NEXT"
  | "FOCUS_PREVIOUS"
  | "ACTIVATE"
  | "GO_BACK"
  | "GO_HOME"
  | "NEXT_SECTION"
  | "PREVIOUS_SECTION"
  | "STOP";

export interface AccessibilityCommand {
  type: AccessibilityCommandType;
  source: "keyboard" | "voice" | "system";
  payload?: any;
}

type CommandHandler = (command: AccessibilityCommand) => void;

class CommandBus {
  private handlers: Map<AccessibilityCommandType, Set<CommandHandler>> = new Map();

  public registerHandler(commandType: AccessibilityCommandType, handler: CommandHandler): () => void {
    if (!this.handlers.has(commandType)) {
      this.handlers.set(commandType, new Set());
    }
    this.handlers.get(commandType)!.add(handler);
    
    return () => {
      const handlersSet = this.handlers.get(commandType);
      if (handlersSet) {
        handlersSet.delete(handler);
      }
    };
  }

  public dispatch(command: AccessibilityCommand) {
    const handlersSet = this.handlers.get(command.type);
    if (handlersSet) {
      handlersSet.forEach((handler) => {
        try {
          handler(command);
        } catch (err) {
          console.error(`Error in CommandBus handler for command ${command.type}:`, err);
        }
      });
    }
  }
}

export const commandBus = new CommandBus();
