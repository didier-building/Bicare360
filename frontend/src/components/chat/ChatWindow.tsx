/**
 * ChatWindow Component
 * 
 * Main chat interface combining message list and input.
 * Manages WebSocket connection and message state.
 * 
 * Features:
 * - Real-time messaging via WebSocket
 * - Typing indicators
 * - Read receipts
 * - Connection status indicator
 * - Message history
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import React, { useState, useEffect, useCallback } from 'react';
import { getMessages, sendMessage as sendMessageApi } from '../../api/chat';
import type { Message } from '../../api/chat';
import { useWebSocket } from '../../hooks/useWebSocket';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

interface ChatWindowProps {
  conversationId: string;
  conversationTitle: string;
  currentUserId: number;
  onClose?: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  conversationId,
  conversationTitle,
  currentUserId,
  onClose,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUserId, setTypingUserId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle incoming WebSocket messages
   */
  const handleNewMessage = useCallback((message: Message) => {
    setMessages(prev => {
      // Avoid duplicates
      if (prev.some(m => m.id === message.id)) {
        return prev;
      }
      return [...prev, message];
    });

    // Auto-scroll handled by MessageList
  }, []);

  /**
   * Handle typing indicator
   */
  const handleTyping = useCallback((userId: number, isTyping: boolean) => {
    if (userId !== currentUserId) {
      setTypingUserId(isTyping ? userId : null);
      setIsTyping(isTyping);
    }
  }, [currentUserId]);

  /**
   * Handle user status changes
   */
  const handleUserStatus = useCallback((userId: number, status: 'online' | 'offline') => {
    console.log(`User ${userId} is now ${status}`);
    // Could update UI to show online/offline status
  }, []);

  /**
   * Handle WebSocket errors
   */
  const handleError = useCallback((errorMessage: string) => {
    setError(errorMessage);
    setTimeout(() => setError(null), 5000); // Clear error after 5 seconds
  }, []);

  /**
   * WebSocket connection
   */
  const {
    isConnected,
    sendMessage,
    startTyping,
    stopTyping,
    reconnect,
  } = useWebSocket(
    conversationId,
    handleNewMessage,
    handleTyping,
    handleUserStatus,
    handleError
  );

  /**
   * Load initial messages on mount
   */
  useEffect(() => {
    const loadMessages = async () => {
      try {
        setIsLoadingMessages(true);
        const response = await getMessages(conversationId);
        setMessages(response.results);
      } catch (error) {
        console.error('Failed to load messages:', error);
        setError('Failed to load messages. Please refresh.');
      } finally {
        setIsLoadingMessages(false);
      }
    };

    loadMessages();
  }, [conversationId]);

  /**
   * Send message with websocket first, fallback to HTTP when realtime is unavailable.
   */
  const handleSend = useCallback(async (content: string) => {
    if (isConnected) {
      sendMessage(content);
      return;
    }

    try {
      const message = await sendMessageApi({ conversation: conversationId, content });
      setMessages((prev) => {
        if (prev.some((m) => m.id === message.id)) {
          return prev;
        }
        return [...prev, message];
      });
    } catch (sendError) {
      console.error('Failed to send message via HTTP fallback:', sendError);
      setError('Message could not be sent. Please try again.');
    }
  }, [conversationId, isConnected, sendMessage]);

  /**
   * Get typing user name
   */
  const typingUserName = typingUserId
    ? messages.find(m => m.sender.id === typingUserId)?.sender.get_full_name
    : undefined;

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-blue-500 text-white px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{conversationTitle}</h2>
          <div className="flex items-center gap-2 text-sm">
            {isConnected ? (
              <>
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                <span>Connected</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></span>
                <span>Disconnected</span>
                <button
                  onClick={reconnect}
                  className="ml-2 text-xs underline hover:no-underline"
                >
                  Reconnect
                </button>
              </>
            )}
          </div>
        </div>

        {/* Close Button */}
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-blue-600 rounded-full transition-colors"
            title="Close chat"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 px-4 py-3">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Messages */}
      <MessageList
        messages={messages}
        currentUserId={currentUserId}
        isLoading={isLoadingMessages}
        isTyping={isTyping}
        typingUserName={typingUserName}
      />

      {/* Input */}
      <MessageInput
        onSend={handleSend}
        onTypingStart={startTyping}
        onTypingStop={stopTyping}
        disabled={false}
        placeholder={isConnected ? 'Type a message...' : 'Type a message (sending without realtime)...'}
      />
    </div>
  );
};
