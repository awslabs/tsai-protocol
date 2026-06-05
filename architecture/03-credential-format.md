<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Credential Format

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 2.1 Overview

TSAI credentials are W3C Verifiable Credentials encoded as VC-JWT (JSON Web Tokens). This section specifies the credential structure, claim semantics, and schemas for each trust tier.

T0 and T1 are normative — they define the credential format and verification protocol for TSAI 1.0. T2 and T3 are informative drafts — they describe proposed credential formats whose verification protocols are deferred to TSAI 1.1 (see Sections 2.7 and 2.8).

---

## 2.2 Base Credential Structure

All TSAI credentials MUST conform to the W3C Verifiable Credentials Data Model 2.0 and use VC-JWT encoding as specified in W3C VC-JOSE-COSE.

### 2.2.1 VC-JWT Structure

A TSAI credential is a JWT with the following structure:

```
<header>.<payload>.<signature>
```

**JWT Header:**
```json
{
  "alg": "ES256",
  "typ": "JWT",
  "kid": "<TA-DID>#<key-id>"
}
```

- `alg` MUST be a supported signature algorithm (ES256, ES384, ES512, EdDSA)
- `typ` MUST be "JWT"
- `kid` MUST reference the TA's signing key in their DID document

**JWT Payload:**

The payload contains the W3C VC structure with TSAI-specific claims.

---

## 2.3 Common Claims

The following claims are REQUIRED in all TSAI credentials:

### 2.3.1 Standard VC Claims

**`@context`** (array of strings, REQUIRED)
- MUST include `https://www.w3.org/ns/credentials/v2`
- MUST include `https://tsai.example.org/credentials/v1` (TSAI context)

**`type`** (array of strings, REQUIRED)
- MUST include `VerifiableCredential`
- MUST include `TSAICredential`
- MUST include tier-specific type (e.g., `TSAICredentialT0`)

**`issuer`** (string or object, REQUIRED)
- MUST be the TA's DID (e.g., `did:web:trust-authority.example:tsai:ta`)

**`validFrom`** (string, REQUIRED)
- ISO 8601 datetime when credential was issued
- Format: `YYYY-MM-DDTHH:MM:SSZ`

**`validUntil`** (string, REQUIRED)
- ISO 8601 datetime when credential expires
- MUST be after `validFrom`
- Expiry duration by tier:
  - T0/T1: 2-4 hours
  - T2: 1 hour
  - T3: 30 minutes

**`credentialSubject`** (object, REQUIRED)
- Contains claims about the agent
- MUST include `id` field with agent's DID

**`credentialStatus`** (object, OPTIONAL for T0/T1, REQUIRED for T2/T3)
- Revocation status information
- MUST use W3C BitstringStatusList format
- See Section 2.9 for details

---

### 2.3.2 TSAI-Specific Claims

The following claims are defined in the TSAI context and appear within `credentialSubject`:

**`id`** (string, REQUIRED)
- Agent's DID
- Supported DID methods:
  - `did:key:...` - Ephemeral agents, no infrastructure (suitable for T0)
  - `did:web:...` - Domain-linked agents, supports key rotation (suitable for T1+)
  - `did:wba:...` - Web-based agent DIDs per W3C AI Agent Protocol (suitable for T0+)
- All methods are W3C DID-compliant and interoperable
- Reputation-bearing credentials (T1+) SHOULD use `did:web` or `did:wba`. `did:key` agents cannot rotate keys or revoke the DID itself — if the private key is compromised, reputation accumulated against that DID is lost.

**`type`** (string, REQUIRED)
- MUST be `Agent`
- Enables semantic reasoning about credential subject

**`tsaiVersion`** (string, REQUIRED)
- TSAI protocol version
- Current version: `1.0`

**`tsaiTier`** (string, REQUIRED)
- Trust tier: `T0`, `T1`, `T2`, or `T3`

**`operatedBy`** (object, REQUIRED)
- Operator (legal entity) responsible for this agent
- Uses TSAI ontology to formally model operator/agent relationship
- Fields:
  - `id` (string, REQUIRED): Operator's DID (format: `did:web:...`)
  - `type` (string, REQUIRED): MUST be `Operator`
  - `name` (string, REQUIRED): Legal entity name
  - `jurisdiction` (string, REQUIRED): ISO 3166-1 alpha-2 country code
  - `kycLevel` (string, REQUIRED): `basic`, `enhanced`, or `institutional`
  - Additional operator-level signals nested here (see Section 2.4)

