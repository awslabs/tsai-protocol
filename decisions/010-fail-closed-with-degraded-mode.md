<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 010: Fail-Closed with Degraded Mode

**Status:** Accepted  
**Date:** 2026-01-27  
**Deciders:** TSAI Working Group  
**Amended by:** [ADR 012 — Service Provider Terminology](./012-service-provider-terminology.md)

---

## Context

Credential verification can fail for two categories of reasons:
1. **Security failures:** Invalid signatures, expired credentials, revoked credentials
2. **Infrastructure failures:** TA DID resolution fails, network timeouts, revocation service unavailable

We need an error handling strategy that:
- Prioritizes security (don't accept invalid credentials)
- Maintains availability during infrastructure outages
- Provides clear signals about trust level
- Aligns with operational reality (networks fail, services go down)

---

## Decision

Use **fail-closed with degraded mode**:
- **Fail closed** on security failures (invalid signatures, expired credentials, etc.)
- **Allow degraded mode** for infrastructure failures (DID resolution, revocation checks)
- **Require clear indication** when operating in degraded mode
- **Platform decides** whether to accept degraded credentials (policy, not protocol)

---

## Options Considered

### Option 1: Always Fail Closed (Rejected)

**Description:** Reject credentials on any verification failure, including infrastructure issues.

**Pros:**
- Maximum security
- Simple policy (always reject on error)
- No ambiguity

**Cons:**
- Poor availability during outages
- TA infrastructure becomes single point of failure
- Breaks T0/T1 offline verification model
- Unrealistic for production systems

---

### Option 2: Always Fail Open

**Description:** Accept credentials even when verification fails.

**Pros:**
- Maximum availability
- Simple fallback

**Cons:**
- Unacceptable security risk
- Could be exploited (cause infrastructure failures to bypass verification)
- Defeats purpose of trust protocol

---

### Option 3: Fail Closed with Degraded Mode

**Description:** Fail closed on security errors, allow degraded mode for infrastructure errors with clear warnings.

**Pros:**
- Security-first (never accept invalid credentials)
- Availability during infrastructure outages
- Clear trust level indication
- Platform retains control (can reject degraded credentials)
- Aligns with operational reality

**Cons:**
- More complex than always fail closed/open
- Requires platforms to handle degraded mode
- Potential for misuse if warnings ignored

---

## Decision

Use **fail-closed with degraded mode** (Option 3):
- **Fail closed** on security failures (invalid signatures, expired credentials, etc.)
- **Allow degraded mode** for infrastructure failures (DID resolution, revocation checks)
- **Require clear indication** when operating in degraded mode
- **Platform decides** whether to accept degraded credentials (policy, not protocol)

---

## Rationale

**Security failures MUST fail closed:**
- Invalid signature → Reject (credential is forged or tampered)
- Expired credential → Reject (credential is no longer valid)
- Revoked credential → Reject (TA explicitly revoked trust)
- Invalid VP signature → Reject (agent doesn't control DID)
- Timestamp outside tolerance → Reject (replay attack or clock issue)

**Infrastructure failures MAY allow degraded mode:**
- TA DID resolution fails → Use cached DID document if available
- Revocation check fails (T0/T1 only) → Skip check with warning
- Network timeout → Retry with exponential backoff, then degrade

**Why this works:**
- T0/T1 designed for offline verification (DID caching is expected)
- Revocation is optional for T0/T1 (short expiry provides protection)
- Platforms can implement circuit breakers and fallbacks
- Clear warnings enable informed decisions

**Degraded mode requirements:**
- Platform MUST indicate degraded trust level
- Platform MUST log degraded operation
- Platform SHOULD limit degraded mode duration
- Platform decides whether to accept (policy decision)

---

## Consequences

**Positive:**
- Security-first approach (never accept invalid credentials)
- Maintains availability during infrastructure outages
- Clear trust level indication enables informed decisions
- Aligns with T0/T1 offline verification model
- Platforms retain control over risk acceptance

**Negative:**
- More complex than simple fail closed/open
- Platforms must implement degraded mode handling
- Risk of warnings being ignored
- Requires monitoring and alerting infrastructure

**Neutral:**
- T2/T3 will have stricter requirements (no degraded mode for revocation)
- Degraded mode policies are platform-specific (not protocol-mandated)

---

## Implementation Notes

**For Platforms:**

**Fail closed on:**
- Signature verification failures
- Expired credentials
- Revoked credentials (when check succeeds)
- Invalid VP signatures
- Timestamp validation failures

**May degrade on:**
- DID resolution failures (use cached DID document)
- Revocation check failures (T0/T1 only, skip with warning)
- Network timeouts (after retries)

**Degraded mode response:**
```json
{
  "verified": true,
  "degraded": true,
  "warnings": [
    "TA DID resolution failed, using cached DID document",
    "Revocation check skipped due to network failure"
  ],
  "cachedUntil": "2026-01-27T11:00:00Z"
}
```

**Monitoring:**
- Track degraded mode frequency
- Alert on sustained degraded operation
- Monitor cache hit rates
- Track verification failure reasons

**For TAs:**
- Design for high availability
- Provide multiple DID resolution endpoints
- Use CDNs for DID documents and status lists
- Document expected availability SLAs

---

## Security Considerations

**Degraded mode risks:**
- Cached DID documents may be stale (TA rotated keys)
- Skipped revocation checks may miss revoked credentials
- Attackers could attempt to cause infrastructure failures

**Mitigations:**
- Limit cache duration (recommend 5-15 minutes for DID documents)
- Require platforms to log and monitor degraded mode
- T2/T3 will not allow degraded mode for critical checks
- Circuit breakers prevent sustained degraded operation
- Multiple TAs provide redundancy

**Attack scenarios:**
- **DDoS TA infrastructure:** Platforms degrade, but still verify signatures (cached keys)
- **DNS hijacking:** DNSSEC and HTTPS mitigate
- **Compromise TA domain:** Multiple TAs provide redundancy, governance body can alert

---

## References

- TSAI Architecture Specification Section 3.5 (Error Handling)
- TSAI Architecture Specification Section 3.6.4 (Revocation Check Bypass)
- Circuit Breaker Pattern (for degraded mode implementation)

