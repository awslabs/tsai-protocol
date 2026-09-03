<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 015: Credential Serialisation Format

**Status:** Accepted  
**Date:** 2026-07-02  
**Deciders:** TSAI Working Group  
**Relationship to ADR 003:** supersedes [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)  
**Depended on by:** the holder-binding decision (ADR 014); carries the signal structure (ADR 016)  

> Note: the illustrative example focuses on serialisation and predates the final profile vocabulary, so it uses placeholder signal names and omits some required profile claims. It is illustrative rather than normative.


---

## Context

ADR 003 chose W3C Verifiable Credentials 2.0, secured as VC-JWT (VC-JOSE-COSE). Three things make the format worth revisiting.

First, the holder binding decided in ADR 014 rests on a key the agent controls and on JWK thumbprints, which is the idiom of the JOSE and SD-JWT world rather than the JSON-LD world. Second, the Web Bot Auth ecosystem that TSAI agents run alongside already uses JWKs and SHA-256 thumbprints. Third, the protocols TSAI sits beside — Web Bot Auth, UCP, and OpenID4VC — are JWT and JWK based, while the only JSON-LD and DID anchors in TSAI are its own earlier decisions.

### Two credential models, not one

W3C VC and SD-JWT VC are two different credential data models from two different bodies, not layers of one another. W3C VC 2.0 is a W3C Recommendation, JSON-LD based, identifying issuer and subject by DID and securing the credential with VC-JOSE-COSE or Data Integrity proofs. SD-JWT VC (IETF `draft-ietf-oauth-sd-jwt-vc-18`) is a JWT-based credential: the type is the `vct` claim, holder binding is the `cnf` key, and it does not use the W3C `@context` or `credentialSubject` structure. Choosing between them is choosing a data model, not adjusting a securing mechanism, so this decision changes the credential, the presentation, the revocation mechanism, and the identity model together.

### Maturity

The two are at different stages, and the distinction matters. The SD-JWT mechanism is published as RFC 9901. The SD-JWT VC profile built on it is working-group draft revision 18 (`draft-ietf-oauth-sd-jwt-vc-18`), not yet an RFC. W3C VC 2.0 is a finalised W3C Recommendation. So on formal finality W3C leads, while for SD-JWT the security-critical mechanism is finalised and only the credential profile is still a late-stage draft, sitting on finalised primitives (JWT, JWS, JWK, RFC 7638 thumbprints, RFC 9901, and the Token Status List).

### Adoption

Neither format has won; they occupy different strongholds. SD-JWT VC is the credential of the wallet and high-assurance identity world, including the EU Digital Identity Wallet and the OpenID Foundation's High Assurance Interoperability Profile. W3C VC is strong in self-sovereign identity and education and has large deployments. The relevant point for TSAI is narrower: the agentic-commerce protocols it must interoperate with, Web Bot Auth and UCP, are JWT-native, and UCP defines a Credential Provider role and first-class verifiable-credential support that a TSAI credential would plug into.

### Selective disclosure, minimisation, and issuer blindness

SD-JWT VC supports holder-controlled selective disclosure natively; W3C VC needs the BBS add-on for the same. Selective disclosure is retained rather than the deciding reason for the format, and the default TSAI credential remains a flat JWT without disclosure structure. TSAI prohibits issuer-generated decoy digests because the verifier exposes unmatched signal digests as the withheld-signal count.

Short lifetime does not remove the need for minimisation. A Trust Authority cannot issue exactly the signals an interaction needs without learning the destination and purpose, which would contradict TSAI's issuer-blindness property. TSAI therefore keeps the Trust Authority blind to the Service Provider. An agent may request a subset above the identity floor during issuance without naming its destination, and Type Metadata constrains what the issuer may make selectively disclosable. This gives a coarse holder-directed minimisation path at issuance and a finer holder-controlled path at presentation.

The format determines how the self-contained binding from ADR 014 is serialised, how the trust signals from ADR 016 are carried, and how their schema and disclosure controls are published.

---