---

## 2.4 Claim Semantics

This section defines the precise meaning of each claim and specifies whether it applies to the operator (legal entity) or the agent (specific program).

Claims nested within `operatedBy` are operator-level — shared across all agents from that operator. Claims at the top level of `credentialSubject` are agent-level — specific to this agent DID.

### 2.4.1 Identity Claims (Operator-Level)

These claims describe the legal entity operating the agent. They are nested within the `operatedBy` object.

**`operatedBy.id`**
- Operator's DID
- Format: `did:web:...` (REQUIRED for operators)
- Enables operator to have verifiable identity
- Supports discovery of all agents from an operator
- Example: `did:web:acme-corp.com`

**`operatedBy.type`**
- MUST be `Operator`
- Enables semantic reasoning about operator entity

**`operatedBy.name`**
- Legal name of the entity operating the agent
- MUST be verified by TA through KYC process
- Example: `Acme Corporation GmbH`

**`operatedBy.jurisdiction`**
- Country where operator is legally registered
- ISO 3166-1 alpha-2 code (e.g., `DE`, `US`, `GB`)
- Determines applicable legal framework

**`operatedBy.kycLevel`**
- Depth of identity verification performed by TA
- Values:
  - `basic`: Name, address, business registration verified
  - `enhanced`: Basic + beneficial ownership, financial checks
  - `institutional`: Enhanced + regulatory compliance, audits

**`operatedBy.verifiedDomain`** (string, OPTIONAL)
- Domain name controlled by operator
- MUST be verified by TA through DNS challenge or email verification
- Example: `acme-corp.com`
- Enables did:web usage for agents
- Provides web presence verification

**`operatedBy.domainAge`** (integer, days, OPTIONAL)
- Number of days since domain was first registered
- Retrieved from WHOIS data
- Older domains indicate more established presence
- Example: `3650` (10 years)

---

### 2.4.2 Reputation Claims (T1+)

These claims describe the behavioral track record of a specific agent, tracked per agent DID. The component signals (`interactionCount`, `successRate`, `timeInOperation`) have standardized semantics and are comparable across TAs. The composite `reputation.score` is TA-specific and not comparable across TAs.

**`reputation.score`** (number, 0-100, OPTIONAL)
- Aggregated trust score calculated by TA for this specific agent
- Higher is better
- 0 = no reputation data, 100 = excellent reputation
- TA-specific: methodology varies by TA, scores are not comparable across TAs
- Service Providers SHOULD use the component signals below for cross-TA comparisons

**`reputation.interactionCount`** (integer, ≥0)
- Total number of interactions evaluated by TA for this Agent
- Used to assess confidence in component signals

**`reputation.successRate`** (number, 0-1)
- Percentage of successful interactions for this agent
- 1.0 = 100% success rate

**`reputation.timeInOperation`** (integer, days, OPTIONAL)
- Number of days this agent has been operational
- Measured from first TA evaluation of this agent DID

**`reputation.confidenceLevel`** (string, OPTIONAL)
- Statistical confidence in component signals for this agent
- Values: `low` (<100 interactions), `medium` (100-1000), `high` (>1000)
- Derivable from `interactionCount`; included for convenience

**`operatedBy.certifications`** (array of strings, OPTIONAL, T1+)
- Industry certifications held by operator
- Examples: `["ISO27001", "SOC2", "FedRAMP", "PCI-DSS", "HIPAA", "GDPR"]`
- MUST be verified by TA through certificate validation or registry lookup
- Easy to verify, high signal value for operational standards
- Shared across all agents from this operator
- Nested within `operatedBy` object

**`operatedBy.organizationalAffiliation`** (string, OPTIONAL, T1+)
- Parent organization or network membership
- Example: `European AI Alliance`, `AWS Partner Network`
- Provides additional context about operator's ecosystem
- MUST be verified by TA through membership confirmation
- Shared across all agents from this operator
- Nested within `operatedBy` object

---

### 2.4.3 Economic Stake Claims (T2+)

These claims describe the operator's economic accountability. They are nested within the `operatedBy.economicStake` object.

**`operatedBy.economicStake.collateralAmount`** (object)
- Funds held in escrow by TA or third party
- Fields:
  - `value` (number, REQUIRED): Amount
  - `currency` (string, REQUIRED): ISO 4217 currency code (e.g., `EUR`, `USD`)

