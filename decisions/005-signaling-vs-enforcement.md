<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 005: Signaling vs. Enforcement (Protocol Scope)

**Status:** Accepted  
**Date:** 2026-01-22  
**Deciders:** TSAI Working Group

---

## Context

The protocol must define its scope: what TSAI specifies vs. what Service Providers implement. Two philosophical approaches:

1. **Enforcement framework:** Protocol mandates how Service Providers must use trust signals and enforce constraints
2. **Signaling protocol:** Protocol defines trust signals; Service Providers decide how to use them

This decision affects protocol complexity, Service Provider flexibility, adoption barriers, and security model.

---

## Options Considered

### Option 1: Enforcement Framework

**Description:** Protocol mandates how Service Providers must use trust signals and enforce constraints.

**Pros:**
- Consistent behavior across Service Providers
- Clear security guarantees
- Easier for Agents (predictable behavior)

**Cons:**
- Complex protocol (must specify enforcement details)
- Inflexible (Service Providers can't adapt to their needs)
- Stifles innovation (no experimentation)
- False security (protocol can't actually enforce)
- High adoption barrier (Service Providers must implement exactly as specified)

---

### Option 2: Signaling Protocol

**Description:** Protocol defines trust signals; Service Providers decide how to use them.

**Pros:**
- Simple protocol (focused on credentials)
- Flexible (Service Providers adapt to their needs)
- Enables innovation (experimentation encouraged)
- Honest scope (explicit about limitations)
- Lower adoption barrier (each Service Provider integrates as fits its systems)

**Cons:**
- Inconsistent behavior across Service Providers
- No guaranteed enforcement
- Agents face different policies across Service Providers
- Requires expertise on the Service Provider side

---

### Option 3: Hybrid (Mandatory Core + Optional Extensions)

**Description:** Protocol mandates core behaviors (e.g., must check expiry) but leaves advanced features optional.

**Pros:**
- Balance between consistency and flexibility
- Core security guaranteed
- Advanced features optional

**Cons:**
- Still complex (must define mandatory vs. optional)
- Ambiguous boundary (what's core vs. advanced?)
- Doesn't solve fundamental issue (protocol can't enforce)

---

## Decision

TSAI is a **signaling protocol** (Option 2), not an enforcement framework.

**Core principle:** "TSAI signals, Service Providers decide."

**Protocol specifies:**
- Credential structure and format
- Trust signal semantics (what claims mean)
- Verification mechanisms (how to check authenticity)
- Standard constraint profiles (for interoperability)

**The Service Provider decides:**
- Which TAs to trust (allowlist)
- How to interpret trust signals
- Whether to enforce constraints
- What access to grant
- How to monitor and respond to Agent behavior

**Rationale:**

### Protocol Simplicity

The signaling approach keeps the protocol focused on credential format and claim semantics. No need to specify Service Provider architecture or implementation. Each Service Provider integrates TSAI in ways that fit its systems. The protocol remains focused and maintainable.

### Service Provider Flexibility

Different Service Providers have different needs. High-security Service Providers use strict interpretation and enforce all constraints. Experimental Service Providers use signals for monitoring only with gradual enforcement rollout. Discovery-oriented Service Providers use reputation for ranking and ignore constraints. The signaling approach enables all these use cases.

### Evolution and Learning

The ecosystem needs to learn how to interpret reputation scores, when to require economic stake, which constraints to enforce, and how to balance security and usability. The signaling approach allows Service Providers to experiment with different interpretations. Best practices emerge from implementation experience. The protocol doesn't need to change as practices evolve.

### Honest Scope

Reality: the protocol cannot enforce anything — only Service Providers can. The signaling approach is explicit about what the protocol provides (trust signals) and doesn't provide (behavioral guarantees). This prevents false security assumptions and is honest about limitations.

### Security Model

TSAI provides cryptographic authenticity, semantic clarity, and revocation mechanisms. TSAI does NOT guarantee that an Agent will behave correctly, enforce constraints, or protect against all attacks. Security model: TSAI signals enable informed decisions, Service Providers implement defense-in-depth.

---

## Example: Constraint Profiles

### Protocol Says

"Credential contains claim `authorizedConstraintProfile: ecommerce-standard-t1`. This profile is defined as:
- Operations: [browse, search, add_to_cart]
- Max transaction value: €500
- Rate limit: 100 requests/hour

The TA asserts the Agent is authorized for this profile."

### The Service Provider Decides

**Questions a Service Provider answers:**
- Do I enforce these constraints? (Recommended: yes)
- How do I enforce? (API gateway, middleware, application layer)
- What if an Agent exceeds the constraint? (Reject, log, alert, revoke)
- Do I trust this TA's assertion? (Check TA allowlist)
- Do I require additional constraints? (Rules specific to the Service Provider)

### Recommendations Document Suggests

"Service Providers should enforce constraint profiles to limit damage from compromised Agents. See implementation patterns in section X."

**Note:** Recommendations are non-normative (guidance, not requirements).

---

## Consequences

### Positive

- **Simple protocol:** Focused on credential format and semantics
- **Flexibility:** Each Service Provider integrates TSAI in ways that fit its existing systems
- **Innovation:** Service Providers experiment with different interpretations
- **Evolution:** Best practices emerge without protocol changes
- **Honest scope:** Explicit about what protocol provides and doesn't provide

### Negative

- **Inconsistent behavior:** Different Service Providers interpret signals differently
- **No guaranteed enforcement:** Service Providers may ignore constraints
- **Agent complexity:** Must understand different Service Provider policies
- **Security variability:** Depends on the implementation quality of each Service Provider

### Neutral

- **Recommendations document:** Captures best practices (non-normative)
- **Ecosystem learning:** Practices evolve based on implementation experience
- **Responsibility:** Service Providers own security decisions and outcomes

---

## Implementation Notes

**Protocol Specification (Normative):**
- Credential structure (W3C VC format)
- Claim semantics (what each claim means)
- Verification mechanisms (signature checks, revocation)
- Standard constraint profiles (definitions for interoperability)

**Recommendations Document (Non-Normative):**
- How to interpret reputation scores
- When to require economic stake
- Constraint enforcement patterns
- Multi-TA trust policies
- Monitoring and incident response

**Service Provider Implementation:**
- Choose which TAs to trust (allowlist)
- Decide how to interpret signals (policy)
- Implement verification (offline/online)
- Enforce constraints (recommended)
- Monitor Agent behavior (required)

**TA Implementation:**
- Issue credentials with trust signals
- Define evaluation methodology
- Provide revocation mechanisms
- Support real-time verification (T2/T3)

---

## References

- TSAI Design Considerations (concept/archive/01-design-considerations.md)
- TSAI High-Level Concept (concept/02-high-level-concept.md)
- "TSAI signals, Service Providers decide" principle
