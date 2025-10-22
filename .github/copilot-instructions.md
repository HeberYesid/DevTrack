# DevTrack AI Agent Instructions

## Project Architecture

**Full-stack academic tracking system**: Django REST backend + React frontend with Docker deployment.

- **Backend**: Django 5.0 + DRF, MySQL, JWT auth, three roles (`STUDENT`, `TEACHER`, `ADMIN`)
- **Frontend**: React 18 + Vite, role-based routing, theme system (dark/light)
- **Deployment**: Docker Compose (dev/prod configs), PowerShell scripts for Windows

## Essential Workflows

### Start Development (Docker - Primary Method)
```powershell
.\scripts\docker-dev.ps1      # Starts all services
.\scripts\docker-logs.ps1     # View logs
.\scripts\docker-shell.ps1 backend  # Django shell/manage.py
.\scripts\docker-test.ps1     # Run backend tests
.\scripts\docker-clean.ps1    # Clean everything
```

**Access**: Frontend http://localhost:5173, Backend http://localhost:8000, API Docs http://localhost:8000/api/docs/

### Testing
```bash
# Backend (pytest)
cd backend && pytest --cov

# Frontend (vitest)
cd frontend && npm test
```

## CRITICAL: Windows Line Ending Issues

**Problem**: When cloning on Windows, shell scripts get CRLF endings which break Docker containers:
```
exec ./entrypoint.sh: no such file or directory
```

**Solution**: The `.gitattributes` file ensures LF endings. If you cloned before this was added, fix manually:
```powershell
# Fix line endings in backend scripts
cd backend
$content = Get-Content entrypoint.sh -Raw; $content = $content -replace "`r`n", "`n"; [System.IO.File]::WriteAllText("$PWD\entrypoint.sh", $content, [System.Text.UTF8Encoding]::new($false))
$content = Get-Content wait-for-it.sh -Raw; $content = $content -replace "`r`n", "`n"; [System.IO.File]::WriteAllText("$PWD\wait-for-it.sh", $content, [System.Text.UTF8Encoding]::new($false))

# Restart Docker
docker-compose down
.\scripts\docker-dev.ps1
```

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
Use **DRF action endpoints** with transactions:
```python
@action(detail=True, methods=['post'])
def upload_csv(self, request, pk=None):
    with transaction.atomic():
        # Parse, validate, bulk create
        return {"created": N, "existed": M, "errors": [...]}
```

See `SubjectViewSet.enrollments_upload_csv` and `results_upload_csv`.

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
import api from './config'  // Has auth interceptors

export const getSubjects = async () => {
  const { data } = await api.get('/courses/subjects/')
  return data
}
```

## Environment Setup

### Backend `.env` (required)
```bash
DJANGO_SECRET_KEY=...  # Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DB_NAME=devtrack
DB_HOST=db  # 'localhost' manual, 'db' Docker
CORS_ALLOWED_ORIGINS=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Frontend `.env`
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

## Common Issues

1. **"exec ./entrypoint.sh: no such file"**: Line ending issue - see CRITICAL section above
2. **403 Forbidden**: Check role permissions AND object-level `IsOwnerTeacherOrAdmin`
3. **Students can't see subjects**: Filtered in `get_queryset()` by enrollment
4. **Notifications missing**: Verify signals imported in `courses/apps.py` (line 10)
5. **Rate limit in dev**: Set `RATELIMIT_ENABLE=False` in backend `.env`

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
- API client: `frontend/src/api/config.js`
- Theme: `frontend/src/styles.css` (search `[data-theme=`)

## Documentation

See `/docs` for comprehensive guides:
- `API_GUIDE.md` - Full REST API reference
- `TESTING.md` - Pytest/Vitest setup
- `DOCKER_SETUP.md` - Docker workflow
- `THEME_SYSTEM_DOCS.md` - CSS variables
