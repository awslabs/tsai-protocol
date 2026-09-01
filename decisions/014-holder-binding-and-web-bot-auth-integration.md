<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 014: Holder Binding and Web Bot Auth Integration

**Status:** Accepted  
**Date:** 2026-07-02  
**Deciders:** TSAI Working Group  
**Relationship to ADR 013:** reaffirms the self-contained binding approach of [ADR 013 — VP-JWT Claim Structure](./013-vp-jwt-claim-structure.md), and amends it: since ADR 015 selects SD-JWT VC, the binding is a key-binding JWT in place of ADR 013's VP-JWT claim structure  
**Depends on:** the credential serialisation format, decided separately in ADR 015  


---

## Context

TSAI credentials are issued by a Trust Authority to an agent and presented by that agent to a Service Provider. Two questions decide whether a presentation is trustworthy. The first is authenticity: did the named Trust Authority issue this credential, unmodified? That is answered by the issuer signature and is out of scope here. The second is holder binding: is the party presenting the credential the party it was issued to, and is this presentation bound to this request rather than replayed or relayed? That is the subject of this decision.

Holder binding prevents a credential from being usable as a bearer token. Without it, any party that observes a credential, including a Service Provider that legitimately received one, can re-present it elsewhere and impersonate the agent. With it, a credential is useless to anyone but the agent that controls the bound key.

### Current state

- **ADR 003** adopts W3C Verifiable Credentials 2.0 with VC-JOSE-COSE (VC-JWT) securing.
- **ADR 013** defines the presentation as a VP-JWT carrying a flat claims set: the presentation properties (`@context`, `type`, `verifiableCredential`) alongside the registered claims `iss`, `aud`, `iat`, `exp`, and `nonce`, signed once by the agent. The agent signature, with `aud` and the timing claims, provides holder binding today.
- **ADR 009** prevents replay with a timestamp the verifier validates within ±30 seconds, with optional signature tracking, and defers stronger mechanisms, challenge-response or real-time verification, to higher-assurance use. It expresses this escalation in terms of the ADR 004 tiers.
- **ADR 006** identifies the agent by a DID (`did:key` for the MVP, `did:web` in production, with `did:wba` listed as supported), whose key signs the VP-JWT.

So TSAI provides holder binding today through its own artifact, the VP-JWT, and depends on nothing external.

### What changed

Web Bot Auth (WBA) is emerging as the way cross-organisational agents authenticate to websites. It is a profile of HTTP Message Signatures (RFC 9421) in which an agent signs each HTTP request with a key published in a directory, defined across a set of IETF Internet-Drafts (`draft-meunier-web-bot-auth-architecture`, `draft-meunier-http-message-signatures-directory`) and deployed today by Cloudflare's Verified Bots. Other RFC 9421-based profiles for agentic commerce exist, with their own agent registries rather than the WBA directory; they share the signature mechanism but are not WBA, and are deliberately not enumerated here. The argument that follows rests on the WBA drafts still changing rather than on the number of such profiles: many public agents will plausibly adopt an RFC 9421 profile before they adopt TSAI.

This matters because such a signature, when present, already proves control of a key. In its current normative form it also binds the request to an audience within a freshness window. That overlaps with what the VP-JWT does for holder binding. This ADR examines whether TSAI should keep its own binding, rely on the request signature, or accept either.

### What the request signature does and does not guarantee

The current WBA drafts are specific about this. In the latest architecture draft, an agent:

- **MUST** sign at least one of `@authority` or `@target-uri` (audience binding);
- **MUST** include `created` and `expires` (freshness);
- **MUST** set `keyid` to a JWK SHA-256 thumbprint and `tag` to `web-bot-auth`.

The same drafts leave the following optional or unspecified for our purposes:

- Signing any header other than the authority and signature parameters is **MAY**. WBA does not require the agent to sign the header that holds the TSAI credential, so a conformant signature does not, by itself, bind the credential to the request.
- `expires` is only **RECOMMENDED** to be within 24 hours, a wide replay window absent a nonce.
- `nonce` is **SHOULD** for the agent and enforced only at the origin's discretion.
- `Signature-Agent` (key discovery) is **RECOMMENDED**, not mandatory; keys may instead be distributed out of band or via a public list.

