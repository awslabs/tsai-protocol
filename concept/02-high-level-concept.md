<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI High-Level Concept

**Version:** 1.0  
**Date:** January 2026  
**Status:** Working Group Draft

---

## Overview

TSAI enables Agents to prove legitimacy through W3C Verifiable Credentials issued by independent Trust Authorities and verified by Service Providers. The protocol uses a three-party model: Trust Authorities evaluate Operators and Agents and issue signed credentials, Agents present credentials to prove legitimacy, and Service Providers verify credentials and make access decisions.

TSAI defines four trust tiers (T0-T3) with increasing trust signals and verification rigor. Lower tiers are lightweight and offline; higher tiers add economic stake, constraints, and real-time verification. Trust Authorities may specialize in specific tiers based on their capabilities and business model.

---

## Actors in the Trust Model

### Operator

An Operator is the legal entity—whether a company, organization, or individual—that owns and operates Agents. The Operator sets the system prompts that define each Agent's purpose and constraints, and undergoes KYC verification with a Trust Authority to establish their identity. The Operator is legally accountable for all Agents they operate and builds reputation through the aggregate behavior of those Agents across the ecosystem. For example, "Acme Corporation GmbH" might operate multiple specialized Agents (shopping-bot, travel-bot, research-bot), each with its own behavioral track record but all sharing the Operator's legal identity and accountability.

### Agent

An Agent is an LLM-driven program with a DID that makes requests on behalf of an Operator. Each Agent has a cryptographic identity (DID) and is defined by its system prompt, model, tools, and configuration. Agents act as clients connecting to Service Providers—whether as MCP clients, A2A participants, or other protocol implementations—and build their own behavioral track records. Multiple invocations of the same Agent are assumed to behave uniformly. For example: `did:web:acme-corp.com:agents:shopping-bot`.

### User

A User is the person using the Agent to accomplish tasks. Users provide input to direct the Agent's actions but remain separate from both the Operator and the Agent. User identity and authorization are out of TSAI scope—these are handled separately through OAuth, accounts held with the Service Provider, or other mechanisms.

### Service Provider

A Service Provider is the party that receives a credential from an Agent, verifies it, and decides whether to grant access. In practice a Service Provider may be a merchant system, an API, an MCP server, an A2A Service Agent, infrastructure middleware such as a CDN or edge gateway, or another Agent acting in a service role. Service Providers verify TSAI credentials, interpret trust signals, make access decisions, and report misbehavior to Trust Authorities.

In W3C Verifiable Credentials terms, the Service Provider fulfills the Verifier role. Earlier drafts of this specification called this actor "Platform"; the term was changed for clarity and implementer resonance (see ADR 012).

### Trust Authority

A Trust Authority is an independent organization that evaluates Operators and Agents. Trust Authorities verify Operator identity through KYC, monitor Agent behavior and reputation, issue credentials that bind Operator identity to Agent DIDs, and maintain revocation status.

---

## Trust Signal Attribution

TSAI credentials contain two types of trust signals that reflect different aspects of trustworthiness.

Operator-level signals apply to the legal entity and are shared across all agents that entity operates. These include legal identity (name, jurisdiction), KYC level (basic, enhanced, institutional), certifications (ISO27001, SOC2, PCI-DSS, GDPR), economic stake (collateral, insurance), domain verification (verified domain, domain age), and organizational affiliation.

Agent-level signals apply to a specific agent program and describe its behavioral track record. These include reputation score (0-100), interaction count, success rate, time in operation, confidence level, complaint rate, and behavioral consistency.

One operator can run multiple agents (shopping-bot, travel-bot, research-bot). Each agent builds its own reputation, but all share the operator's legal identity, certifications, and economic stake.
- Time in operation
- Confidence level
- Complaint rate
- Behavioral consistency

**Key insight:** One operator can run multiple agents (shopping-bot, travel-bot, research-bot). Each agent builds its own reputation, but all share the operator's legal identity, certifications, and economic stake.

---

## How It Works

### 1. Credential Issuance

The operator registers with a Trust Authority, undergoing identity verification and KYC. The TA evaluates the operator's legal identity, certifications, and economic stake, while monitoring agent behavior including reputation, success rate, and interactions. The TA then issues a W3C Verifiable Credential containing operator-level signals (identity, certifications, stake), agent-level signals (reputation, track record), and the binding between operator and agent DID. The credential is cryptographically signed by the TA and includes a revocation mechanism (W3C status list). Credentials are short-lived (2-4 hours for T0/T1), reducing reliance on revocation checks.