## Decision Criteria

1. **Holder-binding fit.** How naturally the format expresses the self-contained binding and the key the credential is bound to.
2. **Selective disclosure.** Whether the holder can present a subset of the signals without revealing the rest, as a retained capability.
3. **Key reuse.** Whether the holder key is a JWK identified by a thumbprint, so it is the same material Web Bot Auth already uses.
4. **Revocation.** The maturity and cost of the revocation mechanism the format brings.
5. **Weight and implementer simplicity.** Payload size and how much supporting structure the format imports beyond a plain signed token.
6. **Ecosystem and tooling maturity.** Availability of libraries and deployed practice, and the standards status of the format.
7. **Continuity with ADR 003.** How far the option departs from the current decision.
8. **Idiom coherence.** Whether the credential's data model shares the JWT and JWK idiom of the binding (ADR 014) and of TSAI's neighbours, or imports a second idiom that nothing else in the stack uses.
9. **Issuer privacy and type validation.** Whether minimisation preserves destination blindness and whether base and extended credential types have machine-readable, non-weakenable validation rules.

---

## Options Considered

### Option A: W3C VC 2.0 with a VP-JWT (status quo, ADR 003)

The credential is a W3C VC 2.0 secured as VC-JWT; the self-contained binding is the VP-JWT.

**Pros.** No change from ADR 003 (criterion 7). A finalised W3C Recommendation with the broadest tooling and deployed practice (criterion 6). DID-native, so it is consistent with ADR 006 as written. The holder key can still be a JWK. Composes with other W3C credentials an agent might carry.

**Cons.** It imports the JSON-LD data model into a stack that is otherwise JWT and JWK throughout, so it is the one component using a second idiom (criterion 8), and that idiom is weight without a matching benefit here (criterion 5). Its holder binding is a VP-JWT wrapper rather than a purpose-built holder mechanism (criterion 1). Selective disclosure is not native and needs BBS (criterion 2). It is further from the JWK and thumbprint material Web Bot Auth uses (criterion 3).

### Option B: SD-JWT VC

The credential is an SD-JWT VC (`draft-ietf-oauth-sd-jwt-vc-18`, on RFC 9901); the self-contained binding is the key-binding JWT, and the holder key is the `cnf` claim.

**Pros.** JWT-native, so the binding is the key-binding JWT and the holder key is a JWK identified by a thumbprint, the same material Web Bot Auth uses (criteria 1 and 3). It shares one idiom with the binding and with the surrounding protocols, so the credential, the binding, the keys, and revocation are all JWT and JWK, with nothing to translate (criterion 8). Selective disclosure is available if needed (criterion 2). Revocation uses the IETF Token Status List, and can be omitted where short expiry suffices, since credentials are short-lived (criterion 4). Lighter than the JSON-LD model, and a flat JWT when disclosure is unused (criterion 5). The mechanism beneath it, RFC 9901, is finalised (criterion 6).

**Cons.** The VC profile is a working-group draft, not yet an RFC (criterion 6). It supersedes ADR 003 and changes the data model wholesale (criterion 7). It pulls the identity model toward key-centric, issuer via `iss` and the `jwt-vc-issuer` endpoint, holder via the `cnf` JWK, which calls for a follow-on ADR on issuer identity and discovery, since ADR 006 is DID-centric.

### Option C: Minimal TA-signed JWT

The credential is a plain TA-signed JWT carrying the signals and a `cnf` key, with no VC data model.

**Pros.** The smallest and most JWT-native option, with the least to implement (criteria 3 and 5).

**Cons.** Revocation, issuer discovery, and type semantics would all be bespoke, which are security-relevant mechanisms TSAI would have to specify and get right itself, a larger flaw surface than adopting standard ones (criteria 4 and 6). It forgoes the verifiable-credential data model and standards interoperability (criteria 6 and 8). It departs furthest from ADR 003 (criterion 7).

---

## Comparison

The table summarises the per-criterion standing; the prose above gives the detail. Entries are relative, not absolute.

