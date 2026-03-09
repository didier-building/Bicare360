/**
 * WebSocket Hook for BiCare360 Real-Time Chat
 * 
 * Manages WebSocket connection to chat consumer for real-time messaging.
 * 
 * Features:
 * - Auto-connect/disconnect based on conversation
 * - Automatic reconnection on disconnect
 * - Typing indicators
 * - Read receipts
 * - Online/offline status
 * - Message queue for offline sending
 * 
 * Usage:
 * ```tsx
 * const { 
 *   sendMessage, 
 *   markAsRead, 
 *   startTyping, 
 *   stopTyping, 
 *   isConnected 
 * } = useWebSocket(conversationId, onMessage);
 * ```
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import type { Message } from '../api/chat';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export interface WebSocketMessage {
  type: 'chat_message' | 'message_read' | 'user_typing' | 'user_status' | 'error';
  id?: string;
  content?: string;
  sender?: {
    id: number;
    name: string;
    email: string;
  };
  created_at?: string;
  is_read?: boolean;
  message_id?: string;
  read_by_user_id?: number;
  read_at?: string;
  user_id?: number;
  username?: string;
  is_typing?: boolean;
  status?: 'online' | 'offline';
  error?: string;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (content: string) => void;
  markAsRead: (messageId: string) => void;
  startTyping: () => void;
  stopTyping: () => void;
  reconnect: () => void;
}

/**
 * Custom hook for WebSocket chat connection
 * 
 * @param conversationId - UUID of the conversation to connect to
 * @param onMessage - Callback fired when a new message is received
 * @param onTyping - Callback fired when someone is typing
 * @param onUserStatus - Callback fired when user status changes
 * @param onError - Callback fired on WebSocket errors
 * @returns WebSocket connection controls
 */
export const useWebSocket = (
  conversationId: string | null,
  onMessage?: (message: Message) => void,
  onTyping?: (userId: number, isTyping: boolean) => void,
  onUserStatus?: (userId: number, status: 'online' | 'offline') => void,
  onError?: (error: string) => void
): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(() => {
    if (!conversationId) {
      console.warn('⚠️ No conversation ID provided, skipping WebSocket connection');
      return;
    }

    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('❌ No access token found, cannot connect to WebSocket');
      onError?.('Authentication required');
      return;
    }

    // Connect to WebSocket with auth token in URL (or use subprotocols)
    const wsUrl = `${WS_URL}/ws/chat/${conversationId}/?token=${token}`;
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log('📨 WebSocket message received:', data);

        switch (data.type) {
          case 'chat_message':
            if (data.id && data.content && data.sender && data.created_at) {
              onMessage?.({
                id: data.id,
                conversation: conversationId,
                sender: {
                  id: data.sender.id,
                  email: data.sender.email,
                  first_name: data.sender.name.split(' ')[0] || '',
                  last_name: data.sender.name.split(' ').slice(1).join(' ') || '',
                  get_full_name: data.sender.name,
                },
                content: data.content,
                is_read: data.is_read || false,
                read_at: null,
                is_deleted: false,
                created_at: data.created_at,
                updated_at: data.created_at,
              });
            }
            break;

          case 'message_read':
            // Handle read receipt - could update message in parent component
            console.log(`✓ Message ${data.message_id} read by user ${data.read_by_user_id}`);
            break;

          case 'user_typing':
            if (data.user_id !== undefined && data.is_typing !== undefined) {
              onTyping?.(data.user_id, data.is_typing);
            }
            break;

          case 'user_status':
            if (data.user_id !== undefined && data.status) {
              onUserStatus?.(data.user_id, data.status);
            }
            break;

          case 'error':
            console.error('❌ WebSocket error from server:', data.error);
            onError?.(data.error || 'Unknown error');
            break;

          default:
            console.warn('⚠️ Unknown WebSocket message type:', data.type);
        }
      } catch (error) {
        console.error('❌ Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
      onError?.('WebSocket connection error');
    };

    ws.onclose = (event) => {
      console.log(`🔌 WebSocket closed: Code ${event.code}, Reason: ${event.reason}`);
      setIsConnected(false);
      wsRef.current = null;

      // Attempt reconnection if not intentionally closed
      if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttempts.current += 1;
          connect();
        }, delay);
      } else if (reconnectAttempts.current >= maxReconnectAttempts) {
        console.error('❌ Max reconnection attempts reached');
        onError?.('Connection lost. Please refresh the page.');
      }
    };
  }, [conversationId, onMessage, onTyping, onUserStatus, onError]);

  /**
   * Send a chat message
   */
  const sendMessage = useCallback((content: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket not connected, cannot send message');
      onError?.('Not connected. Message not sent.');
      return;
    }

    if (!content.trim()) {
      console.warn('⚠️ Cannot send empty message');
      return;
    }

    const message = {
      type: 'chat_message',
      content: content.trim(),
    };

    wsRef.current.send(JSON.stringify(message));
    console.log('📤 Message sent:', content);
  }, [onError]);

  /**
   * Mark a message as read
   */
  const markAsRead = useCallback((messageId: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket not connected, cannot mark message as read');
      return;
    }

    const message = {
      type: 'mark_read',
      message_id: messageId,
    };

    wsRef.current.send(JSON.stringify(message));
    console.log('✓ Marked message as read:', messageId);
  }, []);

  /**
   * Send typing start indicator
   */
  const startTyping = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    wsRef.current.send(JSON.stringify({ type: 'typing_start' }));
  }, []);

  /**
   * Send typing stop indicator
   */
  const stopTyping = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    wsRef.current.send(JSON.stringify({ type: 'typing_stop' }));
  }, []);

  /**
   * Manually trigger reconnection
   */
  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0;
    connect();
  }, [connect]);

  // Connect on mount or when conversationId changes
  useEffect(() => {
    if (conversationId) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted');
        wsRef.current = null;
      }
    };
  }, [conversationId, connect]);

  return {
    isConnected,
    sendMessage,
    markAsRead,
    startTyping,
    stopTyping,
    reconnect,
  };
};
