<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Implementation Roadmap

**Version:** 1.0  
**Date:** January 2026  
**Status:** Working Group Draft

---

## Overview

This document outlines the technical implementation phases for TSAI. It favours incremental delivery: start with a minimal viable protocol and add capability as the ecosystem and security validation justify it. The guiding principles are to start simple, validate security before each step, let real-world feedback drive evolution, keep backward compatibility where feasible, and develop open specifications with reference implementations.

Phases grow by the richness of the signals a Trust Authority can support and the strength a Service Provider can verify, not by a tier ladder.

---

## Phase 0: Proof of Concept (Weeks 1-4)

Phase 0 proves the core: that an SD-JWT VC carrying identity and reputation signals can be issued, bound to a key the agent holds, and verified offline, and that a Service Provider can integrate without excessive complexity.

**Deliverables.** The SD-JWT VC credential format with identity and reputation signals; a Trust Authority issuance service with keys at `/.well-known/jwt-vc-issuer`; a verifier library performing the three checks (issuer signature, key-binding signature against `cnf`, `sd_hash` and `aud`); agent-side credential handling and key-binding JWT creation; a test suite; and a draft specification and integration guide.

**Success.** Issuing and verifying credentials that carry identity and reputation signals, a Service Provider making a decision from those signals, a security review finding no critical flaws, and two or three pilot Service Providers integrating. Known limits at this phase: a single Trust Authority, no block, limited monitoring, and manual incident response.

---

## Phase 1: Foundation (Months 2-4)

Phase 1 delivers production-grade security for early adopters. It adds the compliance and assurance signals, the verification-strength policy of ADR 018 (a Service-Provider nonce challenge and a tighter freshness window where the risk warrants), and the agent or operator block via the Token Status List, and it lays the ground for a multi-TA ecosystem.

**Deliverables.** The full four categories of signals; the verification-strength policy over the signals and the action; the block, keyed to the agent or operator identity, published by the Trust Authority and read by a Service Provider when its risk policy calls for it; a production Trust Authority with key rotation; a complete verifier library; multi-TA support on the Service Provider side; agent credential lifecycle with refresh; logging, anomaly detection, and incident response; and an external security audit with SOC 2 Type I for the Trust Authority.

**Success.** Ten or more Service Providers integrated, a hundred or more agents, the block working end to end, no critical incidents, and the audit passed. Performance: issuance under 500 ms, offline verification well under 100 ms, Trust Authority uptime above 99.9 per cent.

---

## Phase 2: Ecosystem Growth (Months 5-9)

Phase 2 scales for a growing ecosystem. Several independent Trust Authorities operate, selective disclosure (the SD-JWT VC mechanism) lets an agent reveal only the signals a Service Provider needs, and advanced anomaly detection and cross-TA correlation are deployed.

**Deliverables.** Selective disclosure in issuance and presentation; multi-TA verification and cross-TA reputation correlation; anomaly and collusion detection at Trust Authorities; performance optimisation and analytics on the Service Provider side; agent-side multi-TA support and key rotation; SOC 2 Type II and ISO 27001; and a governance process for accreditation, dispute resolution, and protocol evolution.

**Success.** Fifty or more Service Providers, a thousand or more agents, several independent Trust Authorities, no major incidents, and multiple independent audits passed.

---

## Phase 3: Maturity (Months 10-18)

Phase 3 reaches global scale and adds privacy-preserving techniques. Trust Authorities deploy machine-learning threat detection, the ecosystem serves millions of daily interactions, and the working group plans for post-quantum signatures.

**Deliverables.** Research into zero-knowledge techniques over the credential for stronger privacy; machine-learning threat detection and predictive analytics; real-time risk assessment and automated compliance reporting on the Service Provider side; formal verification of the protocol; and post-quantum cryptography planning.

**Success.** Two hundred or more Service Providers, ten thousand or more agents, five or more independent Trust Authorities, global scale, regulatory certifications, and published security research.

---

## Long-Term Evolution (18+ months)

Beyond Phase 3, work continues on post-quantum cryptography (migration to a lattice-based signature, with production readiness targeted around 2030), privacy-preserving reputation, AI-assisted threat detection, and protocol evolution through formal verification and standards engagement. Delegation and mandate, the constraints on what an agent may do, are pursued on their own track (ADR 001), separate from the trust signals.

---

## Implementation Priorities

The critical path is security first: no phase proceeds without security validation. Each phase delivers working functionality, keeps compatibility where feasible, and is driven by real-world feedback and open development. Phase 0 to 1 needs the security review passed and pilots successful; Phase 1 to 2 needs production stability, audits passed, and adoption validated; Phase 2 to 3 needs a working multi-TA ecosystem and the advanced security features validated.

---

## Timeline Summary

| Phase | Duration | Milestone |
|---|---|---|
| Phase 0 | Weeks 1-4 | Proof of concept validated |
| Phase 1 | Months 2-4 | Production-grade foundation |
| Phase 2 | Months 5-9 | Ecosystem growth |
| Phase 3 | Months 10-18 | Global maturity |
| Long-term | 18+ months | Continuous evolution |

---

**Related Documents:**
- `02-high-level-concept.md` — protocol overview
- `TODO.md` — detailed implementation tasks
- `architecture/` — technical specifications
