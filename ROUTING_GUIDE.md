# BiCare360 - Routing Architecture & Navigation Guide

## Overview

This document describes the complete routing architecture of the BiCare360 application, including route protection levels, navigation flows, and user journeys.

---

## Route Structure

### 1. Home Routes (Public Access)

| Route | Purpose | Component | Protected |
|-------|---------|-----------|-----------|
| `/` | Smart home page that routes based on auth status | HomePage | No |
| `/login-selection` | Login type selection (Patient vs Staff) | LoginSelectionPage | No |

**Flow:** 
- Unauthenticated users → `/login-selection`
- Authenticated patients → `/patient/dashboard`
- Authenticated staff → `/dashboard`

### 2. Authentication Routes (Public Access)

| Route | Purpose | Component | Protected |
|-------|---------|-----------|-----------|
| `/login` | Staff/Nurse login | LoginPage | No |
| `/patient/login` | Patient login | PatientLoginPage | No |
| `/patient/register` | Patient registration | PatientRegistrationPage | No |

**Security Note:** These routes bypass protection intentionally to allow login. Login pages check if user is already authenticated and redirect to home if so.

### 3. Patient Routes (Protected)

| Route | Purpose | Component | Layout | Protected | Auth Check |
|-------|---------|-----------|--------|-----------|-----------|
| `/patient/dashboard` | Patient home & overview | PatientDashboardPage | PatientLayout | Yes | Patient |
| `/patient/health` | Health progress & vital trends | HealthProgressChartPage | PatientLayout | Yes | Patient |
| `/patient/appointments` | View/book appointments | PatientAppointmentsPage | PatientLayout | Yes | Patient |
| `/patient/appointments/request` | Request new appointment | PatientAppointmentRequestPage | PatientLayout | Yes | Patient |
| `/patient/medications` | Medication list & adherence | PatientMedicationsPage | PatientLayout | Yes | Patient |
| `/patient/alerts` | Health alerts & notifications | PatientAlertsPage | PatientLayout | Yes | Patient |
| `/patient/caregivers` | Browse available caregivers | CaregiverBrowsePage | PatientLayout | Yes | Patient |
| `/patient/caregivers/:id/book` | Book specific caregiver | PatientCaregiversPage | PatientLayout | Yes | Patient |
| `/patient/profile` | Edit patient profile | PatientProfilePage | PatientLayout | Yes | Patient |
| `/patient/settings` | Account settings | PatientSettingsPage | PatientLayout | Yes | Patient |
| `/patient/medical-info` | Medical history & info | PatientMedicalInfoPage | PatientLayout | Yes | Patient |

**Protection:** `ProtectedPatientRoute` wrapper
- Checks `isAuthenticated` flag
- Redirects unauthenticated users to `/patient/login`
- Renders `PatientLayout` for sidebar navigation

### 4. Staff/Nurse Routes (Protected & Role-Based)

| Route | Purpose | Component | Layout | Protected | Auth Check |
|-------|---------|-----------|--------|-----------|-----------|
| `/dashboard` | Nurse home & overview | NurseDashboard | DashboardLayout | Yes | Nurse/Staff |
| `/alerts` | System & patient alerts | AlertsPage | DashboardLayout | Yes | Nurse/Staff |
| `/health` | Patient health overview | HealthProgressChartPage | DashboardLayout | Yes | Nurse/Staff |
| `/health/:patientId` | Specific patient health data | HealthProgressChartPage | DashboardLayout | Yes | Nurse/Staff |
| `/patients` | Patient queue/list | PatientQueuePage | DashboardLayout | Yes | Nurse/Staff |
| `/patients/search` | Advanced patient search | NursePatientSearchPage | DashboardLayout | Yes | Nurse/Staff |
| `/medications` | Medication management | MedicationsPage | DashboardLayout | Yes | Nurse/Staff |
| `/adherence` | Medication adherence tracking | MedicationAdherencePage | DashboardLayout | Yes | Nurse/Staff |
| `/appointments` | Appointment management | AppointmentsPage | DashboardLayout | Yes | Nurse/Staff |
| `/discharge-summaries` | Discharge documentation | DischargeSummariesPage | DashboardLayout | Yes | Nurse/Staff |
| `/analytics` | Analytics & reporting | AnalyticsDashboard | DashboardLayout | Yes | Nurse/Staff |
| `/settings` | Staff settings & preferences | SettingsPage | DashboardLayout | Yes | Nurse/Staff |

**Protection:** `RoleBasedRoute` wrapper with `allowedRoles: ['nurse', 'staff']`
- Checks `isAuthenticated` flag
- Validates `user.role` is 'nurse' or 'staff'
- Redirects unauthorized users to `/patient/login`
- Redirects unauthenticated users to `/patient/login`
- Renders `DashboardLayout` for sidebar navigation

---

## Protection Mechanisms

### 1. ProtectedPatientRoute

**Location:** `src/components/ProtectedPatientRoute.tsx`

```tsx
<Route element={<ProtectedPatientRoute />}>
  <Route path="/patient/dashboard" element={<PatientDashboardPage />} />
  {/* ... other patient routes ... */}
</Route>
```

