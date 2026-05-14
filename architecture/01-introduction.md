<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Introduction

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 1.1 Scope

This document specifies the Trust Signals for Agentic Interactions (TSAI), a trust signaling protocol that enables Trust Authorities to issue verifiable credentials containing trust signals about Agents, Agents to present credentials to prove legitimacy, and Service Providers to verify credential authenticity and interpret trust signals.

TSAI defines credential format and structure (W3C Verifiable Credentials), trust signal semantics (what claims mean), verification mechanisms (how to check authenticity), and Trust Authority APIs (credential issuance, revocation, verification).

TSAI does not define how Service Providers use trust signals to make access decisions (left to each Service Provider's policy), how Trust Authorities evaluate Agents (TA methodology), or how Agents implement their functionality (Agent implementation).

**Core principle:** TSAI signals, Service Providers decide.

---

## 1.2 Conformance

This specification uses RFC 2119 terminology:

- **MUST** / **REQUIRED** / **SHALL**: Absolute requirement
- **MUST NOT** / **SHALL NOT**: Absolute prohibition
- **SHOULD** / **RECOMMENDED**: Strong recommendation (may ignore with valid reason)
- **SHOULD NOT** / **NOT RECOMMENDED**: Strong discouragement (may do with valid reason)
- **MAY** / **OPTIONAL**: Truly optional

### Conformance Classes

**Conforming Trust Authority:**
- MUST issue credentials conforming to Section 2 (Credential Format)
- MUST implement APIs specified in Section 4 (TA APIs)
- MUST comply with Section 5 (Security and Privacy)

**Conforming Agent:**
- MUST present credentials conforming to Section 3 (Verification)
- MUST comply with Section 5 (Security and Privacy)

**Conforming Service Provider:**
- MUST verify credentials according to Section 3 (Verification)
- MUST comply with Section 5 (Security and Privacy)
- MAY choose which Trust Authorities to trust (a Service Provider policy decision)
- MAY choose how to interpret trust signals (a Service Provider policy decision)

---

## 1.3 Terminology

**Agent:** Software entity that performs actions on behalf of a User or organization. Identified by a DID.

**Credential:** W3C Verifiable Credential issued by a Trust Authority, containing trust signals about an Agent.

**Trust Authority (TA):** Professional entity that evaluates Agents and issues signed credentials. Identified by a `did:web` DID.

**Service Provider:** Party that receives a credential from an Agent, verifies it, and decides whether to grant access. A Service Provider may be a merchant system, an API, an MCP server, an A2A Service Agent, infrastructure middleware such as a CDN or edge gateway, or another Agent acting in a service role. In W3C Verifiable Credentials terms, the Service Provider fulfills the Verifier role. In the W3C AI Agent Protocol, a Service Agent receiving a TSAI credential is acting as a TSAI Service Provider. Earlier drafts of this specification used the term "Platform" (see ADR 012).

**Trust Signal:** Claim in a credential that conveys information about Agent trustworthiness (e.g., identity, reputation, economic stake).

**Tier:** Trust level (T0, T1, T2, T3) indicating the combination of trust signals and verification rigor required.

**Verifiable Presentation (VP):** W3C Verifiable Presentation containing one or more credentials, signed by the Agent to prove possession.

**DID (Decentralized Identifier):** W3C Decentralized Identifier used to identify TAs and Agents.

**Revocation:** Process of invalidating a credential before its expiry time.

**Challenge-Response:** Protocol where a Service Provider sends a random nonce and the Agent signs it to prove freshness and prevent replay attacks.

### Conventions

TSAI actor names — **Trust Authority**, **Operator**, **Agent**, **User**, **Service Provider** — are written in Title case when they name the protocol role. Common English uses of the same words remain lowercase.

The **Service Provider** is the actor; the **verifier** (lowercase) is the software component inside a Service Provider's stack, or provided to it by infrastructure, that performs credential verification.

Compounds combining a multi-word proper noun with a qualifier are reworded rather than hyphenated. This specification uses "across Service Providers" rather than "cross-Service-Provider", "at the Service Provider layer" rather than "Service-Provider-level", and "specific to each Service Provider" rather than "Service-Provider-specific".

---

## 1.4 Document Structure

- **Section 2: TSAI Ontology** - JSON-LD ontology defining Agent and Operator classes with operatedBy relationship
- **Section 3: Credential Format** - Normative specification of credential structure, claims, and schemas for each tier
- **Section 4: Verification** - Normative algorithms for verifying credentials and presentations
- **Section 5: Protocol Integration** - Integration patterns with MCP, A2A, W3C AI Agent Protocol, and HTTP-based protocols
- **Section 6: Security and Privacy** - Normative security and privacy requirements
- **Section 7: References** - Normative and informative references

---

## 1.5 Normative References

- **[VC-DATA-MODEL-2.0]** W3C Verifiable Credentials Data Model 2.0, W3C Recommendation, May 2025
- **[VC-JOSE-COSE]** W3C Securing Verifiable Credentials using JOSE and COSE, W3C Recommendation, May 2025
- **[DID-CORE]** W3C Decentralized Identifiers (DIDs) v1.0, W3C Recommendation, July 2022
- **[RFC2119]** Key words for use in RFCs to Indicate Requirement Levels, IETF RFC 2119
- **[RFC8259]** The JavaScript Object Notation (JSON) Data Interchange Format, IETF RFC 8259
- **[RFC7519]** JSON Web Token (JWT), IETF RFC 7519
- **[RFC7515]** JSON Web Signature (JWS), IETF RFC 7515

---

## 1.6 Informative References

- **[TSAI-CONCEPT]** TSAI High-Level Concept, TSAI Working Group, January 2026
- **[TSAI-ADR-002]** ADR 002: Centralized Trust Authorities, TSAI Working Group, January 2026
- **[TSAI-ADR-003]** ADR 003: W3C Verifiable Credentials, TSAI Working Group, January 2026
- **[TSAI-ADR-004]** ADR 004: Tiered Trust Model, TSAI Working Group, January 2026
- **[TSAI-ADR-005]** ADR 005: Signaling vs. Enforcement, TSAI Working Group, January 2026
- **[TSAI-ADR-006]** ADR 006: DID Methods, TSAI Working Group, January 2026
- **[TSAI-ADR-007]** ADR 007: Short-Lived Credentials, TSAI Working Group, January 2026
- **[TSAI-ADR-012]** ADR 012: Service Provider Terminology, TSAI Working Group, April 2026

---

## 1.7 Design Rationale

This specification is informed by architectural decisions documented in TSAI Architecture Decision Records (ADRs). Centralized Trust Authorities (ADR 002) provide performance, reliability, and legal accountability. W3C Verifiable Credentials (ADR 003) enable interoperability and future extensibility. The tiered trust model (ADR 004) balances performance and security for different risk levels across four tiers (T0-T3). As a signaling protocol (ADR 005), TSAI defines signals while Service Providers decide how to use them. DID methods (ADR 006) use `did:web` for TAs and `did:key` or `did:web` for Agents. Short-lived credentials (ADR 007) with 2-4 hour expiry reduce revocation dependency for low-stakes scenarios. The "Service Provider" terminology and associated conventions are defined in ADR 012.

See ADRs for detailed rationale and alternatives considered.
