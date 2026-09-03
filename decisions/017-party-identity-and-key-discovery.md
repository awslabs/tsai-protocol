<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 017: Party Identity and Key Discovery

**Status:** Accepted  
**Date:** 2026-09-02  
**Deciders:** TSAI Working Group  
**Relationship to ADR 006:** supersedes [ADR 006 — DID Methods for TAs and Agents](./006-did-methods.md)  
**Depends on:** ADR 014 (holder binding) and ADR 015 (credential serialisation format)

---

## Context

ADR 006 identified the Trust Authority, agent, and other parties by DIDs. ADR 014 and ADR 015 replace the verification functions of those DIDs: the issuer key is discovered from HTTPS `iss`, and holder binding verifies the inline `cnf` JWK.

The remaining agent-identity requirement is continuity. A key alone is not a durable identity because keys rotate and an agent may use several context-specific keys. An SP also needs a stable per-agent identifier for local allow/deny decisions without blocking every agent of the operator. The earlier optional, caller-supplied `sub` did not meet that requirement: it could be omitted, changed during issuance, or asserted outside the operator's verified namespace.

TSAI already verifies the accountable operator and its controlled domains. Agent identity can therefore be registered under the authenticated operator account and anchored to a verified domain, while holder binding remains key-centric.

Referenced third parties have a different role. A certifier or assurance provider does not hold a key in the credential, but several TAs may need to name the same party. Its identifier must therefore be controlled outside any single TA and resolve through one defined mechanism.

---

## Decision Criteria

1. **Accountability.** Every agent identity is linked to an enrolled, legally accountable operator.
2. **Durability.** The agent identifier survives key rotation and supports reputation, status, and local SP policy.
3. **No caller-controlled identity at issuance.** Issuance cannot create or replace the agent identifier.
4. **Key control.** Every `cnf` key is registered and proven before use.
5. **Domain control.** The agent identifier remains within a domain the TA currently verifies for the operator.
6. **Offline SP verification.** The SP resolves no agent DID, JWKS, or other holder-key reference.
7. **Minimal core infrastructure.** TSAI does not require a public key directory where authenticated registration and proof of control suffice.
8. **Privacy cost stated.** A stable global agent identifier enables cross-SP correlation and that consequence is explicit.

---

## Options Considered

### Option 1: `did:web` for the agent

The operator publishes a DID document containing the agent's keys; the DID is the stable agent identifier.

**Pros.** Standard identifier and rotation document, with a direct domain-to-key relationship.

**Cons.** Adds DID syntax and resolution to a JWT/JWK protocol. The SP does not need the document because the TA-signed credential already carries `sub` and `cnf`; the legal operator relationship still depends on TA verification. Domain transfer still requires periodic TA revalidation.

### Option 2: Key identity with optional `sub`

The `cnf` JWK identifies the agent and an optional HTTPS `sub` provides continuity.

**Pros.** Minimal issuance state and no holder-key resolution.

**Cons.** Optional identity does not support reliable agent-level blocking. A caller-supplied `sub` can be changed or spoofed, and key rotation changes the primary identity.

### Option 3: Registered HTTPS `sub` with registered binding keys (decided)

The operator registers a stable HTTPS `sub` under an authenticated TA account. The `sub` hostname exactly matches a current verified `dct`. The TA associates one or more registered JWKs with that agent; issuance references a registered key by RFC 7638 thumbprint and proves control. The credential carries the stored `sub` and the selected full JWK in `cnf`.

**Pros.** Meets accountability, continuity, blocking, and offline-verification requirements without DID resolution or a mandatory public JWKS. Rotation changes the key while retaining the agent identity. The TA can accept raw JWK, JWKS, JWKS URL, or WBA directory input through its authenticated management process and normalise each accepted key to the same internal form.

**Cons.** The TA maintains agent and key registration state. Required `sub` creates a stable cross-SP correlation identifier. Domain verification must be repeated to detect loss or transfer of control.

---

## Decision

Adopt **Option 3**.

### Agent identity

`sub` is REQUIRED in every TSAI credential and is the persistent agent identifier. It is an HTTPS URL with no user information, port, query, or fragment. Its hostname MUST exactly equal one current `dct` of the enrolled operator; a subdomain is valid only when that hostname is independently verified as `dct`. The URL path distinguishes agents within the domain.

The operator registers the agent before issuance through an authenticated TA management process. The TA stores the operator-to-agent association and MUST NOT accept `sub` from `IssueRequest`. A stable `sub` may be registered with several TAs, but TSAI cannot enforce cross-TA uniqueness.

### Binding keys

A registered binding key is an EC P-256 public signing JWK identified by its RFC 7638 thumbprint as `kid`. Within one operator account, a registered key maps to one agent; several keys may map to the same agent. Key material may arrive through raw JWK, a JWKS document, a JWKS URL, or a WBA key directory, but DID input and resolution are not part of TSAI.

`IssueRequest` supplies `kid` and proof of control, not `sub` or raw JWK material. The TA resolves the registered key, verifies the proof, copies the stored `sub` into the credential, and places the registered public JWK in `cnf`. An unknown, inactive, repudiated, cross-operator, or ambiguous `kid` is rejected.

Key rotation registers and proves a new key against the existing agent before issuance uses it. Rotation preserves `sub`, status, and reputation and changes `cnf`.

### Domain-control freshness

The TA supports automated DNS and HTTPS challenges. HTTPS validation follows a fixed well-known path and does not follow redirects. `dct.asof` records the last successful domain-control check and is REQUIRED.

The TA MUST NOT issue outside the domain-freshness window defined in Section 2.5.3. It SHOULD use a shorter window for recently enrolled operators or agents and where evidence is limited, and MUST publish its cadence policy. Any failed revalidation stops new issuance. Confirmed loss of control blocks every affected agent immediately; an inconclusive network failure suspends issuance while the TA retries.

### Other parties

The Trust Authority is identified by HTTPS `iss`; signing-key metadata uses the SD-JWT VC `jwt-vc-issuer` well-known insertion rule. Referenced certifiers and assurance providers use their own canonical `did:web`, since they are named rather than key-bound in the credential. The Service Provider is named by HTTPS origin in `aud`, or by the stable audience value declared for a transport without an origin.

---

## Consequences

- The SP treats `sub` as the persistent agent identity and `cnf` as its current proof-of-possession key.
- Agent-level status and SP allow/deny decisions key on `sub`; rotation does not evade them.
- The credential and Type Metadata make `sub` mandatory and non-disclosable.
- Required global `sub` enables cross-SP correlation. TSAI v1 chooses agent-level blockability over pairwise agent unlinkability; the already mandatory operator identity remains globally visible.
- Issuance and refresh depend on authenticated operator and key registration, but SP verification remains offline.
- Public JWKS and WBA are optional registration inputs, not core dependencies.
- DID-based agent identity, `did:key`, and `did:wba` are not part of TSAI.

---

## References

- [ADR 006 — DID Methods for TAs and Agents](./006-did-methods.md)
- ADR 014 — Holder Binding and Web Bot Auth Integration
- ADR 015 — Credential Serialisation Format
- [RFC 7638 — JSON Web Key (JWK) Thumbprint](https://www.rfc-editor.org/rfc/rfc7638)
- [draft-ietf-oauth-sd-jwt-vc-18](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc-18)
- [did:web Method Specification](https://w3c-ccg.github.io/did-method-web/)