### 2. Credential Presentation

The Agent wraps the credential in a Verifiable Presentation (VP) and signs the VP with its DID private key to prove possession. The Agent presents the VP to the Service Provider when connecting—whether as an MCP client, A2A participant, or through other protocols.

### 3. Credential Verification

The Service Provider verifies the TA's signature on the credential (proving authenticity), the Agent's signature on the VP (proving the Agent controls the DID), that the credential hasn't expired, and that the DID in the credential matches the DID that signed the VP.

The result: the Service Provider knows the Operator's legal identity and accountability, the Operator's certifications and economic stake, the Agent's behavioral track record, and that the credential is authentic with the Agent as its legitimate holder.

---

## Tiered Trust Model

TSAI uses a tiered approach where different risk levels require different trust signals and verification methods. The tiers are designed with operational feasibility in mind: T0/T1 prioritize mass adoption with low infrastructure costs, while T2/T3 provide comprehensive trust for high-stakes operations.

### T0: Basic Identity (Mass Market Entry)

T0 distinguishes verified agents from random bots with minimal friction. Use cases include browsing, search, public APIs, and low-risk interactions.

Trust signals include the agent DID (persistent identifier) and operator-level signals: operator identity (verified legal entity name), operator jurisdiction, basic KYC (automated business registry verification), and optionally verified domain (proves web presence) and domain age (indicates established operation).

The operational model is fully automated—verification through business registries and DNS challenges, self-service credential issuance, low cost for operators to enable mass adoption, and no ongoing monitoring required.

Verification uses offline VP verification with TA signature plus agent signature, expiry check (2-4 hours), and optional revocation check. This prevents credential theft through VP binding and suits low-stakes scenarios.

### T1: Identity + Static Trust Signals (Premium Mass Market)

T1 provides enhanced trust through verifiable credentials and basic reputation. Use cases include content creation, moderate-value API calls, and user interactions.

Trust signals build on T0 by adding agent-level basic reputation (score, interaction count, success rate, time in operation, confidence level) and operator-level industry certifications (ISO27001, SOC2, FedRAMP—easy to verify), optional organizational affiliation (network membership), and enhanced KYC.

The operational model is mostly automated with API verification of certifications, light human review for edge cases, affordable pricing for small and medium operators, and static signals only—no continuous monitoring required.

Verification matches T0 (offline VP), with Service Providers interpreting reputation and certification signals. Revocation check is recommended but optional.

**Verification:**
- Same as T0 (offline VP)
- Service Provider interprets reputation and certification signals
- Revocation check recommended but optional

**Security:** Reputation and certifications provide behavioral and operational trust; Service Providers can set minimum thresholds.

---

### T2: Economic Stake + Behavioral Signals (High-Value Operations)

T2 provides accountability through economic stake and proven track record. Use cases include transactions, payments, and sensitive operations.

Trust signals build on T1 by adding operator-level posted collateral (funds in escrow), insurance coverage (liability protection), and institutional KYC, plus agent-level payment reliability, complaint rate (requires monitoring infrastructure), and behavioral consistency (requires analytics).

The operational model requires monitoring infrastructure for feedback collection and analytics, escrow and collateral management, and ongoing behavioral tracking. Higher cost reflects this operational investment.

Verification uses VP plus challenge-response (fresh nonce signed by agent) to prevent replay attacks. Revocation check is required, with optional real-time TA query for current stake and reputation. Economic stake creates accountability, challenge-response prevents replay, behavioral signals provide track record, and revocation catches compromised credentials.

### T3: Maximum Assurance (Enterprise/Regulated)

T3 provides the highest trust for critical operations with fine-grained authorization. Use cases include high-value transactions, regulated operations, and critical systems.

Trust signals build on T2 by adding authorized operations (constraint profile), value limits (per transaction, per day), rate limits (requests per minute/hour), domain restrictions (where agent can operate), human-in-loop indicator (required oversight), and optionally authorization chain (audit trail) and audit reports (third-party verification). Whether these constraints apply at operator-level (all agents from this operator) or agent-level (specific to this agent program) remains an open design question.

The operational model provides high-touch service with dedicated account management, real-time monitoring and verification, and audit coordination and compliance support. The highest cost reflects this white-glove service.

