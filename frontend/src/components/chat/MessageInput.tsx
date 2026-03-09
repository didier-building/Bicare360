/**
 * MessageInput Component
 * 
 * Input field for composing and sending chat messages.
 * 
 * Features:
 * - Multi-line text input with auto-resize
 * - Send button (enabled only when input has content)
 * - Typing indicator broadcast
 * - Enter to send (Shift+Enter for new line)
 * - Character counter (max 5000)
 * - File attachment button (future)
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import React, { useState, useRef, useEffect } from 'react';

interface MessageInputProps {
  onSend: (content: string) => void;
  onTypingStart?: () => void;
  onTypingStop?: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSend,
  onTypingStart,
  onTypingStop,
  disabled = false,
  placeholder = 'Type a message...',
}) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const maxLength = 5000;
  const remainingChars = maxLength - message.length;
  const isNearLimit = remainingChars < 100;

  /**
   * Auto-resize textarea based on content
   */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  /**
   * Handle typing indicator
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    
    // Enforce max length
    if (value.length <= maxLength) {
      setMessage(value);

      // Typing indicator logic
      if (value.length > 0 && !isTyping) {
        setIsTyping(true);
        onTypingStart?.();
      }

      // Reset typing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }

      // Stop typing after 2 seconds of inactivity
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(false);
        onTypingStop?.();
      }, 2000);
    }
  };

  /**
   * Handle send message
   */
  const handleSend = () => {
    const trimmedMessage = message.trim();
    
    if (trimmedMessage && !disabled) {
      onSend(trimmedMessage);
      setMessage('');
      setIsTyping(false);
      onTypingStop?.();
      
      // Clear typing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }

      // Focus back on input
      textareaRef.current?.focus();
    }
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter to send (Shift+Enter for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="border-t bg-white p-4">
      <div className="flex items-end gap-2">
        {/* Message Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={placeholder}
            className={`w-full px-4 py-3 pr-12 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed ${
              isNearLimit ? 'border-orange-400' : 'border-gray-300'
            }`}
            rows={1}
            style={{ minHeight: '48px', maxHeight: '150px' }}
          />
          
          {/* Character Counter */}
          {isNearLimit && (
            <div className="absolute bottom-2 right-2 text-xs text-orange-500 font-medium">
              {remainingChars}
            </div>
          )}
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            disabled || !message.trim()
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600 active:scale-95'
          }`}
          title={disabled ? 'Cannot send message' : 'Send message (Enter)'}
        >
          {disabled ? (
            <span className="inline-block w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></span>
          ) : (
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Helper Text */}
      <div className="mt-2 text-xs text-gray-500">
        Press <kbd className="px-1 py-0.5 bg-gray-100 border border-gray-300 rounded">Enter</kbd> to send, 
        <kbd className="px-1 py-0.5 bg-gray-100 border border-gray-300 rounded ml-1">Shift + Enter</kbd> for new line
      </div>
    </div>
  );
};
