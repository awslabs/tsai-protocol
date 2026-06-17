<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 014: VC-JWT Claim Structure

**Status:** Accepted
**Date:** 2026-06-17
**Deciders:** TSAI Working Group

---

## Context

ADR 003 adopted W3C Verifiable Credentials with VC-JWT encoding per W3C VC-JOSE-COSE, and ADR 013 settled the equivalent question for presentations. Under VCDM 1.1 and the older VC-JWT encoding, a credential was carried inside a JWT under a `vc` claim, and selected VC fields were duplicated as JWT registered claims (`issuer` → `iss`, `credentialSubject.id` → `sub`, `validFrom` → `nbf`, `validUntil` → `exp`, `id` → `jti`). VC-JOSE-COSE changes this: the JWS payload is the credential itself, and the `vc` and `vp` claim names are prohibited.

Unlike a presentation, a TSAI credential carries no request-binding claims — it is long-lived, audience-independent, and re-presented across many requests (the per-request binding lives on the VP, see ADR 013). The only open question is therefore whether the credential is wrapped in a `vc` claim with duplicated registered claims, or is the JWS payload directly.

This decision sets the on-the-wire shape of every TSAI credential. Trust Authorities issue against it and every verifier reads against it, so it is expensive to revise once implementers build to it.

### Decision criteria

1. **Standards conformance** — fit with VC-JOSE-COSE and the VCDM 2.0 data model.
2. **Verifier complexity and tooling** — how much a verifier must build beyond an off-the-shelf JWT/JWS library.
3. **Consistency** — alignment with the presentation encoding chosen in ADR 013.

---

## Options Considered

### Option 1: Flat JWT Claims Set

The credential properties (`@context`, `type`, `issuer`, `validFrom`, `validUntil`, `credentialSubject`, `credentialStatus`, and TSAI-specific claims) are the top-level claims of the JWS payload, signed once by the issuing Trust Authority.

**Pros:** Conforms to VC-JOSE-COSE (no `vc` wrapper; `vc`/`vp` names unused). The payload maps directly to the VCDM 2.0 data model with no transformation. A verifier reads the credential fields with a standard JWS library and ordinary JSON access — no unwrap step. Matches the flat presentation structure of ADR 013, so credentials and presentations share one encoding model.

**Cons:** Implementations built to the VCDM 1.1 `vc`-wrapped encoding must change.

**Decision:** Accepted.

### Option 2: `vc`-wrapped JWT (VCDM 1.1 encoding)

The credential is nested under a `vc` claim, with `iss`/`sub`/`nbf`/`exp`/`jti` duplicated alongside it as registered claims.

**Pros:** Familiar to implementers who built against VCDM 1.1; some older libraries emit this shape by default.

**Cons:** Prohibited by VC-JOSE-COSE, which forbids the `vc`/`vp` claim names. Requires a mapping/duplication table between VC fields and registered claims, which is a recurring source of mismatch bugs (e.g. `exp` disagreeing with `validUntil`). Diverges from the presentation encoding settled in ADR 013.

**Decision:** Rejected — non-conformant with the adopted VC-JOSE-COSE securing format.

---

## Decision

The TSAI VC-JWT payload is the Verifiable Credential itself as a **flat JWT Claims Set** (Option 1). The VC properties appear as top-level claims with no `vc` wrapper; the `vc` and `vp` claim names MUST NOT appear. VC fields are not duplicated into JWT registered claims — the credential's own properties (`issuer`, `validFrom`, `validUntil`, `id`, …) are authoritative. The credential is signed once by the issuing Trust Authority with `typ: vc+jwt`. This is specified in Architecture Section 2 (Credential Format).

---

## Rationale

Against the criteria, the flat structure is the only standards-conformant option (VC-JOSE-COSE prohibits the `vc`/`vp` names), is the simplest to verify (standard JWS library, no unwrap, no claim-duplication to reconcile), and is consistent with the presentation encoding already chosen in ADR 013. The cost — a break from the VCDM 1.1 `vc`-wrapped shape — is one-time and pre-1.0.

---

## Consequences

### Positive

- Conformant with VC-JOSE-COSE: no `vc` wrapper, and the `vc`/`vp` claim names are not used.
- Verifiers read credential fields with standard JWS/JWT tooling; the payload conforms directly to the VCDM 2.0 data model with no mapping.
- One encoding model across credentials (this ADR) and presentations (ADR 013).

### Negative

- Breaking change from the VCDM 1.1 `vc`-wrapped encoding: issuers and verifiers built to that shape must update. Acceptable pre-1.0.

### Accepted Residual Risks

- Selective disclosure (BBS+, noted as a later phase in ADR 003) secures the credential through a different proof mechanism; this ADR covers the VC-JWT (JOSE) encoding and does not settle that path.

---

## References

- ADR 003: W3C Verifiable Credentials (VC-JWT encoding per VC-JOSE-COSE)
- ADR 013: VP-JWT Claim Structure
- Architecture Section 2: Credential Format
- `schemas/tsai-credential-t0.schema.json`, `schemas/tsai-credential-t1.schema.json`
- [W3C VC-JOSE-COSE](https://www.w3.org/TR/vc-jose-cose/)
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
