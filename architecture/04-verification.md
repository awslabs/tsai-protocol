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

The base path is offline: it needs the Trust Authority's published signing key and cached type metadata, and nothing from the Trust Authority at request time. A policy that uses a registered reputation score also needs its cached methodology document. The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

---

## 3.2 Key Discovery and Identity

### 3.2.1 Trust Authority key

The Trust Authority is identified by `iss`, a case-sensitive HTTPS URL containing a host and optionally a port and path, but no query or fragment. The signing-key metadata URL is formed by inserting `/.well-known/jwt-vc-issuer` between the origin and the `iss` path, removing any terminating slash from that path first. Thus `https://ta.example` maps to `https://ta.example/.well-known/jwt-vc-issuer`, while `https://ta.example/tenant/acme` maps to `https://ta.example/.well-known/jwt-vc-issuer/tenant/acme`. `kid` selects one key. A Service Provider MUST obtain the key from that endpoint, MUST confirm by exact string comparison that the metadata's `issuer` value equals the original `iss`, and MUST reject a credential whose header carries `x5c` or names any discovery mechanism other than `jwt-vc-issuer`. There is no DID resolution for the Trust Authority. A Service Provider verifies against a configured set of trusted issuer identifiers; if `iss` is not trusted, or the key cannot be obtained, verification fails closed.

The metadata URL is fetched under the hardening of Section 3.6.

### 3.2.2 Agent key

The verifier treats the signed `sub` as the persistent agent identity and does not resolve it. The current holder-binding key is the inline `cnf` JWK, and the key-binding JWT is verified against it directly.

### 3.2.3 Third-party identifiers

A compliance or assurance signal names its provider by a `did:web` in `prv`. A Service Provider resolves that DID only if it independently checks the provider, which is optional; `prv` is attribution, not proof (Section 5.11). Where a Service Provider does resolve it, the fetch is subject to Section 3.6, and DNSSEC applies per Section 3.6.

---

## 3.3 Verification Algorithm

Given a presentation `<issuer-signed JWT>~<disclosure 1>~...~<disclosure N>~<key-binding JWT>`:

1. Split on `~`. A presentation MUST end with a key-binding JWT; a bare SD-JWT with an empty final element MUST be rejected. Whether to check key binding MUST NOT depend on whether the holder supplied a key-binding JWT (RFC 9901 §7.3).
2. Read the issuer-signed JWT header: confirm `typ` is `dc+sd-jwt` and `alg` is `ES256`, reject every other algorithm and reject `x5c`. Read `iss`, confirm it is trusted, obtain its key (Section 3.2.1), and verify the issuer signature.
3. Resolve the credential type from cache, never by fetching on this path (Section 2.9). Verify `vct#integrity` and load the integrity-pinned JSON Schema. If `aka_vcts` is present, reject it if it contains the primary `vct`. For a derived type, require `aka_vcts` to contain the canonical TSAI `vct`; follow and integrity-check the `extends` chain to that canonical type; reject circular or unrelated chains; confirm the derived schema composes the immutable base schema; process inherited standard `claims` metadata and TSAI `tsai_signal_metadata`; and confirm that every custom signal is declared by the derived metadata and schema. If any document is absent or invalid, fail the presentation and refresh the chain out of band. Field-level schema validation occurs after disclosure processing in step 5.
4. Check the lifetime: reject if `exp` has passed or if `iat` is in the future beyond the skew of Section 3.4.
5. If disclosures are present, confirm `_sd_alg` is `sha-256` before use (RFC 9901 §7.1), verify each disclosure against its digest in `signals`, and reconstruct. Count the signals that remain withheld and surface the count; fail closed if it exceeds the Service Provider's policy threshold. Reject any presentation that discloses `iss`, `exp`, or `cnf`, which are not disclosable under SD-JWT VC §2.2.2.3 (see also RFC 9901 §9.7), or that discloses `sub`, which TSAI marks `sd: never`, or that reveals a signal the effective `tsai_signal_metadata` marks `sd: never`. Validate the processed payload against the complete schema chain, so every disclosed registered or custom signal is checked at field level; each schema-required signal has an effective `sd: never` rule and therefore remains available for this validation. For every registered reputation signal that policy uses, load the methodology document from the out-of-band cache, verify `mtd#integrity`, validate it against the reputation-methodology schema, confirm its `id` equals `mtd`, require `score.minimum < score.maximum`, and require `scr` to fall within that inclusive range. Key policy by `(iss, typ, mtd)`. An absent, unknown, or invalid methodology MUST NOT produce a favourable reputation result; it does not invalidate otherwise valid credential signals unless the Service Provider's policy requires that reputation.
6. Confirm the identity floor and persistent agent identity: `org`, `jur`, `kyc`, required `sub`, and at least one `dct` whose hostname equals the normalised `sub` hostname. The matching `dct` MUST carry `asof`, MUST be within the domain-freshness window of Section 2.5.3 relative to credential `iat`, and MAY be up to 30 seconds later than `iat` under the clock-skew allowance of Section 3.4.
7. Read the key-binding JWT header, confirm `typ` is `kb+jwt` and `alg` is `ES256`, confirm the `cnf` JWK is an EC/P-256 public key, and verify the signature against it.
8. Confirm `aud` is this Service Provider, `nonce` is present (and, when the Service Provider issued one, that it matches and has not been used), and `sd_hash` matches the presented issuer-signed JWT and forwarded disclosures per RFC 9901 §4.3.1.
9. Apply the freshness rule of Section 3.4; for a state-changing or split-topology action, confirm both a Service-Provider-issued single-use `nonce` and `req` (Section 3.4).
10. Where the Service Provider's policy calls for it, check status (Section 3.5).

