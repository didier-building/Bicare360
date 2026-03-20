# BiCare360 - Login Credentials & Testing Guide

**Last Updated**: March 9, 2026  
**Status**: All test users created and verified

---

## ⚠️ IMPORTANT: Different Login Methods

Each portal uses **different login fields**:

| Portal | Login Field | What to Enter | Example |
|--------|-------------|---------------|---------|
| **Patient** | `Username` | username OR national ID | `patient1` |
| **Staff/Nurse** | `Username` | username OR email | `nurse1` |
| **Caregiver** | `Email` ⚠️ | email ONLY | `caregiver@test.com` |
Something went wrong
We encountered an unexpected error. Please try again or contact support if the problem persists.

Error details
TypeError: Cannot read properties of undefined (reading 'first_name')
---

## 📋 Complete Test Credentials

### 1. 📱 Patient Portal

**Login URL**: http://localhost:5173/patient/login

**Login Form Field**: "Username or National ID"

**Credentials Option 1 (Username):**
```
Username: patient1
Password: Patient@2026
```

**Credentials Option 2 (National ID):**
```
National ID: 1199012345678901
Password: Patient@2026
```

**Features Access After Login:**
- Dashboard: `/patient/dashboard`
- My Appointments: `/patient/appointments`
- Medications: `/patient/medications`
- Messages: `/patient/messages`
- Profile: `/patient/profile`

---

### 2. 👨‍⚕️ Staff/Nurse Portal

**Login URL**: http://localhost:5173/login

**Login Form Field**: "Username"

**Credentials Option 1 (Username):**
```
Username: nurse1
Password: Nurse@2026
```

**Credentials Option 2 (Email):**
```
Username: nurse@test.com
Password: Nurse@2026
```

**Note**: The "Username" field accepts EITHER username OR email (if you include @)

**Features Access After Login:**
- Nurse Dashboard: `/nurse/dashboard`
- Patient Alerts: `/nurse/alerts`
- Patient Search: `/nurse/patients`
- Messages: `/messages`
- Analytics: `/analytics`

---

### 3. 🤝 Caregiver Portal

**Login URL**: http://localhost:5173/caregiver/login

**Login Form Field**: "Email Address" ⚠️

**Credentials (EMAIL ONLY):**
```
Email: caregiver@test.com
Password: Caregiver@2026
```

**⚠️ CRITICAL**: 
- The caregiver login form **ONLY accepts email addresses**
- Using "caregiver1" will NOT work
- You MUST use: `caregiver@test.com`

**Features Access After Login:**
- Caregiver Dashboard: `/caregiver/dashboard`
- My Bookings: `/caregiver/bookings`
- Profile: `/caregiver/profile`
- Messages: `/caregiver/messages`
- Browse Requests: `/caregiver/browse`

---

### 4. 👑 Admin Portal

**Login URL**: http://localhost:8000/admin/

**Login Form Fields**: "Username" and "Password"

**Credentials:**
```
Username: admin
Password: Admin@2026
```

**Full Access**: Django Admin Panel with all models

---

## 🧪 Testing Scenarios

### Scenario 1: Patient Login (Quick Test)
1. Go to: http://localhost:5173/patient/login
2. Enter Username: `patient1`
3. Enter Password: `Patient@2026`
4. Click "Login"
5. ✅ Should redirect to `/patient/dashboard`

### Scenario 2: Staff Login (Quick Test)
1. Go to: http://localhost:5173/login
2. Enter Username: `nurse1`
3. Enter Password: `Nurse@2026`
4. Click "Login"
5. ✅ Should redirect to `/nurse/dashboard`

### Scenario 3: Caregiver Login (Quick Test)
1. Go to: http://localhost:5173/caregiver/login
2. Enter Email: `caregiver@test.com` ⚠️ (NOT caregiver1!)
3. Enter Password: `Caregiver@2026`
4. Click "Login"
5. ✅ Should redirect to `/caregiver/dashboard`

---

## 🔍 Common Login Errors

### Error: "Invalid credentials" on Caregiver Portal
**Problem**: You entered `caregiver1` (username) instead of email  
**Solution**: Use `caregiver@test.com`

### Error: "User not found" on Patient Portal
**Problem**: Using email instead of username  
**Solution**: Use `patient1` (not patient@test.com)

