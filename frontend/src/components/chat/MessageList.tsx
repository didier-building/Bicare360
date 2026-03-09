/**
 * MessageList Component
 * 
 * Displays a scrollable list of chat messages in a conversation.
 * 
 * Features:
 * - Auto-scroll to bottom on new messages
 * - Infinite scroll for loading older messages
 * - Typing indicator
 * - Empty state
 * - Loading state
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import React, { useEffect, useRef } from 'react';
import type { Message } from '../../api/chat';
import { ChatBubble } from './ChatBubble';

interface MessageListProps {
  messages: Message[];
  currentUserId: number;
  isLoading?: boolean;
  isTyping?: boolean;
  typingUserName?: string;
  onLoadMore?: () => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  currentUserId,
  isLoading = false,
  isTyping = false,
  typingUserName,
  onLoadMore,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  /**
   * Handle scroll to top for loading more messages
   */
  const handleScroll = () => {
    if (!containerRef.current || !onLoadMore) return;

    const { scrollTop } = containerRef.current;
    if (scrollTop === 0) {
      onLoadMore();
    }
  };

  if (isLoading && messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading messages...</p>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md px-4">
          <div className="text-6xl mb-4">💬</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            No messages yet
          </h3>
          <p className="text-gray-500">
            Start the conversation by sending a message below
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto bg-gray-50 p-4 space-y-1"
    >
      {/* Load More Indicator */}
      {isLoading && messages.length > 0 && (
        <div className="text-center py-2">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Messages */}
      {messages
        .filter(msg => !msg.is_deleted) // Don't show deleted messages
        .map((message) => (
          <ChatBubble
            key={message.id}
            message={message}
            isOwnMessage={message.sender.id === currentUserId}
            showAvatar={true}
          />
        ))}

      {/* Typing Indicator */}
      {isTyping && (
        <div className="flex gap-3 mb-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-gray-400 flex items-center justify-center text-white font-semibold">
              {typingUserName?.[0] || '?'}
            </div>
          </div>
          <div className="bg-gray-200 rounded-2xl rounded-bl-none px-4 py-3">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        </div>
      )}

      {/* Scroll Anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};
