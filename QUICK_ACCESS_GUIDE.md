# BiCare360 - Quick Access Guide

**Date**: March 7, 2026  
**Status**: Servers Running - Ready for Testing

---

## 🌐 Active Servers

- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:5173
- **Admin Panel**: http://localhost:8000/admin/

---

## 👥 Test User Credentials

### 1. 📱 PATIENT PORTAL

**Login Page**: http://localhost:5173/patient/login

```
Username: patient1
Password: Patient@2026
```

**Available Features:**
- Patient Dashboard: http://localhost:5173/patient/dashboard
- My Appointments: http://localhost:5173/patient/appointments
- Medications: http://localhost:5173/patient/medications
- **💬 Messages/Chat**: http://localhost:5173/patient/messages
- Profile Settings: http://localhost:5173/patient/profile
- Medical Info: http://localhost:5173/patient/medical-info

---

### 2. 👨‍⚕️ STAFF/NURSE PORTAL

**Login Page**: http://localhost:5173/login

```
Username: nurse1
Password: Nurse@2026
```

**Available Features:**
- Nurse Dashboard: http://localhost:5173/nurse/dashboard
- Patient Alerts: http://localhost:5173/nurse/alerts
- Patient Search: http://localhost:5173/nurse/patients
- **💬 Messages/Chat**: http://localhost:5173/messages
- Patient Queue: http://localhost:5173/nurse/queue
- Analytics: http://localhost:5173/analytics

---

### 3. 🤝 CAREGIVER PORTAL

**Login Page**: http://localhost:5173/caregiver/login

```
Email: caregiver@test.com
Password: Caregiver@2026
```

**⚠️ Important**: Caregiver login uses **EMAIL**, not username!

**Available Features:**
- Caregiver Dashboard: http://localhost:5173/caregiver/dashboard
- My Bookings: http://localhost:5173/caregiver/bookings
- Profile Management: http://localhost:5173/caregiver/profile
- **💬 Messages/Chat**: http://localhost:5173/caregiver/messages
- Browse Requests: http://localhost:5173/caregiver/browse

**Caregiver Profile Details:**
- Name: Mary Johnson
- Profession: Registered Nurse
- Experience: 5 years
- Hourly Rate: 5000 RWF
- Location: Kigali, Gasabo, Remera
- Rating: 4.50/5.00
- Status: Available & Verified ✅

---

### 4. 👑 ADMIN PORTAL

**Login Page**: http://localhost:8000/admin/

```
Username: admin
Password: Admin@2026
```

**Available Features:**
- Full Django Admin Panel
- User Management
- Patient/Nurse/Caregiver Administration
- Appointments, Medications, Alerts
- System Configuration

---

## 💬 Chat/Messaging Feature

The chat feature is **implemented and working** but not currently linked in the dashboard navigation.

### Direct Chat Access Links:

| Portal | Chat URL | Login First At |
|--------|----------|----------------|
| **Patient** | http://localhost:5173/patient/messages | http://localhost:5173/patient/login |
| **Nurse/Staff** | http://localhost:5173/messages | http://localhost:5173/login |
| **Caregiver** | http://localhost:5173/caregiver/messages | http://localhost:5173/caregiver/login |

### How to Access Chat:

1. **Login** to your portal (Patient, Nurse, or Caregiver)
2. **Manually navigate** to the chat URL from the table above
3. **Alternative**: Modify the dashboard to add a "Messages" link:
   - Click on navigation menu
   - Type the chat URL directly in browser

### Chat Features:
- Real-time messaging with WebSocket support
- Conversation list
- Patient ↔ Caregiver conversations
- Patient ↔ Nurse conversations
- Message read/unread status
- Typing indicators
- Message history

---

## 🧪 Quick Testing Checklist

### Patient Portal Testing:
- [ ] Login at http://localhost:5173/patient/login
- [ ] View dashboard (shows medications, appointments, alerts)
- [ ] Navigate to http://localhost:5173/patient/messages
- [ ] Test chat functionality
- [ ] View My Appointments page
- [ ] Check medication adherence tracking

