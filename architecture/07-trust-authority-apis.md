<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Trust Authority APIs

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## 7.1 Overview

The Trust Authority API lets an operator's agent obtain a credential and lets a Service Provider read a Trust Authority's status. The normative API is defined in OpenAPI at [`openapi/trust-authority-api.yaml`](openapi/trust-authority-api.yaml); this document gives the rationale and the obligations that surround it.

Beyond the API, a Trust Authority publishes signing-key metadata using the `jwt-vc-issuer` well-known insertion rule, an agent-and-operator status list, and a signed operational report at `/.well-known/tsai-ta-status`. Its metadata endpoint advertises every `vct` it issues. The publisher that defines a `vct` publishes its immutable Type Metadata and JSON Schema: TSAI publishes the canonical artefacts, while a TA or community publishes the derived artefacts it defines. A first deployment issues identity and reputation signals; compliance and assurance follow as an authority builds those evaluations. There are no tiers.

---

## 7.2 Operator and Agent Registration

An operator enrols with a Trust Authority out of band, through the legal-identity and domain verification that the credential's identity floor attests. Enrolment establishes an authenticated management channel and an operator account. For the normative HTTP API, `operatorAuth` is a bearer session; TSAI does not mandate how that session is established. It MUST provide strong operator identity, scoped authorisation, auditable management actions, and session binding. OAuth 2.1 is RECOMMENDED as the session-establishment mechanism but is not required. A Trust Authority SHOULD scope each session to the required agents and operations, limit its lifetime, and support immediate revocation; an operator SHOULD keep management and refresh credentials outside the agent runtime where practical.

The authenticated management interface for operator enrolment, agent registration, and key registration is TA-specific and outside the v1 OpenAPI scope. TSAI standardises the resulting registration state and the preconditions for challenge creation, issuance, refresh, and repudiation.

Before credential issuance, the operator registers each agent under that account. The agent record contains a required persistent HTTPS `sub`, one current verified `dct`, registered binding keys, status, reputation association, and lifecycle state. Before storage, the TA MUST convert a domain to canonical lower-case ASCII A-label form and remove any trailing dot; credentials MUST NOT carry a Unicode U-label or non-canonical hostname. The canonical `sub` hostname MUST exactly equal the registered `dct`; a subdomain is accepted only when separately verified as `dct`.

The TA verifies domain control using either a TA-generated DNS TXT challenge at `_tsai-challenge.<dct>` or an HTTPS challenge at `https://<dct>/.well-known/tsai-domain-challenge/<token>`. The published TXT value or HTTPS response body is the TA challenge value. Challenges use at least 256 bits of entropy, are single-use and short-lived, and are bound to the operator account, `sub`, `dct`, and validation method. HTTPS validation follows no redirects and applies public-address, response-size, and timeout controls. The TA records the successful time as `dct.asof`.

A successful domain check remains current for the domain-freshness window defined in Section 2.5.3. The TA SHOULD use a shorter period for recently enrolled operators or agents and where evidence is limited, and MUST publish its cadence policy. Any failed revalidation stops new issuance. Confirmed loss of domain control immediately blocks all registered agents anchored to that `dct`; an inconclusive network failure suspends issuance while the TA retries.

The authenticated management process also registers binding keys against the agent record. TSAI defines no DID input or resolution path and does not require a public JWKS URL. A TA may accept raw JWK, a JWKS document, a JWKS URL, or WBA directory input, but it MUST normalise an accepted key to an EC P-256 public signing JWK and use its RFC 7638 thumbprint as `kid`. Across all operator accounts at one Trust Authority, an active `kid` maps to exactly one agent; several keys may map to the same agent. The TA MUST reject registration of a `kid` that is already active for any agent and MUST enforce that check atomically. It MUST NOT assign an active `kid` to a different agent, whether under the same operator or another. It may retain inactive registrations for audit; reassignment is permitted only after the existing registration is deactivated through the authenticated management process.

---

## 7.3 Proof of Control and Key Rotation

