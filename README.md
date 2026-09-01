<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# Trust Signals for Agentic Interactions (TSAI)

**An open protocol enabling AI Agents to prove legitimacy through verifiable credentials**

## Overview

As agentic AI systems proliferated through 2025 and 2026, Service Providers faced an impossible choice: block all Agent traffic and lose valuable transactions, or accept unverified requests and risk fraud and abuse. Agents representing legitimate users found themselves blocked or forced to disguise their traffic. TSAI provides the missing trust layer, enabling Service Providers to make informed access decisions and enabling well-behaved Agents to distinguish themselves.

TSAI works through a three-party model. Independent Trust Authorities evaluate Agent behavior and issue cryptographically signed credentials as SD-JWT VCs. Agents present these credentials, bound to a key they hold, when accessing services. Service Providers verify credentials offline and make access decisions based on verified trust signals across four categories: identity, reputation, compliance, and assurance. There are no tiers; a Service Provider sets how strongly it verifies from the signals and the risk of the action.

Built on open standards (SD-JWT VC, the key-binding JWT, and the IETF Token Status List), TSAI complements existing agentic protocols like MCP and A2A without replacing them. The protocol is designed for incremental adoption—Service Providers start with simple offline verification and add stronger checks only where the risk of the action calls for them. TSAI is stewarded by AWS with key industry partners.

---

## Repository Structure

### Concept Documentation (`concept/`)

High-level protocol design and rationale. These documents define the conceptual foundation for TSAI and are intended for protocol designers, implementers, Trust Authority developers, integrators on the Service Provider side, and security reviewers.

- **[00-problem-statement.md](./concept/00-problem-statement.md)** - Problem definition, scope, and boundary conditions
- **[01-trust-signals.md](./concept/01-trust-signals.md)** - Catalog of potential trust signals (comprehensive, not all normative)
- **[02-high-level-concept.md](./concept/02-high-level-concept.md)** - Protocol overview, signal categories, security model, and key principles
- **[04-implementation-roadmap.md](./concept/04-implementation-roadmap.md)** - Phased implementation plan from proof of concept to maturity
- **[05-economic-model.md](./concept/05-economic-model.md)** - Revenue streams, growth opportunities, and adoption multipliers

### Architecture Specification (`architecture/`)

Normative technical specification defining the TSAI protocol. These documents specify conformance requirements for Trust Authorities, Agents, and Service Providers implementing TSAI.

