/**
 * ChatList Component
 * 
 * Displays list of all conversations with preview and unread counts.
 * Allows users to select a conversation to open.
 * 
 * Features:
 * - Conversation preview with last message
 * - Unread message count badges
 * - Search/filter conversations
 * - Active conversation highlighting
 * - Create new conversation button
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import React, { useState, useEffect } from 'react';
import { format, isToday, isYesterday } from 'date-fns';
import { getConversations } from '../../api/chat';
import type { Conversation, User } from '../../api/chat';

interface ChatListProps {
  currentUserId: number;
  activeConversationId?: string;
  onSelectConversation: (conversationId: string) => void;
  onCreateConversation?: () => void;
}

export const ChatList: React.FC<ChatListProps> = ({
  currentUserId,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
}) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  /**
   * Load conversations on mount
   */
  useEffect(() => {
    const loadConversations = async () => {
      try {
        setIsLoading(true);
        const response = await getConversations();
        setConversations(response.results);
      } catch (error) {
        console.error('Failed to load conversations:', error);
        setError('Failed to load conversations');
      } finally {
        setIsLoading(false);
      }
    };

    loadConversations();
  }, []);

  /**
   * Filter conversations by search query
   */
  const filteredConversations = conversations.filter(conv => {
    if (!searchQuery.trim()) return true;
    
    const query = searchQuery.toLowerCase();
    
    // Search in participant names
    const searchableUsers: User[] = [];
    if (conv.patient?.user) searchableUsers.push(conv.patient.user);
    if (conv.caregiver?.user) searchableUsers.push(conv.caregiver.user);
    if (conv.nurse?.user) searchableUsers.push(conv.nurse.user);
    
    return searchableUsers.some(user => 
      user.get_full_name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    );
  });

  /**
   * Format timestamp for conversation preview
   */
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    
    if (isToday(date)) {
      return format(date, 'HH:mm');
    } else if (isYesterday(date)) {
      return 'Yesterday';
    } else {
      return format(date, 'MMM d');
    }
  };

  /**
   * Get conversation title
   */
  const getConversationTitle = (conversation: Conversation): string => {
    // Get other participants (not the current user)
    const otherParticipants: User[] = [];
    
    if (conversation.patient?.user && conversation.patient.user.id !== currentUserId) {
      otherParticipants.push(conversation.patient.user);
    }
    if (conversation.caregiver?.user && conversation.caregiver.user.id !== currentUserId) {
      otherParticipants.push(conversation.caregiver.user);
    }
    if (conversation.nurse?.user && conversation.nurse.user.id !== currentUserId) {
      otherParticipants.push(conversation.nurse.user);
    }
    
    if (otherParticipants.length === 1) {
      return otherParticipants[0].get_full_name;
    }
    
    // For group chats, show all participant names
    return otherParticipants
      .map(user => user.get_full_name.split(' ')[0]) // First names only
      .join(', ') || 'Conversation';
  };

  /**
   * Get initials for avatar
   */
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Messages</h2>
          
          {/* New Conversation Button */}
          {onCreateConversation && (
            <button
              onClick={onCreateConversation}
              className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors"
              title="New conversation"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          )}
        </div>

        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <svg
            className="absolute left-3 top-2.5 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : error ? (
          <div className="p-4 text-center text-red-600">
            <p>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 text-sm text-blue-500 hover:underline"
            >
              Retry
            </button>
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
            </svg>
            {searchQuery ? (
              <p>No conversations found for "{searchQuery}"</p>
            ) : (
              <>
                <p className="mb-2">No conversations yet</p>
                {onCreateConversation && (
                  <button
                    onClick={onCreateConversation}
                    className="text-sm text-blue-500 hover:underline"
                  >
                    Start a conversation
                  </button>
                )}
              </>
            )}
          </div>
        ) : (
          <div>
            {filteredConversations.map((conversation) => {
              const isActive = conversation.id === activeConversationId;
              const title = getConversationTitle(conversation);
              
              // Get the other participant's user for avatar
              let otherUser: User | null = null;
              if (conversation.patient?.user && conversation.patient.user.id !== currentUserId) {
                otherUser = conversation.patient.user;
              } else if (conversation.caregiver?.user && conversation.caregiver.user.id !== currentUserId) {
                otherUser = conversation.caregiver.user;
              } else if (conversation.nurse?.user && conversation.nurse.user.id !== currentUserId) {
                otherUser = conversation.nurse.user;
              }
              
              return (
                <button
                  key={conversation.id}
                  onClick={() => onSelectConversation(conversation.id)}
                  className={`w-full p-4 flex items-start gap-3 hover:bg-gray-50 transition-colors border-b border-gray-100 ${
                    isActive ? 'bg-blue-50 hover:bg-blue-50' : ''
                  }`}
                >
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold ${
                    isActive ? 'bg-blue-500' : 'bg-gray-400'
                  }`}>
                    {otherUser ? getInitials(otherUser.get_full_name) : '?'}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0 text-left">
                    <div className="flex items-baseline justify-between mb-1">
                      <h3 className={`font-semibold truncate ${
                        isActive ? 'text-blue-600' : 'text-gray-900'
                      }`}>
                        {title}
                      </h3>
                      {conversation.last_message && (
                        <span className="ml-2 text-xs text-gray-500 flex-shrink-0">
                          {formatTimestamp(conversation.last_message.created_at)}
                        </span>
                      )}
                    </div>

                    {/* Last Message Preview */}
                    {conversation.last_message && (
                      <p className="text-sm text-gray-600 truncate">
                        {conversation.last_message.sender.id === currentUserId && 'You: '}
                        {conversation.last_message.content}
                      </p>
                    )}

                    {/* Unread Badge */}
                    {conversation.unread_count > 0 && (
                      <div className="mt-1">
                        <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                          {conversation.unread_count > 99 ? '99+' : conversation.unread_count}
                        </span>
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
