# BiCare360 - Routing & Navigation Testing Checklist

## Quick Test Guide

**Current Status:** Routing refactor complete, app running on http://localhost:5173

---

## 🎯 Pre-Testing Requirements

- [ ] Backend server running on `http://localhost:8000`
- [ ] Frontend dev server running on `http://localhost:5173`
- [ ] Browser dev tools open (F12) for error checking
- [ ] Clear browser localStorage (to test auth flow)

---

## ✅ Test Scenarios

### Scenario 1: New User Entry Point
**Goal:** Verify new users see login selection page

1. [ ] Open `http://localhost:5173`
2. [ ] Should see "BiCare360" header
3. [ ] Should see two cards: "Patient Portal" and "Staff Portal"
4. [ ] "Patient Portal" should have HeartIcon
5. [ ] "Staff Portal" should have UserIcon
6. [ ] Cards should be interactive (hover effects)
7. [ ] Should show demo credentials at bottom

**Expected:**
- ✅ Clean login selection interface
- ✅ Clear visual distinction between options
- ✅ No errors in browser console

---

### Scenario 2: Patient Login & Navigation
**Goal:** Verify patient authentication and navigation flow

#### Step 1: Patient Login
1. [ ] Click "Patient Portal" button
2. [ ] Should navigate to `/patient/login`
3. [ ] Should see patient login form
4. [ ] Should see "Back to Login Selection" link (optional)
5. [ ] Enter patient credentials
6. [ ] Click login

**Expected:**
- ✅ Form submission works
- ✅ No network errors
- ✅ Redirects after successful login

#### Step 2: Patient Dashboard
1. [ ] Should redirect to `/patient/dashboard`
2. [ ] Should see PatientLayout (sidebar visible)
3. [ ] Should see patient name and email in sidebar
4. [ ] Should see patient navigation items:
   - [ ] Dashboard (active/highlighted)
   - [ ] Health Progress (with HeartIcon)
   - [ ] Appointments
   - [ ] Medications
   - [ ] Alerts
   - [ ] Caregivers
   - [ ] Profile
   - [ ] Settings
5. [ ] Should see Logout button at bottom

**Expected:**
- ✅ Sidebar displays correctly
- ✅ Correct user info shown
- ✅ Navigation items have proper styling
- ✅ Active link is highlighted
- ✅ Mobile sidebar toggle button visible on small screens

#### Step 3: Patient Navigation
1. [ ] Click "Health Progress"
2. [ ] [ ] URL changes to `/patient/health`
3. [ ] [ ] PatientLayout stays (sidebar still visible)
4. [ ] [ ] Health page content loads
5. [ ] Click "Appointments"
6. [ ] [ ] URL changes to `/patient/appointments`
7. [ ] [ ] PatientLayout stays visible
8. [ ] Click "Settings"
9. [ ] [ ] URL changes to `/patient/settings`
10. [ ] [ ] PatientLayout stays visible

**Expected:**
- ✅ Each navigation click works
- ✅ URL updates correctly
- ✅ Sidebar stays visible
- ✅ Active link updates in sidebar
- ✅ No console errors

#### Step 4: Patient Logout
1. [ ] Click "Logout" button in sidebar
2. [ ] Should see confirmation dialog: "Are you sure you want to logout?"
3. [ ] Click "Cancel"
4. [ ] [ ] Dialog closes, still on page
5. [ ] Click "Logout" again
6. [ ] Click "Yes, Logout"
7. [ ] [ ] Should redirect to `/patient/login`
8. [ ] [ ] Should see success toast "Logged out successfully"
9. [ ] Should NOT see sidebar anymore
10. [ ] Should NOT see patient content

**Expected:**
- ✅ Confirmation dialog appears
- ✅ Cancel works
- ✅ Logout clears auth state
- ✅ Redirects to patient login
- ✅ Success notification shown

---

### Scenario 3: Staff Login & Navigation
**Goal:** Verify staff authentication and role-based access

#### Step 1: Staff Login
1. [ ] Go to `/login-selection` or click "Back to Login Selection"
2. [ ] Click "Staff Portal"
3. [ ] Should navigate to `/login`
4. [ ] Should see staff login form
5. [ ] Enter staff credentials (username: nurse_admin, password: password)
6. [ ] Click login

**Expected:**
- ✅ Staff login form appears
- ✅ Form submission works
- ✅ No network errors

#### Step 2: Staff Dashboard
1. [ ] Should redirect to `/dashboard`
2. [ ] Should see DashboardLayout (staff sidebar visible)
3. [ ] Should see staff navigation items:
   - [ ] Dashboard (highlighted)
   - [ ] Alerts (with BellAlertIcon)
   - [ ] Health (with HeartIcon)
   - [ ] Patients (with UsersIcon)
   - [ ] Patient Search
   - [ ] Medications
   - [ ] Med Adherence
   - [ ] Appointments
   - [ ] Discharge Summaries
   - [ ] Analytics
   - [ ] Settings
4. [ ] Should see user name and email
5. [ ] Should see Logout button

