<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI TODO

Open work items, organized by document or workstream.

---

## Trust Authority API

- Block endpoint and agent/operator-keyed Token Status List (`status_list`) publication
- Ensure the credential `status` claim references the agent or operator status list
- Consider splitting OpenAPI spec by bounded context (issuance vs status management) if TAs deploy as separate services

## Reference Implementation

- TA credential issuance service
- Agent SDK: credential lifecycle, key-binding JWT creation, refresh (TypeScript, Python)
- Verifier library: SD-JWT VC presentation parsing, issuer key discovery (`jwt-vc-issuer`), signature verification
- Test vectors for the signal categories (valid, invalid, edge cases); include a stale key-binding JWT and a future-`iat` vector

## Implementation Guide (Non-Normative)

- Issuer-key and verification-result caching strategies (bounds per Section 3.7)
- Clock synchronization and NTP monitoring
- Degraded mode policies and circuit breaker patterns
- Performance optimization (batch verification, issuer-key caching)
- Operational monitoring: metrics, alerting, incident response

## Protocol Design

- TA bootstrapping: machine-readable attestations about TA practices in `/metadata` endpoint
- Signal-to-capability guidance: how a Service Provider might map a set of signals to capabilities (non-normative)
- TA cross-recognition: mechanism for TAs to accept each other's evaluations
- Key rotation: how reputation transfers when an agent rotates its bound key, anchored to the stable `sub`
- Cross-TA reputation: clarify that scores are TA-specific ordinal rankings, or define normative methodology
- Operator model edge cases: agent marketplaces (builder ≠ hoster), open-source agents, agent-of-agents

## Security

- Status list privacy: a Service Provider fetching the agent or operator status list touches the TA; recommend caching proxies or CDN-served lists
- DNSSEC for issuer metadata and third-party `did:web`, given the DNS dependency

## Recommendations Document (Non-Normative)

- Multi-TA trust policies
- Delegation and constraint enforcement guidance (ADR 001)
- Reputation score interpretation
- Monitoring and incident response patterns

## Delegation and Constraint Profiles (ADR 001)

These are authorization constraints (delegation), distinct from the signal profiles of Section 8.

- Standard constraint profiles for delegated authority (operations, value limits, rate limits)
- Profile versioning
- Custom profile guidance

## Protocol Integration Guide (Non-Normative)

- Implementation checklists for servers and clients
- Credential lifecycle management (refresh, expiry, storage)
- Error handling patterns (retry, circuit breakers, fallbacks)
- Integration examples for MCP and A2A
- Testing strategies and test vectors
- Performance benchmarks: issuance latency, verification latency (cold/warm), credential wire size

## Security Analysis

- Threat model across the signal categories
- Attack surfaces: TA compromise, credential theft, agent misbehavior
- Sybil resistance: preventing identity switching after bad reputation
- TA compromise incident response
- Residual risks

## Governance

- TA registry format and membership criteria
- TA accreditation process
- Dispute resolution
- Protocol evolution process
- Governance transition: consortium → independent foundation

## Feedback Protocol (Post-MVP)

- Standardized schema for misbehavior reports from Service Providers to TAs
- Feedback authentication
- Reputation update mechanics
- Privacy considerations

## User-Level Identification and Sybil Prevention (Post-MVP)

- Service Providers managing scarce resources (e.g., ticketing, limited inventory, queue-based access) need assurance that Agents represent distinct end users — not one User operating many Agents to gain unfair advantage
- TSAI v1.0 provides operator accountability and agent reputation but not end-user uniqueness
- ADR 008 explores six approaches ranging from pairwise TA-issued credentials to ZK proofs; none selected for v1.0
- Key design tension: user privacy (unlinkable pseudonyms, minimal disclosure) vs. Sybil prevention (verifiable uniqueness)
- Gather requirements from early-adopter Service Providers to inform v2.0 design
- Explore hybrid approaches: TSAI Operator/Agent identity + user verification managed by the Service Provider as complementary layers
- Evaluate maturity of privacy-preserving technologies (BBS+, ZK proofs) for feasibility in v2.0 timeframe
- Consider whether a non-normative guidance document on Sybil prevention at the Service Provider layer could bridge the gap before v2.0

## Agent Delegation (Post-MVP)

- W3C ZCAP-LD integration
- Delegation chain verification
- Delegation revocation
- Use case examples

## Developer Experience

- Quick Start: 2-3 page minimum viable spec for identity-signal interoperability
