# BiCare360 Portal Access Guide

> DEV ONLY: Internal testing and architecture notes.
> Do not distribute externally with any local/test access details.

## 🏥 **Portal Structure Explained**

BiCare360 currently has **2 portals**, not 3. Here's why:

### Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BiCare360 System                     │
├─────────────────────────────────────────────────────────┤
│  1. 👤 Patient Portal      (/patient/*)                 │
│     - Patients using BiCare360 services                 │
│     - Can book caregivers, view appointments, chat      │
│                                                          │
│  2. 👩‍⚕️ Staff/Nurse Portal  (/dashboard, /messages)    │
│     - Hospital nurses and staff                         │
│     - Monitor patients, manage care, respond to alerts  │
│                                                          │
│  3. 🚫 Caregiver Portal    (DOES NOT EXIST)             │
│     - Caregivers = External contractors (Abafasha)      │
│     - Patients can BROWSE and BOOK them                 │
│     - But caregivers cannot LOGIN to the system         │
└─────────────────────────────────────────────────────────┘
```

## ❓ **Why Only 2 Portals?**

**Caregivers are designed as a marketplace feature:**
- Patients browse available caregivers at `/patient/caregivers`
- Patients book caregivers for home care services
- Caregivers are **external contractors**, not system users
- **No caregiver dashboard/portal was implemented**

**This is an architectural gap** - caregivers can be created in the database but have nowhere to login.

---

## 🔐 **How to Login & Test**

### Option 1: Patient Portal ✅

**URL:** http://localhost:5173/patient/login

**Login:**
- Email: `patient@test.com`
- Password: `test123`

**Features:**
- Dashboard: View health metrics
- Messages: Chat with nurses
- Appointments: Book appointments
- Medications: Track medications
- Caregivers: Browse & book external caregivers

---

### Option 2: Nurse/Staff Portal ✅

**URL:** http://localhost:5173/login

**Login:**
- Email: `nurse@test.com`
- Password: `test123`

**Features:**
- Dashboard: Patient overview
- Messages: Chat with patients
- Alerts: Patient notifications
- Analytics: Care metrics
- Patient Management

---

### Option 3: Caregiver Portal ❌ **NOT AVAILABLE**

**Why it doesn't work:**
```
caregiver@test.com → Cannot login anywhere
                   |
                   ├─ /patient/login → For patients only
                   ├─ /login → For nurses/staff only
                   └─ /caregiver/login → DOES NOT EXIST
```

**The caregiver user you created exists in the database but has no portal to access.**

---

## 🧪 **Testing the Chat Feature**

### Step-by-Step Chat Demo

**1. Login as Patient:**
```
URL: http://localhost:5173/patient/login
Email: patient@test.com
Password: test123
```
→ Click on "Messages" tab

**2. Login as Nurse (in incognito/different browser):**
```
URL: http://localhost:5173/login
Email: nurse@test.com
Password: test123
```
→ Click on "Messages" section

**3. Test Real-Time Chat:**
- You'll see the conversation with 10 demo messages
- Type a new message in one window
- Watch it appear in real-time in the other window
- WebSocket connection enables live updates

---

## 📊 **System Architecture**

### Authentication Flow

```
Patient Login Flow:
┌──────────────┐
│ /patient/login│
└───────┬──────┘
        │
        ▼
  POST /api/v1/patients/login/
        │
        ├─ Check Patient.objects.get(user=user)
        ├─ Generate JWT token
        └─ Return: { patient: {...}, tokens: {...} }
        │
        ▼
  Navigate to /patient/dashboard
```

```
Nurse Login Flow:
┌──────────┐
│  /login  │
└─────┬────┘
       │
       ▼
  POST /api/auth/login/  (Django Auth)
       │
       ├─ Check user.is_staff or has NurseProfile
       ├─ Generate JWT token
       └─ Return: { user: {...}, tokens: {...} }
       │
       ▼
  Navigate to /dashboard
```

```
Caregiver Login Flow:
┌─────────────────┐
│ /caregiver/login│  ← DOES NOT EXIST
└─────────────────┘
       ❌
   NO PORTAL
```

### Database Models

```python
# Patient Portal Users
class Patient(models.Model):
    user = models.OneToOneField(User)
    date_of_birth = models.DateField()
    # ... has portal access ✓

# Nurse/Staff Portal Users  
class NurseProfile(models.Model):
    user = models.OneToOneField(User)
    license_number = models.CharField()
    # ... has portal access ✓

# Caregiver (External Contractors)
class Caregiver(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    first_name = models.CharField()
    profession = models.CharField()
    # ... NO portal access ❌
```

---

## 🛠️ **Building a Caregiver Portal (Future)**

If you need caregivers to login, you would need to:

### 1. Backend (2-3 hours)

**Create login endpoint:**
```python
# apps/caregivers/views.py
@api_view(['POST'])
def caregiver_login(request):
    """Login endpoint for caregivers."""
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(username=email, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=400)
    
    try:
        caregiver = Caregiver.objects.get(user=user)
    except Caregiver.DoesNotExist:
        return Response({'error': 'Caregiver profile not found'}, status=404)
    
    # Generate JWT tokens
    tokens = get_tokens_for_user(user)
    
    return Response({
        'caregiver': CaregiverSerializer(caregiver).data,
        'tokens': tokens,
    })
```

**Add route:**
```python
# apps/caregivers/urls.py
path('login/', views.caregiver_login, name='caregiver-login'),
```

### 2. Frontend (4-5 hours)

**Create pages:**
```
src/pages/caregiver/
  ├── CaregiverLoginPage.tsx
  ├── CaregiverDashboard.tsx
  ├── CaregiverBookings.tsx
  ├── CaregiverProfile.tsx
  └── CaregiverMessages.tsx
```

**Add routes to App.tsx:**
```tsx
// Caregiver Portal Routes
<Route path="/caregiver/login" element={<CaregiverLoginPage />} />
<Route element={<ProtectedCaregiverRoute />}>
  <Route path="/caregiver/dashboard" element={<CaregiverDashboard />} />
  <Route path="/caregiver/messages" element={<ChatPage userType="caregiver" />} />
  <Route path="/caregiver/bookings" element={<CaregiverBookings />} />
  <Route path="/caregiver/profile" element={<CaregiverProfile />} />
</Route>
```

**Create ProtectedCaregiverRoute component:**
```tsx
const ProtectedCaregiverRoute: React.FC = () => {
  const { user } = useAuthStore();
  
  if (!user || user.role !== 'caregiver') {
    return <Navigate to="/caregiver/login" replace />;
  }
  
  return <Outlet />;
};
```

### 3. Features to Implement

- **Dashboard:** Today's bookings, upcoming appointments
- **Bookings:** View/manage patient bookings
- **Messages:** Chat with assigned patients
- **Profile:** Update bio, certifications, hourly rate
- **Availability:** Set availability status
- **Reviews:** View patient reviews

---

## 📋 **Summary**

### Current State
✅ Patient Portal working (`patient@test.com`)  
✅ Nurse Portal working (`nurse@test.com`)  
❌ Caregiver Portal missing (architectural gap)

### Demo Data Created
- Patient: John Doe (patient@test.com)
- Nurse: Jane Smith (nurse@test.com)
- Conversation: 10 messages about medication

### Recommended Actions

**For immediate testing:**
1. Use Patient Portal + Nurse Portal for chat demo
2. Test patient-nurse communication
3. Verify WebSocket real-time updates

**For future development:**
1. Build caregiver portal (1-2 days work)
2. Add caregiver authentication endpoint
3. Create caregiver dashboard & features
4. Enable caregiver-patient messaging

---

## 🔗 **Quick Access Links**

**Frontend:**
- Patient Login: http://localhost:5173/patient/login
- Nurse Login: http://localhost:5173/login
- Patient Dashboard: http://localhost:5173/patient/dashboard
- Nurse Dashboard: http://localhost:5173/dashboard

**Backend:**
- API Root: http://127.0.0.1:8000/api/v1/
- Patient Login Endpoint: http://127.0.0.1:8000/api/v1/patients/login/
- Chat API: http://127.0.0.1:8000/api/v1/chat/
- Django Admin: http://127.0.0.1:8000/admin/

**Demo Credentials:**
```
Patient:
  Email: patient@test.com
  Password: test123

Nurse:
  Email: nurse@test.com
  Password: test123
```

---

## ❓ **FAQ**

**Q: Why can't I login as caregiver@test.com?**  
A: Caregiver portal doesn't exist. Caregivers are external contractors that patients can browse and book, but they don't have system access.

**Q: How do I test the chat feature?**  
A: Login as patient in one browser, nurse in another. Both can access Messages and chat in real-time.

**Q: Can I add a caregiver portal?**  
A: Yes, but it requires backend endpoints, frontend routes, and UI components (1-2 days work).

**Q: What role does the chat support?**  
A: Currently patient-nurse and patient-caregiver conversations (but caregivers can't access them since they have no portal).

---

**Created:** March 2026  
**Last Updated:** March 2026  
**Author:** Didier IMANIRAHARI