### Error: "Authentication failed"
**Problem**: Wrong password or typing error  
**Solution**: Copy-paste the password exactly:
- Patient: `Patient@2026`
- Nurse: `Nurse@2026`
- Caregiver: `Caregiver@2026`
- Admin: `Admin@2026`

---

## 📊 Login Form Comparison

### Patient Login Form (`/patient/login`)
```
Field Label: "Username or National ID"
Input Type: text
Accepts: username | national_id
Example: patient1 OR 1199012345678901
```

### Staff Login Form (`/login`)
```
Field Label: "Username"
Input Type: text
Accepts: username | email (if contains @)
Example: nurse1 OR nurse@test.com
```

### Caregiver Login Form (`/caregiver/login`)
```
Field Label: "Email Address"
Input Type: email
Accepts: email ONLY (must contain @ and .)
Example: caregiver@test.com ONLY
Validation: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
```

---

## 🎯 Quick Copy-Paste Credentials

**For Patient Portal:**
```
patient1
Patient@2026
```

**For Staff Portal:**
```
nurse1
Nurse@2026
```

**For Caregiver Portal:**
```
caregiver@test.com
Caregiver@2026
```

**For Admin Panel:**
```
admin
Admin@2026
```

---

## 🔐 Backend User Details

### Patient User (patient1)
- **Username**: patient1
- **Email**: patient@test.com
- **National ID**: 1199012345678901
- **First Name**: John
- **Last Name**: Doe
- **Phone**: +250788123456
- **Database**: `users` + `patients` tables

### Staff User (nurse1)
- **Username**: nurse1
- **Email**: nurse@test.com
- **First Name**: Jane
- **Last Name**: Smith
- **License**: RN10001
- **Specialization**: General Nursing
- **Phone**: +250788234567
- **Database**: `users` + `nurse_profile` tables

### Caregiver User (caregiver1)
- **Username**: caregiver1
- **Email**: caregiver@test.com ⚠️ (Use this to login!)
- **First Name**: Mary
- **Last Name**: Johnson
- **Profession**: Registered Nurse
- **Experience**: 5 years
- **Hourly Rate**: 5000 RWF
- **Location**: Kigali, Gasabo, Remera
- **Rating**: 4.50/5.00
- **Phone**: +250788345678
- **Database**: `users` + `caregivers` tables

### Admin User (admin)
- **Username**: admin
- **Email**: admin@bicare360.com
- **First Name**: Admin
- **Last Name**: User
- **Superuser**: Yes
- **Staff**: Yes

---

## 🚀 Start Servers & Test

### Step 1: Start Backend
```bash
cd /home/magentle/MyProject/Bicare360/backend
uv run python manage.py runserver 8000
```

### Step 2: Start Frontend
```bash
cd /home/magentle/MyProject/Bicare360/frontend
npm run dev
```

### Step 3: Access Application
Open browser: http://localhost:5173

### Step 4: Select Portal
You'll see 3 cards:
- Blue (Patient)
- Green (Staff)
- Purple (Caregiver)

### Step 5: Login with Correct Credentials
Use the credentials from the table above, **paying attention to which field is required**!

---

## ✅ Verification Checklist

After logging in to each portal, verify:

**Patient Portal:**
- [ ] Dashboard displays patient info
- [ ] Can view appointments
- [ ] Can see medications
- [ ] Can access `/patient/messages`

**Staff Portal:**
- [ ] Dashboard shows nursing interface
- [ ] Can view patient alerts
- [ ] Can search patients
- [ ] Can access `/messages`

**Caregiver Portal:**
- [ ] Dashboard shows caregiver profile
- [ ] Rating shows 4.50/5.00
- [ ] Can view bookings
- [ ] Can access `/caregiver/messages`

---

## 📞 Need Help?

If login still fails:

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Check console** (F12 → Console tab)
3. **Verify servers are running**:
   - Backend: `curl http://localhost:8000/api/v1/`
   - Frontend: Open http://localhost:5173
4. **Re-create test users**:
   ```bash
   cd backend
   uv run python create_test_users.py
   ```

---

**Last Updated**: March 9, 2026  
**Servers**: Backend (8000), Frontend (5173)  
**Status**: ✅ All login methods verified and documented
