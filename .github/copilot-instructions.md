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

### 1. Role-Based Permissions (Backend)
Use **composable permission classes** from `{app}/permissions.py`:
```python
# courses/views.py
from courses.permissions import IsTeacherOrAdmin, IsOwnerTeacherOrAdmin

class SubjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTeacherOrAdmin, IsOwnerTeacherOrAdmin]
    
    def get_queryset(self):
        # Students see only enrolled subjects
        if self.request.user.role == 'STUDENT':
            return Subject.objects.filter(enrollments__student=self.request.user)
```

**Key**: `IsOwnerTeacherOrAdmin` checks `subject.teacher_id == user.id` for object-level ownership.

### 2. Rate Limiting (Backend)
Use **pre-configured decorators** from `accounts/ratelimit.py`:
```python
from accounts.ratelimit import ratelimit_auth, ratelimit_email

@ratelimit_auth  # 5 attempts/min per IP
def login_view(request): ...
```

### 3. Email Verification (Backend)
Uses **6-digit codes** (not URL tokens):
```python
# accounts/models.py
code = user.create_email_verification_code(minutes_valid=15)
# Prints to console in dev, emails in prod
```

### 4. Notifications (Backend)
**All auto-generated via signals** in `courses/signals.py`. Never create manually:
```python
@receiver(post_save, sender=Enrollment)
def notify_enrollment_created(sender, instance, created, **kwargs):
    # Creates notifications for student + teacher
```

### 5. CSV Bulk Operations (Backend)
Use **DRF action endpoints** without explicit transactions (signals handle notifications):
```python
@decorators.action(detail=True, methods=['post'], url_path='enrollments/upload-csv', 
                   parser_classes=[parsers.MultiPartParser])
def upload_enrollments_csv(self, request, pk=None):
    # Parse CSV, get_or_create users, create enrollments
    # Returns: {"created": N, "existed": M, "errors": [...]}
```

**Key implementations**: 
- `SubjectViewSet.upload_enrollments_csv` (lines 75-117 in courses/views.py)
- `SubjectViewSet.upload_results_csv` (lines 175-237 in courses/views.py)

**CSV formats** in `/samples`:
- `enrollments.csv`: email, first_name (optional), last_name (optional)
- `student_results.csv`: student_email, exercise_name, status (GREEN/YELLOW/RED)

### 6. Authentication (Frontend)
**Always use `AuthContext`**:
```javascript
import { useAuth } from '../state/AuthContext'

function Component() {
  const { user, logout, isAuthenticated } = useAuth()
  // user: {id, email, first_name, last_name, role, is_verified}
}
```

Token refresh handled in `api/config.js` axios interceptors.

### 7. Theme System (Frontend)
Use **CSS variables only**:
```css
/* styles.css - switches via [data-theme="dark|light"] */
background: var(--bg-card);
color: var(--text-primary);
```

### 8. API Calls (Frontend)
Centralize in `api/` directory with pre-configured axios:
```javascript
import { api } from './axios'  // Has auth interceptors + auto-refresh

export const getSubjects = async () => {
  const { data } = await api.get('/api/courses/subjects/')
  return data
}
```

**Auto-refresh on 401**: `api/axios.js` (lines 40-75) handles token refresh with queuing to prevent concurrent refresh requests.

### 9. Role-Based Routing (Frontend)
Use `<ProtectedRoute>` wrapper for role restrictions:
```jsx
// App.jsx pattern
<Route path="/subjects" element={
  <ProtectedRoute roles={["TEACHER", "ADMIN"]}>
    <Subjects />
  </ProtectedRoute>
} />
```

### 10. Auto-Logout on Inactivity (Frontend)
`AuthContext` tracks mouse/keyboard events and logs out after `user.session_timeout` minutes (default: 30, configurable per user 5-120).

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
    grade = 5.0
elif yellow / total >= 0.6:
    grade = 3.0
else:
    grade = 5.0 * (green / total)
```

Status enum: `GREEN`/`YELLOW`/`RED` in `StudentExerciseResult.Status`.

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