If any step fails, reject. After successful derived-schema validation, a Service Provider MAY ignore declared extension signals it does not use in policy (Section 2.5.7).

---

## 3.4 Freshness, Replay, Nonce, and Request Binding

The mechanisms are settled by ADR 018 and ADR 014; this section is normative and cites them for rationale.

**Freshness.** A Service Provider MUST reject a key-binding JWT whose `iat` is outside the window: reject if `iat > now + 30` seconds or `iat < now − 90` seconds. The maximum accepted age is therefore 90 seconds, with 30 seconds of skew. Correct time is a dependency; a Service Provider SHOULD monitor clock drift and, on a stale rejection, SHOULD return its own current time so the agent can correct.

**Nonce.** `nonce` is always present (Section 2.4). At baseline the agent generates it, which with `aud` and the bounded `iat` bounds replay to the window against this Service Provider. Where the risk of the action warrants, and always for a state-changing action (Request binding below), the Service Provider issues a single-use, per-request `nonce` as a challenge and rejects a presentation that does not echo it, which closes the window.

**Reuse.** A key-binding JWT is created for a single presentation. On the offline baseline the Service Provider holds no per-request state, so it cannot detect reuse, and a key-binding JWT may be replayed within the freshness window. `req` does not close this on its own: it binds the presentation to one request, so a substituted request is rejected, but an identical resubmission of the same request inside the window still matches every claim. Closing replay needs a Service-Provider-issued single-use `nonce`, which `req` does not replace and which does not replace `req`.

**Request binding.** For a state-changing action, and for any action where the verifying component and the acting component differ, a Service Provider MUST require `req` (Section 2.4, ADR 014) and MUST confirm that `req` matches the request it will act on: the method, the target URI, and, where the request has a body, the body digest. Because `req` binds the action but not its uniqueness, a state-changing action MUST also carry a Service-Provider-issued single-use `nonce`; the two are complementary, `req` closing substitution and the single-use nonce closing replay. A read needs neither: the 90-second window binds the presenter to the credential and to this Service Provider, which is enough when the action has no side effect (Section 5.11).

---

## 3.5 Status and Block

A credential MAY carry a `status` claim (Section 2.7.2). A Service Provider fetches the status list where its risk policy calls for it; the base path does not, and stays offline.

