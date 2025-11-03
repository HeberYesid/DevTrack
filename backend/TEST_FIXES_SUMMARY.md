# Test Fixes Summary

## Status: In Progress
**Date**: Current Session  
**Overall Coverage**: 75% (Target: 95%)  
**Tests Passing**: 158/194 (Target: 194/194)

---

## ✅ COMPLETED FIXES

### 1. Turnstile CAPTCHA Mock Path Issues (7 tests fixed)
**Problem**: Tests were mocking `accounts.utils.verify_turnstile_token` but the function is called from within serializers after import, so the mock path needed to be `accounts.serializers.verify_turnstile_token`.

**Files Modified**: `accounts/tests/test_api.py`

**Tests Fixed**:
- ✅ `TestRegisterAPI.test_register_student_success`
- ✅ `TestRegisterAPI.test_register_without_captcha`
- ✅ `TestRegisterAPI.test_register_duplicate_email`
- ✅ `TestLoginAPI.test_login_success`
- ✅ `TestLoginAPI.test_login_invalid_credentials`
- ✅ `TestLoginAPI.test_login_unverified_email`
- ✅ `TestTeacherRegistrationAPI.test_register_teacher_success`
- ✅ `TestTeacherRegistrationAPI.test_register_teacher_invalid_code`
- ✅ `TestTeacherRegistrationAPI.test_register_teacher_expired_code`
- ✅ `TestTeacherRegistrationAPI.test_register_teacher_wrong_email`

**Pattern Applied**:
```python
# BEFORE (wrong path, context manager)
with patch('accounts.utils.verify_turnstile_token', return_value=True):
    # test code

# AFTER (correct path, decorator)
@patch('accounts.serializers.send_verification_code_email')
@patch('accounts.serializers.verify_turnstile_token', return_value=True)
def test_name(self, mock_turnstile, mock_email, ...):
    # test code
```

**Key Learnings**:
1. Mock where function is **used** (serializers), not where it's **defined** (utils)
2. Use decorator pattern instead of context managers for cleaner code
3. Also mock email sending to prevent actual SMTP calls during tests
4. Remove unused DB object variables (use direct `.create()` without assignment)

---

## 🔧 PARTIALLY FIXED

### 2. Rate Limiting Tests (5/12 passing, 7 failing)
**Problem**: Tests expect HTTP 429 (Too Many Requests) but rate limiter returns 403 (Forbidden).

**Files Modified**: `accounts/tests/test_ratelimit.py`

**What We Fixed**:
- ✅ Added Turnstile mocks to all 12 tests
- ✅ Added email mocks to resend_code tests
- ✅ Fixed test data to create unverified users where needed

**Still Failing (7 tests)**:
- ❌ `test_login_blocks_6th_attempt` - assert 403 == 429
- ❌ `test_register_blocks_6th_attempt` - assert 403 == 429
- ❌ `test_verify_blocks_4th_attempt` - assert 403 == 429
- ❌ `test_resend_blocks_4th_attempt` - assert 403 == 429
- ❌ `test_change_password_blocks_4th_attempt` - assert 403 == 429
- ❌ 2 more similar tests

**Root Cause**: The `accounts/ratelimit.py` decorator may be configured to return 403 instead of 429. Logs show "WARNING django.request:log.py:241 Forbidden" on 6th attempt.

**Options**:
1. **Skip these tests** with `@pytest.mark.skip(reason="Rate limiter returns 403 instead of 429 - known configuration issue")`
2. **Fix the decorator** to return proper HTTP 429 status code
3. **Change test expectations** to assert 403 if that's the intended behavior

---

## 🚫 NOT STARTED

### 3. Missing Endpoint Tests (5 tests)
**Problem**: `NoReverseMatch` errors - endpoints don't exist in urls.py

**Affected Tests**:
- `accounts/tests/test_views.py::TestUserExistsAPI` (3 tests) - URL name: 'user-exists'
- `courses/tests/test_api.py::TestEnrollmentAPI` (3 tests) - URL name: 'enrollment-list'  
- `notifications/tests/test_api.py` - URL name: 'notification-mark-as-read'

**Action Needed**:
1. Search for these URL patterns in `accounts/urls.py`, `courses/urls.py`, `notifications/urls.py`
2. If endpoints don't exist:
   - Mark tests as skip with reason "Endpoint not implemented yet"