**Checks:**
- `isAuthenticated === true`
- No role checking (accepts all authenticated users)

**Behavior:**
- Renders `PatientLayout` for authenticated users
- Redirects to `/patient/login` if not authenticated
- Shows loading spinner while checking auth

### 2. RoleBasedRoute

**Location:** `src/components/RoleBasedRoute.tsx`

```tsx
<Route element={<RoleBasedRoute allowedRoles={['nurse', 'staff']} fallbackPath="/patient/login" />}>
  <Route path="/dashboard" element={<NurseDashboard />} />
  {/* ... other staff routes ... */}
</Route>
```

**Checks:**
- `isAuthenticated === true`
- `user.role` is in `allowedRoles`

**Behavior:**
- Renders `DashboardLayout` for authorized staff
- Redirects to `fallbackPath` if unauthorized
- Shows loading spinner while checking auth

### 3. Authentication Store (useAuthStore)

**Location:** `src/stores/authStore.ts`

**Key Methods:**
- `login(username, password)` - Authenticate user
- `logout()` - Clear auth state
- `checkAuth()` - Verify existing session (called on page load)

**Key State:**
- `isAuthenticated: boolean` - Auth status
- `user: User | null` - User object with role
- `isLoading: boolean` - Loading state during auth checks

---

## Navigation Components

### PatientLayout

**Location:** `src/components/layout/PatientLayout.tsx`

**Features:**
- Sidebar with patient navigation links
- Mobile-responsive with toggle
- User profile display
- Logout button with confirmation
- Dark mode support

**Navigation Items:**
- Dashboard
- Health Progress
- Appointments
- Medications
- Alerts
- Caregivers
- Profile
- Settings

### DashboardLayout

**Location:** `src/components/layout/DashboardLayout.tsx`

**Features:**
- Sidebar with staff navigation links
- Mobile-responsive with toggle
- Top bar with menu button
- Dark mode support

**Navigation Items:** (in Sidebar.tsx)
- Dashboard
- Alerts
- Health
- Patients
- Patient Search
- Medications
- Med Adherence
- Appointments
- Discharge Summaries
- Analytics
- Settings

---

## User Journeys

### Patient User Journey

```
1. Visit app → / (HomePage)
   ↓
2. Not authenticated → /login-selection (LoginSelectionPage)
   ↓
3. Click "Patient Portal" → /patient/login (PatientLoginPage)
   ↓
4. Enter credentials → POST /api/v1/patients/login/
   ↓
5. Success → /patient/dashboard (PatientDashboardPage)
   ↓
6. Can access: Dashboard, Health, Appointments, Medications, Alerts, Caregivers, Profile, Settings
   ↓
7. Click Logout → Confirmation → /patient/login
```

### Staff/Nurse User Journey

```
1. Visit app → / (HomePage)
   ↓
2. Not authenticated → /login-selection (LoginSelectionPage)
   ↓
3. Click "Staff Portal" → /login (LoginPage)
   ↓
4. Enter credentials → POST /api/v1/auth/login/
   ↓
5. Success & role is 'nurse'/'staff' → /dashboard (NurseDashboard)
   ↓
6. Can access: Dashboard, Alerts, Health, Patients, Medications, Appointments, Analytics, Settings
   ↓
7. Click Logout → Confirmation → /login
```

### Cross-Role Access Prevention

```
Patient attempts /dashboard
  → RoleBasedRoute checks role
  → Role is not 'nurse'/'staff'
  → Redirect to /patient/login
  
Staff attempts /patient/health without :patientId
  → Should use /health/:patientId instead
  → /health (staff) shows general health overview
  → /patient/health (patient) shows personal health
```

---

## Authentication Flow

### Initial Page Load

```
App.tsx mounts
  ↓
useAuthStore.checkAuth() called in ProtectedRoute/RoleBasedRoute
  ↓
If token exists:
  - GET /api/v1/auth/me/
  - Set user data
  - Set isAuthenticated = true
  ↓
Render appropriate component based on auth status
```

### Login Flow

```
User submits login form
  ↓
POST /api/v1/auth/login/ or /api/v1/patients/login/
  ↓
Server returns access_token & refresh_token
  ↓
localStorage.setItem('access_token', token)
localStorage.setItem('refresh_token', token)
  ↓
useAuthStore.login() sets user & isAuthenticated
  ↓
Navigate to dashboard (based on role)
```

### Logout Flow

```
User clicks Logout button
  ↓
Show confirmation dialog
  ↓
User confirms
  ↓
authAPI.logout() → POST /api/v1/auth/logout/
  ↓
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')
  ↓
useAuthStore.logout() clears user & isAuthenticated
  ↓
Navigate to login page
```

---

## Protected vs Public Routes Summary

### Public Routes (No Authentication Required)
- `/` - Home (smart routing)
- `/login-selection` - Login type selection
- `/login` - Staff login
- `/patient/login` - Patient login
- `/patient/register` - Patient registration

### Protected Patient Routes (Authentication Required)
- All `/patient/*` routes except `/patient/login` and `/patient/register`
- Protection via `ProtectedPatientRoute`
- Redirects to `/patient/login` if not authenticated

