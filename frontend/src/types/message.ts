// Shared Message type used across chat components.

export type MessageRole = 'user' | 'assistant' | 'error'

export interface Message {
  id: string;
  role: MessageRole;
  text: string;
  sources?: string[];
}