**`operatedBy.economicStake.insuranceCoverage`** (object, OPTIONAL)
- Third-party liability insurance
- Fields:
  - `value` (number, REQUIRED): Coverage amount
  - `currency` (string, REQUIRED): ISO 4217 currency code
  - `provider` (string, REQUIRED): Insurance provider name

**`economicStake.paymentReliability`** (number, 0-1)
- Historical payment success rate for this agent
- 1.0 = 100% reliable payments

**`economicStake.complaintRate`** (number, 0-1, OPTIONAL)
- Frequency of reported issues or complaints for this agent
- 0.0 = no complaints, 1.0 = all interactions resulted in complaints
- Lower is better
- MUST be based on verifiable complaint data
- Requires monitoring infrastructure

**`economicStake.behavioralConsistency`** (number, 0-1, OPTIONAL)
- Stability of performance over time for this agent
- Measured as inverse of variance in success rate
- 1.0 = perfectly consistent, 0.0 = highly erratic
- Higher indicates more predictable behavior
- Requires analytics infrastructure

---

### 2.4.4 Authorization Claims (T3) (TBD: Operator or Agent-Level)

**Note:** Whether authorization constraints apply at operator-level (all agents from this operator) or agent-level (specific to this agent program) is an open design question. Current specification assumes they can be either, depending on use case.

**`authorization.constraintProfile`** (string)
- Reference to standard constraint profile
- Format: `<domain>-<profile>-<tier>` (e.g., `ecommerce-standard-t3`)
- Profile definitions maintained in separate registry

**`authorization.authorizedOperations`** (array of strings)
- Explicit list of allowed operations
- Examples: `["browse", "search", "add_to_cart", "checkout"]`

**`authorization.valueLimits`** (object)
- Maximum transaction values
- Fields:
  - `perTransaction` (object): `{value, currency}`
  - `perDay` (object): `{value, currency}`

**`authorization.rateLimits`** (object)
- Request rate limits
- Fields:
  - `requestsPerMinute` (integer)
  - `requestsPerHour` (integer)

**`authorization.domainRestrictions`** (array of strings, OPTIONAL)
- Domains where agent is authorized to operate
- Examples: `["example.com", "*.example.com"]`

**`authorization.humanInLoop`** (boolean, REQUIRED for T3)
- Whether human oversight is required for agent actions
- `true` = human must approve actions
- `false` = agent operates autonomously
- Critical for high-stakes operations

**`authorization.authorizationChain`** (array of objects, OPTIONAL)
- Chain of authorizations leading to this agent
- Each entry contains:
  - `authorizer` (string): DID of authorizing entity
  - `scope` (string): What was authorized
  - `timestamp` (string): ISO 8601 datetime when authorization was granted
- Example: User → Organization → Agent
- Provides audit trail for delegated authority

**`operatedBy.auditReports`** (array of objects, OPTIONAL)
- Third-party security audit reports
- Each entry contains:
  - `auditor` (string): Name of auditing organization
  - `reportDate` (string): ISO 8601 date of audit
  - `reportUrl` (string): URL to full audit report
  - `scope` (string): What was audited (e.g., "security", "compliance")
- Provides independent verification of operator practices
- Nested within `operatedBy` object

---

### 2.4.5 TA-Specific Signals (Extension Mechanism)

TAs MAY include additional trust signals beyond the standardized claims defined in Sections 2.4.1–2.4.4. These signals appear as additional properties in `credentialSubject`, namespaced by the TA's fully qualified domain name.

**Naming Convention:**

```
<ta-fqdn>:<signalName>
```

- `<ta-fqdn>`: The TA's fully qualified domain name (e.g., `trust-authority.example.com`)
- `:` colon delimiter
- `<signalName>`: camelCase signal name

**Examples:**
- `trust-authority.example.com:behavioralRiskIndex`
- `trust-authority.example.com:llmSafetyScore`
- `ta.otherprovider.io:industryComplianceLevel`

**Rules:**

- TA-specific signals MUST use the TA's own FQDN as namespace prefix
- TAs MUST NOT use another TA's namespace
- Signal values MAY be any JSON-compatible type (string, number, boolean, object, array)
- TAs SHOULD document their custom signals at `/.well-known/tsai-ta-signals` or equivalent discoverable endpoint
- Service Providers MUST ignore TA-specific signals they do not recognize (forward compatibility)
- Service Providers MAY use TA-specific signals in trust decisions when they understand the issuing TA's signal semantics
- TA-specific signals MUST NOT duplicate or contradict standardized claims