There is also a version gap. Cloudflare's deployment tracks an earlier architecture revision in which audience coverage is only recommended, so the largest deployment enforces less than the latest draft mandates. The WBA documents are individual drafts, not yet working-group-adopted, and they sit alongside alternative proposals in the same space, such as Anonymous Bot Authentication (`draft-rescorla-anonymous-webbotauth`), so their normative text is still changing.

The layer beneath these profiles is more stable. HTTP Message Signatures (RFC 9421) is a published standard, as are the JSON Web Key Thumbprint (RFC 7638) and Digest Fields (RFC 9530) it relies on. WBA is one profile on top of RFC 9421, and others exist; the profiles differ, but the signature mechanism they share does not. The profiles are still changing; the mechanism beneath them is stable. TSAI can depend on the mechanism while treating any one profile as a way to use it.

A TSAI verifier therefore cannot treat the presence of a valid request signature as sufficient for holder binding. At minimum it must also confirm that the credential's key matches the signing key, that the credential header was within the signed components, that an audience component was signed, and that the freshness window is short enough.

### Scope: HTTP only

TSAI operates over HTTP, whether direct, over MCP, or over A2A. Transport is not a point of difference between the options below, so it is not among the criteria. The question is how holder binding is achieved within HTTP, and in particular whether it depends on the verifier also running WBA.

---

## Decision Criteria

1. **Binding strength.** How firmly the mechanism ties the credential, audience, freshness, and, where required, the specific request to the key the agent controls.
2. **Robustness against the underlying protocol.** Whether TSAI's guarantees depend on optional or version-dependent behaviour of a protocol TSAI does not control.
3. **Ecosystem reuse.** Whether the mechanism reuses the RFC 9421 signature that the WBA ecosystem already produces, rather than requiring a separate one.
4. **Independence from WBA availability.** Whether the mechanism works for a Service Provider that does not run WBA.
5. **Fit with the existing design.** Consistency with the issuer-holder-verifier model, DID-based identity, and the offline, single-request verification posture of ADR 009.
6. **Implementer simplicity.** Whether the mechanism minimises ambiguity, redundancy, and implementation effort across all parties — agents, Trust Authorities, and Service Providers — rather than the verifier alone.

---

## The binding requirement

Whatever the mechanism, holder binding has to establish the same things: that the party presenting the credential controls the key named as the credential's confirmation key (the `cnf` key in SD-JWT, the holder key in a W3C VC), that the presentation is bound to the audience it is sent to, that it is fresh within a short window, and that it covers the specific credential presented. For a state-changing action, and where verification and action happen in different components, it must also bind the method, target URI, and request body so an observed presentation cannot be attached to a different action. The options below are the distinct ways to meet the core holder-binding requirement, with a null baseline that does not meet it included first to show why the requirement exists.

---

## Options Considered

### Null baseline: no holder binding

The agent puts the issuer-signed credential in an HTTP header with no proof of possession. The Service Provider checks the issuer signature and reads the signals.

**Pros.** Trivial on both sides, smallest payload, and no agent signing at request time. It is the simplest possible arrangement (criterion 6).

**Cons.** The credential is a bearer token. A rogue or compromised Service Provider that received it can relay it to another Service Provider and impersonate the agent (criterion 1). It does not meet the binding requirement.

This is not a candidate. It is shown only to make clear why the requirement exists. The remaining options all meet the requirement, and differ in how.

### Option 1: Self-contained binding

The agent proves binding with its own signature over the presentation, naming the audience and a freshness window, signed by the key the credential is bound to. This is a VP-JWT today (ADR 013), or an SD-JWT VC key-binding JWT under the credential-format decision (ADR 015). Web Bot Auth, where the agent runs it, sits alongside as the agent's general authentication and is not part of TSAI's binding.

This option has **two variants**, which share a common profile and differ only in whether a request signature is also accepted.

**Pros shared by both variants.**

