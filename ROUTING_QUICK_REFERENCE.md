# 🚀 BiCare360 Routing - Quick Reference Card

## Entry Point
```
http://localhost:5173
         ↓
 /login-selection
   ↓              ↓
Patient       Staff
Portal        Portal
   ↓              ↓
/patient/login  /login
   ↓              ↓
Patient Auth  Staff Auth
   ↓              ↓
/patient/      /dashboard
dashboard
```

---

## Routes at a Glance

### 👤 Patient Routes (Protected with Auth)
| Route | Layout | Purpose |
|-------|--------|---------|
| `/patient/dashboard` | PatientLayout | Home |
| `/patient/health` | PatientLayout | Health Progress & Charts |
| `/patient/appointments` | PatientLayout | View/Book Appointments |
| `/patient/medications` | PatientLayout | Medication List |
| `/patient/alerts` | PatientLayout | Health Alerts |
| `/patient/caregivers` | PatientLayout | Browse Caregivers |
| `/patient/profile` | PatientLayout | Edit Profile |
| `/patient/settings` | PatientLayout | Account Settings |

**Protection:** Authentication check only ✓

---

### 👨‍⚕️ Staff Routes (Protected with Auth + Role)
| Route | Layout | Purpose |
|-------|--------|---------|
| `/dashboard` | DashboardLayout | Nurse Home |
| `/alerts` | DashboardLayout | System Alerts |
| `/health` | DashboardLayout | Patient Health Overview |
| `/health/:patientId` | DashboardLayout | Specific Patient Health |
| `/patients` | DashboardLayout | Patient Queue |
| `/patients/search` | DashboardLayout | Advanced Search |
| `/medications` | DashboardLayout | Medication Management |
| `/adherence` | DashboardLayout | Med Adherence |
| `/appointments` | DashboardLayout | Appointment Management |
| `/discharge-summaries` | DashboardLayout | Discharge Docs |
| `/analytics` | DashboardLayout | Reports & Analytics |
| `/settings` | DashboardLayout | Preferences |

**Protection:** Authentication check + Role check (nurse/staff) ✓

---

## Components

### Protection Components
```tsx
<ProtectedPatientRoute />      // Auth check → PatientLayout
<RoleBasedRoute allowedRoles={['nurse','staff']} />  // Auth + Role → DashboardLayout
```

### Layout Components
```tsx
<PatientLayout>         // Patient sidebar (8 items)
<DashboardLayout>       // Staff sidebar (11 items)
```

---

## Protection Logic

### ProtectedPatientRoute
```javascript
if (!isAuthenticated) {
  redirect('/patient/login')
}
// Render PatientLayout + Outlet
```

### RoleBasedRoute
```javascript
if (!isAuthenticated) {
  redirect('/patient/login')
}
if (user.role not in ['nurse', 'staff']) {
  redirect('/patient/login')
}
// Render DashboardLayout + Outlet
```

---

## Patient Navigation Items
```
Dashboard
├─ /patient/dashboard (HomeIcon)

Health Progress
├─ /patient/health (HeartIcon)

Appointments
├─ /patient/appointments (CalendarDaysIcon)

Medications
├─ /patient/medications (BeakerIcon)

Alerts
├─ /patient/alerts (BellAlertIcon)

Caregivers
├─ /patient/caregivers (UserIcon)

Profile
├─ /patient/profile (UserIcon)

Settings
├─ /patient/settings (Cog6ToothIcon)

[Logout Button]
```

---

## Staff Navigation Items
```
Dashboard
├─ /dashboard (HomeIcon)

Alerts
├─ /alerts (BellAlertIcon)

Health
├─ /health (HeartIcon)

Patients
├─ /patients (UsersIcon)

Patient Search
├─ /patients/search (UsersIcon)

Medications
├─ /medications (BeakerIcon)

Med Adherence
├─ /adherence (CalendarDaysIcon)

Appointments
├─ /appointments (CalendarDaysIcon)

Discharge Summaries
├─ /discharge-summaries (DocumentTextIcon)

Analytics
├─ /analytics (ChartBarIcon)

Settings
├─ /settings (Cog6ToothIcon)

[Logout Button]
```

---

## Access Control Matrix