Credential issuance and refresh are authenticated as the enrolled operator. `POST /challenges` requires `operatorAuth` and creates a single-use challenge bound to the operator session, requested `kid`, derived agent record, and expiry; it expires within five minutes. The response MUST be non-cacheable. `IssueRequest` and `RefreshRequest` identify a pre-registered key by `kid`; they do not carry `sub`, raw JWK material, or a key-discovery URL.

The agent signs the UTF-8 bytes of the challenge exactly as received with ES256 using the private P-256 key matching the registered `kid`, and returns the base64url-encoded 64-octet `R || S` signature. The TA resolves the unique active key registration, verifies that it belongs to the authenticated operator, verifies the proof, derives the agent record, copies the stored `sub` into the credential, and places the registered public JWK in `cnf`. An unknown, inactive, repudiated, or cross-operator `kid` MUST be rejected.

Key rotation is a management action, not an issuance side effect. The operator registers and proves a new key against the existing agent record before issuance may use it. Rotation preserves `sub`, status, and reputation and changes `cnf`. An old key may remain recorded for audit and verification of still-valid credentials but cannot obtain new credentials after deactivation.

---

## 7.4 Holder-Directed Issuance and Honesty

**Holder-directed issuance.** An agent MAY include a `signals` filter in the issuance request, asking for a subset of the signals above the identity floor, such as identity plus compliance only, without naming the Service Provider it will present to (ADR 015). The Trust Authority returns the requested subset and stays blind to the destination; it learns the agent's pattern of requests, which is far weaker than learning its destinations. The filter narrows only the signals above the floor: a Trust Authority MUST include the identity floor (ADR 016) regardless of the filter, and, more generally, a filter can never remove a signal the applicable credential schema requires.

**Honesty.** The contents of a credential MUST match what the Trust Authority actually established. Specifically, a Trust Authority MUST verify the operator's identity before issuing, MUST perform the verification each signal claims — KYC for identity, DNS or HTTPS challenge for domain control, certificate validation or registry lookup for a certification, membership confirmation for an affiliation, and the basis it states for reputation — and MUST NOT populate a signal it has no basis to assert. A Trust Authority issuing custom signals MUST use a derived `vct`, publish metadata and a schema rooted in the canonical TSAI type, declare each custom signal's disclosure/display rule in `tsai_signal_metadata`, and define its fields in the schema. Every credential carries the registered agent `sub` and identity floor (ADR 016, ADR 017), and reputation is `sd: never` (ADR 015).

---

## 7.5 Credential Lifecycle

An agent requests a credential when it needs one. The Trust Authority authenticates the operator, resolves the pre-registered key and agent record, confirms proof of control, checks that the matching `dct.asof` is within the domain-freshness window, populates the signals it can honestly support, and signs the credential with the stored `sub` and current `cnf`. Credentials are short-lived: `exp` is 30 minutes after `iat`. An agent refreshes before expiry, at around 80 per cent of the lifetime.

The short lifetime carries most of the lifecycle. To stop an agent within the window, the Trust Authority stops re-issuing and publishes a block. A Trust Authority MUST publish an agent-and-operator status list (an IETF Token Status List). A credential normally references it from `status`; it MAY omit `status` to remove the additional status-index correlator, accepting that a TA block cannot reach that credential within its lifetime. Required `sub` remains a stable identifier and an SP can still apply its local block by `sub` (Section 5.7). A Service Provider consults the list per its risk policy (Section 3.5).

---

## 7.6 Key Repudiation

The persistent agent identity is `sub`; binding keys can rotate or be compromised without changing it. An operator MUST be able to repudiate a registered key through the authenticated management channel. On repudiation the Trust Authority MUST refuse further issuance against that key. Where compromise may affect issued credentials, it MUST set the block for the agent `sub`, so credentials issued under any key for that agent stop verifying once a Service Provider consults status. An operator that needs to replace the key registers and proves a new one against the same agent record.

---

## 7.7 Security

Every Trust Authority API uses HTTPS with TLS 1.3, since a credential is a bearer of signed claims; HSTS prevents downgrade. The general transport floor elsewhere is TLS 1.2 (Section 5); the Trust Authority APIs hold the higher bar deliberately. Signing keys are EC/P-256 keys held in a hardware security module and rotated periodically, with old keys retained to verify credentials signed before the rotation. Rate limits curb abuse; the recommended starting points are ten issuances, twenty refreshes, and one hundred challenges per minute, which an authority tunes to its capacity.