- Self-contained: the binding is contained in the artifact TSAI controls and verified deterministically, with no dependence on a request signature being present, conformant, or at a particular draft version (criteria 2 and 5).
- Works for any Service Provider, including those that do not run WBA (criterion 4).
- Continuous with ADR 013 and the ADR 009 replay posture (criterion 5).

**Cons shared by both variants.**

- Where the agent also runs WBA, it produces two signatures: the request signature for the Service Provider's own bot management, and the TSAI binding signature. The second is sub-millisecond, but it is duplicated work on the agent side (criterion 6).
- It does not, in itself, reuse the RFC 9421 signature the ecosystem is converging on (criterion 3). Variant 1b addresses this; variant 1a does not.

#### Variant 1a: Self-contained binding only

The self-contained signature is the only accepted form of binding. A request signature is never consulted for binding.

**Pros.** One mechanism, one verification path, and no equivalence to define between mechanisms. This is the lowest-ambiguity and lowest-redundancy binding-capable option, and a Service Provider implements exactly one binding check (criterion 6). Binding strength and robustness are those of the shared profile (criteria 1 and 2).

**Cons.** No reuse at all. An agent that already sends a conformant RFC 9421 signature must still send the self-contained binding, so the ecosystem signature does no work for TSAI (criterion 3).

#### Variant 1b: Self-contained baseline, plus an accepted RFC 9421 signature

The self-contained binding remains the mandatory baseline that every implementation supports. In addition, a Service Provider MAY accept an RFC 9421 HTTP Message Signature that meets a TSAI profile — the signed components include an audience component and the credential header, the freshness window is within a TSAI maximum, and the signing key equals the credential's confirmation key — as an equivalent to the self-contained binding. A WBA signature is the common case of such a signature.

**Pros.** Keeps the robustness and independence of the baseline (criteria 2 and 4), while letting a Service Provider that runs WBA reuse the agent's existing signature, so the agent can skip the second signature when it presents to such a Service Provider (criterion 3). The reuse path is defined over RFC 9421, a published standard, so it adds no normative dependence on the WBA drafts.

**Cons.** Two acceptance paths. The specification must define their equivalence precisely so the RFC 9421 path cannot be satisfied with weaker properties than the baseline, and any Service Provider that opts into the RFC 9421 path builds and tests two verification paths. This is the ambiguity and duplicated effort that criterion 6 guards against, accepted in exchange for a saved signature. The reuse is also conditional: an agent can skip its self-contained signature only when it knows the Service Provider accepts the RFC 9421 path, so an agent that cannot assume this still sends both.

### Option 2: RFC 9421 signature only

Binding rests entirely on a profiled RFC 9421 signature, such as a WBA signature. The credential is sent with no self-contained binding. The Service Provider verifies the request signature, checks that the credential header is covered and that the signing key equals the confirmation key.

**Pros.** One signature on the agent side, reusing what the WBA ecosystem already produces (criteria 3 and, on the agent side, 6). The smallest TSAI-specific addition, and the closest match to a setting where agents run WBA before adopting TSAI.

**Cons.** TSAI's only binding now depends on the request signature being applied with the right components. The WBA drafts make covering the credential header and a short `expires` optional, so TSAI must mandate them in a profile, and every verifier must enforce them; a verifier that does not reintroduces the bearer-token weakness (criteria 1 and 2). A Service Provider that does not run WBA has no way to verify binding at all (criterion 4). The protocol's security depends on a draft that is still changing and on a deployed profile, Cloudflare's, that is weaker than the latest text (criterion 2). It also departs from ADR 013 rather than building on it (criterion 5).

---

## Comparison

The table summarises the per-criterion standing; the prose above gives the detail. Entries are relative, not absolute.

