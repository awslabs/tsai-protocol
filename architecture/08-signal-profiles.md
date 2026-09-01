<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Signal Profiles

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## 8.1 Why profiles

The flat signal list removed the tiers, and with them the one thing the tiers did well: a single label a Service Provider, an operator, and an agent could all read to know what a credential established. ADR 016 accepted that cost and noted that any human-facing progression would move elsewhere. Signal profiles are that elsewhere. A profile recovers the communicability without reintroducing a grade on the credential.

A profile is a named, versioned predicate over the signals, published by the governance body rather than carried in the credential. Because it is verifier-side and outside the credential, it puts no ordering on credentials, several profiles coexist, and a new signal type needs no renumbering.

---

## 8.2 What a profile is

A profile has a stable identifier, a version, and a predicate: a set of conditions over the signals a credential must satisfy to meet it. For example, a profile might require the identity floor, `kyc` at `enhanced` or above, and at least one compliance certification.

- A Service Provider advertises which profiles it accepts, in its discovery documents: `tsai-config.json`, the MCP capability, or the A2A extension params (Section 4).
- A Trust Authority advertises which profiles it can satisfy, so an operator knows where to enrol.
- An agent determines admissibility before it connects, by comparing the profiles a Service Provider accepts against what its credential carries.

A profile is applied by the verifier at admission; it is not an issuer obligation and not a claim in the credential. This is the distinction from the identity floor (ADR 016), which is an issuer obligation on every credential.

---

## 8.3 The base profile

The base profile is the identity floor and nothing more: a verified operator legal name, jurisdiction, verification depth, and a controlled domain. Every conforming credential satisfies it by construction, so a Service Provider that accepts only the base profile gets the accountability guarantee with no further policy. Richer profiles add conditions on reputation, compliance, and assurance.

---

## 8.4 Registry

The governance body maintains the profile registry: the identifier, version, and predicate of each profile, published at a well-known location. The registry is the mechanism the cross-authority portability of ADR 016 depends on, since a profile names signal categories and types that the registry defines. This section consolidates what earlier notes called signal-to-capability guidance and a constraint-profile registry; note that authorization constraints are delegation (ADR 001) and are not signal profiles.

---

## 8.5 Normative Requirements

- A Service Provider that uses profiles MUST evaluate a credential against the profile's predicate over the verified signals, and MUST NOT treat a profile as a grade carried in the credential.
- A Trust Authority MAY advertise the profiles it can satisfy; it MUST NOT assert a profile in a credential, since a profile is verifier-side.
- The base profile is the identity floor (ADR 016), which every credential satisfies.

---

## References

- ADR 016 (trust signal structure and identity floor), ADR 001 (delegation)
- TSAI Protocol Integration (Section 4), TSAI Credential Format (Section 2)
