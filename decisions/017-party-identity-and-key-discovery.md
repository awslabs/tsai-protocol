<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 017: Party Identity and Key Discovery

**Status:** Accepted  
**Date:** 2026-07-16  
**Amended:** 2026-08-26 — names the Service Provider audience, including the transport with no HTTP origin (MCP over stdio); Sections 2.4 and 4.2 are authoritative.  
**Deciders:** TSAI Working Group  
**Relationship to ADR 006:** supersedes [ADR 006 — DID Methods for TAs and Agents](./006-did-methods.md)  
**Depends on:** ADR 014 (holder binding) and ADR 015 (credential serialisation format)


---

## Context

ADR 006 identified every party by a DID: the Trust Authority by `did:web`, the agent by `did:key`, `did:web`, or `did:wba`. Three later decisions change that.

- ADR 014 makes holder binding a key-binding JWT signed by the credential's `cnf` key, so the agent's binding identity is a JWK, not a DID.
- ADR 015 adopts SD-JWT VC, which discovers the issuer's key through an HTTPS `iss` and the `jwt-vc-issuer` endpoint, and carries revocation as a `status` claim inside the credential.
- The protocols TSAI sits beside, Web Bot Auth and OpenID4VC, identify keys by JWK and RFC 7638 thumbprint.

Two functions ADR 006 assigned to DIDs are now handled without them. To verify a credential, the verifier obtains the issuer's key from the `jwt-vc-issuer` endpoint and the revocation status from the credential's own `status` claim, so it does not resolve the issuer to find either.

### The identifier problem for referenced parties

Some identifiers in a credential are not the issuer or the holder but parties the TA refers to: the certifier behind an attestation, the backer behind an assurance, the agency behind a reputation score. Two requirements apply to those identifiers. First, if two Trust Authorities reference the same party, they must use the same identifier, so its authority has to sit outside any single TA; a TA-minted identifier fails this. Second, a verifier must be able to resolve it by one defined mechanism, or it cannot act on the identifier consistently.

### Scope

This decides identity and key discovery for three roles: the issuer (Trust Authority), the holder (agent), and referenced third parties. It also names the Service Provider, the audience a presentation is addressed to. Agent-to-agent discovery and service-endpoint publication are agent-ecosystem concerns and out of scope.

---

## Decision Criteria

1. **External authority.** An identifier referenced by more than one TA is decided by the entity itself or by a neutral registry, not by any single TA.
2. **Uniform resolution.** The identifier resolves by one defined mechanism.
3. **Idiom coherence.** Consistency with the JWK idiom of the binding, the format, and the surrounding protocols.
4. **Minimal infrastructure.** A party runs no identity infrastructure it does not otherwise need.
5. **Rotation and durable identity.** Keys can rotate without losing the identity that reputation and records attach to.
6. **Discoverability the verifier needs.** The issuer key and the revocation status are obtainable without extra resolution steps.

---

## Options Considered

### Option 1: `did:web` for every party

TA, agent, and referenced parties are all `did:web`.

**Pros.** One uniform scheme, with external authority and uniform resolution for all roles, and key rotation through the DID document.

**Cons.** Key-holders do not need it. The credential already discovers the issuer key through `jwt-vc-issuer` and binds the holder through `cnf`, so a `did:web` for the TA and agent is a second idiom and a resolution step that buys nothing (criteria 3, 4). It also retains `did:wba`.

### Option 2: Key-holders by their key, referenced parties by `did:web` (decided)

- **Trust Authority:** an HTTPS `iss` with keys at `/.well-known/jwt-vc-issuer`. Key rotation is publishing a new key there.
- **Agent:** the `cnf` JWK is the identity. A stable name in `sub` is optional and, if present, is an HTTPS identifier the operator controls.
- **Referenced third parties:** their own `did:web`, one canonical DID per party.

**Pros.** Key-holders use their native key discovery, which is idiom-coherent and needs no extra infrastructure (criteria 3, 4). Referenced parties get an entity-controlled, uniformly resolvable identifier (criteria 1, 2). The verifier obtains the issuer key and the status without resolving the issuer (criterion 6). Rotation is handled by `jwt-vc-issuer` for the TA and by re-issuance against the durable identity for the agent (criterion 5).