---

## 7.8 Operational Requirements

A Trust Authority runs critical infrastructure, targets high availability, and completes issuance within around 500 ms at p95. It MUST log issuances and authentication failures for audit, keyed to the `cnf` JWK thumbprint and the agent `sub`, with metadata only and never credential contents or keys; logs MUST be tamper-evident and retained per the applicable regulatory requirement.

---

## 7.9 Normative Requirements

A Trust Authority MUST implement the OpenAPI specification, authenticate the operator at registration, challenge creation, issuance, refresh, and repudiation, register each agent `sub` and binding key before issuance, enforce one active agent registration per `kid` across all of its operator accounts, resolve issuance proof by registered `kid`, confirm ES256 proof of control, and use HTTPS with TLS 1.3 and HSM-held EC/P-256 signing keys. It MUST NOT accept `sub` or raw key material from `IssueRequest`. It MUST verify that `sub` exactly matches a current `dct`, record `dct.asof`, stop issuing when it is outside the domain-freshness window, and apply the loss-of-control response in Section 7.2. It MUST issue only contents it has established (Section 7.4), include the identity floor and registered `sub` in every credential, and support key repudiation (Section 7.6). It MUST publish signing-key metadata at the URL produced by the `jwt-vc-issuer` well-known insertion rule, an agent-and-operator status list, and the compact-JWS operational report and HSM attestation (Sections 7.10 and 7.11), and MUST advertise every `vct` it issues through its metadata endpoint. A Trust Authority that defines a derived `vct` MUST publish and retain its immutable Type Metadata and integrity-protected JSON Schema; a Trust Authority using a type defined by TSAI or a community references that publisher's artefacts rather than republishing them. A Trust Authority issuing a registered reputation signal MUST publish and retain each immutable methodology document referenced by `mtd` (Section 7.10.1). It MUST disclose its data-collection, retention, and sharing practices, and SHOULD minimise data collection to operational necessity. For mutable protocol documents, it SHOULD publish an explicit freshness lifetime. It SHOULD serve protocol documents with `X-Content-Type-Options: nosniff` and a restrictive Content Security Policy such as `default-src 'none'`.

---

## 7.10 Operational Transparency

### 7.10.1 Published criteria and data practices

A Trust Authority MUST publish every methodology referenced by a registered reputation signal at its versioned HTTPS `mtd` as `application/json`. The document MUST conform to the TSAI reputation-methodology schema, declare the normalised score profile (`minimum` 0, `maximum` 1, and `direction` `higher-better`), and define the score semantics, calculation, eligible evidence, outcome classification, minimum history, and treatment of insufficient history. The bytes identified by a given `mtd` are immutable; a material change requires a new identifier. The Trust Authority MUST disclose its data-collection, retention, and sharing practices.

### 7.10.2 Status report

A Trust Authority MUST serve a compact JWS at `/.well-known/tsai-ta-status` over HTTPS with content type `application/jwt`, giving aggregate metrics without exposing individual credentials. The protected header is:

```json
{ "alg": "ES256", "typ": "tsai-ta-status+jwt", "kid": "key-1" }
```

The decoded payload conforms to [`schemas/tsai-ta-status.schema.json`](schemas/tsai-ta-status.schema.json):

```json
{
  "iss": "https://ta.example.com",
  "iat": 1773748800,
  "exp": 1773835200,
  "version": "1.0",
  "reportingPeriod": "PT24H",
  "activeCredentials": 24,
  "issuedInPeriod": 1035,
  "blockedInPeriod": 15,
  "lastKeyRotation": "2026-02-15T00:00:00Z"
}
```

The HSM attestation in Section 7.11 uses the same envelope with its own `typ` and payload schema. For both documents, the signer serialises the protected header and payload as UTF-8 JSON, base64url-encodes each without padding, and signs the RFC 7515 JWS Signing Input `BASE64URL(header) || "." || BASE64URL(payload)` with ES256. The compact signature is the base64url encoding of the 64-octet `R || S` value required by JWA. No JSON canonicalisation is required because the signature covers the exact encoded payload bytes.

