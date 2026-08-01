<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Credential Verification

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## 3.1 Overview

This section specifies how a Service Provider verifies a TSAI credential presented by an agent. A presentation is an SD-JWT VC (Section 2) with a key-binding JWT appended. Verification establishes that a trusted Trust Authority issued the credential, that it carries the identity floor, that it has not expired, that the presenter holds the bound key, that the presentation is fresh and addressed to this Service Provider, and, where the risk of the action warrants, that it is bound to the request and that the agent or operator is not blocked.

The base path is offline: it needs the Trust Authority's published signing key and nothing from the Trust Authority at request time. The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

---

## 3.2 Key Discovery and Identity

### 3.2.1 Trust Authority key

The Trust Authority is identified by `iss`, an HTTPS URL with no query or fragment. Its signing keys are published at `iss` joined with `/.well-known/jwt-vc-issuer`, and `kid` selects one. A Service Provider MUST obtain the key from that endpoint, MUST confirm that the metadata's `issuer` value equals `iss`, and MUST reject a credential whose header carries `x5c` or names any discovery mechanism other than `jwt-vc-issuer`. There is no DID resolution for the Trust Authority. A Service Provider verifies against a configured set of trusted issuers; if `iss` is not trusted, or the key cannot be obtained, verification fails closed.

The metadata URL is fetched under the hardening of Section 3.6.

### 3.2.2 Agent key

The agent is not resolved. Its key is the `cnf` JWK inside the credential, and the key-binding JWT is verified against it directly.

### 3.2.3 Third-party identifiers

A compliance or assurance signal names its provider by a `did:web` in `prv`. A Service Provider resolves that DID only if it independently checks the provider, which is optional; `prv` is attribution, not proof (Section 5.11). Where a Service Provider does resolve it, the fetch is subject to Section 3.6, and DNSSEC applies per Section 3.6.

---

## 3.3 Verification Algorithm

Given a presentation `<issuer-signed JWT>~<disclosure 1>~...~<disclosure N>~<key-binding JWT>`:

1. Split on `~`. A presentation MUST end with a key-binding JWT; a bare SD-JWT with an empty final element MUST be rejected. Whether to check key binding MUST NOT depend on whether the holder supplied a key-binding JWT (RFC 9901 §7.3).
2. Read the issuer-signed JWT header: confirm `typ` is `dc+sd-jwt` and `alg` is in the permitted set (EdDSA, ES256, ES384, ES512), reject `x5c`. Read `iss`, confirm it is trusted, obtain its key (Section 3.2.1), and verify the issuer signature.
3. Confirm `vct` is recognised; obtain its type metadata (Section 2.9).
4. Check the lifetime: reject if `exp` has passed or if `iat` is in the future beyond the skew of Section 3.4.
5. If disclosures are present, confirm `_sd_alg` is a supported digest algorithm before use (RFC 9901 §7.1), verify each disclosure against its digest in `signals`, and reconstruct. Count the signals that remain withheld and surface the count; fail closed if it exceeds the Service Provider's policy threshold. Reject any presentation that discloses `iss`, `exp`, or `cnf`, which are not disclosable (RFC 9901 §9.7), or that reveals a signal the type metadata marks `sd: never`.
6. Confirm the identity floor is present: `org`, `jur`, `kyc`, and at least one `dct` (Section 2.5.3).
7. Read the key-binding JWT header (`typ` `kb+jwt`) and verify its signature against the `cnf` JWK.
8. Confirm `aud` is this Service Provider, `nonce` is present (and, when the Service Provider issued one, that it matches and has not been used), and `sd_hash` matches the presented issuer-signed JWT and forwarded disclosures per RFC 9901 §4.3.1.
9. Apply the freshness rule of Section 3.4, and, where the action requires it, confirm `req` (Section 3.4).
10. Where the Service Provider's policy calls for it, check status (Section 3.5).

If any step fails, reject. Ignore signal types that are not recognised (Section 2.5.7).

---

## 3.4 Freshness, Replay, Nonce, and Request Binding

The mechanisms are settled by ADR 018 and ADR 020; this section is normative and cites them for rationale.

**Freshness.** A Service Provider MUST reject a key-binding JWT whose `iat` is outside the window: reject if `iat > now + 30` seconds or `iat < now − 90` seconds. The maximum accepted age is therefore 90 seconds, with 30 seconds of skew. Correct time is a dependency; a Service Provider SHOULD monitor clock drift and, on a stale rejection, SHOULD return its own current time so the agent can correct.

**Nonce.** `nonce` is always present (Section 2.4). At baseline the agent generates it, which with `aud` and the bounded `iat` bounds replay to the window against this Service Provider. Where the risk of the action warrants, the Service Provider issues a single-use, per-request `nonce` as a challenge and rejects a presentation that does not echo it, which closes the window.

**Reuse.** A key-binding JWT is created for a single presentation. Where the Service Provider issues the nonce, it is single-use and a repeat MUST be rejected. On the offline baseline the Service Provider holds no per-request state, so it cannot detect reuse, and a key-binding JWT may be replayed within the freshness window; for a state-changing action `req` binds the presentation to one request, which is why `req` is required there.

**Request binding.** For a state-changing action, and for any action where the verifying component and the acting component differ, a Service Provider MUST require `req` (Section 2.4, ADR 020) and MUST confirm the `req` digest matches the request it will act on. Without `req`, the 90-second window is defensible only for a read: it binds the presenter to the credential and to this Service Provider, not to the action (Section 5.11).

