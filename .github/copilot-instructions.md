# DevTrack AI Agent Instructions

## Project Overview

**Full-stack academic grade tracking system** built with Django REST backend and React frontend. Tracks student exercise results using a traffic-light system (🟢GREEN/🟡YELLOW/🔴RED) with automatic grade calculation.

### Architecture
- **Backend**: Django 5.0 + DRF + MySQL (local) or PostgreSQL (production)
- **Frontend**: React 18 + Vite + Context API
- **Auth**: JWT with refresh tokens, email verification via 6-digit codes
- **Roles**: Three-tier system (`STUDENT`, `TEACHER`, `ADMIN`) with composable permissions
- **Database**: Dual support — set `USE_MYSQL=True` in `.env` for local MySQL; production uses `DATABASE_URL` (Render/Railway)

### Key Django Apps
```
backend/
  accounts/          # Auth, user management, rate limiting
    ratelimit.py     # apply_ratelimit() decorator factory (django_ratelimit)
    models.py        # User, EmailVerificationCode, TeacherInvitationCode
  courses/           # Core domain logic
    models.py        # Subject, Enrollment, Exercise, StudentExerciseResult
    signals.py       # Auto-notification generation (never create manually!)
    permissions.py   # Composable permission classes
  notifications/     # Standalone Notification model (type, link_url, is_read)
  messaging/         # Conversation + Message models (direct messaging)
  config/settings.py # DB switching, CORS, JWT config

frontend/
  src/
    state/           # AuthContext (user + session), ThemeContext (CSS vars)
    api/axios.js     # Pre-configured axios with JWT + 401 refresh interceptors
    styles.css       # Theme CSS variables (--bg-*, --text-*)
    components/      # ProtectedRoute, NavBar, StatusBadge, CSVUpload, AppTour
    pages/           # Dashboard, SubjectDetail, Calendar, messaging/, MyResults…
```

## Essential Workflows

### Development Setup
```powershell
# Backend (PowerShell on Windows)
cd backend
python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install && npm run dev
```

### Testing
```bash
# Backend — pytest (>90% coverage target)
cd backend
pytest --cov                    # all tests + coverage
pytest --cov --cov-report=html  # HTML report → htmlcov/
pytest accounts/tests/          # single app

# Frontend — vitest
cd frontend
npm test              # watch mode
npm run test:coverage # with coverage
```

## Critical Patterns

### 1. Role-Based Permissions
Compose permission classes from `courses/permissions.py` using AND logic:
```python
from courses.permissions import IsTeacherOrAdmin, IsOwnerTeacherOrAdmin

class SubjectViewSet(viewsets.ModelViewSet):
    # both must pass: is Teacher/Admin AND owns the subject (or is Admin)
    permission_classes = [IsTeacherOrAdmin, IsOwnerTeacherOrAdmin]
```
Available classes: `IsAdmin`, `IsTeacher`, `IsStudent`, `IsTeacherOrAdmin`, `IsOwnerTeacherOrAdmin`.

### 2. Notifications — Never Create Manually
**All `Notification` objects are created by signals** in `courses/signals.py` — never instantiate them in views.
- `Notification` lives in `notifications/models.py` (fields: `type`, `title`, `message`, `link_url`, `is_read`)
- Types: `ENROLLMENT_CREATED`, `RESULTS_UPDATED`, `REPORT_READY`, `NEW_MESSAGE`, `GENERAL`
- New students are auto-enrolled in `DEMO-101` subject via a post-save signal.

### 3. Authentication & Rate Limiting
- **Rate Limiting**: Use `apply_ratelimit()` from `accounts/ratelimit.py` (wraps `django_ratelimit`).
- **Email Verification**: 6-digit codes, not tokens — call `user.create_email_verification_code()`.
- **Auto-Logout**: `AuthContext` enforces `user.session_timeout` (default 30 min).
- **Captcha**: Cloudflare Turnstile on register/login; key in `VITE_TURNSTILE_SITE_KEY`.

### 4. CSV Upload for Results
Use the `upload_results_csv` DRF action on `SubjectViewSet`.
- Use `normalize_status()` helper: accepts `"verde"`, `"TRUE"`, `"1"` → `GREEN`.
- Required CSV headers: `student_email`, `exercise_name`, `status` — see `samples/` for examples.

### 5. Grade Calculation Logic
```python
# courses/models.py — Enrollment.stats()
if green == total:
    grade = 5.0                            # perfect
elif yellow / total >= 0.6:
    grade = 3.0                            # passing threshold
else:
    grade = round(5.0 * (green / total), 2)  # proportional
```
Semaphore indicator: GREEN ≥ 4.5, YELLOW ≥ 3.0, RED otherwise.
Status enum values: `GREEN`, `YELLOW`, `RED`, `SUBMITTED`.

### 6. Frontend Conventions
- **State**: `AuthContext` (user, tokens, timeout), `ThemeContext` (CSS vars via `data-theme`).
- **API calls**: always use `api` from `src/api/axios.js` — it handles token refresh and 401 loops.
- **Route protection**: `<ProtectedRoute roles={["TEACHER"]}>` wraps role-specific pages.
- **Styling**: CSS variables only — `--bg-card`, `--text-primary`, etc. from `styles.css`.
- **Theming**: toggle handled by `ThemeToggle` component; themes defined under `[data-theme=...]` selectors.

## Environment Variables

### Backend (`backend/.env`)
```env
DJANGO_SECRET_KEY=<generate with django command>
USE_MYSQL=True           # omit or set False to use SQLite
DB_NAME=devtrack
DB_USER=devtrack
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# Production: set DATABASE_URL instead of DB_* vars
```
Generate secret: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

## Key Files Reference

| Purpose | File |
|---|---|
| Auth views | `backend/accounts/views.py` |
| Permission classes | `backend/courses/permissions.py` |
| Notification signals | `backend/courses/signals.py` |
| Grade logic | `backend/courses/models.py` → `Enrollment.stats()` |
| Notification model | `backend/notifications/models.py` |
| Messaging models | `backend/messaging/models.py` |
| DB + JWT config | `backend/config/settings.py` |
| Frontend routing | `frontend/src/App.jsx` |
| API client | `frontend/src/api/axios.js` |
| Theme CSS vars | `frontend/src/styles.css` |

## Documentation (`/docs`)
- `API_GUIDE.md` — Full REST API reference
- `TESTING.md` — Pytest/Vitest setup details
- `RENDER_DEPLOY.md` — Production deployment (Render/Railway)
- `LOCAL_SETUP.md` — Full local dev setup guide