When it fetches, a Service Provider MUST confirm the status-list token uses `ES256`, MUST verify its signature, MUST confirm the token's issuer matches the credential's `iss`, MUST reject a token older than a bounded age, and MUST fetch the status URI only after confirming it shares the origin of `iss` (the status URI is issuer-controlled and is not otherwise pinned). The fetch is subject to Section 3.6. If the status entry for the agent or operator is set, the credential MUST be rejected with the `BLOCKED` code. If the status list is unreachable, the Service Provider applies the degraded-mode rule of Section 3.7.

---

## 3.6 Fetch Hardening

A Service Provider fetches URLs it did not choose: the issuer metadata at `iss`, Type Metadata, schema, and reputation-methodology documents out of band, and, where used, the status list, an HSM-attestation `reportUrl`, and a `prv` `did:web`. Each is a server-side request-forgery vector (SD-JWT VC §6.1). For each, a Service Provider MUST validate the URL, MUST refuse a private, loopback, or link-local address after DNS resolution, and MUST bound the response size and the timeout. A Service Provider SHOULD use DNSSEC-validated resolution, and MUST do so where it resolves a `prv` `did:web` on which it relies for a material decision.

---

## 3.7 Error Handling, Degraded Mode, and Caching

### 3.7.1 Verification failure

This section governs the verification outcome; the access decision on a failed verification is the Service Provider's (Section 4.4.1). The following MUST result in a verification failure, and a failed verification MUST NOT be reported as verified: an invalid or unsupported issuer or key-binding signature, an untrusted `iss`, an `x5c` header, an `alg` other than `ES256`, an unrecognised `vct`, a Type Metadata, schema, `vct#integrity`, `extends#integrity`, or `tsai_schema_uri#integrity` failure, a missing identity floor, missing or invalid `sub`, a `sub`/`dct` mismatch, stale `dct`, an expired credential, a key-binding JWT that is stale, missing, or whose `aud`, `nonce`, `sd_hash`, or required `req` does not match, a set status entry, and a malformed presentation.

The default access posture on a failure is to reject. A Service Provider MAY instead log or annotate (Section 4.4.1); what it MUST NOT do is treat a failed verification as verified.

Standard error codes:

- `SIGNATURE_INVALID`, `ISSUER_UNTRUSTED`, `UNKNOWN_TYPE`, `UNSUPPORTED_ALG`, `MALFORMED`.
- `EXPIRED` — the credential lifetime has passed.
- `STALE_PRESENTATION` — the key-binding JWT is well-formed and correctly signed but outside the freshness window; distinct from `BINDING_INVALID`, because clock drift presents this way.
- `BINDING_INVALID` — the key-binding signature, `aud`, `nonce`, `sd_hash`, or `req` failed.
- `MISSING_IDENTITY` — the identity floor or persistent `sub` is absent.
- `IDENTITY_MISMATCH` — `sub` is not anchored to a matching, fresh `dct`.
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
- Obtain the Trust Authority EC/P-256 key from `iss` and `/.well-known/jwt-vc-issuer`, confirm `issuer` equals `iss`, reject `x5c`, require `alg` `ES256`, and verify the issuer signature.
- Confirm `alg` is `ES256`, validate the complete `vct` metadata and schema chain, confirm the identity floor and required `sub`, and verify that `sub` matches a `dct` within the domain-freshness window.
- Verify the key-binding JWT against `cnf`; confirm `aud`, `nonce`, `sd_hash`, the freshness window (reject if `iat > now + 30` or `iat < now − 90`), and `req` where the action requires it.
- Reject a set status entry with `BLOCKED`, verify the status-list token and pin its URI to the `iss` origin, and harden every fetch (Section 3.6).
- Treat any of the above as a verification failure, never report a failed verification as verified, bound degraded-mode duration and cache lifetimes, and not leak issuer or algorithm detail in errors.

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
- ADR 018 (verification strength), ADR 016 (identity floor), ADR 014 (request binding)
