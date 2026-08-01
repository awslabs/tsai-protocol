<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI High-Level Concept

**Version:** 1.0  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## Overview

TSAI lets an agent prove its legitimacy with a verifiable credential that an independent Trust Authority issues and a Service Provider verifies. The model has three parties: a Trust Authority evaluates operators and agents and issues a signed credential, an agent presents the credential to prove legitimacy, and a Service Provider verifies it and decides on access.

A credential is an SD-JWT VC. It carries a flat list of trust signals in four categories, and it is bound to a key the agent holds. The protocol does not grade credentials into tiers. How much a Service Provider requires of the signals, and how strongly it verifies a presentation, is its own policy over the signals and the risk of the action, specified in the verification section.

---

## Actors

### Operator

The operator is the legal entity, a company, organisation, or individual, that runs agents. The operator sets each agent's purpose and constraints, undergoes identity verification with a Trust Authority, and is legally accountable for the agents it runs. Its reputation accrues from the aggregate behaviour of those agents. For example, Acme Corporation GmbH might run several agents, each with its own track record but all sharing the operator's legal identity and accountability.

### Agent

The agent is an LLM-driven program that makes requests on behalf of an operator. It is identified by the key it holds, the key the credential is bound to, and it may carry a stable HTTPS name for continuity. It acts as a client to Service Providers, as an MCP client, an A2A participant, or through another protocol, and it builds its own behavioural record.

### User

The user is the person directing the agent. User identity and authorization are out of TSAI scope and are handled separately, through OAuth, an account with the Service Provider, or another mechanism.

### Service Provider

The Service Provider receives a credential, verifies it, and decides whether to grant access. It may be a merchant system, an API, an MCP server, an A2A service agent, edge infrastructure, or another agent in a service role. In W3C Verifiable Credentials terms it is the Verifier. An earlier draft called this actor the Platform; the term changed for clarity (ADR 012).

### Trust Authority

The Trust Authority is an independent organisation that evaluates operators and agents. It verifies the operator's identity, observes agent behaviour, issues credentials that bind an operator's identity to an agent's key, and, where it offers this, publishes a block against an agent or operator it no longer trusts.

---

## Trust Signals

A credential carries a flat list of signals. Each signal has a category, a type, and type-specific fields. A signal is about either the operator, shared across that operator's agents, or the specific agent.

The four categories answer four questions a Service Provider asks.

- **Identity** — who the agent and operator are: the operator's legal identity and jurisdiction, the depth of identity verification, a controlled domain and its age.
- **Reputation** — how the agent has behaved: a score, the number of interactions behind it, and the window observed.
- **Compliance** — what third-party certifications the operator holds, such as ISO 27001 or SOC 2, each naming the certifier.
- **Assurance** — what economic backing stands behind the agent, such as insurance or posted collateral, each naming the backer.

One operator can run several agents. Each agent builds its own reputation, while all share the operator's identity, compliance, and assurance signals.

Authorization, the constraints on what an agent may do, is not a trust signal. It is a matter of delegation and is handled separately (ADR 001), not as a signal category.

---

## How It Works

### Issuance

The operator registers with a Trust Authority and undergoes identity verification. The Trust Authority evaluates the operator's identity, compliance, and assurance, observes the agent's behaviour, and issues an SD-JWT VC. The credential carries the signals and binds the operator's identity to the agent's key. The Trust Authority signs it, and it is short-lived, thirty minutes, which limits reliance on any block.

### Presentation

The agent appends a key-binding JWT signed with the private key matching the credential's bound key, which proves possession, and presents the pair to the Service Provider on connecting.

### Verification

The Service Provider checks the Trust Authority's signature on the credential, the agent's signature on the key-binding JWT, that the credential has not expired, and that the presentation is addressed to it. The result is that the Service Provider knows the operator's identity and accountability, the operator's compliance and assurance, the agent's record, and that the presentation comes from the legitimate holder.

---

## Verification Strength

A Service Provider decides how strongly to verify from the risk of the action, not from a tier on the credential. The base path is offline and fast: it needs the Trust Authority's published key and nothing from the Trust Authority at request time. Where the risk warrants, a Service Provider can require a nonce it issues, apply a tighter freshness window to the presentation, or fetch the agent or operator status list, at the cost of a round trip. The precise rules, and how they follow from the signals and the action, are specified in the verification section (ADR 018).

This replaces the earlier tiered model, where the credential carried a tier and the tier fixed the verification method. Grading is now the Service Provider's policy over the signals, which keeps the credential uniform and lets each Service Provider match rigour to its own risk.

---

## Security Model

**Binding prevents theft.** The credential is bound to the agent's key. The agent proves possession with the key-binding JWT, so a stolen credential is useless without the private key.