| Criterion | A W3C VC + VP-JWT | B SD-JWT VC | C minimal JWT |
|---|---|---|---|
| 1 Holder-binding fit | workable, VP-JWT wrapper | strong, native KB-JWT | strong |
| 2 Selective disclosure | needs BBS | native, retained | none |
| 3 Key reuse | partial | strong | strong |
| 4 Revocation | mature (BitstringStatusList) | mature (Token Status List), optional under short expiry | bespoke |
| 5 Weight and simplicity | imports JSON-LD | flat JWT without disclosure | plain JWT, smallest |
| 6 Ecosystem and maturity | finalised Recommendation, broadest tooling | mechanism finalised (RFC 9901), profile still a draft | none beyond plain JWT |
| 7 Continuity with ADR 003 | unchanged | supersedes it | supersedes it, furthest |
| 8 Idiom coherence | second idiom (JSON-LD) | one idiom with binding and neighbours | JWT, but non-standard |

---

## Decision

Adopt **Option B**, SD-JWT VC.

This was a close decision, and it is worth setting out the tensions rather than presenting it as clear-cut, so a later reader can judge whether the trade still holds.

The deciding axis is idiom coherence. The credential should share one idiom with the binding it carries and the protocols it sits beside. The binding decided in ADR 014 is a key-bound JWT, and TSAI's neighbours, Web Bot Auth, UCP, and OpenID4VC, are JWT and JWK based. SD-JWT VC makes the credential, the binding, the keys, and revocation one idiom: the holder key is the `cnf` JWK, which is the same key material Web Bot Auth signs with, so nothing needs translating between layers. Option A would leave the credential in JSON-LD, foreign to everything else in the stack, and would express binding as a VP-JWT wrapper rather than the native key-binding JWT.

Three tensions run against that choice, and the decision accepts them knowingly:

- **Finality against coherence.** W3C VC 2.0 is a finished Recommendation, while the SD-JWT VC profile is still a working-group draft. Choosing B accepts a profile that can still change for the sake of fit. What softens the tension is that the mechanism beneath, RFC 9901, is finalised, so the cryptography is stable and only the profile is in motion.
- **Continuity against fit.** Option A changes nothing, whereas B supersedes ADR 003 and calls for a follow-on ADR on issuer identity and discovery, since ADR 006 is DID-centric. The data-model change is a real cost, not a formality. It is justified because TSAI is defined by its interoperability, so fit with the surrounding protocols outweighs the cost of change; for a protocol that did not live among other protocols, the balance could go the other way.
- **First impression against actual shape.** SD-JWT reads as bloated because of the digests and disclosures that selective disclosure adds. That is fair when disclosure is used, but TSAI does not use it by default, so the credential it ships is a flat JWT, and in that form it is simpler than the W3C VC-JWT it replaces. The complexity sits in a feature TSAI mostly leaves off, not in the baseline.

Two further qualifications matter. Selective disclosure looks like the obvious reason to choose B, and it is not the reason. It appeared decisive at first and then proved to be a nice-to-have, because short-lived, purpose-issued credentials let a Trust Authority omit what an interaction does not need. The case for B rests on idiom coherence, which is the more durable ground. And the choice ultimately rests on an assumption about where TSAI lives: that its future is beside the JWT-native agentic-commerce and wallet protocols rather than the JSON-LD and DID self-sovereign-identity world. On today's evidence that assumption favours B, but if the surrounding ecosystem shifts toward the self-sovereign-identity world, Option A would have been the better choice, and that assumption is the thing to re-examine later.

Option C was not chosen for the reason that decided ADR 014: inventing revocation, issuer discovery, and type semantics is a larger security-flaw surface than adopting standardised ones.

### Holder-directed issuance

`IssueRequest` carries an optional `signals` filter. It requests a subset above the identity floor without naming the Service Provider. The Trust Authority remains blind to the destination and cannot remove a signal the applicable schema requires. This replaces purpose-specific issuance, which would require the Trust Authority to learn the interaction.