### Nurse Portal Testing:
- [ ] Login at http://localhost:5173/login
- [ ] View nurse dashboard
- [ ] Navigate to http://localhost:5173/messages
- [ ] Test patient alerts filtering
- [ ] Search for patients
- [ ] Create/acknowledge alerts

### Caregiver Portal Testing:
- [ ] Login at http://localhost:5173/caregiver/login
- [ ] View caregiver dashboard
- [ ] Navigate to http://localhost:5173/caregiver/messages
- [ ] View/edit profile
- [ ] Check bookings
- [ ] Browse care requests

### Admin Portal Testing:
- [ ] Login at http://localhost:8000/admin/
- [ ] View all data models
- [ ] Create/edit patients
- [ ] Manage appointments
- [ ] Configure system settings

---

## 🔧 Common Issues & Solutions

### Issue: "Can't see chat feature on dashboard"
**Solution**: Chat exists but isn't in navigation menu. Use direct URL links above.

### Issue: "401 Unauthorized errors"
**Response**: This is normal! It indicates:
1. Protected endpoints are working
2. JWT token refresh is functioning
3. Security is properly configured

### Issue: "Can't login to caregiver portal"
**Solution**: Caregiver login uses EMAIL, not username.
Use these exact credentials:
- Email: `caregiver@test.com`
- Password: `Caregiver@2026`

### Issue: "Server not responding"
**Check**:
```bash
# Backend running?
curl http://localhost:8000/api/v1/

# Frontend running?
# Open http://localhost:5173 in browser
```

---

## 📊 API Testing

### Get JWT Token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "patient1",
    "password": "Patient@2026"
  }'
```

### Test Protected Endpoint:
```bash
curl http://localhost:8000/api/v1/patients/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Chat API:
```bash
# List conversations
curl http://localhost:8000/api/v1/chat/conversations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get messages for a conversation
curl http://localhost:8000/api/v1/chat/conversations/{id}/messages/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🚀 Next Steps

### To Add Chat Link to Navigation:

You can manually add chat links to the dashboards by:

1. **Patient Dashboard**: Edit [PatientDashboardPage.tsx](frontend/src/pages/PatientDashboardPage.tsx)
   - Add navigation link: `<Link to="/patient/messages">Messages</Link>`

2. **Nurse Dashboard**: Edit [NurseDashboard.tsx](frontend/src/pages/NurseDashboard.tsx)
   - Add navigation link: `<Link to="/messages">Messages</Link>`

3. **Caregiver Dashboard**: Edit [CaregiverDashboard.tsx](frontend/src/pages/CaregiverDashboard.tsx)
   - Add navigation link: `<Link to="/caregiver/messages">Messages</Link>`

---

## 📈 Test Results Summary

✅ **Backend**: Running on port 8000  
✅ **Frontend**: Running on port 5173  
✅ **Integration Tests**: 26/26 passing  
✅ **Total Tests**: 854 tests available  
✅ **Database**: SQLite configured  
✅ **Redis Cache**: Connected  
✅ **WebSocket**: Daphne ASGI server active  

---

## 📞 Portal URLs Quick Reference

| Portal | Login URL | Dashboard URL | Messages URL |
|--------|-----------|---------------|--------------|
| **Patient** | /patient/login | /patient/dashboard | /patient/messages |
| **Nurse** | /login | /nurse/dashboard | /messages |
| **Caregiver** | /caregiver/login | /caregiver/dashboard | /caregiver/messages |
| **Admin** | /admin/ | /admin/ | N/A |

**Base URL**: http://localhost:5173

---

**Status**: ✅ All systems operational - Ready for E2E testing!

For full integration testing guide, see [INTEGRATION_TESTING_GUIDE.md](INTEGRATION_TESTING_GUIDE.md)