**Replay is prevented per presentation.** Each presentation carries a fresh key-binding JWT addressed to one Service Provider, on a clock independent of the credential lifetime. A captured presentation is not usable elsewhere.

**Short lifetime bounds exposure.** A credential lives thirty minutes, so a compromised agent loses access quickly, and a Trust Authority stops re-issuing to a misbehaving agent. Where the in-window risk justifies it, a Trust Authority publishes a block against the agent or operator, keyed to its identity, which a Service Provider checks online when its policy calls for it.

**Defence in depth.** Credentials give identity and signals, but a Service Provider still monitors behaviour, rate-limits, detects anomalies, and keeps a kill switch. Multiple Trust Authorities give redundancy.

**Acknowledged limits.** TSAI does not prevent prompt injection, misbehaviour within authorised scope, or LLM hallucination and deception. It gives accountability and trust signals, not behavioural guarantees.

---

## Standards Base

TSAI builds on SD-JWT VC (draft-ietf-oauth-sd-jwt-vc) for the credential, the key-binding JWT for holder binding, and the IETF Token Status List for a block. A Trust Authority is identified by an HTTPS issuer with keys at `/.well-known/jwt-vc-issuer`; an agent by the key it holds; a referenced third party by its own `did:web` (ADR 017). This keeps TSAI within the JWT and JOSE idiom shared by Web Bot Auth and OpenID4VC, and away from a second identifier scheme.

---

## Incremental Adoption

Adoption grows by the richness of the signals, not by a tier ladder.

- A Trust Authority first issues identity signals, so a Service Provider can tell a verified agent from an unknown bot, verifying offline.
- It then adds reputation, so a Service Provider can make risk-calibrated decisions, still offline.
- It then adds compliance and assurance, which a Service Provider weighs for higher-value interactions, fetching a status list or issuing a nonce where its risk warrants.
- Across the ecosystem, several Trust Authorities compete on evaluation methodology, agents carry portable trust across Service Providers, and TSAI composes with MCP, A2A, and payment protocols.

---

## Performance

The base path is offline verification against a cached Trust Authority key, which is fast enough for high-frequency interactions such as browsing and search. Where a Service Provider's policy adds a nonce challenge or a status fetch, that adds a network round trip, acceptable for the higher-value interactions that call for it. Latency targets belong with the verification-strength policy (ADR 018), not a tier table.

---

## Key Principles

- **TSAI signals, Service Providers decide.** The protocol defines the credential and the meaning of the signals; the Service Provider interprets them and decides on access. Enforcement is the Service Provider's responsibility.
- **Light yet secure.** The common path is offline verification; strength scales with the risk of the action, as the Service Provider's policy, not as a protocol tier.
- **One idiom.** SD-JWT VC, JWK binding, and HTTPS issuer discovery keep TSAI within one identifier and signing idiom.
- **Centralised authorities, distributed trust.** Professional Trust Authorities compete; agents choose one, and Service Providers choose which to trust.
- **Honest about limits.** Credentials do not prevent LLM misbehaviour; TSAI gives accountability and signals, not guarantees.

---

## Integration with the W3C AI Agent Protocol

TSAI complements the W3C AI Agent Protocol, which handles agent discovery, description, and agent-to-agent communication. The W3C protocol authenticates an agent with its own DIDWba scheme, which uses a `did:wba` identifier. TSAI does not use `did:wba`; it identifies the agent by the key its credential is bound to. The two layers are orthogonal: the W3C proof establishes control of the W3C identity, and the TSAI presentation carries the trust signals, in the same way TSAI composes with Web Bot Auth (ADR 014).

For example, Alice's personal agent discovers a hotel booking agent that requires TSAI, obtains a credential from a Trust Authority, and sends a request carrying both its DIDWba proof and its TSAI presentation. The hotel agent verifies both and decides on the signals per its own policy.

---

## What TSAI Is Not

TSAI is complementary. MCP handles agent-to-tool access, A2A handles agent-to-agent communication, the W3C AI Agent Protocol handles discovery, and payment protocols handle payment authorization. TSAI is the trust-signalling layer across them.

TSAI uses centralised Trust Authorities for performance, reliability, and legal accountability, not a blockchain or a web of trust, though a Trust Authority may anchor data publicly for transparency.

TSAI gives trust signals about an agent's identity, reputation, compliance, and assurance. It does not carry authorization constraints as signals; that is delegation. It does not prevent prompt injection, hallucination, or runtime subversion of the model. A Service Provider still needs monitoring, validation, rate limiting, and kill switches. Trust signals inform decisions; they do not replace security controls.