**Expected:**
- ✅ Staff sidebar displays (different from patient)
- ✅ More navigation options than patient
- ✅ Correct icons for each item
- ✅ Active link highlighted

#### Step 3: Staff Navigation
1. [ ] Click "Alerts"
2. [ ] [ ] URL changes to `/alerts`
3. [ ] [ ] DashboardLayout stays visible
4. [ ] Click "Health"
5. [ ] [ ] URL changes to `/health`
6. [ ] [ ] DashboardLayout stays visible
7. [ ] Click "Patients"
8. [ ] [ ] URL changes to `/patients`
9. [ ] [ ] DashboardLayout stays visible

**Expected:**
- ✅ Navigation works correctly
- ✅ Sidebar stays visible
- ✅ No console errors

#### Step 4: View Specific Patient Health (Nurse Feature)
1. [ ] On `/patients` page, get a patient ID (e.g., 4)
2. [ ] Navigate to `/health/4`
3. [ ] [ ] URL changes to `/health/4`
4. [ ] [ ] Should show health data for patient ID 4
5. [ ] [ ] DashboardLayout still visible

**Expected:**
- ✅ Can view specific patient health data
- ✅ URL parameters work
- ✅ Staff can access this route

#### Step 5: Staff Logout
1. [ ] Click "Logout" in sidebar
2. [ ] Confirm logout
3. [ ] Should redirect to `/login` (staff login, not patient)
4. [ ] Should see success notification

**Expected:**
- ✅ Redirects to staff login page
- ✅ Different from patient logout destination

---

### Scenario 4: Route Protection - Access Control
**Goal:** Verify unauthorized users cannot access protected routes

#### Test 4A: Patient Cannot Access Staff Routes
1. [ ] Login as patient
2. [ ] In address bar, go to `/dashboard`
3. [ ] [ ] Should redirect to `/patient/login`
4. [ ] [ ] Should NOT see staff dashboard
5. [ ] In address bar, go to `/alerts`
6. [ ] [ ] Should redirect to `/patient/login`
7. [ ] In address bar, go to `/patients`
8. [ ] [ ] Should redirect to `/patient/login`

**Expected:**
- ✅ Patient cannot access any `/` routes
- ✅ Always redirected to `/patient/login`
- ✅ No unauthorized access

#### Test 4B: Staff Cannot Access Patient Routes
1. [ ] Login as staff
2. [ ] In address bar, go to `/patient/dashboard`
3. [ ] [ ] Should redirect to `/patient/login`
4. [ ] [ ] Should NOT see patient dashboard
5. [ ] In address bar, go to `/patient/health`
6. [ ] [ ] Should redirect to `/patient/login`
7. [ ] In address bar, go to `/patient/medications`
8. [ ] [ ] Should redirect to `/patient/login`

**Expected:**
- ✅ Staff cannot access `/patient/*` routes
- ✅ Always redirected to `/patient/login`
- ✅ Note: Staff can access `/health` (their version), not `/patient/health`

#### Test 4C: Unauthenticated Cannot Access Any Protected Route
1. [ ] Logout
2. [ ] Clear localStorage (optional: more thorough test)
3. [ ] Try accessing `/dashboard`
4. [ ] [ ] Should redirect to `/patient/login`
5. [ ] [ ] Should NOT load dashboard
6. [ ] Try accessing `/patient/dashboard`
7. [ ] [ ] Should redirect to `/patient/login`
8. [ ] [ ] Should NOT load patient dashboard
9. [ ] Try accessing `/patient/health`
10. [ ] [ ] Should redirect to `/patient/login`

**Expected:**
- ✅ No protected route accessible without auth
- ✅ Always redirects to login
- ✅ No data leakage

---

### Scenario 5: Mobile Responsiveness
**Goal:** Verify routing works on mobile devices

#### Desktop (>1024px)
1. [ ] Sidebar should be visible by default
2. [ ] No hamburger menu button visible
3. [ ] Navigation items visible in sidebar
4. [ ] Can scroll sidebar if content overflows

#### Mobile (<1024px)
1. [ ] Sidebar hidden by default (off-screen)
2. [ ] Hamburger menu button visible in top-left
3. [ ] Click hamburger menu
4. [ ] [ ] Sidebar slides in from left
5. [ ] [ ] Backdrop appears behind sidebar
6. [ ] Click on a navigation item
7. [ ] [ ] Navigates to page
8. [ ] [ ] Sidebar automatically closes
9. [ ] Click X button in sidebar
10. [ ] [ ] Sidebar closes
11. [ ] Click backdrop
12. [ ] [ ] Sidebar closes

**Expected:**
- ✅ Responsive design works
- ✅ Navigation accessible on all screen sizes
- ✅ Touch-friendly buttons
- ✅ Smooth animations

---

### Scenario 6: Dark Mode (If Implemented)
**Goal:** Verify routing works in dark mode

1. [ ] Switch to dark mode (if available in settings)
2. [ ] Navigate through routes
3. [ ] [ ] Sidebar visible with dark theme
4. [ ] [ ] Text readable
5. [ ] [ ] Icons visible
6. [ ] [ ] Links still work
7. [ ] [ ] No contrast issues

