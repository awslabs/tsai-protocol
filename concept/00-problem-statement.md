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

The rise of agentic AI has created a trust crisis between Service Providers and Agents. Service Providers face a flood of Agent traffic but cannot distinguish legitimate Agents from malicious actors. They experience infrastructure strain, fraud attempts, and security breaches, forcing them to resort to blanket blocking or expensive bot detection systems that catch legitimate Agents alongside bad actors.

Meanwhile, Agents cannot prove their legitimacy. They face unreliable access as Service Providers block them defensively, and some resort to disguising their traffic as human browsing—a practice that creates its own security concerns. Worse, reputation earned with one Service Provider doesn't transfer to others, forcing Agents to rebuild trust from scratch with each new service.

The result is an adversarial dynamic: legal disputes, lost economic opportunity, and fragmented trust mechanisms that benefit no one.

---

## Scope

TSAI provides a trust signaling protocol that enables Agents to present verifiable credentials containing trust signals, Service Providers to verify credential authenticity and interpret those signals, and independent Trust Authorities to evaluate Agents and issue credentials.

### What TSAI IS

TSAI is a credential format and structure specification that defines how trust signals are encoded and transmitted. It specifies the semantics of trust signals—what claims like reputation scores or compliance certifications actually mean—and provides verification mechanisms for checking credential authenticity cryptographically.

### What TSAI IS NOT

TSAI is not an implementation guide for Service Providers. It doesn't dictate how Service Providers use signals to make decisions or how they enforce constraints. The protocol conveys trust information; Service Providers interpret that information and make access control decisions based on their own policies and risk tolerance. Similarly, TSAI doesn't guarantee Agent behavior—signals inform decisions but don't prevent Agent misbehavior.

### Key Principle

**TSAI signals, Service Providers decide.** This principle runs through every design choice in the protocol.

---

## Boundary Conditions

TSAI's design rests on six boundary conditions that shape its architecture and increase the likelihood of adoption.

### 1. Centralized Approach

TSAI uses professional Trust Authorities rather than web-of-trust models. This choice stems from performance requirements (sub-100ms verification for common cases), reliability requirements (99.9%+ uptime), and the need for legal accountability. Professional TAs can meet regulatory compliance standards (SOC 2, insurance, audits) that volunteer networks cannot.

This creates an oligopoly market structure with 3-10 TAs globally, but enables the professional operation and legal accountability that Service Providers require.

### 2. Viable Economic Model

The ecosystem requires professional operation, not volunteer effort. TAs need substantial infrastructure (€500K+ annually) to operate reliably. In return, Agents gain portable trust that works across Service Providers, and Service Providers gain reliable trust signals that reduce fraud and improve service.

High barriers to TA entry ensure quality and sustainability rather than a race to the bottom.

### 3. Independent Governance

A neutral governance body with multi-stakeholder representation prevents vendor capture and ensures the protocol serves the ecosystem rather than individual interests. This builds trust across competing organizations and enables transparent specification evolution.

The path runs from industry consortium to independent foundation (such as Linux Foundation).

### 4. Lightweight Yet Secure

Adoption requires low friction—simple integration with clear value. Security requires rigor—cryptographic proofs and tamper-evident credentials. TSAI balances these with an offline base path for common cases and stronger checks where the risk of the action warrants them, set by the Service Provider's policy over the signals rather than by a tier on the credential.

Service Providers bear the implementation burden (verification, interpretation, enforcement), but this beats the current state where no trust mechanism exists.

### 5. Standards-Based

TSAI builds on SD-JWT VC, JWK-based holder binding, and HTTPS issuer discovery. This keeps TSAI within the JWT and JOSE idiom shared by Web Bot Auth and OpenID4VC, provides interoperability with that ecosystem, and avoids a proprietary format or a second identifier scheme.

TSAI credentials work alongside other JWT-based credentials, allowing an agent to present more than one credential type.

### 6. Designed for Agentic AI

Traditional trust mechanisms—reputation alone—prove insufficient for Agents with dynamic behavior. LLM-based Agents require richer signals: identity verification, behavioral reputation, and economic backing. This enables Service Providers to make informed, risk-calibrated decisions while acknowledging that Agents may be compromised or unreliable at runtime.

TSAI addresses this with trust signals in four categories, where the Service Provider sets verification strength from the signals and the risk of the action rather than from a tier on the credential.

---

## Success Criteria

TSAI succeeds when multiple independent Trust Authorities operate and compete, Service Providers adopt the protocol across verticals (e-commerce, services, APIs), and Agents carry portable trust credentials. Success means reduced friction between Service Providers and Agents—fewer blocks, less disguising—and demonstrated economic value for all parties.

---

## Non-Goals

TSAI complements existing protocols (MCP, A2A, AP2) rather than replacing them. It does not solve AI alignment or prevent all Agent misbehavior. It does not mandate Service Provider implementations or policies, create a universal reputation system (TAs compete on methodology), or eliminate all trust-related risks (defense-in-depth remains required).

---

**Next Steps:** the high-level concept (`concept/02-high-level-concept.md`) and the architecture specification (`architecture/`).
