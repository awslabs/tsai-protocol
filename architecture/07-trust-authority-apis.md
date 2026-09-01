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

Beyond the API, a Trust Authority publishes its signing keys at `/.well-known/jwt-vc-issuer`, an agent-and-operator status list, and a signed operational report at `/.well-known/tsai-ta-status`. Its metadata endpoint advertises every `vct` it issues. The publisher that defines a `vct` publishes its immutable Type Metadata and JSON Schema: TSAI publishes the canonical artefacts, while a TA or community publishes the derived artefacts it defines. A first deployment issues identity and reputation signals; compliance and assurance follow as an authority builds those evaluations. There are no tiers.

---

## 7.2 Operator Enrolment and Authentication

An operator enrols with a Trust Authority out of band, through the identity verification (KYC, domain control, and the rest) that the credential's identity floor attests. Enrolment establishes an authenticated channel for that operator.

Issuance is authenticated as the enrolled operator: `POST /credentials/issue` and `POST /credentials/refresh` require the operator's credentials (the `operatorAuth` security scheme in the OpenAPI), and the proof of control (Section 7.3) then proves the binding key within that authenticated session. Without this, the API would grant a credential to any party that can generate a key pair; with it, a credential is tied to a real, verified operator. A Trust Authority MUST authenticate the operator at issuance and MUST bind the proof-of-control challenge to the requesting session. When an enrolled operator presents a new binding key, the Trust Authority associates the new key with the same operator and its evaluation.

---

## 7.3 Proof of Control

Before binding a credential to a key, the Trust Authority confirms the operator's agent controls that key. The agent requests a challenge, signs the UTF-8 bytes of the challenge value exactly as received with ES256 using the P-256 key to be bound, and returns the base64url-encoded 64-octet `R || S` signature, which the Trust Authority verifies against the public key it will place in `cnf`. Challenges are single-use and expire after five minutes; issuing and tracking them is the one piece of state the Trust Authority holds.

---

## 7.4 Holder-Directed Issuance and Honesty

**Holder-directed issuance.** An agent MAY include a `signals` filter in the issuance request, asking for a subset of the signals above the identity floor, such as identity plus compliance only, without naming the Service Provider it will present to (ADR 015). The Trust Authority returns the requested subset and stays blind to the destination; it learns the agent's pattern of requests, which is far weaker than learning its destinations. The filter narrows only the signals above the floor: a Trust Authority MUST include the identity floor (ADR 016) regardless of the filter, and, more generally, a filter can never remove a signal the applicable credential schema requires.

**Honesty.** The contents of a credential MUST match what the Trust Authority actually established. Specifically, a Trust Authority MUST verify the operator's identity before issuing, MUST perform the verification each signal claims — KYC for identity, DNS challenge or email for domain control, certificate validation or registry lookup for a certification, membership confirmation for an affiliation, and the basis it states for reputation — and MUST NOT populate a signal it has no basis to assert. A Trust Authority issuing custom signals MUST use a derived `vct`, publish metadata and a schema rooted in the canonical TSAI type, declare each custom signal's disclosure/display rule in `tsai_signal_metadata`, and define its fields in the schema. Every credential carries the identity floor (ADR 016), and reputation is `sd: never` (ADR 015).

---

## 7.5 Credential Lifecycle

An agent requests a credential when it needs one. The Trust Authority authenticates the operator, confirms proof of control, evaluates the agent, populates the signals it can honestly support, binds the credential to the key, and signs it. Credentials are short-lived: `exp` is 30 minutes after `iat`. An agent refreshes before expiry, at around 80 per cent of the lifetime.

The short lifetime carries most of the lifecycle. To stop an agent within the window, the Trust Authority stops re-issuing and publishes a block. A Trust Authority MUST publish an agent-and-operator status list (an IETF Token Status List) and reference it from the credential's `status` claim, so a Service Provider can depend on the mechanism existing; a credential MAY omit `status` only for an agent that requires unlinkability (Section 5.7). A Service Provider consults the list per its risk policy (Section 3.5).

---

## 7.6 Key Repudiation

An agent's binding key is its identity, so its compromise needs a path (Section 5.11). An operator MUST be able to repudiate a binding key at the Trust Authority through the authenticated channel. On repudiation the Trust Authority MUST refuse further issuance against that key and set the block for the affected agent, so that credentials already issued against the key stop verifying once a Service Provider consults status. Because the status list is keyed to the agent or operator rather than to the key, repudiating one key of an agent that uses a distinct key per Service Provider blocks the agent; an operator that needs finer granularity re-enrols the affected agent.

---

## 7.7 Security

