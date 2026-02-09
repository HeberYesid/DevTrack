# DevTrack AI Agent Instructions

## Project Overview

**Full-stack academic grade tracking system** built with Django REST backend and React frontend. Tracks student exercise results using a traffic-light system (🟢GREEN/🟡YELLOW/🔴RED) with automatic grade calculation.

### Architecture
- **Backend**: Django 5.0 + DRF + MySQL (local) or PostgreSQL (production)
- **Frontend**: React 18 + Vite + Context API
- **Auth**: JWT with refresh tokens, email verification via 6-digit codes
- **Roles**: Three-tier system (`STUDENT`, `TEACHER`, `ADMIN`) with composable permissions
- **Database**: Dual support - MySQL for local dev, PostgreSQL for production (Render/Railway)

### Key Components
```
backend/
  accounts/          # Auth, user management, rate limiting
    ratelimit.py     # Pre-configured rate limit decorators
    models.py        # User, EmailVerificationCode, TeacherInvitationCode
  courses/           # Core domain logic
    models.py        # Subject, Enrollment, Exercise, StudentExerciseResult
    signals.py       # Auto-notification generation (never create manually!)
    permissions.py   # Composable permission classes
  config/settings.py # DB switching, CORS, JWT config

frontend/
  src/
    state/           # Global state (AuthContext, ThemeContext)
    api/axios.js     # Pre-configured axios with auth interceptors
    styles.css       # Theme CSS variables (--bg-*, --text-*)
```

## Essential Workflows

### Development Setup
```powershell
# Backend (PowerShell on Windows)
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Backend (pytest with >90% coverage target)
cd backend
pytest --cov                    # Run all tests
pytest --cov --cov-report=html  # HTML report in htmlcov/
pytest accounts/tests/          # Single app

# Frontend (vitest)
cd frontend
npm test                        # Watch mode
npm run test:coverage           # With coverage
```

### Database Switching
Backend automatically detects environment:
- **Local**: MySQL if `DB_NAME`, `DB_USER` in `.env` (no `DATABASE_URL`)
- **Production**: PostgreSQL/MySQL via `DATABASE_URL` from Render/Railway

## Critical Patterns

### 1. Role-Based Permissions
Use **composable permission classes** from `courses/permissions.py`:
```python
# courses/views.py
from courses.permissions import IsTeacherOrAdmin, IsOwnerTeacherOrAdmin

class SubjectViewSet(viewsets.ModelViewSet):
    # AND logic: must be Teacher/Admin AND Owner/Admin
    permission_classes = [IsTeacherOrAdmin, IsOwnerTeacherOrAdmin]
```

### 2. Signals & Notifications
**NEVER** create `Notification` objects manually in views. Use signals in `courses/signals.py`.
- **Enrollment Created**: Notifies Student + Teacher.
- **Result Updated**: Notifies Student.
- **Submission**: Notifies Teacher.
- **Demo Subject**: New students automatically get `DEMO-101` subject.

*Note: Notifications include a `link` field for frontend routing.*

### 3. Authentication & Limits
- **Rate Limiting**: Use `@ratelimit_auth` decorator (5 attempts/min).
- **Email Verification**: Uses 6-digit codes (not tokens). `user.create_email_verification_code()`.
- **Auto-Logout**: `AuthContext` enforces `user.session_timeout` (default 30m).

### 4. CSV Operations
Use **DRF action endpoints** (e.g., `SubjectViewSet.upload_results_csv`).
- **Strictness**: Validation is critical.
- **Normalization**: Use `normalize_status` helper for flexible inputs ("verde", "TRUE", "1" → `GREEN`).
- **Format**: See `/samples` for headers (`student_email`, `exercise_name`, `status`).

### 5. Frontend Architecture
- **State**: `AuthContext` (User), `ThemeContext` (CSS vars).
- **Styling**: Use CSS variables (`--bg-card`) from `styles.css`.
- **API**: Use `api` from `src/api/axios.js` (handles 401 refresh loops).
- **Routing**: `<ProtectedRoute roles={["TEACHER"]}>`.

## Environment Setup

### Backend `.env`
```env
DJANGO_SECRET_KEY=<use-python-command-to-generate>
DB_NAME=devtrack
DB_USER=devtrack
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # dev
# For production, use DATABASE_URL instead of DB_* vars
```

Generate secret: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### Frontend `.env`
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

### MySQL Setup (Local Dev)
```sql
CREATE DATABASE devtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'devtrack'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON devtrack.* TO 'devtrack'@'%';
FLUSH PRIVILEGES;
```



## Grade Calculation Logic

```python
# courses/models.py - Enrollment.stats()
if green == total:
    grade = 5.0  # Perfect score
elif yellow / total >= 0.6:
    grade = 3.0  # Passing threshold
else:
    grade = round(5.0 * (green / total), 2) # Proportional
```

**Semaphore Logic** (Visual Indicator):
- `GREEN`: Grade = 5.0 OR Grade >= 4.5
- `YELLOW`: Yellows >= 60% OR Grade >= 3.0
- `RED`: Otherwise

Status Enum: `GREEN`, `YELLOW`, `RED`, `SUBMITTED`.

## Key Files

- Auth: `backend/accounts/views.py`
- Permissions: `backend/courses/permissions.py`
- Signals: `backend/courses/signals.py`
- Grade logic: `backend/courses/models.py` → `Enrollment.stats()`
- Frontend routing: `frontend/src/App.jsx`
- API client: `frontend/src/api/axios.js`
- Theme: `frontend/src/styles.css` (search `[data-theme=`)

## Documentation

See `/docs` for comprehensive guides:
- `API_GUIDE.md` - Full REST API reference
- `TESTING.md` - Pytest/Vitest setup
- `THEME_SYSTEM_DOCS.md` - CSS variables
- `TROUBLESHOOTING.md` - Common issues and solutions
- `RENDER_DEPLOY.md` - Production deployment guide
