<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 013: VP-JWT Claim Structure

**Status:** Superseded  
**Date:** 2026-06-11  
**Deciders:** TSAI Working Group  
**Amended by:** [ADR 014 — Holder Binding and Web Bot Auth Integration](./014-holder-binding-and-web-bot-auth-integration.md)  
**Superseded by:** [ADR 015 — Credential Serialisation Format](./015-credential-serialisation-format.md)

---

## Context

ADR 003 adopted W3C Verifiable Credentials with VC-JWT encoding per W3C VC-JOSE-COSE. Under VCDM 1.1 and the older VC-JWT encoding, a Verifiable Presentation was carried inside a JWT under a `vp` claim, with the JWT registered claims (`iss`, `aud`, `iat`, `exp`, `nonce`) sitting beside that wrapper. VC-JOSE-COSE changes this: the JWS payload is the credential or presentation itself, and the `vc` and `vp` claim names are prohibited. Removing the `vp` wrapper to conform is not in question.

What the removal forces is a separate decision. An Agent proves possession of a credential by presenting it to a specific Service Provider, once, within a short freshness window (see ADR 009). That binding requires audience, timing, and replay data — `iss`, `aud`, `iat`, `exp`, and `nonce`. With the `vp` wrapper gone, these claims need a defined home, and the options are not equivalent. They differ in how cleanly the result maps to the VCDM data model, how much verifier machinery they require, and how strongly the binding is tied to the presentation's signature.

This decision sets the on-the-wire shape of every TSAI presentation. Service Providers implement verification against it, so it is expensive to revise once implementers build to it.

### Decision criteria

1. **Standards conformance** — fit with VC-JOSE-COSE and the VCDM 2.0 data model.
2. **Verifier complexity and tooling** — how much a Service Provider must build beyond an off-the-shelf JWT/JWS library.
3. **Binding strength** — how firmly audience, freshness, and single-use are tied to the Agent's signature over the presentation.
4. **Fit with existing TSAI design** — consistency with offline T0/T1 verification and the timestamp-based replay model of ADR 009.

---

## Options Considered

### Option 1: Flat JWT Claims Set

The VP properties (`@context`, `type`, `verifiableCredential`) and the JWT registered claims (`iss`, `aud`, `iat`, `exp`, `nonce`) are all top-level claims of a single JWS payload, signed once by the Agent.

**Pros:** Conforms to VC-JOSE-COSE (no `vp` wrapper; `vc`/`vp` names unused); VCDM 2.0 permits additional properties on a presentation, so the registered claims are allowed. A Service Provider verifies it with a standard JWS library and reads the binding claims with ordinary JWT semantics — no Data Integrity proof processing, no second signature. The single Agent signature covers both the presentation and the binding claims, so audience and freshness are bound to the same signature that proves possession. Matches the offline, single-request T0/T1 model directly.

**Cons:** The payload is not a bare Verifiable Presentation — it is a presentation intermixed with request-binding claims. A consumer that strictly expects "the payload is a VP" will find non-VP claims at the top level, and the distinction must be documented to avoid confusion. The binding claims are TSAI profile conventions on the JWS, not VCDM presentation properties, so the meaning lives in this specification rather than in the data model.

**Decision:** Accepted.

### Option 2: VCDM-native presentation

Use the VCDM presentation `holder` property for the Agent identity, and express audience and replay through the proof's `challenge` and `domain` parameters, keeping the payload a pure Verifiable Presentation.

**Pros:** Cleanest data-model fit — the payload is unambiguously a Verifiable Presentation, with binding expressed through proof parameters defined for exactly that purpose. Audience and challenge are part of the proof, so binding is tied to the signature by construction.

**Cons:** `challenge` and `domain` are well defined for Data Integrity proofs but not cleanly specified for the JWS/JOSE proof path that VC-JOSE-COSE uses; placing them requires profile design that the standard does not settle for us. Tooling for this path is thin, so Service Providers would build non-standard verification rather than reuse a JWT library. This is design and specification effort, not an editorial change, and it raises the verifier cost — against criteria 2 and, given the unsettled standard, criterion 1.

