<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Introduction

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## 1.1 Scope

This document specifies Trust Signals for Agentic Interactions (TSAI), a trust-signalling protocol. A Trust Authority issues a verifiable credential carrying trust signals about an agent, the agent presents the credential to prove legitimacy, and a Service Provider verifies it and reads the signals.

TSAI defines the credential format (SD-JWT VC), the meaning of the signals, the verification algorithm, and the Trust Authority APIs for issuance and status. It does not define how a Service Provider uses the signals to decide on access, how a Trust Authority evaluates an agent, or how an agent is implemented.

**Core principle:** TSAI signals, Service Providers decide.

---

## 1.2 Conformance

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in all capitals.

**A conforming Trust Authority** MUST issue credentials conforming to Section 2, implement the APIs of Section 7, and comply with Section 5.

**A conforming agent** MUST present credentials that verify under Section 3, prove possession of the bound key, and comply with Section 5.

**A conforming Service Provider** MUST verify credentials per Section 3 and comply with Section 5. It MAY choose which Trust Authorities to trust and how to weigh the signals; both are its own policy.

---

## 1.3 Terminology

**Agent** — a software entity that acts on behalf of a user or organisation and presents TSAI credentials when interacting with a Service Provider.

**Operator** — the legal entity that runs agents and is accountable for them.

**Credential** — an SD-JWT VC issued by a Trust Authority, carrying trust signals about an agent.

**Trust Authority (TA)** — a professional entity that evaluates agents and issues signed credentials. Identified by an HTTPS issuer, with signing-key metadata found through the `jwt-vc-issuer` well-known insertion rule.

**Service Provider** — the party that receives a credential, verifies it, and decides on access. It may be a merchant system, an API, an MCP server, an A2A service agent, edge infrastructure, or another agent in a service role. In W3C Verifiable Credentials terms it is the Verifier. An earlier draft used the term Platform (ADR 012).

**Trust Signal** — a claim in a credential in one of four categories: identity, reputation, compliance, or assurance.

**Presentation** — a credential with a key-binding JWT appended, by which the agent proves possession of the bound key.

**Key-binding JWT** — the JWT the holder signs with the private key matching `cnf` to bind a presentation to itself and to one Service Provider.

**Block** — a Trust Authority marking an agent or operator no longer trusted, keyed to its identity in a status list.

**DID** — a W3C Decentralised Identifier. In TSAI, used only to identify referenced third parties (a certifier or a backer) by their own `did:web`.

**Type metadata** — the per-`vct` document carrying standard path-based claim controls plus TSAI signal disclosure/display controls. The TSAI profile binds each type to an integrity-protected JSON Schema that is authoritative for format and presence (Section 2.9).

**Request binding** — an optional `req` digest in the key-binding JWT that binds a presentation to the request it accompanies (Section 3.4).

### Conventions

TSAI actor names — Trust Authority, Operator, Agent, User, Service Provider — are Title case when naming the protocol role. The Service Provider is the actor; the verifier (lowercase) is the component that performs verification. Compounds are reworded rather than hyphenated: "across Service Providers", not "cross-Service-Provider".

---

## 1.4 Document Structure

The specification is in numbered sections. The section numbers and the file names do not currently coincide; the mapping is:

| Section | Document |
|---|---|
| 1 | `01-introduction.md` |
| 2 | `03-credential-format.md` |
| 3 | `04-verification.md` |
| 4 | `05-protocol-integration.md` |
| 5 | `06-security-privacy.md` |
| 6 | `07-references.md` |
| 7 | `07-trust-authority-apis.md` |

- **Section 2: Credential Format** — the SD-JWT VC structure, the four signal categories, the identity floor, type metadata, and the schema.
- **Section 3: Verification** — the algorithm, freshness, request binding, status, and fetch hardening.
- **Section 4: Protocol Integration** — MCP, A2A, the W3C AI Agent Protocol, HTTP, and the payments boundary.
- **Section 5: Security and Privacy** — the trust model, threats, limitations, and requirements.
- **Section 6: References.**
- **Section 7: Trust Authority APIs** — enrolment, issuance, refresh, status, key repudiation, and transparency.

The domain model behind the credential is in `02-tsai-ontology.md`. The JSON schemas and the OpenAPI are under `architecture/schemas/` and `architecture/openapi/`, and per-`vct` type metadata under `architecture/type-metadata/`.

---

## 1.5 Normative References

- **[SD-JWT-VC]** SD-JWT-based Verifiable Credentials, draft-ietf-oauth-sd-jwt-vc-19
- **[SD-JWT]** Selective Disclosure for JWTs (SD-JWT), RFC 9901
- **[STATUS-LIST]** Token Status List, draft-ietf-oauth-status-list-21
- **[RFC7519]** JSON Web Token (JWT); **[RFC7515]** JSON Web Signature (JWS); **[RFC7638]** JWK Thumbprint; **[RFC7800]** Proof-of-Possession Key Semantics (`cnf`); **[RFC7517]** JSON Web Key (JWK); **[RFC7518]** JSON Web Algorithms (ES256)
- **[RFC2119]** and **[RFC8174]** BCP 14 requirement-level keywords; **[RFC8259]** JSON

---

## 1.6 Informative References

- **[TSAI-CONCEPT]** TSAI High-Level Concept
- **[TSAI-ADR-001]** Agent Delegation Mechanism
- **[TSAI-ADR-002]** Centralized Trust Authorities
- **[TSAI-ADR-005]** Signaling vs Enforcement
- **[TSAI-ADR-007]** Short-Lived Credentials
- **[TSAI-ADR-012]** Service Provider Terminology
- **[TSAI-ADR-014]** Holder Binding and Web Bot Auth Integration (retains the self-contained binding rationale of ADR 013; ADR 015 supersedes its VP-JWT serialisation)
- **[TSAI-ADR-015]** Credential Serialisation Format (supersedes ADR 003)
- **[TSAI-ADR-016]** Trust Signal Structure (supersedes ADR 004)
- **[TSAI-ADR-017]** Party Identity and Key Discovery (supersedes ADR 006)
- **[TSAI-ADR-018]** Verification Strength and Replay (amends ADR 009)

---

## 1.7 Design Rationale

This specification follows a set of architectural decisions. Centralised Trust Authorities (ADR 002) give performance, reliability, and legal accountability. The credential is an SD-JWT VC (ADR 015), which keeps TSAI within the JWT and JOSE idiom. Signals are a flat list in four categories with no tiers (ADR 016); a Service Provider sets verification strength from the signals and the risk of the action (ADR 018) rather than from a tier. As a signalling protocol (ADR 005), TSAI defines the signals and the Service Provider decides. Identity follows ADR 017: a Trust Authority is an HTTPS issuer, an agent is its registered persistent HTTPS `sub`, and a referenced third party is its own `did:web`; `cnf` is the agent's current rotating binding key. Holder binding is a key-binding JWT (ADR 014). Credentials are short-lived, thirty minutes (ADR 018, amending ADR 007).

See the ADRs for the reasoning and the alternatives considered.
