/**
 * Chat API Client for BiCare360
 * 
 * Provides REST API methods for managing conversations and messages.
 * WebSocket connection is handled separately via useWebSocket hook.
 * 
 * Features:
 * - Fetch user's conversations
 * - Create new conversations
 * - Send and receive messages
 * - Mark messages as read
 * - Soft delete messages
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import client from './client';

// Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  get_full_name: string;
}

export interface Participant {
  patient?: {
    id: number;
    user: User;
  };
  caregiver?: {
    id: number;
    user: User;
    profession: string;
  };
  nurse?: {
    id: number;
    user: User;
    specialization: string;
  };
}

export interface Message {
  id: string;
  conversation: string;
  sender: User;
  content: string;
  is_read: boolean;
  read_at: string | null;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  patient: Participant['patient'];
  caregiver: Participant['caregiver'];
  nurse: Participant['nurse'];
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message: Message | null;
  unread_count: number;
}

export interface ConversationCreatePayload {
  patient_id?: number;
  caregiver_id?: number;
  nurse_id?: number;
}

export interface MessageCreatePayload {
  conversation: string;
  content: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Fetch all conversations for the current user
 */
export const getConversations = async (): Promise<PaginatedResponse<Conversation>> => {
  const response = await client.get<PaginatedResponse<Conversation>>('/v1/chat/conversations/');
  return response.data;
};

/**
 * Get a specific conversation by ID
 */
export const getConversation = async (conversationId: string): Promise<Conversation> => {
  const response = await client.get<Conversation>(`/v1/chat/conversations/${conversationId}/`);
  return response.data;
};

/**
 * Create a new conversation
 * Must specify exactly 2 participants (e.g., patient + caregiver)
 */
export const createConversation = async (
  payload: ConversationCreatePayload
): Promise<Conversation> => {
  const response = await client.post<Conversation>('/v1/chat/conversations/', payload);
  return response.data;
};

/**
 * Get messages for a specific conversation
 */
export const getMessages = async (
  conversationId: string,
  page = 1
): Promise<PaginatedResponse<Message>> => {
  const response = await client.get<PaginatedResponse<Message>>('/v1/chat/messages/', {
    params: { conversation: conversationId, page },
  });
  return response.data;
};

/**
 * Send a new message
 * Note: WebSocket should be used for real-time messaging.
 * This is a fallback for HTTP-only clients.
 */
export const sendMessage = async (payload: MessageCreatePayload): Promise<Message> => {
  const response = await client.post<Message>('/v1/chat/messages/', payload);
  return response.data;
};

/**
 * Mark a message as read
 */
export const markMessageAsRead = async (messageId: string): Promise<Message> => {
  const response = await client.patch<Message>(`/v1/chat/messages/${messageId}/`, {
    is_read: true,
  });
  return response.data;
};

/**
 * Soft delete a message (sender only)
 */
export const deleteMessage = async (messageId: string): Promise<void> => {
  await client.delete(`/v1/chat/messages/${messageId}/`);
};

/**
 * Get unread message count across all conversations
 */
export const getUnreadCount = async (): Promise<number> => {
  const conversations = await getConversations();
  return conversations.results.reduce((sum, conv) => sum + conv.unread_count, 0);
};

/**
 * Search messages by content
 */
export const searchMessages = async (query: string): Promise<PaginatedResponse<Message>> => {
  const response = await client.get<PaginatedResponse<Message>>('/v1/chat/messages/', {
    params: { search: query },
  });
  return response.data;
};