### Type Metadata, schema, and derived types

TSAI publishes immutable Type Metadata and an integrity-protected JSON Schema for each `vct`. The schema is authoritative for field shape and required presence. Standard Type Metadata `claims` remains path-based; because standard paths cannot select signal-array elements by `cat` and `typ`, TSAI adds `tsai_signal_metadata` for signal disclosure and display controls. Reputation and every schema-required signal are `sd: never`.

A Trust Authority or community defining custom signals mints a derived `vct`. Its metadata uses `extends` and `extends#integrity`; its schema composes the immutable parent schema with `allOf`; and the credential carries the canonical TSAI type in `aka_vcts`, which cannot contain the primary `vct`. A child cannot relax inherited disclosure controls. The publisher defining a type retains its versioned metadata and schema while any credential or derived type refers to them. Any vocabulary, constraint, display, or disclosure change mints a new `vct`.

A Trust Authority does not insert decoy digests, so a verifier can surface the number of withheld signal elements and may reject above its policy threshold. It accepts a derived type only from an issuer it trusts and after validating the complete metadata and schema chain to the canonical TSAI type.

### TSAI v1 cryptographic profile

TSAI v1 fixes one cryptographic suite rather than offering algorithm choice. Every protocol signature uses `ES256`, and every signing JWK uses `kty` `EC` with `crv` `P-256`. This applies to issuer-signed credentials, key-binding JWTs, proof-of-control challenges, Status List Tokens, Trust Authority operational reports, and HSM attestations. Verifiers reject every other signature algorithm, key type, and curve; there is no v1 algorithm negotiation.

SHA-256 is likewise fixed for SD-JWT disclosure digests and `sd_hash`, RFC 7638 JWK thumbprints, type-metadata integrity, and RFC 9530 request content digests. The single suite gives every implementation one signing and verification path and avoids carrying alternatives without a concrete interoperability requirement. ES256 and P-256 are `Recommended+` in the JOSE registry.

ES256 is a signature algorithm, not an encryption algorithm. TSAI v1 defines no JWE or payload-encryption scheme; TLS provides confidentiality in transit, and signing keys are not reused for encryption or key agreement. Future algorithm migration is a protocol-version transition with an explicit migration period, not an extension of the v1 allowlist.

The residual cost is that TSAI depends on a credential profile that is not yet an RFC. ADR 017 settles the identity consequence: the issuer uses HTTPS `iss`, the registered agent uses persistent HTTPS `sub`, and holder binding uses the inline `cnf` JWK; TSAI does not depend on `did:wba`.

---

## Consequences

- ADR 003 is superseded.
- The self-contained binding of ADR 014 is realised as an ES256-signed SD-JWT key-binding JWT, and the holder key is the EC/P-256 `cnf` JWK.
- Revocation uses the IETF Token Status List, referenced by an optional `status` claim. Where a Service Provider relies on short expiry, `status` may be omitted.
- Trust-Authority blindness is preserved. Holder-directed issuance provides coarse minimisation without revealing the destination; selective disclosure provides fine minimisation at presentation.
- A Trust Authority does not insert decoy digests; a verifier surfaces the resulting withheld-signal count and may fail closed above its policy threshold.
- TSAI adopts the `vct` type claim and the `application/dc+sd-jwt` media type, and publishes Type Metadata for each `vct`. Standard metadata carries path-based claim controls; the TSAI profile adds signal disclosure/display controls and binds each type to an integrity-protected JSON Schema that is authoritative for format and presence. A custom extension uses a derived `vct` rooted in immutable, versioned TSAI metadata and its base schema; the publisher defining each type retains those artefacts without in-place changes.
- The trust signals from ADR 016 are carried in a single top-level `signals` claim, holding the flat list of category-discriminated objects that decision fixes. Selective disclosure is available per claim, and within the list per array element, but is unused by default, so a credential is a flat JWT and only the fields deliberately made disclosable ever appear as digests. Disclosing the `signals` claim as a whole is all-or-nothing across the list; revealing individual signals while withholding others requires the per-element form.
- The identity model under ADR 017 uses HTTPS `iss` for the issuer and required registered HTTPS `sub` for the agent; the inline `cnf` JWK is the current holder-binding key. A `did:web` issuer or agent is not used.
- Where an agent carries credentials from several Trust Authorities, each is a separate SD-JWT VC bound to the same agent `cnf` key; there is no single presentation wrapper, so carrying several together is a protocol-layer concern rather than a credential-format one.

