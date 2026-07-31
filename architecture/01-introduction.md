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

This document specifies Trust Signals for Agentic Interactions (TSAI), a trust-signalling protocol. A Trust Authority issues a verifiable credential carrying trust signals about an agent, the agent presents the credential to prove legitimacy, and a Service Provider verifies it and reads the signals.

TSAI defines the credential format (SD-JWT VC), the meaning of the signals, the verification algorithm, and the Trust Authority APIs for issuance and status. It does not define how a Service Provider uses the signals to decide on access, how a Trust Authority evaluates an agent, or how an agent is implemented.

**Core principle:** TSAI signals, Service Providers decide.

---

## 1.2 Conformance

This specification uses RFC 2119 terminology: MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY.

**A conforming Trust Authority** MUST issue credentials conforming to Section 2, implement the APIs of Section 7, and comply with Section 5.

**A conforming agent** MUST present credentials that verify under Section 3, prove possession of the bound key, and comply with Section 5.

**A conforming Service Provider** MUST verify credentials per Section 3 and comply with Section 5. It MAY choose which Trust Authorities to trust and how to weigh the signals; both are its own policy.

---

## 1.3 Terminology

**Agent** — a software entity that acts on behalf of a user or organisation. Identified by the key its credential is bound to (`cnf`).

**Operator** — the legal entity that runs agents and is accountable for them.

**Credential** — an SD-JWT VC issued by a Trust Authority, carrying trust signals about an agent.

**Trust Authority (TA)** — a professional entity that evaluates agents and issues signed credentials. Identified by an HTTPS issuer, with keys at `/.well-known/jwt-vc-issuer`.

**Service Provider** — the party that receives a credential, verifies it, and decides on access. It may be a merchant system, an API, an MCP server, an A2A service agent, edge infrastructure, or another agent in a service role. In W3C Verifiable Credentials terms it is the Verifier. An earlier draft used the term Platform (ADR 012).

**Trust Signal** — a claim in a credential in one of four categories: identity, reputation, compliance, or assurance.

**Presentation** — a credential with a key-binding JWT appended, by which the agent proves possession of the bound key.

**Key-binding JWT** — the JWT the holder signs with the private key matching `cnf` to bind a presentation to itself and to one Service Provider.

**Block** — a Trust Authority marking an agent or operator no longer trusted, keyed to its identity in a status list.

**DID** — a W3C Decentralised Identifier. In TSAI, used only to identify referenced third parties (a certifier or a backer) by their own `did:web`.

### Conventions

TSAI actor names — Trust Authority, Operator, Agent, User, Service Provider — are Title case when naming the protocol role. The Service Provider is the actor; the verifier (lowercase) is the component that performs verification. Compounds are reworded rather than hyphenated: "across Service Providers", not "cross-Service-Provider".

---

## 1.4 Document Structure

- **Section 2: Credential Format** — the SD-JWT VC structure, the signal categories, and the schema.
- **Section 3: Verification** — the algorithm for verifying a presentation.
- **Section 4: Protocol Integration** — MCP, A2A, the W3C AI Agent Protocol, and HTTP.
- **Section 5: Security and Privacy** — the trust model, threats, and requirements.
- **Section 7: Trust Authority APIs** — issuance, refresh, status, and transparency.

The domain model behind the credential is in the ontology document; the references are collected in the references document.

---

## 1.5 Normative References

- **[SD-JWT-VC]** SD-JWT-based Verifiable Credentials, draft-ietf-oauth-sd-jwt-vc
- **[SD-JWT]** Selective Disclosure for JWTs (SD-JWT), RFC 9901
- **[STATUS-LIST]** Token Status List, draft-ietf-oauth-status-list
- **[RFC7519]** JSON Web Token (JWT); **[RFC7515]** JSON Web Signature (JWS); **[RFC7638]** JWK Thumbprint; **[RFC7800]** Proof-of-Possession Key Semantics (`cnf`); **[RFC7517]** JSON Web Key (JWK)
- **[RFC2119]** Requirement-level keywords; **[RFC8259]** JSON

---

## 1.6 Informative References

- **[TSAI-CONCEPT]** TSAI High-Level Concept
- **[TSAI-ADR-001]** Agent Delegation Mechanism
- **[TSAI-ADR-002]** Centralized Trust Authorities
- **[TSAI-ADR-005]** Signaling vs Enforcement
- **[TSAI-ADR-007]** Short-Lived Credentials
- **[TSAI-ADR-012]** Service Provider Terminology
- **[TSAI-ADR-014]** Holder Binding and Web Bot Auth Integration (supersedes the binding parts of ADR 013)
- **[TSAI-ADR-015]** Credential Serialisation Format (supersedes ADR 003)
- **[TSAI-ADR-016]** Trust Signal Structure (supersedes ADR 004)
- **[TSAI-ADR-017]** Party Identity and Key Discovery (supersedes ADR 006)
- **[TSAI-ADR-018]** Verification Strength and Replay (amends ADR 009)

---

## 1.7 Design Rationale

This specification follows a set of architectural decisions. Centralised Trust Authorities (ADR 002) give performance, reliability, and legal accountability. The credential is an SD-JWT VC (ADR 015), which keeps TSAI within the JWT and JOSE idiom. Signals are a flat list in four categories with no tiers (ADR 016); a Service Provider sets verification strength from the signals and the risk of the action (ADR 018) rather than from a tier. As a signalling protocol (ADR 005), TSAI defines the signals and the Service Provider decides. Identity follows ADR 017: a Trust Authority is an HTTPS issuer, an agent is its bound key, and a referenced third party is its own `did:web`. Holder binding is a key-binding JWT (ADR 014). Credentials are short-lived, thirty minutes (ADR 018, amending ADR 007).

See the ADRs for the reasoning and the alternatives considered.
