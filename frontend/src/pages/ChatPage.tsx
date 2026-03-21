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
import toast from 'react-hot-toast';
import { ChatList, ChatWindow } from '../components/chat';
import { createConversation, getConversations } from '../api/chat';

type ConversationTarget = {
  label: string;
  payload: {
    patient_id?: number;
    caregiver_id?: number;
    nurse_id?: number;
  };
};

export const ChatPage: React.FC = () => {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  /**
   * Read current user id from localStorage user object or JWT as fallback.
   */
  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        if (user?.id) {
          setCurrentUserId(Number(user.id));
          return;
        }
      } catch (error) {
        console.error('Failed to parse user:', error);
      }
    }

    // Fallback: decode JWT payload to get user_id
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const payloadBase64 = token.split('.')[1];
        const payload = JSON.parse(atob(payloadBase64));
        if (payload?.user_id) {
          setCurrentUserId(Number(payload.user_id));
          return;
        }
      } catch (error) {
        console.error('Failed to decode access token:', error);
      }
    }

    setCurrentUserId(1);
  }, []);

  /**
   * Handle conversation selection
   */
  const handleSelectConversation = (conversationId: string) => {
    setActiveConversationId(conversationId);
  };

  /**
   * Ask user to choose a target when multiple options exist.
   */
  const pickTarget = (targets: ConversationTarget[]): ConversationTarget | null => {
    if (targets.length === 0) return null;
    if (targets.length === 1) return targets[0];

    const options = targets
      .map((target, index) => `${index + 1}. ${target.label}`)
      .join('\n');

    const raw = window.prompt(`Choose who to chat with:\n\n${options}\n\nEnter number:`);
    if (!raw) return null;

    const selectedIndex = Number(raw) - 1;
    if (Number.isNaN(selectedIndex) || selectedIndex < 0 || selectedIndex >= targets.length) {
      toast.error('Invalid selection. Please try again.');
      return null;
    }

    return targets[selectedIndex];
  };

  /**
   * Handle new conversation creation from role-based relationships.
   */
  const handleCreateConversation = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        toast.error('Please log in first.');
        return;
      }
      const apiUrl = import.meta.env.VITE_API_URL || '/api';

      const role = (localStorage.getItem('user_role') || '').toLowerCase();
      const targets: ConversationTarget[] = [];

      // Patient and caregiver both derive chat pairs from caregiver bookings.
      if (role === 'patient' || role === 'caregiver') {
        const bookingsResponse = await fetch(`${apiUrl}/v1/caregivers/bookings/`, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!bookingsResponse.ok) {
          toast.error('Failed to load bookings to start conversation.');
          return;
        }

        const bookingsData = await bookingsResponse.json();
        const bookings = bookingsData.results || bookingsData;

        if (!Array.isArray(bookings) || bookings.length === 0) {
          toast.error('No bookings found. You need at least one booking to start a chat.');
          return;
        }

        const uniquePairs = new Set<string>();

        for (const booking of bookings) {
          const patientId = Number(booking?.patient);
          const caregiverId = Number(booking?.caregiver);

          if (!patientId || !caregiverId) continue;

          const key = `${patientId}:${caregiverId}`;
          if (uniquePairs.has(key)) continue;
          uniquePairs.add(key);

          const patientName = booking?.patient_name || `Patient #${patientId}`;
          const caregiverName = booking?.caregiver_name || `Caregiver #${caregiverId}`;

          targets.push({
            label: role === 'patient' ? caregiverName : patientName,
            payload: {
              patient_id: patientId,
              caregiver_id: caregiverId,
            },
          });
        }
      }

      // Nurses derive chat pairs from nurse-patient assignments.
      if (role === 'nurse') {
        const assignmentsResponse = await fetch(`${apiUrl}/v1/nursing/assignments/my_patients/`, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!assignmentsResponse.ok) {
          toast.error('Failed to load nurse assignments to start conversation.');
          return;
        }

        const assignmentsData = await assignmentsResponse.json();
        const assignments = assignmentsData.results || assignmentsData;

        if (!Array.isArray(assignments) || assignments.length === 0) {
          toast.error('No active assignments found. Assign a patient first to start a chat.');
          return;
        }

        const uniquePairs = new Set<string>();

        for (const assignment of assignments) {
          const patientId = Number(assignment?.patient?.id || assignment?.patient);
          const nurseId = Number(assignment?.nurse?.id || assignment?.nurse);

          if (!patientId || !nurseId) continue;

          const key = `${patientId}:${nurseId}`;
          if (uniquePairs.has(key)) continue;
          uniquePairs.add(key);

          const firstName = assignment?.patient?.user?.first_name || assignment?.patient?.first_name || 'Patient';
          const lastName = assignment?.patient?.user?.last_name || assignment?.patient?.last_name || '';
          const patientName = `${firstName} ${lastName}`.trim();

          targets.push({
            label: patientName || `Patient #${patientId}`,
            payload: {
              patient_id: patientId,
              nurse_id: nurseId,
            },
          });
        }
      }

      if (targets.length === 0) {
        toast.error('No eligible chat participants found for your role yet.');
        return;
      }

      const selectedTarget = pickTarget(targets);
      if (!selectedTarget) {
        return;
      }

      try {
        const conversation = await createConversation(selectedTarget.payload);
        setActiveConversationId(conversation.id);
        toast.success(`Conversation opened with ${selectedTarget.label}.`);
      } catch (error: any) {
        // Defensive fallback: find existing conversation in list.
        const conversations = await getConversations();
        const existing = conversations.results.find((c) => {
          const patientMatch = selectedTarget.payload.patient_id
            ? c.patient?.id === selectedTarget.payload.patient_id
            : c.patient == null;
          const caregiverMatch = selectedTarget.payload.caregiver_id
            ? c.caregiver?.id === selectedTarget.payload.caregiver_id
            : c.caregiver == null;
          const nurseMatch = selectedTarget.payload.nurse_id
            ? c.nurse?.id === selectedTarget.payload.nurse_id
            : c.nurse == null;
          return patientMatch && caregiverMatch && nurseMatch;
        });

        if (existing) {
          setActiveConversationId(existing.id);
          toast.success(`Opened existing conversation with ${selectedTarget.label}.`);
          return;
        }

        const responseData = error?.response?.data;
        console.error('Conversation create failed:', responseData || error);
        toast.error('Could not open conversation. Please try again.');
      }
    } catch (error) {
      console.error('Create conversation failed:', error);
      toast.error('Could not create conversation.');
    }
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