**Decision:** Rejected for 1.0. Revisitable if VC-JOSE-COSE tooling and the JWS proof-parameter story mature.

### Option 3: Outer request envelope

Wrap a clean VP-JWT inside a second, outer JWS (the request envelope) that carries `iss`, `aud`, `iat`, `exp`, and `nonce`. The inner object is a pure presentation; the outer object carries request binding.

**Pros:** Cleanest separation of concerns — the presentation and the request that carries it are distinct, independently signed objects. Each layer validates against its own schema, and the inner VP stays a pure VP.

**Cons:** Two signatures and two verification passes for every request, against a model (ADR 009) deliberately built for a single offline request with minimal state. Larger payloads and an additional schema. The separation is real but buys little here: TSAI presents exactly one credential to one Service Provider per request, so there is no independent reuse of the inner VP that would justify the second layer. Heaviest option on criteria 2 and 4.

**Decision:** Rejected for 1.0. Remains available later if a use case emerges that reuses the inner presentation independently of the request.

---

## Decision

The TSAI VP-JWT payload is a **flat JWT Claims Set** (Option 1). The VP properties appear as top-level claims with no `vp` wrapper, alongside the JWT registered claims `iss`, `aud`, `iat`, `exp`, and `nonce`, which bind the presentation to a specific Service Provider request. The payload is signed once by the Agent. This is specified in Architecture Section 3.3.5 and constrained by `schemas/verifiable-presentation.schema.json`.

---

## Rationale

Against the stated criteria, the flat structure wins on verifier complexity, binding strength, and fit with the existing design, and is conformant on standards; its cost is conceptual cleanliness, the weakest of the four dimensions for a 1.0 whose priority is to get verifiers implementing.

The VCDM-native option is conceptually superior but depends on a part of VC-JOSE-COSE that is not settled enough to build on without original profile work; choosing it would trade a documentation note for a research effort and a non-standard verifier. The envelope option pays a permanent two-signature cost for a separation that TSAI's one-credential-per-request model does not need. The flat structure lets a Service Provider verify a presentation with a standard JWS library and read the binding claims as ordinary JWT claims, and it keeps the audience and freshness data under the same Agent signature that proves possession — which is exactly what the replay model in ADR 009 relies on.

The cost is named and bounded: the payload is not a bare presentation, and that is made explicit in the specification and the schema so no reader has to infer it.

---

## Consequences

### Positive

- Service Providers verify presentations with standard JWS/JWT tooling; no Data Integrity proof processing and no second signature.
- Audience, freshness, and single-use are bound to the same Agent signature that proves credential possession.
- Consistent with the offline, single-request T0/T1 verification and timestamp replay model of ADR 009.
- Conformant with VC-JOSE-COSE: no `vp` wrapper, and the `vc`/`vp` claim names are not used.

### Negative

- The payload is a presentation intermixed with request-binding claims, not a bare Verifiable Presentation. The specification and schema state this explicitly so the structure is not mistaken for a pure VP.
- The binding claims are TSAI profile conventions on the JWS rather than VCDM presentation properties; their meaning is defined here, not by the data model.

### Accepted Residual Risks

- A future move to selective disclosure (BBS+, noted as a later phase in ADR 003) places the credential proof inside the VC while the request binding stays on the outer JWS. That split is workable but will need its own treatment; this ADR does not settle it.
- A strict VCDM consumer that expects the payload to validate as a presentation will reject the extra claims. TSAI presentations are consumed by TSAI verifiers built to this specification, so this is acceptable for 1.0.

---

## References

- ADR 003: W3C Verifiable Credentials (VC-JWT encoding per VC-JOSE-COSE)
- ADR 009: Timestamp-Based Replay Prevention
- Architecture Section 3.3.5: Verifiable Presentation Verification
- `schemas/verifiable-presentation.schema.json`
- [W3C VC-JOSE-COSE](https://www.w3.org/TR/vc-jose-cose/)
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
