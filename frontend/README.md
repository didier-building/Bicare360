# BiCare360 Frontend

BiCare360 is a home-care coordination and caregiver support platform that helps care teams, caregivers, and patients stay connected after hospital discharge.

This frontend provides role-based experiences for:
- Patients tracking appointments, medications, and care plans
- Nurses and staff coordinating follow-up care and monitoring alerts
- Caregivers managing bookings and patient home visits

## Tech Stack
- React 18
- TypeScript
- Vite
- React Router
- Axios

## Development

Install dependencies:

```bash
npm install
```

Start the dev server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Configuration

Set API and WebSocket URLs with Vite environment variables in `.env` files (for example `.env.local`):

```env
VITE_API_URL=https://your-backend.example.com/api
VITE_WS_URL=wss://your-backend.example.com/ws
```

If these values are not set, the app falls back to project defaults defined in `src/api/config.ts`.
