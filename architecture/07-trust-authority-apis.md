<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Trust Authority APIs

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 7.1 Overview

The Trust Authority API lets an agent obtain a credential and lets a Service Provider read a Trust Authority's status. The normative API is defined in OpenAPI at [`openapi/trust-authority-api.yaml`](openapi/trust-authority-api.yaml); this document gives the rationale and operational context.

A first deployment issues credentials carrying identity and reputation signals; compliance and assurance signals follow as a Trust Authority builds those evaluations. There are no tiers. How strongly a Service Provider verifies a presentation is its own policy (Section 3).

---

## 7.2 Proof of Control

Before issuing, a Trust Authority confirms the agent controls the key the credential will be bound to. The agent requests a challenge, signs it with that key, and returns the signature. The Trust Authority verifies the signature against the key it will place in `cnf`, so the binding key is proven at issuance without any DID resolution.

Challenges are single-use and expire after five minutes, which prevents replay while leaving time to sign. The exchange is stateless beyond the short-lived challenge.

---

## 7.3 Credential Lifecycle

An agent requests a credential when it needs one rather than holding a store of them. The Trust Authority evaluates the agent, populates the signals it can support, binds the credential to the agent's key, and signs it. Credentials are short-lived: `exp` is 30 minutes after `iat`. An agent refreshes before expiry, at around 80 per cent of the lifetime, to keep continuous access; a refresh can skip re-evaluation when the agent's standing has not moved.

The short lifetime carries most of the lifecycle. To stop an agent within the window, a Trust Authority stops re-issuing and, where it offers this, publishes a block keyed to the agent or operator identity through the Token Status List referenced by the credential's `status` claim (Section 2.7). Blocking one agent invalidates all of its current credentials. A Service Provider consults the list when its risk policy calls for it (Section 3.4).

---

## 7.4 Security

Every Trust Authority API uses HTTPS with TLS 1.3, since a credential is a bearer of signed claims; HSTS prevents downgrade. The general transport floor elsewhere is TLS 1.2 (Section 5); the Trust Authority APIs hold the higher bar deliberately. Signing keys are held in a hardware security module, which protects them even if the application layer is breached, and are rotated periodically with old keys retained to verify credentials signed before the rotation.

Rate limiting curbs abuse while allowing normal use; the recommended limits (ten issuances, twenty refreshes, and one hundred challenges per minute) are a starting point a Trust Authority tunes to its capacity.

---

## 7.5 Operational Requirements

A Trust Authority runs critical infrastructure, targets high availability, and completes issuance within around 500 ms at p95 so it does not stall an agent. It logs issuances and authentication failures for audit, with metadata only, never credential contents or keys.

---

## 7.6 Normative Requirements

A Trust Authority MUST implement the OpenAPI specification, confirm proof of control of the binding key before issuing, use HTTPS with TLS 1.3, and hold signing keys in an HSM. It SHOULD publish discovery metadata at `/.well-known/tsai-trust-authority` and its signing keys at `/.well-known/jwt-vc-issuer`.

---

## 7.7 Operational Transparency

### 7.7.1 Status report

A Trust Authority MUST serve a signed JSON document at `/.well-known/tsai-ta-status` over HTTPS. The report gives aggregate metrics that let a Service Provider assess the Trust Authority's health and spot anomalies, without exposing individual credentials.

```json
{
  "version": "1.0",
  "taIdentifier": "https://ta.example.com",
  "reportTimestamp": "2026-03-17T12:00:00Z",
  "reportingPeriod": "PT24H",
  "activeCredentials": 24,
  "issuedInPeriod": 1035,
  "blockedInPeriod": 15,
  "lastKeyRotation": "2026-02-15T00:00:00Z",
  "supportedAlgorithms": ["ES256", "EdDSA"],
  "proof": { "alg": "EdDSA", "kid": "key-1" }
}
```

### 7.7.2 Fields

| Field | Description |
|---|---|
| `version` | Report format version. MUST be `1.0`. |
| `taIdentifier` | The Trust Authority's HTTPS issuer identifier. |
| `reportTimestamp` | ISO 8601 time of generation. |
| `reportingPeriod` | ISO 8601 duration for the period counts. |
| `activeCredentials` | Count of non-expired credentials. |
| `issuedInPeriod` | Credentials issued during the period. |
| `blockedInPeriod` | Agents or operators blocked during the period. |
| `lastKeyRotation` | ISO 8601 time of the most recent signing-key rotation. |
| `supportedAlgorithms` | Signature algorithms supported. |
| `proof` | A signature over the report by the Trust Authority's signing key, identified by `kid` in the issuer key set. |

### 7.7.3 Requirements

- A Trust Authority MUST publish the report, update it at least every 24 hours, sign it with its current signing key, and exclude any individual credential, agent, or operator identifier. Counts SHOULD be accurate within a stated tolerance.
- A Service Provider SHOULD fetch reports periodically and SHOULD alert on anomalies: sudden issuance spikes, no blocks over a long period, a stale key rotation, or a stale report. It MAY use the data in its trust decisions, and MUST NOT have the protocol mandate any threshold.

### 7.7.4 Privacy and limits

Reports carry aggregate counts only, never data that identifies a holder, which preserves the privacy properties of Section 5.7. Self-reported data can be falsified by a compromised Trust Authority, so reports detect systemic anomalies rather than individual fraud (ADR 011).

---

## 7.8 HSM Attestation

### 7.8.1 Purpose

HSM key storage is required, but the protocol has no way to check it. A Trust Authority publishes evidence that its signing keys are held in a hardware security module, which closes the gap between the claim and the proof. This is an assurance a Service Provider MAY weigh; it is not gated to a tier.

### 7.8.2 Document

A Trust Authority SHOULD serve an attestation at `/.well-known/tsai-ta-hsm-attestation` over HTTPS.

```json
{
  "version": "1.0",
  "taIdentifier": "https://ta.example.com",
  "attestationType": "independent-audit",
  "auditor": "Example Audit Corp",
  "auditDate": "2026-01-15",
  "auditStandard": "SOC2-Type2",
  "scope": "Signing key generation, storage, and use for TSAI credential issuance",
  "summary": "An independent auditor confirmed that all TSAI signing keys are generated and held in FIPS 140-2 Level 3 HSMs, with multi-person authorisation for key operations.",
  "reportUrl": "https://ta.example.com/audits/2026-hsm-attestation.pdf",
  "nextAuditDate": "2027-01-15",
  "proof": { "alg": "EdDSA", "kid": "key-1" }
}
```

### 7.8.3 Assurance levels

- `independent-audit`: a third party verified HSM use. The strongest form.
- `vendor-attestation`: the HSM vendor confirms key residency.
- `self-attestation`: the Trust Authority declares it. The weakest, suitable only as a transitional measure.

### 7.8.4 Requirements

- A Trust Authority that publishes an attestation MUST sign it with its current signing key, keep it current within 18 months, and update it at least annually.
- A Service Provider MAY check the attestation and weigh it, and MUST NOT have the protocol mandate a vendor or certification level.

### 7.8.5 Limits

Attestation proves HSM use at audit time, not continuously. The short credential lifetime and the operational report (Section 7.7) are complementary detections.

---

## References

- OpenAPI Specification: [`openapi/trust-authority-api.yaml`](openapi/trust-authority-api.yaml)
- TSAI Credential Format (Section 2), TSAI Verification (Section 3)
- draft-ietf-oauth-sd-jwt-vc, draft-ietf-oauth-status-list
