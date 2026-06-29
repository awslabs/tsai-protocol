<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR XXX: Credential Serialisation Format

**Status:** Proposed  
**Date:** 2026-06-29  
**Deciders:** TSAI Working Group (pending)  
**Relationship to ADR 003:** may supersede [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md), depending on the option chosen  
**Depended on by:** the holder-binding decision (draft-xx1); carries the signal structure (draft-xx3)

---

## Context

ADR 003 chose W3C Verifiable Credentials 2.0, secured as VC-JWT (VC-JOSE-COSE). Two developments since then make the format worth revisiting. First, the holder-binding direction in draft-xx1 rests on a key the agent controls and on JWK thumbprints, which is the native idiom of the JOSE and SD-JWT world rather than the JSON-LD world. Second, the WBA and Visa TAP ecosystems that TSAI agents are likely to run already use JWKs and SHA-256 thumbprints, so a format whose holder key is a JWK reuses that material directly.

The format determines how two things are serialised: the self-contained binding from draft-xx1 (a VP-JWT, a key-binding JWT, or a bespoke proof-of-possession signature), and the trust signals from draft-xx3. This ADR records the format options and their trade-offs. It does not settle the binding mechanism or the signal structure, which are decided in their own ADRs.

---

## Decision Criteria

1. **Holder-binding fit.** How naturally the format expresses the self-contained binding and the key the credential is bound to.
2. **Selective disclosure.** Whether the holder can present a subset of the signals without revealing the rest.
3. **Standards alignment and key reuse.** Whether the holder key is a JWK identified by a thumbprint, so it is the same material WBA and TAP already use.
4. **Revocation.** The maturity and cost of the revocation mechanism the format brings.
5. **Weight and implementer simplicity.** Payload size and how much supporting structure the format imports beyond a plain signed token.
6. **Ecosystem and tooling maturity.** Availability of libraries, validators, and deployed practice.
7. **Continuity with ADR 003.** How far the option departs from the current decision.

---

## Options Considered

### Option A: W3C VC 2.0 with a VP-JWT (status quo, ADR 003)

The credential is a W3C VC 2.0 secured as VC-JWT; the self-contained binding is the VP-JWT.

**Pros.** No change from ADR 003 (criterion 7). Mature data model, broad ecosystem, and an established revocation mechanism in BitstringStatusList (criteria 4 and 6). The holder key can still be a JWK.

**Cons.** It imports the JSON-LD context and the W3C processing rules into a setting otherwise built around keys and JWTs, which is weight without a matching benefit here (criterion 5). Selective disclosure is not native to the base model and needs additional primitives such as BBS (criterion 2). The idiom is further from the JWK and thumbprint material that WBA uses (criterion 3).

### Option B: SD-JWT VC

The credential is an SD-JWT VC (IETF `draft-ietf-oauth-sd-jwt-vc`, built on RFC 9901); the self-contained binding is the key-binding JWT, and the holder key is the `cnf` claim.

**Pros.** JWT-native, so the binding is a key-binding JWT and the holder key is a JWK identified by a thumbprint, the same material WBA and TAP use (criteria 1 and 3). Selective disclosure is native (criterion 2). Revocation uses the IETF Token Status List, and issuer discovery uses the `jwt-vc-issuer` well-known endpoint (criterion 4). Lighter than the JSON-LD model (criterion 5).

**Cons.** It departs from ADR 003 (criterion 7) and brings its own OAuth-world conventions, such as the `vct` type claim and the `application/dc+sd-jwt` media type, which the team would need to adopt. Its tooling is younger than the W3C VC ecosystem, and the specification is still an IETF draft (criterion 6).

### Option C: Minimal TA-signed JWT

The credential is a plain TA-signed JWT carrying the signals and a `cnf` key, with no VC data model.

**Pros.** The smallest and most WBA-native option, with the least to implement and the holder key as a JWK (criteria 1, 3, 5). Simple to implement and to validate.

**Cons.** It forgoes selective disclosure, the verifiable-credential data model, and the standards-alignment that lets TSAI credentials interoperate with the wider VC ecosystem (criteria 2, 6). Revocation, issuer discovery, and type semantics would all be bespoke, which is work the other options get from their standards (criterion 4). It departs furthest from ADR 003 (criterion 7).

---

## Comparison

The table summarises the per-criterion standing; the prose above gives the detail. Entries are relative, not absolute.

| Criterion | A W3C VC + VP-JWT | B SD-JWT VC | C minimal JWT |
|---|---|---|---|
| 1 Holder-binding fit | workable | strong | strong |
| 2 Selective disclosure | needs add-on | native | none |
| 3 Standards alignment and key reuse | partial | strong | strong |
| 4 Revocation | mature (BitstringStatusList) | mature (Token Status List) | bespoke |
| 5 Weight and simplicity | imports JSON-LD | JWT-native | plain JWT, smallest |
| 6 Ecosystem maturity | strongest | growing, still a draft | none beyond plain JWT |
| 7 Continuity with ADR 003 | unchanged | departs | departs furthest |

The trade is between the maturity and continuity of the W3C model and the JWT-native fit of SD-JWT VC. Option A keeps everything decided in ADR 003 and the most mature tooling, at the cost of importing JSON-LD weight and a weaker fit with the JWK material WBA uses. Option B aligns the credential with the binding direction and the WBA ecosystem and adds native selective disclosure, at the cost of leaving the W3C ecosystem for a younger draft. Option C is the smallest and most WBA-native, but it gives up the data model and the standards that the other two get revocation, discovery, and interoperability from.

---

## Decision

Open. This ADR recommends nothing. It records the format options and their pros and cons for the working group to weigh. The chosen option and its rationale will be recorded here on acceptance.

---

## Consequences

The consequences depend on the option chosen.

- **Option A** keeps ADR 003 in force and changes nothing in the data model; selective disclosure, if needed, is a later addition.
- **Option B** supersedes ADR 003. The self-contained binding becomes a key-binding JWT, revocation moves to the Token Status List, issuer discovery moves to the `jwt-vc-issuer` endpoint, and the team adopts the `vct` type claim and the `application/dc+sd-jwt` media type.
- **Option C** supersedes ADR 003 and commits TSAI to specifying revocation, issuer discovery, and type semantics itself.

The holder key is a JWK under all three options, so the key reuse described in draft-xx1 holds regardless of the format. The signal structure from draft-xx3 is carried as claims under any of the three.

---

## Dependencies

- **draft-xx1 (holder binding).** The concrete form of the self-contained binding is format-specific: a VP-JWT under A, a key-binding JWT under B, a bespoke proof-of-possession signature under C. The binding requirement is written to hold across all three, so the binding mechanism can be chosen before the format, but the format must be settled before implementation.
- **draft-xx3 (trust signal structure).** The signals are serialised as claims in whichever format is chosen; the structure is independent of the format.
- **ADR 003.** This ADR revisits the format ADR 003 decided, and Options B and C would supersede it.

---

## References

- [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)
- draft-xx1 — Holder Binding and Web Bot Auth Integration (this branch)
- draft-xx3 — Trust Signal Structure (this branch)
- [draft-ietf-oauth-sd-jwt-vc](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc)
- [RFC 9901 — Selective Disclosure for JSON Web Tokens (SD-JWT)](https://www.rfc-editor.org/rfc/rfc9901)
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [IETF Token Status List](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-status-list)