**Example in credential:**

```json
{
  "credentialSubject": {
    "id": "did:web:acme-corp.com:agents:agent123",
    "type": "Agent",
    "tsaiVersion": "1.0",
    "tsaiTier": "T1",
    "operatedBy": { "..." : "..." },
    "reputation": {
      "interactionCount": 1247,
      "successRate": 0.94,
      "timeInOperation": 180,
      "confidenceLevel": "high"
    },
    "trust-authority.example.com:behavioralRiskIndex": 0.12,
    "trust-authority.example.com:llmSafetyScore": 87
  }
}
```

**Rationale:** TAs compete on evaluation methodology. Proprietary signals enable differentiation without fragmenting the interoperable baseline. The FQDN namespace prevents collisions and makes signal provenance self-evident. Service Providers that trust a specific TA can leverage its custom signals; others safely ignore them.

---

## 2.5 Tier 0 (T0): Basic Identity

**Purpose:** Distinguish verified agents from random bots

**Use Cases:** Browsing, search, public APIs, low-risk interactions

**Required Claims:**
- All common claims (Section 2.3)
- Identity claims (Section 2.4.1): name, jurisdiction, KYC level

**Optional Claims:**
- Verified domain
- Domain age

**Expiry:** 2-4 hours

**Revocation:** Optional

### 2.5.1 T0 Example

**JSON Schema:** [`schemas/tsai-credential-t0.schema.json`](schemas/tsai-credential-t0.schema.json)

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://tsai.example.org/credentials/v1"
  ],
  "type": ["VerifiableCredential", "TSAICredential", "TSAICredentialT0"],
  "issuer": "did:web:trust-authority.example:tsai:ta",
  "validFrom": "2026-01-23T10:00:00Z",
  "validUntil": "2026-01-23T14:00:00Z",
  "credentialSubject": {
    "id": "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH",
    "type": "Agent",
    "tsaiVersion": "1.0",
    "tsaiTier": "T0",
    "operatedBy": {
      "id": "did:web:acme-corp.com",
      "type": "Operator",
      "name": "Acme Corporation GmbH",
      "jurisdiction": "DE",
      "kycLevel": "basic",
      "verifiedDomain": "acme-corp.com",
      "domainAge": 3650
    }
  }
}
```

---

## 2.6 Tier 1 (T1): Identity + Reputation

**Purpose:** Enable risk-calibrated decisions based on behavioral history and verifiable credentials

**Use Cases:** Content creation, moderate-value API calls, user interactions

**Required Claims:**
- All T0 claims
- Reputation claims (Section 2.4.2): interactionCount, successRate

**Optional Claims:**
- score (TA-specific composite, not comparable across TAs)
- timeInOperation, confidenceLevel
- Industry certifications
- Organizational affiliation
- TA-specific signals (Section 2.4.5)

**Expiry:** 2-4 hours

**Revocation:** Recommended but optional

### 2.6.1 T1 Example

**JSON Schema:** [`schemas/tsai-credential-t1.schema.json`](schemas/tsai-credential-t1.schema.json)

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://tsai.example.org/credentials/v1"
  ],
  "type": ["VerifiableCredential", "TSAICredential", "TSAICredentialT1"],
  "issuer": "did:web:trust-authority.example:tsai:ta",
  "validFrom": "2026-01-23T10:00:00Z",
  "validUntil": "2026-01-23T14:00:00Z",
  "credentialSubject": {
    "id": "did:web:acme-corp.com:agents:agent123",
    "type": "Agent",
    "tsaiVersion": "1.0",
    "tsaiTier": "T1",
    "operatedBy": {
      "id": "did:web:acme-corp.com",
      "type": "Operator",
      "name": "Acme Corporation GmbH",
      "jurisdiction": "DE",
      "kycLevel": "enhanced",
      "verifiedDomain": "acme-corp.com",
      "domainAge": 3650,
      "certifications": ["ISO27001", "SOC2", "GDPR"],
      "organizationalAffiliation": "European AI Alliance"
    },
    "reputation": {
      "interactionCount": 1247,
      "successRate": 0.94,
      "timeInOperation": 180,
      "confidenceLevel": "high"
    },
    "trust-authority.example.com:behavioralRiskIndex": 0.12
  }
}
```