Verification uses VP plus challenge-response (fresh nonce signed by Agent), with real-time TA verification required for revocation, constraints, and stake. Service Providers enforce constraints based on credential claims. Short expiry (30 minutes) adds another layer of protection. This provides maximum assurance: real-time verification catches compromised Agents immediately, constraint validation ensures Agents operate within authorized scope, and human oversight protects critical actions.

---

## Security Model

### Credential Binding (Prevents Theft)

Credentials are bound to the agent's DID. The agent must prove DID possession via VP signature, making stolen credentials useless without the private key.

### Replay Prevention

For T0/T1, the VP signature includes a timestamp with a short validity window; revocation is optional. For T2/T3, challenge-response with a fresh nonce prevents replay completely, and revocation check is required.

### Short Expiry + Revocation

Credentials expire in 2-4 hours, reducing revocation dependency. A revocation mechanism is available through W3C status list or TA API. For T0/T1, short expiry is sufficient and revocation is optional. For T2/T3, revocation check is required for high-stakes scenarios. Compromised agents lose access quickly through either expiry or revocation, and TAs refuse renewal for misbehaving agents.

### Defense in Depth

Credentials prove identity and provide trust signals, but Service Providers must still monitor Agent behavior in real-time. Rate limiting, anomaly detection, and kill switches remain essential. Multiple TAs provide redundancy and competition.

### Acknowledged Limitations

TSAI does not prevent prompt injection attacks (Service Providers must defend), Agent misbehavior within authorized scope (monitoring required), or LLM hallucination or deception (output validation needed).

TSAI provides accountability (know who to hold responsible), trust signals (inform risk-calibrated decisions), and cryptographic proof of legitimacy.

---

## Standards-Based Approach

TSAI builds on W3C Verifiable Credentials Data Model 2.0 (standard credential format with broad ecosystem support and existing libraries), W3C VC-JOSE-COSE (VC-JWT encoding for credentials, standard signature formats, algorithm-agnostic and future-proof), and W3C DIDs (decentralized identifiers for agents and TAs).

For DIDs, TSAI uses `did:web` for TAs (DNS-based, enables TA discovery via governance body registry), `did:key` for agents in MVP (simplest, no infrastructure), and `did:web` for agents in production (allows key rotation and service endpoints). The protocol supports multiple agent DID methods.

This provides interoperability with the broader identity ecosystem, avoids proprietary formats, ensures vendor neutrality, and enables future extensibility.

---

## Incremental Adoption Path

Phase 1 (MVP): TAs issue credentials with identity signals (T0), Agents present VPs to Service Providers, Service Providers verify offline. This solves the problem of distinguishing verified Agents from random bots.

Phase 2: TAs add reputation signals to credentials (T1), Service Providers make risk-calibrated decisions, still using offline verification.

Phase 3: TAs include stake and insurance (T2), challenge-response for high-value scenarios, optional real-time TA queries.

Phase 4: Credentials include authorized operations (T3), Service Providers enforce constraints (a Service Provider responsibility), real-time verification for critical operations.

Phase 5 (Ecosystem Maturity): Multiple competing TAs, rich reputation methodologies, trust portability across Service Providers, integration with MCP, A2A, and AP2 protocols.

---

## Success Criteria

TSAI succeeds when multiple independent Trust Authorities can issue interoperable credentials, Service Providers can verify credentials without TA runtime dependency (T0/T1), and credentials are portable across any TSAI-enabled Service Provider. Verification must meet performance requirements: <5ms for T0/T1, <500ms for T2, <5s for T3.

The ecosystem succeeds when multiple competing TAs operate (3-10 globally), Agents carry portable trust across Service Providers, Service Providers welcome Agent traffic with confidence, and clear accountability enables dispute resolution.

Adoption succeeds through significant Service Provider adoption across verticals, a growing Agent ecosystem using credentials, geographic and vertical TA specialization, and no single TA dominance—healthy competition.

The protocol must scale to millions or billions of daily interactions, with individual Service Providers handling thousands to millions of Agent requests per day, TAs issuing and managing credentials for thousands to millions of Agents, and verification infrastructure scaling horizontally.

---

## Performance Requirements

TSAI is designed for production use at scale. Performance targets by tier:

| Tier | Verification Latency | Throughput | TA Dependency |
|------|---------------------|------------|---------------|
| T0 | <5ms (p95) | High (offline) | None (offline VP) |
| T1 | <5ms (p95) | High (offline) | None (offline VP) |
| T2 | <500ms (p95) | Medium | Optional (challenge-response) |
| T3 | <5s (p95) | Low | Required (real-time) |

