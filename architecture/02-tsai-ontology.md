<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Ontology

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## Overview

TSAI uses W3C Verifiable Credentials with JSON-LD to formally model the relationship between operators (legal entities) and agents (LLM-driven programs). This document defines the TSAI ontology.

**Namespace:** `https://tsai.example.org/credentials/v1#`

---

## Classes

### Operator
Legal entity (company, organization, or individual) that owns and operates agents.

**Properties:**
- `id` (DID) - Operator's decentralized identifier
- `name` (string) - Legal entity name
- `jurisdiction` (string) - ISO 3166-1 alpha-2 country code
- `kycLevel` (string) - KYC verification level: `basic`, `enhanced`, `institutional`
- `verifiedDomain` (string, optional) - DNS-verified domain
- `domainAge` (integer, optional) - Days since domain registration
- `certifications` (array, optional) - Industry certifications
- `organizationalAffiliation` (string, optional) - Network membership
- `economicStake` (object, optional) - Collateral and insurance

### Agent
LLM-driven program with a DID that makes requests on behalf of an operator.

**Properties:**
- `id` (DID) - Agent's decentralized identifier
- `operatedBy` (Operator) - The operator responsible for this agent
- `reputation` (object, optional) - Behavioral track record
- `authorization` (object, optional) - Authorized operations and constraints

---

## Properties

### operatedBy
Relates an Agent to its Operator.

**Domain:** Agent  
**Range:** Operator  
**Cardinality:** Exactly one (each agent has exactly one operator)

---

## Signal Attribution

### Operator-Level Signals
Properties of the Operator class that apply to all agents operated by that entity:
- Legal identity (name, jurisdiction, KYC)
- Certifications
- Economic stake (collateral, insurance)
- Domain verification
- Organizational affiliation

### Agent-Level Signals
Properties of the Agent class that describe the specific agent's behavioral track record:
- Reputation (score, interaction count, success rate, time in operation)
- Payment reliability
- Complaint rate
- Behavioral consistency
- Authorization constraints (may be operator-level or agent-level depending on use case)

---

## Example Structure

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://tsai.example.org/credentials/v1"
  ],
  "credentialSubject": {
    "id": "did:web:acme-corp.com:agents:shopping-bot",
    "type": "Agent",
    "operatedBy": {
      "id": "did:web:acme-corp.com",
      "type": "Operator",
      "name": "Acme Corporation GmbH",
      "jurisdiction": "DE",
      "kycLevel": "enhanced",
      "certifications": ["ISO27001", "SOC2"]
    },
    "reputation": {
      "interactionCount": 1247,
      "successRate": 0.94
    }
  }
}
```

---

## Design Rationale

**Why operators have DIDs:**
Operators have DIDs to enable verifiable identity, support discovery of all agents from an operator, provide a natural fit with semantic web (proper URI), and ensure that operator DID compromise affects all their agents (accountability feature).

**Why DID resolution is optional:**
Credentials contain all necessary information for verification. Resolution enables discovery and updates but isn't required. This works offline while supporting online enhancements.

**Why one operator per agent:**
Each agent has exactly one operator for clear accountability (one party operationally responsible), which simplifies the trust model. Joint ventures designate one party as operator.

---

## References

- W3C Verifiable Credentials Data Model 2.0
- W3C Decentralized Identifiers (DIDs)
- JSON-LD 1.1
- TSAI Credential Format (architecture/03-credential-format.md)