| Criterion | Null | 1a self-contained only | 1b self-contained + RFC 9421 | 2 RFC 9421 only |
|---|---|---|---|---|
| 1 Binding strength | fails | strong | strong | strong only if the profile is enforced |
| 2 Robustness | n/a | strong | strong | weak; depends on the request signature's optional parts |
| 3 Ecosystem reuse | none | none | yes, conditional on the Service Provider | yes |
| 4 Independence from WBA | n/a | yes | yes | no; the verifier must run WBA |
| 5 Fit with ADR 013 | n/a | reaffirms it | extends it | replaces it |
| 6 Implementer simplicity | highest, but fails 1 | high; one mechanism | low; two paths and an equivalence | moderate; one mechanism but profile-bound and verifier-only |

The options trade off as follows. The self-contained variants (1a, 1b) keep TSAI's binding in an artifact TSAI controls, so they are strong on robustness and independence and continuous with the current design, at the price of a second signature where the agent also runs WBA. Within them, 1a is the simpler, and 1b adds conditional reuse at the cost of a second verification path and an equivalence to specify. Option 2 requires the least additional work where WBA is already present and reuses the ecosystem signature directly, but it makes TSAI's security depend on a changing profile, requires every verifier to run WBA, and leaves a Service Provider without WBA unable to verify binding. The reuse that 1b and 2 offer is the same underlying signature; the difference is whether TSAI also keeps a baseline that does not depend on it.

---

## Decision

Adopt **Variant 1a**: the self-contained binding is the only accepted form of holder binding.

The decision rests on the criteria that bear on security, binding strength (1), robustness against the underlying protocol (2), and implementer simplicity (6). A single binding mechanism with one verification path is the smallest surface for an implementation to get wrong. There is no equivalence to define between mechanisms and no optional path that a verifier could implement too loosely.

Variant 1b is not adopted. Its only advantage over 1a is reuse of an existing RFC 9421 signature (criterion 3), which saves the agent a sub-millisecond signature, and only when it presents to a Service Provider that accepts the RFC 9421 path. Against that marginal and conditional saving, 1b requires the specification to define an equivalence between two paths precisely enough that the RFC 9421 path cannot be satisfied with weaker properties than the baseline, and requires every Service Provider that opts in to build and test two verification paths. The concrete risk is a verifier that accepts a request signature which does not cover the credential header, or carries a long expiry, and so admits a relayed or replayed credential. That downgrade is created by having two paths, and it is the class of implementation flaw a single-path design removes.

Option 2 is not adopted, for the same reason more strongly. Resting binding entirely on the request signature would make TSAI's security depend on every verifier correctly enforcing a profile over an external signature whose defaults, credential-header coverage and a short expiry, are optional in the source drafts, defined in a specification that is still changing, with the largest current deployment running a weaker revision than the latest text. Wide WBA adoption is an argument for availability, not for security: it does not remove the requirement that every verifier enforce the profile correctly, and a verifier that does not reintroduces the bearer-token weakness.

Variant 1a keeps binding in an artifact TSAI defines and verifies deterministically, so none of that external enforcement is load-bearing. It also works where WBA is absent, which is a consequence of the choice rather than its motivation.

### Request binding within the self-contained path

The key-binding JWT binds the presentation to the credential (`sd_hash`), audience (`aud`), time (`iat`), and nonce. It does not by itself bind the HTTP or RPC request. Within the freshness window, a party inside the audience boundary could attach an observed presentation to a different request. The risk is material where an edge verifier forwards to an origin and on JSON-RPC transports where method and URI do not distinguish individual calls.

TSAI therefore adds an OPTIONAL `req` claim to the key-binding JWT. It carries the request method and target URI and, where a body is present, its SHA-256 Content-Digest per RFC 9530. A Service Provider MUST require and verify `req` for state-changing actions and where the verifying and acting components differ. A state-changing action also uses a Service-Provider-issued single-use nonce: `req` prevents substitution, while the nonce prevents the same bound request being replayed.

This is a deliberate extension of the RFC 9901 key-binding JWT claim set. The alternative was to adopt the RFC 9421 acceptance path rejected above. Keeping the digest inside TSAI's single self-contained artifact preserves Variant 1a's one-path design while closing the request-substitution property on which a profiled HTTP Message Signature would otherwise be stronger.

---

## Consequences

