<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 012: Service Provider Terminology

**Status:** Accepted
**Date:** 2026-04-27
**Deciders:** TSAI Working Group

---

## Context

Early drafts of the TSAI specification used "Platform" as the name of the TSAI actor that receives a credential from an Agent, verifies it, and makes an access decision. As the working group entered commercial discussions with prospective implementers, three problems with this term surfaced.

The term is too broad. The specification defined a Platform as "any service or system that agents connect to — whether a merchant MCP server, another agent, an API, or a service." A term that requires that much definition to carry meaning is not pulling its weight.

The term collides with adjacent ecosystems. The W3C AI Agent Protocol uses "Service Agent" for what TSAI called a "Platform", and the TSAI integration section already had to document this mapping. More broadly, "platform" in common English evokes a multi-sided marketplace (AWS, Stripe, Shopify), which misleads readers when the actor in question is a single merchant, a single MCP server, or another agent.

The term does not resonate with implementers. Companies that would adopt TSAI — merchants, APIs, SaaS services, infrastructure middleware — identify themselves as service providers, not as platforms. The term should let an implementer place themselves on the protocol diagram without translation.

A related inconsistency had also begun to leak into the documents: the PRFAQ used "platforms" and "service providers" interchangeably in adjacent sentences.

---

## Options Considered

### Option 1: Keep "Platform", tighten the definition

Retain the existing term and make the definition more restrictive.

**Decision:** Rejected. The definition is broad because the set of entities the term refers to is genuinely heterogeneous, including other Agents. No tightening avoids the A2A collision or the commercial-resonance problem.

### Option 2: Rename to "Verifier"

Adopt the W3C Verifiable Credentials canonical role name directly.

**Pros:** Exact standards alignment; unambiguous; short.
**Cons:** Describes a software function, not a business identity. Implementers do not introduce themselves as "verifiers". Loses the commercial-narrative fit.

**Decision:** Rejected as the primary term. Retained as the lowercase name for the software component that performs verification (see Conventions below).

### Option 3: Rename to "Service Provider"

Adopt a business-oriented term that matches how prospective implementers describe themselves, with a documented bridge to the W3C Verifier role.

**Pros:** Matches implementer self-identification; covers the full range of actors (services, APIs, merchants, middleware, other Agents acting in a service role); neutralizes the A2A "Service Agent" collision (the mapping becomes Service Agent ↔ Service Provider, which is clearer than the previous Platform ↔ Service Agent); consistent with the term already leaking into business-facing documents.
**Cons:** Two words. "Service" is a somewhat overloaded word in the broader ecosystem (MCP servers, AWS services, A2A Service Agents). Mitigated by the Title-case convention and by avoiding the bare word "service" as a TSAI role term.

**Decision:** Accepted.

---

## Decision

Rename the TSAI actor previously called "Platform" to **Service Provider**.

Adopt the following terminology conventions across all TSAI-authored specification, concept, and business-facing documents.

### Actor naming

The five TSAI actors are written in Title case when they name the protocol role:

- **Trust Authority**
- **Operator**
- **Agent**
- **User**
- **Service Provider**

Common English uses of the same words remain lowercase. "The user opens a browser" is generic English; "the User provides input to the Agent" names TSAI roles.

### Actor vs. component

The Service Provider is the actor — the party, organization, or entity. The component inside a Service Provider's stack that performs credential verification is called a **verifier** (lowercase). This distinction allows accurate description of cases where verification is delegated to infrastructure — for example, a CDN or edge gateway acting as a verifier on behalf of its customer Service Providers.

### Cross-standard mapping

TSAI documents surface the mapping to adjacent standards explicitly where relevant, not implicitly through term reuse:

- W3C Verifiable Credentials: Issuer ↔ Trust Authority; Holder ↔ Agent; Verifier ↔ Service Provider.
- W3C AI Agent Protocol: Service Agent ↔ Service Provider (a W3C Service Agent that receives a TSAI credential is acting as a TSAI Service Provider).
- OAuth / OIDC: Relying Party is a close informal analogue to Service Provider.

### Compound phrasing

Hyphenated compounds that combine a multi-word proper noun with a qualifier read poorly in English. TSAI documents prefer prepositional or possessive phrasings:

- "across Service Providers" rather than "cross-Service-Provider"
- "at the Service Provider layer" rather than "Service-Provider-level"
- "specific to each Service Provider" rather than "Service-Provider-specific"
- "the Service Provider's policy" rather than "Service Provider policy" where ownership is meant
- "trust between the Agent and the Service Provider" rather than "Agent-to-Service-Provider trust"

Short idiomatic `X-to-Y` forms remain when both sides are single words. "Agent-to-agent" stays.

### Core principle restated

The protocol's guiding principle is restated accordingly:

> TSAI signals, Service Providers decide.

---

## Rationale

The rename resolves three issues at once: it removes the need for the specification to repeatedly explain what "platform" means, it eliminates the terminology collision with the W3C AI Agent Protocol's "Service Agent", and it aligns the protocol's vocabulary with the self-identification of the parties it asks to implement it.

The accompanying Title-case and compound-phrasing conventions are independent improvements that the rename made a natural moment to adopt. Title-casing defined protocol terms is standard practice in W3C and IETF specifications and visibly distinguishes term-of-art usage from ordinary English. Rewording hyphenated compounds into prepositional and possessive forms is a readability choice consistent with technical-writing convention for multi-word proper nouns.

No normative field names, schema identifiers, HTTP headers, or DID paths contain "platform", so the rename has no wire-format or API impact. Only human-language descriptions and identifiers change.

---

## Consequences

### Positive

- The protocol's term for its receiving actor matches how implementers describe themselves.
- The collision with W3C AI Agent Protocol "Service Agent" is resolved.
- The specification no longer has to define its actor as "any service or system".
- The core principle gains clarity: "Service Providers decide" correctly names who is making the decision.
- Title-casing TSAI actors consistently removes a class of ambiguity where common English words coincide with protocol roles.

### Negative

- Every TSAI-authored document requires updating. The rename covers roughly 480 occurrences in `trusted-agents-protocol/` and roughly 630 in `tsai-docs/`, most of which are in prose.
- External readers familiar with pre-1.0 drafts must learn the new term. A one-line historical note in the Terminology section mitigates this.
- The word "service" is moderately overloaded across adjacent ecosystems. The Title-case convention and the avoidance of bare "service" as a TSAI role term keep the overloading contained.

### Accepted Residual Risks

- Occasional ambiguity between "Service Agent" (W3C AI Agent Protocol) and "Service Provider" (TSAI). Mitigated by the explicit mapping in the Protocol Integration section and by the convention that a W3C Service Agent receiving a TSAI credential is a TSAI Service Provider.
- Contributors reading older drafts may continue to use "Platform". The terminology section notes the prior term explicitly.

---

## References

- Architecture Section 1.3: Terminology
- Architecture Section 4.7.2: W3C AI Agent Protocol mapping
- ADR 003: W3C Verifiable Credentials (Issuer / Holder / Verifier model)
- ADR 005: Signaling vs. Enforcement (the "signals, Service Providers decide" principle)
