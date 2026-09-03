<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 001: Agent-to-Agent Trust Delegation

**Status:** Accepted  
**Date:** 2026-01-22  
**Deciders:** TSAI Working Group  
**Amended by:** [ADR 012 — Service Provider Terminology](./012-service-provider-terminology.md)

---

## Context

Multi-agent architectures require agents to delegate tasks to other agents and establish trust chains. The protocol must support scenarios where:

1. Agent A calls Agent B's API and B needs to verify A's legitimacy
2. Agent A delegates a subtask to Agent B, and platforms need to know B is authorized by A
3. Chains of agents (A → B → C) collaborate, requiring transitive authorization

Without delegation support, each agent operates independently with no way to express "Agent B is acting on behalf of Agent A."

---

## Options Considered

### Option 1: Direct Credential Presentation (Chosen for MVP)

**Description:** Each agent has its own TSAI credential; presents it when calling other agents.

**Pros:**
- Simple, already supported by current design
- Each agent independently verified by TA
- Clear accountability
- No new protocol mechanisms needed

**Cons:**
- Doesn't capture delegation relationship
- No transitive trust

**Decision:** Use for MVP

---

### Option 2: Delegation Credentials (W3C ZCAP-LD)

**Description:** Agent A issues a delegation credential to Agent B, authorizing specific actions.

**Pros:**
- Explicit delegation chain (A → B → C)
- Fine-grained authorization
- Revocable
- Standards-based (W3C Authorization Capabilities)

**Cons:**
- Adds complexity
- Agents must be able to issue credentials
- Verification requires checking entire delegation chain

---

### Option 3: Proxy Credentials (TA-issued)

**Description:** Agent A requests TA to issue a credential for Agent B that includes "acting on behalf of A."

**Pros:**
- TA validates delegation relationship
- Single credential to verify

**Cons:**
- TA becomes bottleneck for delegation
- Less flexible
- Higher TA operational burden
- Doesn't scale

---

### Option 4: Credential + Signed Authorization

**Description:** Agent A presents its credential + a signed authorization message for Agent B.

**Pros:**
- Lightweight
- Agent A controls delegation directly

**Cons:**
- Not a standard pattern (custom protocol)
- Platforms must verify two signatures

---

## Decision

**MVP (Phase 1-2):** Direct credential presentation only (Option 1)
- Each agent presents its own TSAI credential
- No delegation mechanism in core protocol
- Sufficient for independent agent-to-agent interactions

**Phase 2+ (Optional Extension):** W3C Authorization Capabilities (ZCAP-LD) (Option 2)
- Agents can issue delegation credentials to other agents
- Delegation credentials specify authorized actions, scope, and duration
- Platforms verify: TA credential + delegation chain
- Optional protocol extension (platforms choose whether to support)

---

## Rationale

**Start simple:** MVP doesn't require delegation support. Most early use cases involve agents directly accessing platforms, not complex multi-agent workflows.

**Standards-based future:** W3C ZCAP-LD provides a proven, standards-based delegation mechanism. Adopting it as an optional extension allows the ecosystem to mature before adding complexity.

**Optional, not mandatory:** Platforms can choose whether to support delegation. This keeps the core protocol simple while enabling advanced use cases.

**Early introduction possible:** ZCAP-LD could be introduced as early as Phase 2 if demand exists, as it doesn't conflict with the core protocol.

---

## Consequences

**Positive:**
- Simple MVP enables rapid adoption
- Standards-based delegation path for future
- Clear separation between core protocol and extensions
- Platforms can adopt delegation incrementally

**Negative:**
- Multi-agent workflows not fully supported in MVP
- Platforms must implement delegation verification if they want to support it
- Delegation credentials add verification complexity

**Neutral:**
- Agents operating independently don't need delegation support
- Early adopters can experiment with ZCAP-LD before formal protocol integration

---

## Implementation Notes

**MVP:**
- No changes to core protocol
- Each agent presents own TSAI credential
- Agent-to-agent calls treated same as agent-to-platform calls

**Phase 2+ (ZCAP-LD Extension):**
- Define delegation credential format (based on W3C ZCAP-LD)
- Specify delegation chain verification algorithm
- Add delegation examples to architecture document
- Update platform integration guidance

**TODO:**
- Research W3C ZCAP-LD specification details
- Define TSAI-specific delegation credential schema
- Specify delegation chain verification requirements
- Create delegation use case examples

---

## References

- [W3C Authorization Capabilities (ZCAP-LD)](https://w3c-ccg.github.io/zcap-spec/)
- TSAI High-Level Concept (concept/02-high-level-concept.md)
