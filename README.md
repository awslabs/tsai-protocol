<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# Trust Signals for Agentic Interactions (TSAI)

**An open protocol enabling AI Agents to prove legitimacy through verifiable credentials**

## Overview

As agentic AI systems proliferated through 2025 and 2026, Service Providers faced an impossible choice: block all Agent traffic and lose valuable transactions, or accept unverified requests and risk fraud and abuse. Agents representing legitimate users found themselves blocked or forced to disguise their traffic. TSAI provides the missing trust layer, enabling Service Providers to make informed access decisions and enabling well-behaved Agents to distinguish themselves.

TSAI works through a three-party model. Independent Trust Authorities evaluate Agent behavior and issue cryptographically signed credentials based on W3C Verifiable Credentials. Agents present these credentials when accessing services. Service Providers verify credentials offline and make access decisions based on verified trust signals—identity, reputation, economic stake, and authorization constraints. The protocol uses a tiered approach (T0-T3) matching trust signals to risk levels: basic identity verification for browsing, reputation signals for transactions, economic accountability for high-value operations, and fine-grained constraints for critical systems.

Built on open standards (W3C Verifiable Credentials, DIDs, VC-JOSE-COSE), TSAI complements existing agentic protocols like MCP and A2A without replacing them. The protocol is designed for incremental adoption—Service Providers can start with simple offline verification (T0/T1) and add complexity only when needed. An independent foundation will assume governance in 2027 to ensure broad industry participation and vendor neutrality.

---

## Repository Structure

### Concept Documentation (`concept/`)

High-level protocol design and rationale. These documents define the conceptual foundation for TSAI and are intended for protocol designers, implementers, Trust Authority developers, integrators on the Service Provider side, and security reviewers.

- **[00-problem-statement.md](./concept/00-problem-statement.md)** - Problem definition, scope, and boundary conditions
- **[01-trust-signals.md](./concept/01-trust-signals.md)** - Catalog of potential trust signals (comprehensive, not all normative)
- **[02-high-level-concept.md](./concept/02-high-level-concept.md)** - Protocol overview, tiered model, security model, key principles, and success criteria
- **[04-implementation-roadmap.md](./concept/04-implementation-roadmap.md)** - Phased implementation plan from proof of concept to maturity
- **[05-economic-model.md](./concept/05-economic-model.md)** - Revenue streams, growth opportunities, and adoption multipliers

### Architecture Specification (`architecture/`)

Normative technical specification defining the TSAI protocol. These documents specify conformance requirements for Trust Authorities, Agents, and Service Providers implementing TSAI.

