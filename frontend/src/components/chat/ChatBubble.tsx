/**
 * ChatBubble Component
 * 
 * Displays an individual chat message with:
 * - Sender name and avatar
 * - Message content
 * - Timestamp
 * - Read status indicator
 * - Different styling for sent vs received messages
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import React from 'react';
import type { Message } from '../../api/chat';
import { formatDistanceToNow } from 'date-fns';

interface ChatBubbleProps {
  message: Message;
  isOwnMessage: boolean;
  showAvatar?: boolean;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  message,
  isOwnMessage,
  showAvatar = true,
}) => {
  const formatTime = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return '';
    }
  };

  return (
    <div
      className={`flex gap-3 mb-4 ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      {showAvatar && (
        <div className="flex-shrink-0">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
            isOwnMessage ? 'bg-blue-500' : 'bg-gray-400'
          }`}>
            {message.sender.first_name[0]}{message.sender.last_name[0]}
          </div>
        </div>
      )}

      {/* Message Bubble */}
      <div className={`flex flex-col max-w-[70%] ${isOwnMessage ? 'items-end' : 'items-start'}`}>
        {/* Sender Name (only show for received messages) */}
        {!isOwnMessage && (
          <span className="text-sm font-medium text-gray-700 mb-1">
            {message.sender.get_full_name}
          </span>
        )}

        {/* Message Content */}
        <div
          className={`px-4 py-2 rounded-2xl break-words ${
            isOwnMessage
              ? 'bg-blue-500 text-white rounded-br-none'
              : 'bg-gray-200 text-gray-900 rounded-bl-none'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Timestamp and Read Status */}
        <div className="flex items-center gap-2 mt-1 px-2">
          <span className="text-xs text-gray-500">
            {formatTime(message.created_at)}
          </span>
          
          {isOwnMessage && (
            <span className="text-xs">
              {message.is_read ? (
                <span className="text-blue-500" title="Read">✓✓</span>
              ) : (
                <span className="text-gray-400" title="Delivered">✓</span>
              )}
            </span>
          )}
        </div>

        {/* Deleted Indicator */}
        {message.is_deleted && (
          <span className="text-xs text-gray-400 italic mt-1">
            Message deleted
          </span>
        )}
      </div>
    </div>
  );
};