- **[01-introduction.md](./architecture/01-introduction.md)** - Scope, conformance classes, terminology, and design rationale
- **[02-tsai-ontology.md](./architecture/02-tsai-ontology.md)** - The operator and agent domain model and how signals attach to each
- **[03-credential-format.md](./architecture/03-credential-format.md)** - SD-JWT VC credential structure, the four signal categories, and the schema
- **[04-verification.md](./architecture/04-verification.md)** - Normative verification algorithm: issuer signature, key-binding, and freshness
- **[05-protocol-integration.md](./architecture/05-protocol-integration.md)** - Integration patterns with MCP, A2A, W3C AI Agent Protocol, and HTTP-based protocols
- **[06-security-privacy.md](./architecture/06-security-privacy.md)** - Trust model, security requirements, threat analysis, and privacy considerations
- **[07-references.md](./architecture/07-references.md)** - Normative and informative references to W3C and IETF specifications
- **[07-trust-authority-apis.md](./architecture/07-trust-authority-apis.md)** - Trust Authority API design rationale and operational context
- **[08-signal-profiles.md](./architecture/08-signal-profiles.md)** - Verifier-side signal profiles, with the identity floor as the base
- **[openapi/trust-authority-api.yaml](./architecture/openapi/trust-authority-api.yaml)** - OpenAPI 3.1 specification for Trust Authority APIs (issuance, refresh, status, repudiation, well-known endpoints)
- **schemas/** - JSON schemas for credential validation and protocol extensions
  - [tsai-credential.schema.json](./architecture/schemas/tsai-credential.schema.json) - Credential (SD-JWT VC payload) structure
  - [key-binding-jwt.schema.json](./architecture/schemas/key-binding-jwt.schema.json) - Key-binding JWT claims set
  - [mcp-capability-tsai.schema.json](./architecture/schemas/mcp-capability-tsai.schema.json) - MCP capability declaration
  - [a2a-agent-card-tsai.schema.json](./architecture/schemas/a2a-agent-card-tsai.schema.json) - A2A agent card extension
  - [tsai-type-metadata.schema.json](./architecture/schemas/tsai-type-metadata.schema.json) - Type-metadata document structure
  - [tsai-ta-status.schema.json](./architecture/schemas/tsai-ta-status.schema.json) - Decoded operational-report JWS payload
  - [tsai-ta-hsm-attestation.schema.json](./architecture/schemas/tsai-ta-hsm-attestation.schema.json) - Decoded HSM-attestation JWS payload
  - [example-ta-tsai-credential.schema.json](./architecture/schemas/example-ta-tsai-credential.schema.json) - Illustrative derived TSAI credential schema
- **type-metadata/** - Canonical and illustrative derived per-`vct` Type Metadata
- **test-vectors/** - Key-binding JWT freshness, derived-`vct`, and signed TA publication vectors exercised by the checker

### Tooling (`tools/`)

- **[tools/check.py](./tools/check.py)** - Conformance checker. Validates the JSON schemas as Draft 2020-12, every JSON example in the documents against its schema, Type Metadata and schema inheritance and integrity, the test vectors, internal cross-references, and the OpenAPI servers block. Run `python3 tools/check.py` before pushing; it requires `jsonschema`, `pyyaml`, and `cryptography`.

### Architecture Decision Records (`decisions/`)

Documented design decisions with rationale and alternatives considered:

- **[001-agent-delegation-mechanism.md](./decisions/001-agent-delegation-mechanism.md)** - Whether and how Agents delegate to other Agents
- **[002-centralized-trust-authorities.md](./decisions/002-centralized-trust-authorities.md)** - Professional TAs vs. web-of-trust
- **[003-w3c-verifiable-credentials.md](./decisions/003-w3c-verifiable-credentials.md)** - Standards-based credential format (superseded by ADR 015)
- **[004-tiered-trust-model.md](./decisions/004-tiered-trust-model.md)** - Four-tier approach matching signals to risk (superseded by ADR 016)
- **[005-signaling-vs-enforcement.md](./decisions/005-signaling-vs-enforcement.md)** - Protocol defines signals, Service Providers decide
- **[006-did-methods.md](./decisions/006-did-methods.md)** - DID method selection for TAs and Agents (superseded by ADR 017)
- **[007-short-lived-credentials.md](./decisions/007-short-lived-credentials.md)** - Short-lived credentials (amended by ADR 018)
- **[008-user-privacy-and-sybil-prevention.md](./decisions/008-user-privacy-and-sybil-prevention.md)** - End-user delegation deferred to v2.0
- **[009-timestamp-based-replay-prevention.md](./decisions/009-timestamp-based-replay-prevention.md)** - Timestamp-based replay prevention (amended by ADR 018)
- **[010-fail-closed-with-degraded-mode.md](./decisions/010-fail-closed-with-degraded-mode.md)** - Fail-closed verification with degraded-mode fallback
- **[011-ta-operational-transparency.md](./decisions/011-ta-operational-transparency.md)** - TA-published operational status reports
- **[012-service-provider-terminology.md](./decisions/012-service-provider-terminology.md)** - "Service Provider" terminology and conventions
- **[013-vp-jwt-claim-structure.md](./decisions/013-vp-jwt-claim-structure.md)** - VP-JWT claim structure (superseded by ADR 015)
- **[014-holder-binding-and-web-bot-auth-integration.md](./decisions/014-holder-binding-and-web-bot-auth-integration.md)** - Self-contained key binding and request binding; Web Bot Auth kept orthogonal
- **[015-credential-serialisation-format.md](./decisions/015-credential-serialisation-format.md)** - SD-JWT VC format, holder-directed issuance, and Type Metadata (supersedes ADR 003)
- **[016-trust-signal-structure.md](./decisions/016-trust-signal-structure.md)** - Flat four-category signal model, identity floor, and reputation semantics (supersedes ADR 004)
- **[017-party-identity-and-key-discovery.md](./decisions/017-party-identity-and-key-discovery.md)** - HTTPS issuer, `cnf`-key agent, `did:web` third parties (supersedes ADR 006)
- **[018-verification-strength-and-replay.md](./decisions/018-verification-strength-and-replay.md)** - Verification strength, replay, and the 30-minute lifetime without tiers (amends ADR 007 and ADR 009)

---

## Quick Start

**For Newcomers:**
1. Review [concept/02-high-level-concept.md](./concept/02-high-level-concept.md) - Understand the signal categories and security approach

**For Implementers:**
1. Review [architecture/01-introduction.md](./architecture/01-introduction.md) - Understand scope and conformance
2. Study [architecture/openapi/trust-authority-api.yaml](./architecture/openapi/trust-authority-api.yaml) - Trust Authority API specification
3. Study [architecture/03-credential-format.md](./architecture/03-credential-format.md) - Credential structure and claims
4. Implement [architecture/04-verification.md](./architecture/04-verification.md) - Start with offline verification
5. Use [architecture/schemas/](./architecture/schemas/) - JSON schemas for validation

**For Protocol Designers:**
1. Read [concept/00-problem-statement.md](./concept/00-problem-statement.md) - Problem definition and scope
2. Review [decisions/](./decisions/) - Understand design rationale and trade-offs
3. Study [architecture/06-security-privacy.md](./architecture/06-security-privacy.md) - Security model and limitations

---

## Key Principles

- **TSAI signals, Service Providers decide** - Protocol defines trust signals; Service Providers interpret them and make access decisions
- **Lightweight yet secure** - Offline verification for the common case; stronger checks where the risk of the action calls for them
- **Standards-based** - SD-JWT VC, the key-binding JWT, and HTTPS issuer discovery for interoperability
- **Incremental adoption** - Start with identity signals; add reputation, compliance, and assurance as they become available
- **Honest about limitations** - Credentials don't prevent LLM vulnerabilities or all Agent misbehavior
- **Stewarded by AWS with key partners** - Vendor-neutral by design: any Trust Authority can issue, and any Service Provider chooses which to trust

---

## Status

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

TSAI is stewarded by AWS with key industry partners.

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