- Holder binding is the agent's self-contained signature over the presentation, and it is the only binding path a verifier implements. There is no RFC 9421 acceptance path and no equivalence between mechanisms to define.
- The key-binding JWT carries the TSAI `req` extension. It is required for state-changing and split-topology actions, with SHA-256 fixed for the body digest; reads retain the bounded-replay baseline.
- Variant 1a's strength is qualified accordingly: its standard claims do not bind the request, and `req` supplies that property without a second signature-verification path.
- The credential-format decision (ADR 015) selects SD-JWT VC, so the self-contained binding is the key-binding JWT: a holder-signed JWT carrying `aud`, `nonce`, `iat`, and `sd_hash`, appended to the credential as `‹credential›~‹KB-JWT›`. This ADR fixed the binding approach independent of format; the format decision makes it concrete.
- Relationship to ADR 013: the self-contained binding approach is reaffirmed, and ADR 013 is amended rather than retired. Because ADR 015 selects SD-JWT VC, the binding is a key-binding JWT, which replaces ADR 013's VP-JWT claim structure while the rest of that decision stands.
- Where an agent also runs WBA, it produces two signatures: the WBA request signature for the Service Provider's own bot management, and the TSAI binding signature. This duplicated signing is accepted; it is sub-millisecond and does not affect verification.
- The binding key is the credential's confirmation key, an EC/P-256 JWK used with ES256 and identified by its RFC 7638 SHA-256 thumbprint (the `cnf` key under SD-JWT VC; ADR 015). One key can serve three roles without coordination: the Web Bot Auth signing key identified by its thumbprint, the credential's `cnf`, and, where a DID string is required, a `did:jwk` or `did:key`. Variant 1a does not require the `cnf` key to equal the agent's Web Bot Auth signing key, since Web Bot Auth is not consulted for binding, though an operator may use one key for both. Because the bare-key DID forms do not rotate, durable identity and rotation are anchored above the key, at the Trust Authority or, where Web Bot Auth is used, at its key directory, so an agent can rotate keys across short-lived credentials without losing its Trust-Authority-held identity. TSAI does not depend on the `did:wba` method, which despite the shared letters is an emerging single-project method unrelated to Web Bot Auth.
- Variant 1b remains available as a forward-compatible extension. It adds only an optional acceptance path on top of this baseline, so it can be introduced later, if ecosystem reuse becomes worth the second verification path, without changing anything decided here.

---

## Dependent decision: credential serialisation format

The binding requirement here was written to hold across credential formats, so it was decided independent of the format. That format choice is recorded in ADR 015, which selects SD-JWT VC. Under that decision the self-contained binding is the ES256-signed SD-JWT key-binding JWT and the confirmation key is the EC/P-256 `cnf` JWK. Had the format been W3C VC the binding would have been a VP-JWT, and under a minimal TA-signed JWT a bespoke proof-of-possession signature; those are noted for completeness, but SD-JWT VC is the decided format.

---

## References

- [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)
- [ADR 006 — DID Methods for TAs and Agents](./006-did-methods.md)
- [ADR 009 — Timestamp-Based Replay Prevention](./009-timestamp-based-replay-prevention.md)
- [ADR 013 — VP-JWT Claim Structure](./013-vp-jwt-claim-structure.md)
- ADR 015 — Credential Serialisation Format
- [RFC 9421 — HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
- [RFC 7638 — JSON Web Key (JWK) Thumbprint](https://www.rfc-editor.org/rfc/rfc7638)
- [RFC 9530 — Digest Fields](https://www.rfc-editor.org/rfc/rfc9530)
- [RFC 9901 — Selective Disclosure for JWTs](https://www.rfc-editor.org/rfc/rfc9901)
- [draft-meunier-web-bot-auth-architecture](https://datatracker.ietf.org/doc/html/draft-meunier-web-bot-auth-architecture)
- [draft-meunier-http-message-signatures-directory](https://datatracker.ietf.org/doc/html/draft-meunier-http-message-signatures-directory)
- [draft-rescorla-anonymous-webbotauth](https://datatracker.ietf.org/doc/html/draft-rescorla-anonymous-webbotauth)
