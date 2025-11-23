# Changelog

Todos los cambios notables del proyecto DevTrack se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Fixed
- Fixed student dashboard black screen issue caused by undefined grade values
- Added null check for grade display: shows "0.0" when grade is not available
- Fixed emoji rendering issues across all user interfaces

### Changed
- **UI Overhaul**: Removed all emoji icons from student and teacher dashboards for a more professional appearance
- Replaced emoji notification bell (🔔) with professional SVG icon
- Updated all view components for consistent, emoji-free interface
  - StudentDashboard.jsx
  - Dashboard.jsx (Teacher/Admin)
  - SubjectDetail.jsx (87+ emoji instances removed)
  - Notifications.jsx
  - UserProfile.jsx
  - Subjects.jsx
  - MyResults.jsx
  - NotificationBell.jsx

### Removed
- **Backend Dependencies** (54 → 40 packages, -26%)
  - `httpie==3.2.4` - HTTP CLI tool not used in production
  - `git-filter-repo==2.47.0` - Git utility not needed
  - `factory-boy==3.3.0` - Not used in test suite
  - `Faker==22.6.0` - Not used in test suite
  - `psycopg==3.2.3` - Duplicate of psycopg2-binary
  - `sendgrid==6.11.0` - Email service (using Django backend instead)
  - Related httpie dependencies: `markdown-it-py`, `multidict`, `pygments`, `rich`, `requests-toolbelt`, `rpds-py`, `jsonschema-specifications`, `referencing`

- **Frontend Dependencies** (16 → 13 packages, -19%)
  - `framer-motion` - Animation library not currently used
  - `lucide-react` - Icon library (using inline SVG instead)
  - `recharts` - Chart library (no graphs implemented yet)
  - Impact: ~38 sub-dependencies also removed

### Performance
- Reduced backend installation size by ~20 MB
- Reduced frontend bundle size by ~500 KB
- Smaller security surface area with fewer dependencies
- Faster installation and build times

### Testing
- Improved frontend test suite with better query selectors
- Fixed test assertions to use `getByPlaceholderText` instead of `getByLabelText`
- Updated Dashboard tests with proper authentication mocking
- Backend tests: 16/16 passing in accounts module

---

## [1.1.0] - 2024-11-XX

### Added
- Student dashboard with progress tracking
- Teacher dashboard with subject management
- CSV upload functionality for enrollments and results
- Real-time notification system
- Email verification with 6-digit codes
- Rate limiting on authentication endpoints
- Session timeout configuration
- Dark/Light theme toggle
- Guided tour for new users (react-joyride)

### Security
- Cloudflare Turnstile integration for bot protection
- JWT-based authentication with refresh tokens
- Role-based access control (Student, Teacher, Admin)
- Password strength validation (minimum 8 characters)

---

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Django REST Framework backend
- React + Vite frontend
- MySQL database support
- Basic CRUD operations for subjects, enrollments, exercises, and results
- User authentication and authorization
- PostgreSQL support for production (Render)
- Static file serving with WhiteNoise
- CORS configuration

---

## Links

- [GitHub Repository](https://github.com/HeberYesid/DevTrack)
- [Backend (Render)](https://devtrack-ntjm.onrender.com)
- [Frontend (Vercel)](https://devtrack-frontend.vercel.app)
