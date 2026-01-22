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

The protocol must define its scope: what TSAI specifies vs. what platforms implement. Two philosophical approaches:

1. **Enforcement framework:** Protocol mandates how platforms must use trust signals and enforce constraints
2. **Signaling protocol:** Protocol defines trust signals; platforms decide how to use them

This decision affects protocol complexity, platform flexibility, adoption barriers, and security model.

---

## Options Considered

### Option 1: Enforcement Framework

**Description:** Protocol mandates how platforms must use trust signals and enforce constraints.

**Pros:**
- Consistent behavior across platforms
- Clear security guarantees
- Easier for agents (predictable behavior)

**Cons:**
- Complex protocol (must specify enforcement details)
- Inflexible (platforms can't adapt to their needs)
- Stifles innovation (no experimentation)
- False security (protocol can't actually enforce)
- High adoption barrier (platforms must implement exactly as specified)

---

### Option 2: Signaling Protocol

**Description:** Protocol defines trust signals; platforms decide how to use them.

**Pros:**
- Simple protocol (focused on credentials)
- Flexible (platforms adapt to their needs)
- Enables innovation (experimentation encouraged)
- Honest scope (explicit about limitations)
- Lower adoption barrier (integrate as fits platform)

**Cons:**
- Inconsistent behavior across platforms
- No guaranteed enforcement
- Agents face different policies per platform
- Requires platform expertise

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

**Core principle:** "TSAI signals, platforms decide."

**Protocol specifies:**
- Credential structure and format
- Trust signal semantics (what claims mean)
- Verification mechanisms (how to check authenticity)
- Standard constraint profiles (for interoperability)

**Platform decides:**
- Which TAs to trust (allowlist)
- How to interpret trust signals
- Whether to enforce constraints
- What access to grant
- How to monitor and respond to agent behavior

**Rationale:**

### Protocol Simplicity

Signaling approach keeps protocol focused on credential format and claim semantics. No need to specify platform architecture or implementation. Platforms integrate TSAI in ways that fit their systems. Protocol remains focused and maintainable.

### Platform Flexibility

Different platforms have different needs. High-security platforms use strict interpretation and enforce all constraints. Experimental platforms use signals for monitoring only with gradual enforcement rollout. Discovery platforms use reputation for ranking and ignore constraints. Signaling approach enables all these use cases.

### Evolution and Learning

Ecosystem needs to learn how to interpret reputation scores, when to require economic stake, which constraints to enforce, and how to balance security and usability. Signaling approach allows platforms to experiment with different interpretations. Best practices emerge from implementation experience. Protocol doesn't need to change as practices evolve.

### Honest Scope

Reality: Protocol cannot enforce anything—only platforms can. Signaling approach is explicit about what protocol provides (trust signals) and doesn't provide (behavioral guarantees). Prevents false security assumptions. Honest about limitations.

### Security Model

TSAI provides cryptographic authenticity, semantic clarity, and revocation mechanisms. TSAI does NOT provide guarantee agent will behave correctly, enforcement of constraints, or protection against all attacks. Security model: TSAI signals enable informed decisions, platforms implement defense-in-depth.

---

## Example: Constraint Profiles

### Protocol Says

"Credential contains claim `authorizedConstraintProfile: ecommerce-standard-t1`. This profile is defined as:
- Operations: [browse, search, add_to_cart]
- Max transaction value: €500
- Rate limit: 100 requests/hour

TA asserts agent is authorized for this profile."

### Platform Decides

**Questions platforms answer:**
- Do I enforce these constraints? (Recommended: yes)
- How do I enforce? (API gateway, middleware, application layer)
- What if agent exceeds? (Reject, log, alert, revoke)
- Do I trust this TA's assertion? (Check TA allowlist)
- Do I require additional constraints? (Platform-specific rules)

### Recommendations Document Suggests

"Platforms should enforce constraint profiles to limit damage from compromised agents. See implementation patterns in section X."

**Note:** Recommendations are non-normative (guidance, not requirements).

---

## Consequences

### Positive

- **Simple protocol:** Focused on credential format and semantics
- **Platform flexibility:** Integrate TSAI in ways that fit existing systems
- **Innovation:** Platforms experiment with different interpretations
- **Evolution:** Best practices emerge without protocol changes
- **Honest scope:** Explicit about what protocol provides and doesn't provide

### Negative

- **Inconsistent behavior:** Different platforms interpret signals differently
- **No guaranteed enforcement:** Platforms may ignore constraints
- **Agent complexity:** Must understand different platform policies
- **Security variability:** Platform security depends on implementation quality

### Neutral

- **Recommendations document:** Captures best practices (non-normative)
- **Ecosystem learning:** Practices evolve based on implementation experience
- **Platform responsibility:** Platforms own security decisions and outcomes

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

**Platform Implementation:**
- Choose which TAs to trust (allowlist)
- Decide how to interpret signals (policy)
- Implement verification (offline/online)
- Enforce constraints (recommended)
- Monitor agent behavior (required)

**TA Implementation:**
- Issue credentials with trust signals
- Define evaluation methodology
- Provide revocation mechanisms
- Support real-time verification (T2/T3)

---

## References

- TSAI Design Considerations (concept/archive/01-design-considerations.md)
- TSAI High-Level Concept (concept/02-high-level-concept.md)
- "TSAI signals, platforms decide" principle