- **[01-introduction.md](./architecture/01-introduction.md)** - Scope, conformance classes, terminology, and design rationale
- **[02-tsai-ontology.md](./architecture/02-tsai-ontology.md)** - JSON-LD ontology defining Agent and Operator classes with operatedBy relationship
- **[03-credential-format.md](./architecture/03-credential-format.md)** - W3C Verifiable Credential structure, claim semantics, and schemas by tier (T0-T3)
- **[04-verification.md](./architecture/04-verification.md)** - Normative verification algorithms, DID resolution requirements, offline/online protocols
- **[05-protocol-integration.md](./architecture/05-protocol-integration.md)** - Integration patterns with MCP, A2A, W3C AI Agent Protocol, and HTTP-based protocols
- **[06-security-privacy.md](./architecture/06-security-privacy.md)** - Trust model, security requirements, threat analysis, and privacy considerations
- **[07-references.md](./architecture/07-references.md)** - Normative and informative references to W3C and IETF specifications
- **[07-trust-authority-apis.md](./architecture/07-trust-authority-apis.md)** - Trust Authority API design rationale and operational context
- **[openapi/trust-authority-api.yaml](./architecture/openapi/trust-authority-api.yaml)** - OpenAPI 3.1 specification for Trust Authority APIs (credential issuance, refresh, challenges)
- **schemas/** - JSON schemas for credential validation and protocol extensions
  - [tsai-credential-t0.schema.json](./architecture/schemas/tsai-credential-t0.schema.json) - T0 credential structure
  - [tsai-credential-t1.schema.json](./architecture/schemas/tsai-credential-t1.schema.json) - T1 credential structure
  - [verifiable-presentation.schema.json](./architecture/schemas/verifiable-presentation.schema.json) - VP wrapper structure
  - [mcp-capability-tsai.schema.json](./architecture/schemas/mcp-capability-tsai.schema.json) - MCP capability declaration
  - [a2a-agent-card-tsai.schema.json](./architecture/schemas/a2a-agent-card-tsai.schema.json) - A2A agent card extension

### Architecture Decision Records (`decisions/`)

Documented design decisions with rationale and alternatives considered:

- **[001-agent-delegation-mechanism.md](./decisions/001-agent-delegation-mechanism.md)** - Whether and how Agents delegate to other Agents
- **[002-centralized-trust-authorities.md](./decisions/002-centralized-trust-authorities.md)** - Professional TAs vs. web-of-trust
- **[003-w3c-verifiable-credentials.md](./decisions/003-w3c-verifiable-credentials.md)** - Standards-based credential format
- **[004-tiered-trust-model.md](./decisions/004-tiered-trust-model.md)** - Four-tier approach matching signals to risk
- **[005-signaling-vs-enforcement.md](./decisions/005-signaling-vs-enforcement.md)** - Protocol defines signals, Service Providers decide
- **[006-did-methods.md](./decisions/006-did-methods.md)** - DID method selection for TAs and Agents
- **[007-short-lived-credentials.md](./decisions/007-short-lived-credentials.md)** - Expiry times by tier and rationale
- **[008-user-privacy-and-sybil-prevention.md](./decisions/008-user-privacy-and-sybil-prevention.md)** - End-user delegation deferred to v2.0
- **[009-timestamp-based-replay-prevention.md](./decisions/009-timestamp-based-replay-prevention.md)** - Timestamp-based freshness for T0/T1
- **[010-fail-closed-with-degraded-mode.md](./decisions/010-fail-closed-with-degraded-mode.md)** - Fail-closed verification with degraded-mode fallback
- **[011-ta-operational-transparency.md](./decisions/011-ta-operational-transparency.md)** - TA-published operational status reports
- **[012-service-provider-terminology.md](./decisions/012-service-provider-terminology.md)** - "Service Provider" terminology and conventions

---

## Quick Start

**For Newcomers:**
1. Review [concept/02-high-level-concept.md](./concept/02-high-level-concept.md) - Understand the tiered model and security approach

**For Implementers:**
1. Review [architecture/01-introduction.md](./architecture/01-introduction.md) - Understand scope and conformance
2. Study [architecture/openapi/trust-authority-api.yaml](./architecture/openapi/trust-authority-api.yaml) - Trust Authority API specification
3. Study [architecture/03-credential-format.md](./architecture/03-credential-format.md) - Credential structure and claims
4. Implement [architecture/04-verification.md](./architecture/04-verification.md) - Start with T0/T1 offline verification
5. Use [architecture/schemas/](./architecture/schemas/) - JSON schemas for validation

**For Protocol Designers:**
1. Read [concept/00-problem-statement.md](./concept/00-problem-statement.md) - Problem definition and scope
2. Review [decisions/](./decisions/) - Understand design rationale and trade-offs
3. Study [architecture/06-security-privacy.md](./architecture/06-security-privacy.md) - Security model and limitations

---

## Key Principles

- **TSAI signals, Service Providers decide** - Protocol defines trust signals; Service Providers interpret them and make access decisions
- **Lightweight yet secure** - Offline verification for common cases (T0/T1), real-time for high-stakes (T2/T3)
- **Standards-based** - W3C Verifiable Credentials, DIDs, VC-JOSE-COSE for interoperability
- **Incremental adoption** - Start simple (T0), add complexity only when needed
- **Honest about limitations** - Credentials don't prevent LLM vulnerabilities or all Agent misbehavior
- **Vendor-neutral governance** - Independent foundation with multi-stakeholder participation

---

## Status

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

The protocol is in active development with pilot implementations planned for Q1-Q2 2026. Governance will transition to an independent foundation in 2027.

---

## Contributing

This is a working group project. For questions or contributions, please contact the TSAI working group.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

```
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
```

## AI Disclosure

These documents were drafted with assistance from AI tools. All technical decisions, architectural choices, and protocol specifications reflect human judgment and working group consensus.

## Disclaimer

Sample code, software libraries, command line tools, proofs of concept, templates, or other related technology are provided as AWS Content or Third-Party Content under the AWS Customer Agreement, or the relevant written agreement between you and AWS (whichever applies). You should not use this AWS Content or Third-Party Content in your production accounts, or on production or other critical data. You are responsible for testing, securing, and optimizing the AWS Content or Third-Party Content, such as sample code, as appropriate for production grade use based on your specific quality control practices and standards. Deploying AWS Content or Third-Party Content may incur AWS charges for creating or using AWS chargeable resources, such as running Amazon EC2 instances or using Amazon S3 storage.