### Protected Staff Routes (Authentication + Role Required)
- All `/` and `/health`, `/health/:patientId` routes (except `/patient/*`)
- Protection via `RoleBasedRoute`
- Requires `user.role === 'nurse'` or `user.role === 'staff'`
- Redirects to `/patient/login` if unauthorized

---

## Key Components & Files

| File | Purpose |
|------|---------|
| `src/App.tsx` | Routes definition & setup |
| `src/components/ProtectedRoute.tsx` | ⚠️ **DEPRECATED** - Use ProtectedPatientRoute or RoleBasedRoute |
| `src/components/ProtectedPatientRoute.tsx` | Patient route protection wrapper |
| `src/components/RoleBasedRoute.tsx` | Role-based route protection |
| `src/components/layout/PatientLayout.tsx` | Patient sidebar & navigation |
| `src/components/layout/DashboardLayout.tsx` | Staff sidebar & navigation |
| `src/pages/HomePage.tsx` | Smart home page (auth-based routing) |
| `src/pages/LoginSelectionPage.tsx` | Login type selection UI |
| `src/stores/authStore.ts` | Authentication state management |
| `src/api/auth.ts` | Authentication API calls |

---

## Configuration & Customization

### Adding a New Protected Patient Route

1. Add route to App.tsx under `<Route element={<ProtectedPatientRoute />}>`
2. Route automatically gets PatientLayout with sidebar
3. Route automatically protected with auth check

```tsx
<Route element={<ProtectedPatientRoute />}>
  <Route path="/patient/new-feature" element={<NewFeaturePage />} />
</Route>
```

### Adding a New Protected Staff Route

1. Add route to App.tsx under `<Route element={<RoleBasedRoute allowedRoles={['nurse', 'staff']} />}>`
2. Must be nested under `<Route element={<DashboardLayout />}>`
3. Route automatically gets DashboardLayout with sidebar
4. Route automatically protected with role check

```tsx
<Route element={<RoleBasedRoute allowedRoles={['nurse', 'staff']} fallbackPath="/patient/login" />}>
  <Route element={<DashboardLayout />}>
    <Route path="/new-feature" element={<NewFeaturePage />} />
  </Route>
</Route>
```

### Changing Fallback Path for Role Check

```tsx
<Route element={<RoleBasedRoute 
  allowedRoles={['nurse', 'staff']} 
  fallbackPath="/custom-unauthorized-page"  // Custom redirect
/>}>
  {/* routes */}
</Route>
```

---

## Testing Routes

### Test Patient Flow
1. Go to `http://localhost:5173/patient/login`
2. Use patient credentials
3. Verify redirects to `/patient/dashboard`
4. Verify sidebar shows patient navigation
5. Test clicking different sidebar links
6. Test logout functionality

### Test Staff Flow
1. Go to `http://localhost:5173/login`
2. Use staff credentials
3. Verify redirects to `/dashboard`
4. Verify sidebar shows staff navigation
5. Verify `/health/:patientId` works with valid patient ID
6. Test logout functionality

### Test Protection
1. Try accessing `/dashboard` without login → Should redirect to `/patient/login`
2. Try accessing `/patient/dashboard` without login → Should redirect to `/patient/login`
3. Patient tries accessing `/dashboard` → Should redirect to `/patient/login`
4. Staff tries accessing `/patient/health` → Should work (different route)

---

## Known Issues & TODOs

- [ ] Update ProtectedRoute component or mark as deprecated
- [ ] Add breadcrumb navigation for better UX
- [ ] Add "back" navigation buttons where applicable
- [ ] Add loading skeletons during auth check
- [ ] Add error boundary for better error handling
- [ ] Add 404 page with helpful links
- [ ] Test all routes with various network conditions
- [ ] Add analytics tracking for route changes

---

## Troubleshooting

### User gets stuck in login loop
- Check `localStorage` has valid tokens
- Check `useAuthStore.checkAuth()` is being called
- Check API `/api/v1/auth/me/` returns user with role

### Routes not rendering
- Check route is in correct section (patient vs staff)
- Check route is wrapped with correct protection component
- Check component is exported correctly

### Sidebar not showing
- Verify route is under `<DashboardLayout>` or `<PatientLayout>`
- Check component is nested under `<Outlet />`
- Check CSS classes are not hidden

### Users seeing wrong navigation
- Check `user.role` is set correctly from API
- Verify authentication store has correct user object
- Check sidebar navigation array has correct hrefs

---

## Summary

✅ **Clear entry point:** `/login-selection` for new users
✅ **Smart home routing:** `/` redirects based on auth + role
✅ **Patient protection:** All `/patient/*` routes protected with auth
✅ **Staff protection:** All staff routes protected with auth + role
✅ **Sidebar navigation:** Patient and Staff have dedicated sidebars
✅ **Logout flow:** Clear logout with confirmation
✅ **Role-based access:** Staff cannot access patient routes without role
✅ **No hardcoded paths:** Uses useNavigate for routing

---

**Last Updated:** January 27, 2026
**Status:** Complete - All routing refactored and documented