3. If endpoints exist but with different names:
   - Update test URL reverse() calls

### 4. Signal Tests Not Firing (3 tests)
**Problem**: Notifications not being created via signals

**Affected Tests**:
- `courses/tests/test_signals.py::TestEnrollmentSignals.test_enrollment_creates_notifications`
- `courses/tests/test_signals.py::TestResultSignals.test_result_create_notification`
- `courses/tests/test_signals.py::TestResultSignals.test_result_update_notification`

**Errors**: 
- `assert 0 == 2` (expected 2 notifications, got 0)
- `assert 0 > 0` (expected some notifications, got none)

**Action Needed**:
1. Verify `courses/apps.py` imports signals: `from . import signals`
2. Check `courses/signals.py` signal registration
3. Ensure signals are connected in AppConfig.ready() method
4. Debug why post_save signals aren't firing in tests

### 5. Permission Tests Failing (2 tests)
**Problem**: `IsOwnerTeacherOrAdmin` permission allows read access to non-owners

**Affected Tests**:
- `courses/tests/test_permissions.py::TestIsOwnerTeacherOrAdmin.test_other_teacher_no_permission` - Returns True, should be False
- `courses/tests/test_permissions.py::TestIsOwnerTeacherOrAdmin.test_student_no_permission` - Returns True, should be False

**Root Cause**: Permission class likely treats SAFE_METHODS (GET, HEAD, OPTIONS) differently, allowing all authenticated users to read.

**Action Needed**:
1. Review `courses/permissions.py::IsOwnerTeacherOrAdmin.has_object_permission()`
2. Check logic for `request.method in permissions.SAFE_METHODS`
3. Determine if GET should require ownership or if tests are wrong
4. Update either permission logic or test expectations

### 6. Remaining Coverage Gap
**Current**: 75% (1653 statements, 419 missed)  
**Target**: 95% (need +20% = ~330 more statements covered)

**Focus Areas**:
- `accounts/views.py` - 69% coverage, target 90%+
- `accounts/permissions.py` - 0% coverage, target 80%+
- `courses/views.py` - 71% coverage, target 85%+
- Edge cases in serializers (time_ago calculations, validation branches)

**Strategy**:
1. Generate coverage report with missed lines: `pytest --cov --cov-report=term-missing`
2. Identify critical uncovered code paths
3. Create targeted tests for edge cases
4. Document intentionally skipped code (if any) with `# pragma: no cover`

---

## 🎯 NEXT STEPS (Priority Order)

1. **[HIGH - Quick Win]** Decision on rate limiting tests (skip vs fix)
2. **[MEDIUM]** Investigate missing endpoints (grep URLs, skip if not found)
3. **[MEDIUM]** Fix signal tests (verify apps.py configuration)
4. **[LOW]** Fix permission tests (review SAFE_METHODS logic)
5. **[FINAL PUSH]** Write new tests for uncovered code to reach 95%

---

## 📊 Coverage Progress Tracker

| Phase | Coverage | Tests Passing | Improvement |
|-------|----------|---------------|-------------|
| Initial | 57% | 49 | Baseline |
| Phase 2 (courses/views) | 65% | 73 | +8%, +24 tests |
| Phase 3 (serializers) | 75% | 158 | +10%, +85 tests |
| **Current** | **75%** | **158-165?** | **+18% total** |
| Target | 95% | 194 | +38% from start |

---

## 🐛 Known Issues

1. **Rate Limiter HTTP Status**: Returns 403 instead of 429 for rate limit exceeded
2. **Unused Variable Warnings**: Fixed in accounts/tests/test_api.py by removing assignments
3. **Line Ending Issues**: .gitattributes ensures LF for shell scripts in Docker
4. **Admin Fixture**: Fixed to include `role='ADMIN'` in conftest.py

---

## 📚 Testing Best Practices Applied

1. ✅ Mock external services (Turnstile CAPTCHA, email sending)
2. ✅ Use decorators for persistent mocks instead of context managers
3. ✅ Mock at point of use, not point of definition
4. ✅ Clean up unused variables to avoid lint warnings
5. ✅ Use fixtures for common test data (users, clients)
6. ✅ Test both success and error paths
7. ✅ Verify database state changes (refresh_from_db())
8. ✅ Use descriptive test names and docstrings

