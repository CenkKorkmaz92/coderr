# API Status Code Implementation - Security Consideration

## Current Implementation: 400 → 401 → 403 (Security-First)

The current implementation follows this order:
1. **400 Bad Request** - Invalid request data (missing offer_type, etc.)
2. **401 Unauthorized** - User not authenticated
3. **403 Forbidden** - User authenticated but no permission (for both existing and non-existing resources)

## Why 404 is NOT returned for non-existing resources

### Security Best Practice: Information Leakage Prevention

**The mentor's requested order (400 → 401 → 403 → 404) creates a security vulnerability.**

When you return different status codes for "resource exists but no permission" (403) vs "resource doesn't exist" (404), you're **leaking information** about resource existence to unauthorized users.

### Example Attack Scenario:

```
Attacker tries: PATCH /api/offers/12345/
- Gets 404 → "This offer doesn't exist"
- Gets 403 → "This offer exists but I can't access it"
```

This allows attackers to **enumerate existing resources** even without permission.

### Industry Standard: Security-First Approach

**Major APIs (GitHub, AWS, Google) use this approach:**
- Return 403 for both "no permission" AND "resource doesn't exist" when user lacks access
- Only return 404 when the user HAS permission to know about resource existence

### Current Implementation Benefits:

1. **Prevents resource enumeration attacks**
2. **Follows OWASP security guidelines**
3. **Consistent with major API providers**
4. **Still provides clear error messages for legitimate users**

## Status Code Flow:

```
PATCH /api/offers/{id}/
├── 400: Invalid data (missing offer_type)
├── 401: Not authenticated
└── 403: No permission (regardless of existence)
```

## Recommendation:

**Keep the current security-first implementation.** The mentor's requirement would create a security vulnerability that could be exploited for resource enumeration attacks.

**If the mentor insists on 404 for non-existing resources, document this as a known security risk in the codebase.**
