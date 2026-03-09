/**
 * ChatPage Component
 * 
 * Main chat page combining conversation list and chat window.
 * Provides full messaging functionality for patients and caregivers.
 * 
 * Features:
 * - Two-column layout: conversation list + active chat
 * - Real-time messaging via WebSocket
 * - Responsive design (mobile-first)
 * - Conversation selection
 * - New conversation creation
 * 
 * Author: Didier IMANIRAHARI
 * Date: March 2026
 */

import React, { useState, useEffect } from 'react';
import { ChatList, ChatWindow } from '../components/chat';

export const ChatPage: React.FC = () => {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  /**
   * Get current user from auth context/store
   * For demo purposes, using localStorage or a mock value
   */
  useEffect(() => {
    // TODO: Replace with actual auth context/store
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        setCurrentUserId(user.id);
      } catch (error) {
        console.error('Failed to parse user:', error);
        // Fallback for demo
        setCurrentUserId(1);
      }
    } else {
      // Fallback for demo
      setCurrentUserId(1);
    }
  }, []);

  /**
   * Handle conversation selection
   */
  const handleSelectConversation = (conversationId: string) => {
    setActiveConversationId(conversationId);
  };

  /**
   * Handle new conversation creation
   */
  const handleCreateConversation = () => {
    // TODO: Implement new conversation modal/page
    console.log('Create new conversation');
    alert('New conversation feature coming soon!');
  };

  /**
   * Close chat window (mobile view)
   */
  const handleCloseChat = () => {
    setActiveConversationId(null);
  };

  // Loading state while getting user
  if (!currentUserId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Conversation List - Desktop: always visible, Mobile: togglable */}
      <div className={`
        w-full md:w-96 md:flex-shrink-0 bg-white
        ${activeConversationId ? 'hidden md:block' : 'block'}
      `}>
        <ChatList
          currentUserId={currentUserId}
          activeConversationId={activeConversationId || undefined}
          onSelectConversation={handleSelectConversation}
          onCreateConversation={handleCreateConversation}
        />
      </div>

      {/* Chat Window - Desktop: beside list, Mobile: full screen */}
      <div className={`
        flex-1 
        ${activeConversationId ? 'block' : 'hidden md:flex md:items-center md:justify-center'}
      `}>
        {activeConversationId ? (
          <ChatWindow
            conversationId={activeConversationId}
            conversationTitle="Chat"
            currentUserId={currentUserId}
            onClose={handleCloseChat}
          />
        ) : (
          // Empty state for desktop
          <div className="text-center text-gray-500 p-8">
            <svg
              className="w-24 h-24 mx-auto mb-4 text-gray-300"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"
                clipRule="evenodd"
              />
            </svg>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              Select a conversation
            </h3>
            <p className="text-gray-500">
              Choose a conversation from the list to start messaging
            </p>
          </div>
        )}
      </div>

      {/* Mobile Back Button (when chat is open) */}
      {activeConversationId && (
        <button
          onClick={handleCloseChat}
          className="fixed bottom-4 right-4 md:hidden bg-blue-500 text-white p-4 rounded-full shadow-lg hover:bg-blue-600 transition-colors"
          title="Back to conversations"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}
    </div>
  );
};

export default ChatPage;