---

## 2.7 Tier 2 (T2): Identity + Reputation + Economic Stake

> **Status: Informative (Draft) — targeted for TSAI 1.1 (Phase 1)**
>
> This section describes the proposed T2 credential format. The verification protocol for T2 credentials (challenge-response, real-time revocation) is under development. Implementers SHOULD NOT issue or verify T2 credentials until the verification protocol is specified.

**Purpose:** Provide accountability through economic stake for transactions

**Use Cases:** Transactions, payments, sensitive operations

**Required Claims:**
- All T1 claims
- Economic stake claims (Section 2.4.3): collateral, payment reliability
- Credential status (revocation)

**Optional Claims:**
- Insurance coverage
- Complaint rate
- Behavioral consistency

**Expiry:** 1 hour

**Revocation:** Required

### 2.7.1 T2 Example

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://tsai.example.org/credentials/v1"
  ],
  "type": ["VerifiableCredential", "TSAICredential", "TSAICredentialT2"],
  "issuer": "did:web:trust-authority.example:tsai:ta",
  "validFrom": "2026-01-23T10:00:00Z",
  "validUntil": "2026-01-23T11:00:00Z",
  "credentialSubject": {
    "id": "did:web:acme-corp.com:agents:agent123",
    "type": "Agent",
    "tsaiVersion": "1.0",
    "tsaiTier": "T2",
    "operatedBy": {
      "id": "did:web:acme-corp.com",
      "type": "Operator",
      "name": "Acme Corporation GmbH",
      "jurisdiction": "DE",
      "kycLevel": "institutional",
      "verifiedDomain": "acme-corp.com",
      "domainAge": 3650,
      "certifications": ["ISO27001", "SOC2", "PCI-DSS", "GDPR"],
      "economicStake": {
        "collateralAmount": {
          "value": 50000,
          "currency": "EUR"
        },
        "insuranceCoverage": {
          "value": 1000000,
          "currency": "EUR",
          "provider": "Allianz SE"
        }
      }
    },
    "reputation": {
      "interactionCount": 5420,
      "successRate": 0.97,
      "timeInOperation": 365,
      "confidenceLevel": "high"
    },
    "economicStake": {
      "paymentReliability": 0.99,
      "complaintRate": 0.02,
      "behavioralConsistency": 0.95
    },
    "trust-authority.example.com:behavioralRiskIndex": 0.05
  },
  "credentialStatus": {
    "id": "https://trust-authority.example/tsai/status/1#94567",
    "type": "BitstringStatusListEntry",
    "statusPurpose": "revocation",
    "statusListIndex": "94567",
    "statusListCredential": "https://trust-authority.example/tsai/status/1"
  }
}
```

---

## 2.8 Tier 3 (T3): Full Trust Signals + Constraints

> **Status: Informative (Draft) — targeted for TSAI 1.1 (Phase 1)**
>
> This section describes the proposed T3 credential format. The verification protocol for T3 credentials (challenge-response, constraint enforcement, real-time revocation) is under development. The scope of authorization claims (operator-level vs agent-level) is also unresolved (see Section 2.4.4). Implementers SHOULD NOT issue or verify T3 credentials until the verification protocol is specified.

**Purpose:** Maximum assurance for high-value and regulated operations

**Use Cases:** High-value transactions, regulated operations, critical systems

**Required Claims:**
- All T2 claims
- Authorization claims (Section 2.4.4): constraint profile, authorized operations, value limits, rate limits, human-in-loop indicator

**Optional Claims:**
- Domain restrictions
- Authorization chain
- Audit reports

**Expiry:** 30 minutes

**Revocation:** Required (real-time verification)

### 2.8.1 T3 Example

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://tsai.example.org/credentials/v1"
  ],
  "type": ["VerifiableCredential", "TSAICredential", "TSAICredentialT3"],
  "issuer": "did:web:trust-authority.example:tsai:ta",
  "validFrom": "2026-01-23T10:00:00Z",
  "validUntil": "2026-01-23T10:30:00Z",
  "credentialSubject": {
    "id": "did:web:acme-corp.com:agents:agent123",
    "type": "Agent",
    "tsaiVersion": "1.0",
    "tsaiTier": "T3",
    "operatedBy": {
      "id": "did:web:acme-corp.com",
      "type": "Operator",
      "name": "Acme Corporation GmbH",
      "jurisdiction": "DE",
      "kycLevel": "institutional",
      "verifiedDomain": "acme-corp.com",
      "domainAge": 3650,
      "certifications": ["ISO27001", "SOC2", "PCI-DSS", "FedRAMP", "GDPR"],
      "economicStake": {
        "collateralAmount": {
          "value": 100000,
          "currency": "EUR"
        },
        "insuranceCoverage": {
          "value": 5000000,
          "currency": "EUR",
          "provider": "Allianz SE"
        }
      },
      "auditReports": [
        {
          "auditor": "TÜV SÜD",
          "reportDate": "2025-12-15",
          "reportUrl": "https://acme-corp.com/audits/2025-q4-security.pdf",
          "scope": "security"
        }
      ]
    },
    "reputation": {
      "interactionCount": 8932,
      "successRate": 0.98,
      "timeInOperation": 540,
      "confidenceLevel": "high"
    },
    "economicStake": {
      "paymentReliability": 0.995,
      "complaintRate": 0.01,
      "behavioralConsistency": 0.97
    },
    "authorization": {
      "constraintProfile": "ecommerce-standard-t3",
      "authorizedOperations": [
        "browse",
        "search",
        "add_to_cart",
        "checkout",
        "payment"
      ],
      "valueLimits": {
        "perTransaction": {
          "value": 5000,
          "currency": "EUR"
        },
        "perDay": {
          "value": 50000,
          "currency": "EUR"
        }
      },
      "rateLimits": {
        "requestsPerMinute": 60,
        "requestsPerHour": 1000
      },
      "domainRestrictions": [
        "shop.example.com",
        "api.example.com"
      ],
      "humanInLoop": false,
      "authorizationChain": [
        {
          "authorizer": "did:web:acme-corp.com:ceo",
          "scope": "ecommerce operations up to 50k EUR/day",
          "timestamp": "2026-01-20T09:00:00Z"
        }
      ]
    }
  },
  "credentialStatus": {
    "id": "https://trust-authority.example/tsai/status/1#94568",
    "type": "BitstringStatusListEntry",
    "statusPurpose": "revocation",
    "statusListIndex": "94568",
    "statusListCredential": "https://trust-authority.example/tsai/status/1"
  }
}
```

