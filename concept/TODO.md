<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI TODO

Open work items, organized by document or workstream.

---

## Trust Authority API

- Revocation endpoint (`/credentials/revoke`) and status list endpoint (`/status/{listId}`) for T2/T3
- Extend credential response schema with `statusListUrl` and `statusListIndex` for T2/T3
- Consider splitting OpenAPI spec by bounded context (issuance vs status management) if TAs deploy as separate services

## Reference Implementation

- TA credential issuance service (T0/T1)
- Agent SDK: credential lifecycle, VP-JWT creation, refresh (TypeScript, Python)
- Platform verifier library: VP-JWT parsing, DID resolution, signature verification
- Test vectors for each tier (valid, invalid, edge cases)

## Implementation Guide (Non-Normative)

- DID document and verification result caching strategies
- Clock synchronization and NTP monitoring
- Degraded mode policies and circuit breaker patterns
- Performance optimization (batch verification, parallel DID resolution)
- Operational monitoring: metrics, alerting, incident response

## Protocol Design

- TA bootstrapping: machine-readable attestations about TA practices in `/metadata` endpoint
- Credential downgrade: structured tier-to-capability mappings (e.g., T0 → read-only, T1 → read-write)
- TA cross-recognition: mechanism for TAs to accept each other's evaluations
- `did:key` → `did:web` migration: how reputation transfers when agents upgrade DID methods
- Cross-TA reputation: clarify that scores are TA-specific ordinal rankings, or define normative methodology
- Operator model edge cases: agent marketplaces (builder ≠ hoster), open-source agents, agent-of-agents

## Security

- BitstringStatusList privacy: revocation checking leaks platform identity to TA via HTTP logs; recommend caching proxies or CDN-served status lists
- DNSSEC for T2/T3: strengthen from SHOULD to MUST given `did:web` DNS dependency

## Recommendations Document (Non-Normative)

- Multi-TA trust policies
- Constraint enforcement guidance for T3
- Reputation score interpretation
- Monitoring and incident response patterns

## Constraint Profile Registry

- Standard profiles (e.g., `ecommerce-standard-t3`)
- Profile definitions: operations, limits, rate limits
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

- Threat models per tier
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

- Standardized schema for platform-to-TA misbehavior reports
- Feedback authentication
- Reputation update mechanics
- Privacy considerations

## Agent Delegation (Post-MVP)

- W3C ZCAP-LD integration
- Delegation chain verification
- Delegation revocation
- Use case examples

## Developer Experience

- T0 Quick Start: 2-3 page minimum viable spec for T0 interoperability
