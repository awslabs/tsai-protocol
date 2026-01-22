<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Problem Statement and Scope

**Version:** 1.0  
**Date:** January 2026  
**Status:** Working Group Draft

---

## Problem Statement

The rise of agentic AI has created a trust crisis between platforms and agents. Platforms face a flood of agent traffic but cannot distinguish legitimate agents from malicious actors. They experience infrastructure strain, fraud attempts, and security breaches, forcing them to resort to blanket blocking or expensive bot detection systems that catch legitimate agents alongside bad actors.

Meanwhile, agents cannot prove their legitimacy. They face unreliable access as platforms block them defensively, and some resort to disguising their traffic as human browsing—a practice that creates its own security concerns. Worse, reputation earned on one platform doesn't transfer to others, forcing agents to rebuild trust from scratch with each new service.

The result is an adversarial dynamic: legal disputes, lost economic opportunity, and fragmented trust mechanisms that benefit no one.

---

## Scope

TSAI provides a trust signaling protocol that enables agents to present verifiable credentials containing trust signals, platforms to verify credential authenticity and interpret those signals, and independent Trust Authorities to evaluate agents and issue credentials.

### What TSAI IS

TSAI is a credential format and structure specification that defines how trust signals are encoded and transmitted. It specifies the semantics of trust signals—what claims like reputation scores or authorized constraints actually mean—and provides verification mechanisms for checking credential authenticity cryptographically.

### What TSAI IS NOT

TSAI is not a platform implementation guide. It doesn't dictate how platforms use signals to make decisions or how they enforce constraints. The protocol conveys trust information; platforms interpret that information and make access control decisions based on their own policies and risk tolerance. Similarly, TSAI doesn't guarantee agent behavior—signals inform decisions but don't prevent agent misbehavior.

### Key Principle

**TSAI signals, platforms decide.** This principle runs through every design choice in the protocol.

---

## Boundary Conditions

TSAI's design rests on six boundary conditions that shape its architecture and increase the likelihood of adoption.

### 1. Centralized Approach

TSAI uses professional Trust Authorities rather than web-of-trust models. This choice stems from performance requirements (sub-100ms verification for common cases), reliability requirements (99.9%+ uptime), and the need for legal accountability. Professional TAs can meet regulatory compliance standards (SOC 2, insurance, audits) that volunteer networks cannot.

This creates an oligopoly market structure with 3-10 TAs globally, but enables the professional operation and legal accountability that platforms require.

### 2. Viable Economic Model

The ecosystem requires professional operation, not volunteer effort. TAs need substantial infrastructure (€500K+ annually) to operate reliably. In return, agents gain portable trust that works across platforms, and platforms gain reliable trust signals that reduce fraud and improve service.

High barriers to TA entry ensure quality and sustainability rather than a race to the bottom.

### 3. Independent Governance

A neutral governance body with multi-stakeholder representation prevents vendor capture and ensures the protocol serves the ecosystem rather than individual interests. This builds trust across competing organizations and enables transparent specification evolution.

The path runs from industry consortium to independent foundation (such as Linux Foundation).

### 4. Lightweight Yet Secure

Adoption requires low friction—simple integration with clear value. Security requires rigor—cryptographic proofs and tamper-evident credentials. TSAI balances these through tiered verification: offline for common cases (T0/T1), real-time for high-stakes operations (T2/T3).

Platforms bear implementation burden (verification, interpretation, enforcement), but this beats the current state where no trust mechanism exists.

### 5. Standards-Based

TSAI builds on W3C Verifiable Credentials, DIDs, and Data Integrity proofs. This provides interoperability with broader identity ecosystems, future-proofing through extensible and algorithm-agnostic designs, and vendor neutrality through open standards rather than proprietary formats.

TSAI credentials work alongside other VC-based systems, allowing agents to present multiple credential types.

### 6. Designed for Agentic AI

Traditional trust mechanisms—reputation alone—prove insufficient for agents with dynamic behavior. LLM-based agents require richer signals: identity verification, behavioral reputation, economic stake, and authorized constraints. This enables platforms to make informed, risk-calibrated decisions while acknowledging that agents may be compromised or unreliable at runtime.

TSAI addresses this through a tiered trust model (T0-T3) with different signal combinations for different risk levels.

---

## Success Criteria

TSAI succeeds when multiple independent Trust Authorities operate and compete, platforms adopt the protocol across verticals (e-commerce, services, APIs), and agents carry portable trust credentials. Success means reduced friction between platforms and agents—fewer blocks, less disguising—and demonstrated economic value for all parties.

---

## Non-Goals

TSAI complements existing protocols (MCP, A2A, AP2) rather than replacing them. It does not solve AI alignment or prevent all agent misbehavior. It does not mandate platform implementations or policies, create a universal reputation system (TAs compete on methodology), or eliminate all trust-related risks (defense-in-depth remains required).

---

**Next Steps:** Design considerations (`01-design-considerations.md`), technical architecture (`02-architecture.md`), security analysis (`03-security.md`).