---

## 2.9 Credential Status (Revocation)

TSAI uses W3C BitstringStatusList for revocation.

### 2.9.1 BitstringStatusList Structure

**`credentialStatus`** (object)
- `id` (string, REQUIRED): URL to specific bit in status list
- `type` (string, REQUIRED): MUST be `BitstringStatusListEntry`
- `statusPurpose` (string, REQUIRED): MUST be `revocation`
- `statusListIndex` (string, REQUIRED): Index of this credential's bit
- `statusListCredential` (string, REQUIRED): URL to status list credential

### 2.9.2 Status List Credential

TAs MUST publish a BitstringStatusList credential at the URL specified in `statusListCredential`.

The status list credential contains a compressed bitstring where:
- Bit = 0: Credential is valid
- Bit = 1: Credential is revoked

Service Providers check revocation by:
1. Fetching the status list credential
2. Decompressing the bitstring
3. Checking the bit at `statusListIndex`
4. If bit = 1, credential is revoked

See W3C BitstringStatusList specification for full details.

---

## 2.10 Versioning

**`tsaiVersion`** indicates the TSAI protocol version.

**Current version:** `1.0`

**Version compatibility:**
- Service Providers MUST reject credentials with unknown `tsaiVersion`
- Minor version changes (e.g., 1.0 → 1.1) MUST be backward compatible
- Major version changes (e.g., 1.0 → 2.0) MAY break compatibility

**Version format:** `<major>.<minor>`

---

## 2.11 Normative Requirements Summary

**Trust Authorities MUST:**
- Issue credentials conforming to W3C VC Data Model 2.0
- Use VC-JWT encoding
- Include all required claims for the specified tier
- Sign credentials with key referenced in TA's DID document
- Set appropriate expiry times by tier
- Include credential status for T2/T3
- Maintain BitstringStatusList for revocation

**Agents MUST:**
- Present credentials that have not expired
- Present credentials for appropriate tier based on use case
- Prove possession via Verifiable Presentation (see Section 3)

**Service Providers MUST:**
- Verify credential signature against TA's DID document
- Check credential expiry
- Check revocation status for T2/T3
- Reject credentials with unknown `tsaiVersion`