| User Type | Can Access | Redirects |
|-----------|-----------|-----------|
| Unauthenticated | /login, /patient/login, /login-selection | Protected → /patient/login |
| Patient (Auth) | /patient/* | Staff routes → /patient/login |
| Staff (Auth) | /dashboard, /alerts, /health, /patients, etc. | Patient routes → /patient/login |
| Staff (Wrong Role) | ❌ Nothing | All protected → /patient/login |

---

## Testing Quick Checklist

### Patient Flow
- [ ] Go to `/patient/login` → Enter creds → `/patient/dashboard` ✓
- [ ] Click "Health" → `/patient/health` with PatientLayout ✓
- [ ] Click "Settings" → `/patient/settings` with PatientLayout ✓
- [ ] Try `/dashboard` → Redirect to `/patient/login` ✓
- [ ] Logout → Confirm → `/patient/login` ✓

### Staff Flow
- [ ] Go to `/login` → Enter creds → `/dashboard` ✓
- [ ] Click "Alerts" → `/alerts` with DashboardLayout ✓
- [ ] Click "Patients" → `/patients` with DashboardLayout ✓
- [ ] Try `/patient/dashboard` → Redirect to `/patient/login` ✓
- [ ] Logout → Confirm → `/login` ✓

### Protection Check
- [ ] Patient tries `/dashboard` → Redirect ✓
- [ ] Staff tries `/patient/health` → Redirect ✓
- [ ] Unauthenticated tries any protected → Redirect ✓

---

## File Locations

### Core Routing
- `src/App.tsx` - All routes defined here
- `src/components/RoleBasedRoute.tsx` - Role validation
- `src/components/ProtectedPatientRoute.tsx` - Patient auth wrapper

### Layouts
- `src/components/layout/PatientLayout.tsx` - Patient sidebar
- `src/components/layout/DashboardLayout.tsx` - Staff sidebar

### Pages
- `src/pages/HomePage.tsx` - Smart home routing
- `src/pages/LoginSelectionPage.tsx` - Login choice page

### Auth Store
- `src/stores/authStore.ts` - Auth state management

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Loop between pages | Wrong layout | Check route is under correct protection |
| Can't login | API issue | Check backend `/api/v1/auth/login/` works |
| Sidebar missing | Not using layout | Check route is under DashboardLayout/PatientLayout |
| Redirects to login | Role mismatch | Check user.role is 'nurse' or 'staff' |
| Deep link 404 | Route not defined | Add route to App.tsx |
| Can access /dashboard as patient | No protection | Check route is under RoleBasedRoute |

---

## Code Examples

### Add New Patient Route
```tsx
<Route element={<ProtectedPatientRoute />}>
  <Route path="/patient/new-page" element={<NewPageComponent />} />
</Route>
```

### Add New Staff Route
```tsx
<Route element={<RoleBasedRoute allowedRoles={['nurse', 'staff']} />}>
  <Route element={<DashboardLayout />}>
    <Route path="/new-page" element={<NewPageComponent />} />
  </Route>
</Route>
```

### Check User Role
```tsx
const { user } = useAuthStore();

if (user?.role === 'nurse') {
  // Show nurse-only feature
}
```

### Redirect After Login
```tsx
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
navigate('/patient/dashboard');  // Patient
navigate('/dashboard');          // Staff
```

---

## Security Reminders

✅ **Never** put patient data route without ProtectedPatientRoute  
✅ **Always** check role before showing staff features  
✅ **Always** verify token on app load (checkAuth)  
✅ **Always** clear tokens on logout  
✅ **Never** store sensitive data in localStorage  
✅ **Always** redirect unauthorized users  

---

## Status Summary

| Item | Status |
|------|--------|
| Patient Routes Protected | ✅ Complete |
| Staff Routes Protected | ✅ Complete |
| Role Validation | ✅ Complete |
| Patient Navigation | ✅ Complete |
| Staff Navigation | ✅ Complete |
| Smart Home Routing | ✅ Complete |
| Login Selection | ✅ Complete |
| Documentation | ✅ Complete |
| Build Status | ✅ Clean |
| Ready for Testing | ✅ Yes |

---

## Documentation Files

- 📄 `ROUTING_GUIDE.md` - Full technical docs (400+ lines)
- 📄 `ROUTING_SUMMARY.md` - Executive summary
- 📄 `ROUTING_TESTING_CHECKLIST.md` - Test cases (50+)
- 📄 `ROUTING_REFACTOR_REPORT.md` - Implementation report
- 📄 `ROUTING_QUICK_REFERENCE.md` - This file

---

## Need Help?

**Can't find something?** → Check `ROUTING_GUIDE.md`  
**Want overview?** → Read `ROUTING_SUMMARY.md`  
**Want to test?** → Use `ROUTING_TESTING_CHECKLIST.md`  
**Want details?** → Check `ROUTING_REFACTOR_REPORT.md`  
**Want quick answer?** → You're reading it!

---

**Last Updated:** January 27, 2026  
**Status:** READY FOR TESTING ✅
