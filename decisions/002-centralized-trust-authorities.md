<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 002: Centralized Trust Authorities

**Status:** Accepted  
**Date:** 2026-01-22  
**Deciders:** TSAI Working Group

---

## Context

The protocol requires a mechanism for evaluating agents and issuing trust credentials. Three primary architectural approaches exist:

1. **Centralized Trust Authorities** - Professional entities that evaluate agents
2. **Blockchain-based trust** - Decentralized ledger for reputation and credentials
3. **Web-of-trust** - Peer-to-peer trust network without central authorities

The choice fundamentally shapes the protocol's performance, security, governance, and adoption characteristics.

---

## Options Considered

### Option 1: Blockchain-based Trust

**Description:** Store credentials and reputation on blockchain; agents and platforms interact with smart contracts.

**Pros:**
- Decentralized (no single point of control)
- Transparent (all data on-chain)
- Censorship-resistant

**Cons:**
- Latency: 1-60 seconds per transaction (incompatible with e-commerce)
- Cost: Gas fees for high-frequency credentials
- Scalability: Limited throughput
- Regulatory uncertainty: On-chain reputation data
- Privacy: Public blockchain exposes all data
- Complexity: Smart contract security, chain selection

**Future consideration:** Blockchain anchoring for TA transparency (audit trail, stake management)

---

### Option 2: Web-of-Trust

**Description:** Peer-to-peer trust network where agents vouch for each other; no central authorities.

**Pros:**
- Fully decentralized
- No central authority required
- Community-driven trust

**Cons:**
- No performance guarantees (graph traversal complexity)
- Sybil attack vulnerability (fake identities vouch for each other)
- No legal accountability (who to sue if agent misbehaves?)
- Historical failure: PGP web-of-trust never achieved mainstream adoption
- Incompatible with professional operation requirements

---

### Option 3: Centralized Trust Authorities

**Description:** Professional entities evaluate agents and issue signed credentials; multiple competing TAs.

**Pros:**
- Performance: Sub-100ms verification for T0/T1
- Reliability: 99.9%+ uptime (professional operation)
- Legal accountability: Established entities with liability
- Regulatory compliance: SOC 2, insurance, audits
- Proven model: Similar to SSL/TLS certificate authorities
- Scalability: Standard web infrastructure patterns

**Cons:**
- Oligopoly market structure (3-10 TAs globally)
- High barriers to entry (favors established organizations)
- Centralized attack surface (each TA is a target)
- Regulatory pressure (governments can compel TAs)
- Potential for commercial pressure from large platforms

---

## Decision

Use **centralized Trust Authorities** (Option 3) - multiple competing TAs rather than blockchain or web-of-trust architectures.

**Expected ecosystem:**
- Small number of professional TAs (3-10 globally)
- High accreditation barriers (SOC 2 Type II, HSM infrastructure, insurance)
- Geographic and vertical specialization
- Established trust/reputation companies extending existing services

**Rationale:**

### Performance Requirements

**Target latency:**
- T0/T1: <5ms verification
- T2: <500ms verification
- T3: <5s verification

Centralized TAs achieve sub-100ms for offline verification (T0/T1) and predictable latency for online verification (T2/T3) using standard HTTP/REST APIs. Blockchain (1-60 seconds per transaction) and web-of-trust (unpredictable graph traversal) cannot meet these requirements.

### Operational Requirements

Trust evaluation requires professional infrastructure, 24/7 operations, substantial investment in reputation systems, and legal accountability. Regulatory compliance demands SOC 2 Type II certification, insurance, established legal entities, and audit trails. Historical precedent shows SSL/TLS certificate authorities achieved broad adoption while PGP web-of-trust failed mainstream adoption.

### Scalability

Target of millions to billions of agent interactions daily requires:
- 10,000+ credential issuances/sec per TA
- 100,000+ verifications/sec per platform (offline)
- Proven scaling patterns (CDN, caching, load balancing)

Blockchain's limited throughput (10-1000 tx/sec) and increasing gas costs cannot achieve required scale.

---

## Risk Mitigation

### Distributed Control

**Platform TA allowlists:**
- Platforms independently choose which TAs to trust
- No mandatory TA (platforms decide)

**Multiple TA credentials:**
- Agents can obtain credentials from multiple TAs
- T3 operations can require credentials from multiple TAs (platform policy)

**TA revocation:**
- Governance body can revoke TA accreditation for policy violations

**Agent TA selection:**
- Agents choose which TAs to work with
- Competition on methodology and pricing

### Transparency and Accountability

**Published methodologies:**
- TAs must publish evaluation criteria
- Agents can understand how reputation is calculated

**Agent rights:**
- Access to own reputation data
- Dispute and correction mechanisms
- Explanation of reputation changes

**Audit requirements:**
- Comprehensive logging
- Regular third-party audits
- Incident reporting

**Legal liability:**
- Insurance requirements
- Liability for negligent evaluation
- Contractual obligations

### Architectural Resilience

**Hybrid verification:**
- T0/T1: Offline verification (no TA dependency)
- T2/T3: Online verification (TA dependency only for high-stakes)
- 95%+ of traffic uses offline verification

**Graceful degradation:**
- System continues operating with reduced functionality during TA outages
- Cached credentials remain valid until expiry
- Platforms can fall back to lower trust tiers

**Multiple TA support:**
- Agents and platforms can work with multiple TAs simultaneously
- No single point of failure

---

## Consequences

### Positive

- **Performance:** Achieves sub-100ms verification for common cases
- **Reliability:** Professional operation enables 99.9%+ uptime
- **Accountability:** Legal entities with liability and insurance
- **Adoption:** Proven model (similar to SSL/TLS CAs)
- **Scalability:** Standard web infrastructure patterns

### Negative

- **Market structure:** Oligopoly (3-10 TAs globally)
- **Barriers to entry:** High costs favor established organizations
- **Centralization risks:** Each TA is attack surface and regulatory pressure point
- **Limited competition:** Small number of TAs may reduce innovation

### Neutral

- **Governance:** Requires independent body to accredit TAs and resolve disputes
- **Economic model:** TAs must be financially sustainable (credential fees)
- **Geographic distribution:** TAs likely concentrated in major markets

---

## Implementation Notes

**TA Requirements:**
- SOC 2 Type II certification
- HSM infrastructure for key management
- Insurance coverage (liability, E&O)
- 24/7 operations and incident response
- Published evaluation methodology
- Audit logging and reporting

**Platform Integration:**
- Maintain TA allowlist (which TAs to trust)
- Implement offline verification for T0/T1
- Implement online verification for T2/T3
- Monitor TA availability and performance

**Governance:**
- Establish TA accreditation criteria
- Create TA registry (governance body maintains)
- Define dispute resolution process
- Monitor TA compliance

---

## References

- TSAI Design Considerations (concept/archive/01-design-considerations.md)
- TSAI High-Level Concept (concept/02-high-level-concept.md)
- SSL/TLS Certificate Authority model
- PGP Web-of-Trust (historical failure analysis)