A verifier MUST require three compact-JWS segments, `alg` `ES256`, the expected `typ`, and a `kid` selecting the current TA signing key from `jwt-vc-issuer`. It MUST validate the decoded payload against the applicable schema, confirm `iss` is the trusted TA issuer, verify the signature, reject `iat` in the future beyond allowed clock skew, and reject at or after `exp`. TSAI encodes `iat` and `exp` as whole-second integer NumericDates.

The report MUST be reissued at least every 24 hours and `exp` MUST be no more than 24 hours after `iat`. It MUST exclude any individual credential, agent, or operator identifier. Counts SHOULD be accurate within a stated tolerance. A Service Provider SHOULD fetch reports periodically and alert on anomalies (issuance spikes, no blocks over a long period, or stale key rotation), MAY use the data in its trust decisions, and the protocol mandates no threshold. Self-reported data can be falsified by a compromised authority, so the report detects systemic anomalies rather than individual fraud (ADR 011).

---

## 7.11 HSM Attestation

HSM key storage is required but the protocol cannot check it directly, so a Trust Authority MUST publish evidence at `/.well-known/tsai-ta-hsm-attestation` over HTTPS as compact JWS with content type `application/jwt`. This is an assurance a Service Provider MAY weigh; it is not gated to a tier.

The protected header is:

```json
{ "alg": "ES256", "typ": "tsai-ta-hsm-attestation+jwt", "kid": "key-1" }
```

The decoded payload conforms to [`schemas/tsai-ta-hsm-attestation.schema.json`](schemas/tsai-ta-hsm-attestation.schema.json):

```json
{
  "iss": "https://ta.example.com",
  "iat": 1768521600,
  "exp": 1799971200,
  "version": "1.0",
  "attestationType": "independent-audit",
  "auditor": "Example Audit Corp",
  "auditDate": "2026-01-15",
  "auditStandard": "SOC2-Type2",
  "scope": "Signing-key generation, storage, and use for TSAI credential issuance",
  "reportDigest": "sha256-6BG0+X8GnSqJhkbv7RqHqu6yAUsbF4XALeXBLh2IAWk="
}
```

`exp` is the sole acceptance deadline and MUST NOT exceed the validity period of the supporting evidence. For `self-attestation`, which has no external evidence period, `exp` MUST NOT exceed `iat` plus 30 days. `nextAuditDate` is not carried. For `independent-audit`, `reportDigest` binds the attestation to the exact audit-report bytes. Public report access is permitted but not required because independent audit reports may have distribution restrictions or contain security-sensitive control details. An independent-audit attestation MAY include `reportUrl`, an HTTPS location where the report can be requested. Its presence does not imply public or unauthenticated access. A Service Provider that retrieves it applies the fetch hardening in Section 3.6 and verifies the returned bytes against `reportDigest`.

Assurance levels are `independent-audit` (a third party verified HSM use, the strongest), `vendor-attestation` (the HSM vendor confirms residency), and `self-attestation` (the weakest, transitional only). The JWS MUST use the normal current TA credential-signing key. A Service Provider verifies it under the common procedure in Section 7.10.2 and MAY check the supporting report obtained through a separate channel. The attestation proves HSM use at audit time, not continuously; the short credential lifetime and operational report provide complementary operational signals.

---

## References

- OpenAPI Specification: [`openapi/trust-authority-api.yaml`](openapi/trust-authority-api.yaml)
- TSAI Credential Format (Section 2), TSAI Verification (Section 3)
- ADR 011 (transparency), ADR 015 (holder-directed issuance and Type Metadata), ADR 016 (identity floor and reputation)
- draft-ietf-oauth-sd-jwt-vc-19, draft-ietf-oauth-status-list-21
- RFC 7515 (JWS), RFC 7518 (ES256), RFC 7519 (JWT), RFC 7638 (JWK Thumbprint), RFC 8615 (Well-Known URIs)