**Expected:**
- ✅ Dark mode doesn't break routing
- ✅ Navigation still functional
- ✅ Readable text and icons

---

### Scenario 7: Error Handling
**Goal:** Verify error states work correctly

#### Test 7A: API Error During Login
1. [ ] Stop backend server
2. [ ] Try to login
3. [ ] [ ] Should show error message
4. [ ] [ ] Should NOT redirect
5. [ ] [ ] Should stay on login page
6. [ ] Start backend server again
7. [ ] Try login again
8. [ ] [ ] Should work if credentials correct

**Expected:**
- ✅ Network errors handled gracefully
- ✅ User can retry
- ✅ No crash

#### Test 7B: Invalid Token Handling
1. [ ] Login successfully
2. [ ] Open dev console
3. [ ] In localStorage, change `access_token` to invalid value
4. [ ] Refresh page
5. [ ] [ ] Should redirect to `/patient/login` or `/login`
6. [ ] [ ] Should clear invalid token

**Expected:**
- ✅ Invalid tokens detected
- ✅ User logged out automatically
- ✅ Redirected to login

---

### Scenario 8: Browser Back/Forward Buttons
**Goal:** Verify browser navigation works correctly

1. [ ] Login as patient
2. [ ] Click through several pages: Dashboard → Health → Appointments
3. [ ] Press browser back button 3 times
4. [ ] [ ] Should go back through Health → Dashboard → (previous page)
5. [ ] [ ] URLs should update correctly
6. [ ] [ ] Content should update
7. [ ] Press forward button
8. [ ] [ ] Should go forward correctly

**Expected:**
- ✅ Browser history works
- ✅ URL and content stay in sync
- ✅ No state conflicts

---

### Scenario 9: Deep Linking
**Goal:** Verify direct URL access works correctly

1. [ ] Login as patient
2. [ ] Copy URL of specific page (e.g., `/patient/appointments`)
3. [ ] Open new tab
4. [ ] Paste URL
5. [ ] [ ] Should load page correctly (no redirect)
6. [ ] [ ] Should show correct content
7. [ ] Try same with staff route while logged in as patient
8. [ ] [ ] Should redirect to `/patient/login`

**Expected:**
- ✅ Deep links work when authenticated
- ✅ Deep links redirect when not authorized
- ✅ No infinite redirect loops

---

### Scenario 10: Concurrent Tabs
**Goal:** Verify app works correctly with multiple tabs

1. [ ] Login in Tab A (patient)
2. [ ] Open new tab (Tab B)
3. [ ] Go to `/patient/dashboard` in Tab B
4. [ ] [ ] Should work (share same localStorage)
5. [ ] Go to Tab A and logout
6. [ ] Go to Tab B and refresh
7. [ ] [ ] Should redirect to `/patient/login` (auth state synced)
8. [ ] Open Tab C with staff login

**Expected:**
- ✅ Auth state shared across tabs
- ✅ Logout in one tab affects others
- ✅ Multiple users can be in different tabs

---

## 📊 Issue Tracking

### Issues Found During Testing

| # | Issue | Severity | Status | Notes |
|---|-------|----------|--------|-------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## ✨ Additional Observations

### Performance
- [ ] Page loads quickly (< 2 seconds)
- [ ] Navigation is smooth (no lag)
- [ ] Sidebar animations are smooth
- [ ] No unnecessary re-renders

### User Experience
- [ ] Navigation is intuitive
- [ ] Clear where you are (active link)
- [ ] Easy to find what you need
- [ ] Good error messages

### Accessibility
- [ ] Keyboard navigation works
- [ ] Tab order makes sense
- [ ] Sidebar toggle accessible
- [ ] Icons have labels/alt text

---

## 📝 Tester Notes

**Tester Name:** ___________________
**Date:** ___________________
**Browser:** ___________________
**OS:** ___________________

### Overall Assessment

**Patient Route Protection:** ☐ Pass ☐ Fail ☐ Partial
**Staff Route Protection:** ☐ Pass ☐ Fail ☐ Partial
**Navigation Clarity:** ☐ Pass ☐ Fail ☐ Partial
**Mobile Responsiveness:** ☐ Pass ☐ Fail ☐ Partial
**Error Handling:** ☐ Pass ☐ Fail ☐ Partial

**Overall Status:** ☐ PASS ☐ FAIL ☐ NEEDS WORK

### Recommendations

1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

---

## Summary

- **Total Test Scenarios:** 10
- **Critical Tests:** 4 (Entry Point, Login Flows, Protection, Navigation)
- **Optional Tests:** 6 (Mobile, Dark Mode, Errors, History, Deep Links, Tabs)

**Pass Criteria:**
- ✅ All critical tests pass
- ✅ No security vulnerabilities
- ✅ No console errors
- ✅ Navigation is intuitive

**When Complete:**
Send results to development team and proceed to:
1. Feature 4 (Health Charts) testing
2. Integration testing
3. Performance optimization
4. Deployment

---

*Generated: January 27, 2026*
*Routing Refactor Complete - Ready for Testing*