**Cons.** Two identifier kinds in play, keys and HTTPS for the first parties and `did:web` for referenced parties. Referenced parties must publish a `did:web`. `did:web` inherits DNS, so a referenced DID can change hands over the life of a long-lived reference.

### Option 3: Referenced parties by a registry identifier

Key-holders as in Option 2, but referenced parties identified by a registry identifier such as an LEI.

**Pros.** A neutral registry supplies the external authority (criterion 1).

**Cons.** No uniform resolution: registries are heterogeneous, with no single mechanism a verifier can apply (criterion 2). Coverage is narrow, since an LEI identifies legal entities only, not individuals or unregistered parties.

---

## Comparison

| Criterion | 1 `did:web` all | 2 key + `did:web` refs | 3 registry refs |
|---|---|---|---|
| 1 External authority | met | met | met |
| 2 Uniform resolution | met | met | fails (many registries) |
| 3 Idiom coherence | second idiom for first parties | one idiom per role | one idiom per role |
| 4 Minimal infrastructure | DID for key-holders too | least | least |
| 5 Rotation / durable identity | via `did:web` | via `jwt-vc-issuer` and re-issuance | as Option 2 |
| 6 Discoverability the verifier needs | resolves DIDs | native | native |

---

## Decision

Adopt **Option 2**.

The Trust Authority is identified by an HTTPS `iss`, with its signing keys at `/.well-known/jwt-vc-issuer`. The agent is identified by its `cnf` key, with an optional `sub` that, if used, is an HTTPS identifier the operator controls. Referenced third parties are identified by their own `did:web`, and each publishes one canonical DID. `did:wba` is dropped.

The split follows a single rule: a party that holds a key in the credential is identified by that key or its discovery, the TA by `jwt-vc-issuer` and the agent by `cnf`; a party that is only referenced holds no key here and is identified by a resolvable identifier it controls, `did:web`. That gives references an authority outside any single TA and one resolution mechanism, without adding DID resolution to the parties the credential already identifies by key.

Any further identifier that a specific signal type needs, for example a legal-entity identifier for a liability-bearing party, is a schema field defined with the schema, not fixed here.

The Service Provider, the audience of a presentation, is named by its HTTPS origin in `aud`. On a transport with no HTTP origin, such as MCP over stdio, the server declares a stable audience identifier in its unauthenticated capability exchange, and the agent uses that value as `aud` (Sections 2.4 and 4.2). The identifier is stable across the server's sessions, so a presentation is bound to one audience and cannot be redirected. This extends the party-identity model to the verifier without giving it a key in the credential.

---

## Consequences

- Supersedes ADR 006. ADR 006 takes a forward pointer to this ADR; its body is unchanged except for the later TAP-to-TSAI naming rename, which was a naming purge rather than a decision change.
- The Trust Authority publishes its signing keys at `/.well-known/jwt-vc-issuer` and identifies itself by an HTTPS `iss`. A `did:web` for the TA is not used.
- The agent is identified by its `cnf` JWK; `sub`, if present, is an HTTPS identifier for continuity, not a DID.
- Referenced third parties publish one canonical `did:web` each and are referenced by it.
- Platforms no longer resolve multiple DID methods for core verification, which removes the platform-complexity cost ADR 006 accepted.
- Revocation status is read from the credential's `status` claim; issuance discovery is agent-facing and out of scope.
- `did:wba` is dropped.
- Additional per-type identifiers (such as a legal-entity identifier on an assurance signal) are optional schema fields, decided with the schema.
- The Service Provider is named by its HTTPS origin in `aud`; on a transport without an origin (MCP over stdio) the server declares a stable audience identifier in its capability exchange, which the agent uses as `aud` (Sections 2.4 and 4.2).

---

## References

- [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)
- [ADR 006 — DID Methods for TAs and Agents](./006-did-methods.md)
- ADR 014 — Holder Binding and Web Bot Auth Integration
- ADR 015 — Credential Serialisation Format
- [RFC 7638 — JSON Web Key (JWK) Thumbprint](https://www.rfc-editor.org/rfc/rfc7638)
- [draft-ietf-oauth-sd-jwt-vc](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc)
- [did:web Method Specification](https://w3c-ccg.github.io/did-method-web/)
