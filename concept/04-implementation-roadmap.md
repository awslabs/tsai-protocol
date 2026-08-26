<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Implementation Roadmap

**Version:** 1.0  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## Overview

This document describes the planned capability progression for TSAI and the order in which the capabilities depend on one another. It is not a schedule and not a statement of status; it makes no adoption or timeline commitments. The guiding principles are to start simple, validate security before each step, keep backward compatibility where feasible, and develop open specifications with reference implementations.

The stages grow by the richness of the signals a Trust Authority can support and the strength a Service Provider can verify, not by a tier ladder. Each stage depends on the one before it, and no stage proceeds without security validation.

---

## Stage 0: Proof of Concept

Stage 0 proves the core: that an SD-JWT VC carrying identity and reputation signals can be issued, bound to a key the agent holds, and verified offline, and that a Service Provider can integrate without excessive complexity.

**Capability.** The SD-JWT VC credential format with identity and reputation signals; a Trust Authority issuance service with keys at `/.well-known/jwt-vc-issuer`; a verifier library performing the core checks (issuer signature, key-binding signature against `cnf`, `sd_hash`, and `aud`); agent-side credential handling and key-binding JWT creation; a test suite; and a draft specification and integration guide.

**Establishes.** Credentials carrying identity and reputation signals are issued and verified, a Service Provider makes a decision from those signals, and a security review finds no critical flaws. Known limits at this stage: a single Trust Authority, no block, limited monitoring, and manual incident response.

---

## Stage 1: Foundation

Stage 1 adds production-grade security. It adds the compliance and assurance signals, the verification-strength policy of ADR 018 (a Service-Provider nonce challenge and a tighter freshness window where the risk warrants), request binding for state-changing actions (ADR 020), the type metadata that carries the mandatory identity floor and the selective-disclosure controls (ADR 022) so that selective disclosure is safe to use from the start, and the agent or operator block via the Token Status List, and it lays the ground for a multi-TA ecosystem.

**Capability.** The full four categories of signals; the verification-strength policy over the signals and the action; type metadata per `vct` carrying the mandatory identity floor and the `sd: never` controls; selective disclosure in issuance and presentation; request binding for state-changing actions; the block, keyed to the agent or operator identity, published by the Trust Authority and read by a Service Provider when its risk policy calls for it; a production Trust Authority with key rotation; a complete verifier library; multi-TA support on the Service Provider side; agent credential lifecycle with refresh; and logging, anomaly detection, and incident response.

**Establishes.** The block works end to end, an external security audit is passed, and offline verification is fast enough for high-frequency interactions such as browsing and search.

---

## Stage 2: Ecosystem Growth

Stage 2 scales for a multi-authority ecosystem. Several independent Trust Authorities operate, cross-TA reputation correlation is deployed, and advanced anomaly and collusion detection are added. Selective disclosure, which ships in Stage 1, is now exercised across the ecosystem.

**Capability.** Multi-TA verification and cross-TA reputation correlation; anomaly and collusion detection at Trust Authorities; performance optimisation and analytics on the Service Provider side; agent-side multi-TA support and key rotation; and a governance process for accreditation, dispute resolution, and protocol evolution.

**Establishes.** Several independent Trust Authorities interoperate, and a Service Provider consumes and compares their credentials without per-authority logic.

---

## Stage 3: Maturity

Stage 3 adds privacy-preserving techniques and prepares for post-quantum signatures.

**Capability.** Research into zero-knowledge techniques over the credential for stronger privacy; machine-learning threat detection and predictive analytics; real-time risk assessment and automated compliance reporting on the Service Provider side; formal verification of the protocol; and post-quantum cryptography planning.

**Establishes.** The protocol is formally verified and has a post-quantum migration path.

---

## Beyond Stage 3

Work continues on post-quantum cryptography (migration to a lattice-based signature), privacy-preserving reputation, AI-assisted threat detection, and protocol evolution through formal verification and standards engagement. Delegation and mandate, the constraints on what an agent may do, are pursued on their own track (ADR 001), separate from the trust signals.

---

## Sequencing

The critical path is security first: no stage proceeds without security validation, and each stage keeps compatibility where feasible. Stage 0 to 1 needs the security review passed; Stage 1 to 2 needs production stability and the audit passed; Stage 2 to 3 needs a working multi-TA ecosystem and the advanced security capabilities validated.

| Stage | Focus |
|---|---|
| Stage 0 | Proof of concept |
| Stage 1 | Production-grade foundation |
| Stage 2 | Multi-authority ecosystem |
| Stage 3 | Privacy and post-quantum readiness |

---

**Related Documents:**
- `02-high-level-concept.md` — protocol overview
- `TODO.md` — detailed implementation tasks
- `architecture/` — technical specifications