---

## 3.5 Status and Block

A credential MAY carry a `status` claim (Section 2.7.2). A Service Provider fetches the status list where its risk policy calls for it; the base path does not, and stays offline.

When it fetches, a Service Provider MUST verify the status-list token's signature, MUST confirm the token's issuer matches the credential's `iss`, MUST reject a token older than a bounded age, and MUST fetch the status URI only after confirming it shares the origin of `iss` (the status URI is issuer-controlled and is not otherwise pinned). The fetch is subject to Section 3.6. If the status entry for the agent or operator is set, the credential MUST be rejected with the `BLOCKED` code. If the status list is unreachable, the Service Provider applies the degraded-mode rule of Section 3.7.

---

## 3.6 Fetch Hardening

A Service Provider fetches URLs it did not choose: the issuer metadata at `iss`, and, where used, the status list and a `prv` `did:web`. Each is a server-side request-forgery vector (SD-JWT VC §6.1). For each, a Service Provider MUST validate the URL, MUST refuse a private, loopback, or link-local address after DNS resolution, and MUST bound the response size and the timeout. A Service Provider SHOULD use DNSSEC-validated resolution, and MUST do so where it resolves a `prv` `did:web` on which it relies for a material decision.

---

## 3.7 Error Handling, Degraded Mode, and Caching

### 3.7.1 Fail closed

The following MUST result in rejection: an invalid or unsupported issuer or key-binding signature, an untrusted `iss`, an `x5c` header, an `alg` outside the permitted set, an unrecognised `vct`, a missing identity floor, an expired credential, a key-binding JWT that is stale, missing, or whose `aud`, `nonce`, `sd_hash`, or required `req` does not match, a set status entry, and a malformed presentation.

Standard error codes:

- `SIGNATURE_INVALID`, `ISSUER_UNTRUSTED`, `UNKNOWN_TYPE`, `UNSUPPORTED_ALG`, `MALFORMED`.
- `EXPIRED` — the credential lifetime has passed.
- `STALE_PRESENTATION` — the key-binding JWT is well-formed and correctly signed but outside the freshness window; distinct from `BINDING_INVALID`, because clock drift presents this way.
- `BINDING_INVALID` — the key-binding signature, `aud`, `nonce`, `sd_hash`, or `req` failed.
- `MISSING_IDENTITY` — the identity floor is absent.
- `BLOCKED` — the agent or operator is blocked.

A Service Provider SHOULD return a structured error and MUST NOT include issuer identifiers, algorithm details, or key-discovery information in the response; it SHOULD log the detail server-side.

```json
{ "verified": false, "error": { "code": "BINDING_INVALID", "message": "Verification failed" } }
```

### 3.7.2 Degraded mode

If the issuer metadata is temporarily unreachable, a Service Provider MAY continue with a cached issuer key, and MUST indicate the degraded trust level and log it. Degraded mode MUST NOT relax any cryptographic, lifetime, identity-floor, or binding check. A Service Provider MUST bound the issuer-key cache lifetime, MUST bound the degraded-mode duration and fail closed once it is exceeded, and MUST provide an out-of-band path for emergency key rotation that does not depend on the metadata endpoint. Comparing the `lastKeyRotation` in the Trust Authority's signed report (§7.7) against the cache is a partial detection channel.

### 3.7.3 Verification-result caching

A Service Provider MAY cache a verification result. A cached result MUST NOT be used beyond the credential's `exp`. The cache key MUST include the presented credential, so a new presentation is verified rather than assumed. A Service Provider that consults the status list MUST NOT serve a cached positive result across a status change it could have observed.

---

## 3.8 Normative Requirements Summary

**Service Providers MUST:**
- Obtain the Trust Authority key from `iss` and `/.well-known/jwt-vc-issuer`, confirm `issuer` equals `iss`, reject `x5c`, and verify the issuer signature.
- Confirm `alg` is permitted, `vct` is recognised, and the identity floor is present.
- Verify the key-binding JWT against `cnf`; confirm `aud`, `nonce`, `sd_hash`, the freshness window (reject if `iat > now + 30` or `iat < now − 90`), and `req` where the action requires it.
- Reject a set status entry with `BLOCKED`, verify the status-list token and pin its URI to the `iss` origin, and harden every fetch (Section 3.6).
- Fail closed on any of the above, bound degraded-mode duration and cache lifetimes, and not leak issuer or algorithm detail in errors.

**Service Providers SHOULD:**
- Monitor clock drift, return their time on a stale rejection, and use DNSSEC-validated resolution.

**Service Providers MAY:**
- Cache issuer keys and verification results within the bounds of Section 3.7.

---

## References

- draft-ietf-oauth-sd-jwt-vc — SD-JWT VC (§3 discovery, §6.1 fetch hardening)
- RFC 9901 — SD-JWT (§4.3, §4.3.1, §7.1, §7.3, §9.7)
- draft-ietf-oauth-status-list — Token Status List
- RFC 9530 — Digest Fields; RFC 7519 — JWT; RFC 7515 — JWS; RFC 7638 — JWK Thumbprint
- ADR 018 (verification strength), ADR 019 (identity floor), ADR 020 (request binding)
