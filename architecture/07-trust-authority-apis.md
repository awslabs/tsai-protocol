<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Trust Authority APIs

**Version:** 1.0-MVP (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft  
**Scope:** Phase 0 (T0/T1 only)

---

## 7.1 Overview

The Trust Authority API enables Agents to obtain verifiable credentials and Service Providers to verify credential status. The normative API specification is defined in OpenAPI format at [`openapi/trust-authority-api.yaml`](openapi/trust-authority-api.yaml). This document explains the design rationale and operational context.

This MVP specification covers T0 and T1 credentials only. Revocation endpoints and status lists are deferred to Phase 1 (T2/T3 implementation). T0/T1 credentials rely on natural expiry rather than active revocation.

---

## 7.2 Authentication Model

TSAI uses challenge-response authentication to prove DID control without requiring agents to maintain long-lived sessions or API keys. When an agent requests a credential, it first obtains a random challenge from the TA, signs it with its DID private key, and submits the signature as proof of control. This approach prevents unauthorized credential requests while remaining stateless—the TA doesn't need to track agent sessions.

Challenges are single-use and expire after 5 minutes. This prevents replay attacks while giving agents enough time to complete the signing operation. The TA verifies the signature against the agent's DID document, which it resolves using standard W3C DID resolution. If verification succeeds, the TA proceeds with credential issuance.

---

## 7.3 Credential Lifecycle

Agents request credentials just-in-time rather than maintaining a persistent credential store. When an Agent needs to interact with a Service Provider, it requests a credential from the TA at the appropriate tier. The TA evaluates the Agent against tier requirements: T0 requires identity verification through KYC, T1 adds reputation data. The TA issues a credential at the highest tier the Agent qualifies for, which may be lower than requested if the Agent doesn't meet requirements.

Credentials are short-lived by design. T0 and T1 credentials expire after 2-4 hours. Short expiry reduces revocation dependency—most credentials naturally expire before revocation becomes necessary. Agents refresh credentials before expiry (recommended at 80% of lifetime) to maintain continuous access. Refresh is faster than issuance because the TA can skip re-evaluation if the agent's status hasn't changed significantly.

For Phase 0, revocation is not supported. If an agent must be immediately disabled, operators should update their internal systems to reject future credential requests. Existing credentials will expire naturally within 4 hours.

---

## 7.4 Security Considerations

All TA APIs use HTTPS with TLS 1.3. This is non-negotiable because credentials are bearer tokens—anyone possessing a valid credential can use it. TAs should enable HSTS to prevent downgrade attacks.

Credential signing keys must be stored in hardware security modules (HSMs). This protects against key extraction even if the TA's application layer is compromised. TAs issuing T2/T3 credentials must publish an HSM attestation statement (see Section 7.8). Keys are rotated annually, with old keys remaining available during transition periods to verify credentials issued before rotation.

Rate limiting prevents abuse while allowing legitimate usage. The recommended limits (10 issuance requests per minute, 20 refresh requests per minute, 100 challenge requests per minute) are based on expected agent behavior patterns. TAs may adjust limits based on their infrastructure capacity and observed usage patterns.

---

## 7.5 Operational Requirements

Trust Authorities operate critical infrastructure. Phase 0 targets 99.9% availability. Credential issuance must complete within 500ms (p95) to avoid blocking agent workflows.

TAs must log all credential issuance and authentication failures for audit purposes. Logs must not contain credential contents or private keys—only metadata like agent DIDs, tiers, and timestamps. This enables security monitoring and incident response while protecting sensitive data.

---

## 7.6 Normative Requirements

Trust Authorities must implement the OpenAPI specification, verify agent proof of control using challenge-response, use HTTPS with TLS 1.3, and use HSMs for signing keys. TAs issuing T2/T3 credentials must additionally publish an HSM attestation statement (Section 7.8).

Trust Authorities should publish metadata at `/.well-known/tsai-trust-authority` for discovery.

---

## References

- OpenAPI Specification: [`openapi/trust-authority-api.yaml`](openapi/trust-authority-api.yaml)
- TSAI Credential Format (Section 2)
- TSAI Verification (Section 3)

---

## 7.7 Operational Transparency

### 7.7.1 Status Report Endpoint

Trust Authorities MUST serve a signed JSON document at `/.well-known/tsai-ta-status` over HTTPS. This report provides aggregate operational metrics that enable Service Providers to assess TA health and detect anomalies without exposing individual credential data.

### 7.7.2 Report Format

```json
{
  "version": "1.0",
  "taIdentifier": "did:web:ta.example.com",
  "reportTimestamp": "2026-03-17T12:00:00Z",
  "reportingPeriod": "PT24H",
  "activeCredentials": {
    "t0": 12450,
    "t1": 3200,
    "t2": 0,
    "t3": 0
  },
  "issuedInPeriod": {
    "t0": 890,
    "t1": 145,
    "t2": 0,
    "t3": 0
  },
  "revokedInPeriod": {
    "t0": 12,
    "t1": 3,
    "t2": 0,
    "t3": 0
  },
  "lastKeyRotation": "2026-02-15T00:00:00Z",
  "supportedAlgorithms": ["ES256", "EdDSA"],
  "proof": {
    "type": "JsonWebSignature2020",
    "verificationMethod": "did:web:ta.example.com#key-1",
    "created": "2026-03-17T12:00:00Z"
  }
}
```

### 7.7.3 Field Definitions

| Field | Type | Description |
|---|---|---|
| `version` | string | Report format version. MUST be `1.0`. |
| `taIdentifier` | string | TA's DID. MUST match the TA's published DID document. |
| `reportTimestamp` | string | ISO 8601 timestamp of report generation. |
| `reportingPeriod` | string | ISO 8601 duration for `issuedInPeriod` and `revokedInPeriod`. |
| `activeCredentials` | object | Non-expired, non-revoked credential count by tier. |
| `issuedInPeriod` | object | Credentials issued during the reporting period, by tier. |
| `revokedInPeriod` | object | Credentials revoked during the reporting period, by tier. |
| `lastKeyRotation` | string | ISO 8601 timestamp of most recent signing key rotation. |
| `supportedAlgorithms` | array | Signature algorithms the TA supports. |
| `proof` | object | Signature over the report using the TA's signing key. |

### 7.7.4 Normative Requirements

**Trust Authorities:**
- TAs MUST publish a status report at `/.well-known/tsai-ta-status`
- Reports MUST be updated at least every 24 hours
- Reports MUST be signed by the TA's current signing key
- Reports MUST NOT contain individual credential data, agent identifiers, or operator information
- Report counts MUST be accurate within ±5% (to accommodate eventual consistency)

**Service Providers:**
- Service Providers SHOULD fetch TA status reports periodically (recommended: daily)
- Service Providers SHOULD alert on anomalies: sudden issuance spikes, zero revocations over extended periods, stale key rotation (>12 months), report staleness (>48 hours)
- Service Providers MAY use status report data in TA trust decisions
- Service Providers MUST NOT require specific metric thresholds in the protocol (thresholds are a Service Provider's policy)

### 7.7.5 Privacy

Status reports contain aggregate counts only. Reports MUST NOT include agent DIDs, operator identifiers, credential identifiers, or any data that could identify individual credential holders. This preserves the privacy properties described in Section 5.7.

### 7.7.6 Limitations

Self-reported data can be falsified by a compromised TA. Status reports detect systemic anomalies (mass forgery, standards erosion, operational failures) but cannot detect individual fraudulent credentials. See ADR 011 for the design rationale and accepted residual risks.

---

## 7.8 HSM Attestation

### 7.8.1 Purpose

The protocol requires HSM key storage for all TAs, but provides no verification mechanism. TAs issuing T2/T3 credentials MUST publish evidence that signing keys are protected by hardware security modules. This closes the gap between claiming HSM usage and proving it.

### 7.8.2 Attestation Endpoint

TAs issuing T2/T3 credentials MUST serve an HSM attestation document at `/.well-known/tsai-ta-hsm-attestation` over HTTPS.

### 7.8.3 Attestation Format

```json
{
  "version": "1.0",
  "taIdentifier": "did:web:ta.example.com",
  "attestationType": "independent-audit",
  "auditor": "Example Audit Corp",
  "auditDate": "2026-01-15",
  "auditStandard": "SOC2-Type2",
  "scope": "Signing key generation, storage, and usage for TSAI credential issuance",
  "keyIdentifiers": ["did:web:ta.example.com#key-1"],
  "summary": "Independent auditor verified that all TSAI signing keys are generated and stored in FIPS 140-2 Level 3 certified HSMs. Key operations require multi-person authorization.",
  "reportUrl": "https://ta.example.com/audits/2026-hsm-attestation.pdf",
  "nextAuditDate": "2027-01-15",
  "proof": {
    "type": "JsonWebSignature2020",
    "verificationMethod": "did:web:ta.example.com#key-1",
    "created": "2026-01-20T00:00:00Z"
  }
}
```

### 7.8.4 Field Definitions

| Field | Type | Description |
|---|---|---|
| `version` | string | Attestation format version. MUST be `1.0`. |
| `taIdentifier` | string | TA's DID. MUST match the TA's published DID document. |
| `attestationType` | string | One of: `independent-audit`, `vendor-attestation`, `self-attestation`. |
| `auditor` | string | Name of the auditing organization or HSM vendor. |
| `auditDate` | string | ISO 8601 date of the most recent audit or attestation. |
| `auditStandard` | string | Standard used (e.g., `SOC2-Type2`, `ISO27001`, `FIPS-140-2`). |
| `scope` | string | What the audit covered. |
| `keyIdentifiers` | array | DID key references covered by this attestation. |
| `summary` | string | Brief description of findings. |
| `reportUrl` | string | URL to the full audit report (MAY be access-controlled). |
| `nextAuditDate` | string | ISO 8601 date of the next scheduled audit. |
| `proof` | object | Signature over the attestation using the TA's signing key. |

### 7.8.5 Attestation Types

**`independent-audit`**: Third-party auditor verified HSM usage. Highest assurance. RECOMMENDED for TAs issuing T3 credentials.

**`vendor-attestation`**: HSM vendor provides a signed certificate confirming key residency. Acceptable for T2.

**`self-attestation`**: TA self-declares HSM usage. Acceptable only as a transitional measure during the first 12 months after TSAI 1.1 publication. After that period, T2/T3 TAs MUST provide `independent-audit` or `vendor-attestation`.

### 7.8.6 Normative Requirements

**Trust Authorities issuing T2/T3 credentials:**
- MUST publish an HSM attestation document at `/.well-known/tsai-ta-hsm-attestation`
- Attestation MUST be signed by the TA's current signing key
- Attestation MUST be updated at least annually
- `auditDate` MUST be within the last 18 months

**Trust Authorities issuing T0/T1 credentials only:**
- MAY publish an HSM attestation document
- HSM usage remains REQUIRED but attestation publication is OPTIONAL

**Service Providers:**
- Service Providers verifying T2/T3 credentials SHOULD check the TA's HSM attestation
- Service Providers MAY reject T2/T3 credentials from TAs without a current HSM attestation
- Service Providers MUST NOT require specific HSM vendors or certification levels in the protocol (vendor choice is TA policy)

### 7.8.7 Limitations

Attestation proves HSM usage at audit time, not continuously. A TA could extract keys after an audit. Short credential lifetimes and operational transparency (Section 7.7) provide complementary detection. Independent audits are the strongest form but impose cost; the tiered attestation types balance assurance with practicality.

---

## Future Work (Phase 1+)

Revocation support will be added in Phase 1 for T2/T3 credentials:
- `/credentials/revoke` endpoint for operator-initiated revocation
- `/status/{listId}` endpoint for W3C BitstringStatusList credentials
- Status list references in credential responses (`statusListUrl`, `statusListIndex`)
- Real-time verification APIs for high-value operations

See `concept/TODO.md` for detailed Phase 1 tasks.