Every Trust Authority API uses HTTPS with TLS 1.3, since a credential is a bearer of signed claims; HSTS prevents downgrade. The general transport floor elsewhere is TLS 1.2 (Section 5); the Trust Authority APIs hold the higher bar deliberately. Signing keys are EC/P-256 keys held in a hardware security module and rotated periodically, with old keys retained to verify credentials signed before the rotation. Rate limits curb abuse; the recommended starting points are ten issuances, twenty refreshes, and one hundred challenges per minute, which an authority tunes to its capacity.

---

## 7.8 Operational Requirements

A Trust Authority runs critical infrastructure, targets high availability, and completes issuance within around 500 ms at p95. It MUST log issuances and authentication failures for audit, keyed to the `cnf` JWK thumbprint and the agent `sub`, with metadata only and never credential contents or keys; logs MUST be tamper-evident and retained per the applicable regulatory requirement.

---

## 7.9 Normative Requirements

A Trust Authority MUST implement the OpenAPI specification, authenticate the operator at issuance, confirm ES256 proof of control of the P-256 binding key, and use HTTPS with TLS 1.3 and HSM-held EC/P-256 signing keys. It MUST issue only contents it has established (Section 7.4), include the identity floor in every credential, and support key repudiation (Section 7.6). It MUST publish its signing keys at `/.well-known/jwt-vc-issuer`, an agent-and-operator status list, and a signed operational report (Section 7.10), and MUST advertise every `vct` it issues through its metadata endpoint. A Trust Authority that defines a derived `vct` MUST publish and retain its immutable Type Metadata and integrity-protected JSON Schema; a Trust Authority using a type defined by TSAI or a community references that publisher's artefacts rather than republishing them. It MUST publish its evaluation criteria and disclose its data-collection, retention, and sharing practices (Section 7.10), and SHOULD minimise data collection to operational necessity.

---

## 7.10 Operational Transparency

### 7.10.1 Published criteria and data practices

A Trust Authority MUST publish its evaluation criteria, including how it maps its own reputation scale to the portable `band` (ADR 016), so a Service Provider can interpret a score and an operator can tell what standing it needs. It MUST disclose its data-collection, retention, and sharing practices.

### 7.10.2 Status report

A Trust Authority MUST serve a signed JSON document at `/.well-known/tsai-ta-status` over HTTPS, giving aggregate metrics without exposing individual credentials.

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
  "proof": { "alg": "ES256", "kid": "key-1" }
}
```

The report MUST be updated at least every 24 hours, MUST be signed by the current signing key, and MUST exclude any individual credential, agent, or operator identifier. Counts SHOULD be accurate within a stated tolerance. A Service Provider SHOULD fetch reports periodically and alert on anomalies (issuance spikes, no blocks over a long period, a stale key rotation or report), MAY use the data in its trust decisions, and the protocol mandates no threshold. Self-reported data can be falsified by a compromised authority, so the report detects systemic anomalies rather than individual fraud (ADR 011).

---

## 7.11 HSM Attestation

HSM key storage is required but the protocol cannot check it, so a Trust Authority publishes evidence at `/.well-known/tsai-ta-hsm-attestation` over HTTPS. This is an assurance a Service Provider MAY weigh; it is not gated to a tier.

```json
{
  "version": "1.0",
  "taIdentifier": "https://ta.example.com",
  "attestationType": "independent-audit",
  "auditor": "Example Audit Corp",
  "auditDate": "2026-01-15",
  "auditStandard": "SOC2-Type2",
  "scope": "Signing key generation, storage, and use for TSAI credential issuance",
  "reportUrl": "https://ta.example.com/audits/2026-hsm-attestation.pdf",
  "nextAuditDate": "2027-01-15",
  "proof": { "alg": "ES256", "kid": "key-1" }
}
```

Assurance levels: `independent-audit` (a third party verified HSM use, the strongest), `vendor-attestation` (the HSM vendor confirms residency), and `self-attestation` (the weakest, transitional only). The attestation MUST be signed by the current key and kept current within 18 months. A Service Provider MAY check and weigh it, and the protocol mandates no vendor or certification level. Attestation proves HSM use at audit time, not continuously; the short lifetime and the operational report are complementary detections.

---

## References

- OpenAPI Specification: [`openapi/trust-authority-api.yaml`](openapi/trust-authority-api.yaml)
- TSAI Credential Format (Section 2), TSAI Verification (Section 3)
- ADR 011 (transparency), ADR 015 (holder-directed issuance and Type Metadata), ADR 016 (identity floor and reputation)
- draft-ietf-oauth-sd-jwt-vc, draft-ietf-oauth-status-list