**Rationale:**

- **T0/T1:** Offline verification enables <5ms latency, suitable for high-frequency interactions (browsing, search, API calls)
- **T2:** Challenge-response adds round-trip, but <500ms acceptable for transactions
- **T3:** Real-time TA verification for maximum assurance, <5s acceptable for high-value operations with human oversight

**Implementation notes:**
- Latency targets are for verification only (not including network transport to the Service Provider)
- Service Providers should cache DID documents and verification results to meet targets
- T0/T1 targets assume local verification with cached TA public keys
- T2/T3 targets assume network round-trip to TA

---

## Key Principles

**TSAI signals, Service Providers decide.** The protocol defines credential format and signal semantics. Service Providers interpret signals and make access decisions. Enforcement is the Service Provider's responsibility, not a protocol mandate.

**Lightweight yet secure.** MVP requires only offline VP verification. Complexity scales with risk through the tiered approach. No TA runtime dependency for common cases.

**Standards-based.** W3C VCs, DIDs, and VC-JOSE-COSE provide existing tooling, libraries, and interoperability with the broader ecosystem.

**Centralized TAs, distributed trust.** Professional TAs (not web-of-trust) with multiple competing authorities. Agents choose TAs; Service Providers choose which TAs to trust.

**Honest about limitations.** Credentials don't prevent all Agent misbehavior. LLM-specific vulnerabilities require additional defenses. TSAI provides accountability and trust signals, not guarantees.

---

## Integration with W3C AI Agent Protocol

TSAI complements the W3C AI Agent Protocol, which focuses on agent-to-agent communication, discovery, and description. The W3C protocol provides agent identity (`did:wba` method), agent discovery (`.well-known/agent-descriptions`), agent description (capabilities, interfaces), and A2A communication patterns. TSAI provides trust signaling (reputation, certifications, economic stake), Trust Authority evaluation, verifiable credentials with trust signals, and risk-calibrated access decisions.

Combined value: the W3C protocol enables Agents to find and communicate with each other; TSAI enables Service Providers to trust the Agents they communicate with.

### Example: Hotel Booking with Trust Verification

Alice's Personal Agent (W3C protocol) wants to book a hotel. The hotel Service Agent requires T1 credentials to prevent spam and fraud.

The process: Alice's agent discovers the hotel agent via Search Agent, retrieves the hotel's agent description (which declares TSAI T1 requirement), obtains a T1 TSAI credential from a Trust Authority (if not cached), and sends a request with both W3C DIDWba authentication (proves identity) and TSAI credential (proves trustworthiness). The hotel agent verifies both identity and trust, then grants access. Alice's agent completes the booking.

The hotel agent gets both identity proof (W3C protocol) and trust signals (TSAI), enabling risk-calibrated decisions.

TSAI supports `did:wba` (W3C protocol's DID method) in addition to `did:web` and `did:key`.

---

## What TSAI Is NOT

TSAI is a complementary protocol that works alongside existing agentic protocols—MCP handles agent-to-tools/data access, A2A handles agent-to-agent communication, W3C AI Agent Protocol handles agent discovery and A2A communication, and AP2 handles payment-specific authorization. TSAI provides the trust signaling layer across all of them.

TSAI uses centralized Trust Authorities for performance and reliability, not blockchain or web-of-trust. There is no on-chain reputation or distributed ledger, though blockchain may be used for transparency (anchoring TA data). Independent professional Trust Authorities with high barriers to entry ensure operational quality and legal accountability through established entities.

TSAI provides trust signals about Agent identity, reputation, and authorization. It does not prevent prompt injection, hallucination, or LLM misbehavior. Service Providers must implement defense-in-depth with monitoring, validation, and guardrails.

TSAI signals trustworthiness; Service Providers decide how to use those signals. The protocol defines what signals exist and what they mean. Service Providers interpret signals and make access decisions. TSAI conveys authorization claims (what the TA asserts the Agent is authorized to do), but Service Providers make access decisions based on those claims. Authorization enforcement is the Service Provider's responsibility.

Credentials prove identity and provide trust signals, but LLMs are runtime-subvertible through prompt injection, sycophancy, and deception. TSAI provides accountability (know who to hold responsible), not behavioral guarantees. Service Providers must monitor Agent behavior in real-time.

TSAI is one layer in defense-in-depth. Service Providers still need rate limiting, anomaly detection, output validation, and kill switches. Trust signals inform decisions; they don't replace security controls.

---