### Illustrative structure

A minimal TSAI credential with no selective disclosure is a plain signed JWT. TSAI-specific field names, the `exp` requirement, and signal-presence rules are defined by the credential schema and Type Metadata rather than by SD-JWT VC itself. Values are illustrative. The `signals` claim follows the shape fixed in ADR 016: a flat list of objects, each carrying a category, a type, and type-specific fields.

Issuer-signed JWT (header, then payload):

```json
{ "alg": "ES256", "typ": "dc+sd-jwt", "kid": "key-1" }
```
```json
{
  "iss": "https://trust-authority.example",
  "vct": "https://tsaiprotocol.org/credential/tsai/1",
  "exp": 1781866800,
  "sub": "https://acme-corp.example/agents/shopper-v3",
  "cnf": { "jwk": { "kty": "EC", "crv": "P-256", "x": "TCAER19Zvu3OHF4j4W4vfSVoHIP1ILilDls7vCeGemc", "y": "ZxjiWWbZMQGHVWKVQ4hbSIirsVfuecCE6t4jT9F2HZQ" } },
  "signals": [
    { "category": "‹category›", "type": "‹type›", "verified_at": "2026-06-14" },
    { "category": "‹category›", "type": "‹type›", "score": 0.87, "count": 3518 }
  ]
}
```

Key-binding JWT at presentation (header, then payload), signed by the `cnf` key:

```json
{ "alg": "ES256", "typ": "kb+jwt" }
```
```json
{
  "iat": 1781863260,
  "aud": "https://shop.example",
  "nonce": "3d9f1c0a8b7e4f26",
  "sd_hash": "M2lKJvuicevsgHpLmdmEjV_BlHIJpzNobRWkLgQDCls"
}
```

On the wire the presentation is `‹issuer-JWT›~‹KB-JWT›`. The issuer signature proves the signals are authentic, the key-binding JWT proves possession of the `cnf` key for this audience and this request, and `sd_hash` binds the two together. With selective disclosure in use, only the disclosed claims would move to `_sd` digests with accompanying disclosures; everything else stays as shown.

---

## Dependencies

- **ADR 014 (holder binding).** This decision makes the self-contained binding a key-binding JWT and the holder key the `cnf` JWK.
- **ADR 016 (trust signal structure).** The signals are carried as claims; the structure is independent of the format.
- **ADR 003.** Superseded by this decision.
- **ADR 006 (DID methods).** Superseded by ADR 017, which adopts HTTPS issuer discovery and the inline `cnf` JWK for the holder.

---

## References

- [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)
- [ADR 006 — DID Methods for TAs and Agents](./006-did-methods.md)
- ADR 014 — Holder Binding and Web Bot Auth Integration
- ADR 016 — Trust Signal Structure
- ADR 017 — Party Identity and Key Discovery
- [draft-ietf-oauth-sd-jwt-vc-18](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc-18)
- [RFC 9901 — Selective Disclosure for JSON Web Tokens (SD-JWT)](https://www.rfc-editor.org/rfc/rfc9901)
- [RFC 7638 — JSON Web Key (JWK) Thumbprint](https://www.rfc-editor.org/rfc/rfc7638)
- [RFC 7518 — JSON Web Algorithms](https://www.rfc-editor.org/rfc/rfc7518)
- [RFC 8725 — JSON Web Token Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)
- [RFC 6979 — Deterministic Usage of DSA and ECDSA](https://www.rfc-editor.org/rfc/rfc6979)
- [IETF Token Status List](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-status-list-21)
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
