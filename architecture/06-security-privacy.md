<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Security and Privacy

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## 5.1 Trust Model and Assumptions

### 5.1.1 What TSAI trusts

- **Trust Authorities** operate honestly, perform the verification they claim (identity, reputation, backing), populate a credential only with what they established (§7.4), protect their signing keys, and keep the block current.
- **Cryptography**: ES256, P-256, and SHA-256 are sound, keys have adequate length, random generation has sufficient entropy, and hashes are collision-resistant.
- **Infrastructure**: HTTPS and DNS operate correctly, the certificate authorities behind HTTPS are trustworthy, and systems keep time with NTP.
- **Participants**: Service Providers verify before granting access and read the signals honestly; agents present credentials they legitimately hold.

### 5.1.2 What TSAI does not trust

- **Agents** are the subject of verification. Their behaviour must be constrained by the Service Provider and their outputs validated.
- **The network** may be compromised, so HTTPS is required, signatures are verified, issuer metadata is fetched over HTTPS with DNSSEC where available, and fetched URLs are hardened (§3.6).
- **Any single Trust Authority**: several give redundancy, and a Service Provider chooses which to trust.
- **Credential holders**: a credential may be stolen, so it is short-lived and bound to the `cnf` key; a presentation may be captured, so each carries a fresh key-binding JWT addressed to one Service Provider, and a state-changing action binds the request (§3.4).

### 5.1.3 Non-goals

TSAI does not monitor runtime behaviour, validate outputs, prevent prompt injection or other LLM-specific attacks, authenticate end users, or prevent a malicious operator holding a valid credential from misusing it. These are the Service Provider's responsibility or a separate concern.

### 5.1.4 Centralisation risks

Professional Trust Authorities (ADR 002) bring centralisation risks and mitigations: outage is covered by the offline base path and the 30-minute lifetime and by several authorities; key compromise by HSM storage, several authorities, the short lifetime, and the block; misbehaviour by the signed operational report (§7.10); oligopoly and lock-in by open verification and portable SD-JWT VCs; regulatory capture by authorities in different jurisdictions. Service Providers choose which to trust, agents which to use, and the governance body is multi-stakeholder.

---

## 5.2 Protocol and Implementation Boundaries

Normative at the protocol level: the SD-JWT VC format (Section 2), the verification algorithm (Section 3), HTTPS transmission, and the meaning of each signal. What a Service Provider does with the signals is its policy: which Trust Authorities to trust, how to weigh the signals, how strongly to verify a given action, and its caching, logging, and degraded-mode choices within the bounds Section 3 sets. TSAI signals; the Service Provider decides.

---

## 5.3 Threat Model

| Surface | Response |
|---|---|
| Steal a credential from storage or the wire | Useless without the `cnf` private key; short lifetime bounds exposure |
| Replay a captured presentation to another Service Provider | `aud` binds it to one |
| Substitute the request on a captured presentation at this Service Provider | `req` binds the request for state-changing actions (§3.4, ADR 014) |
| Forge a credential | Issuer signature verified against the key from `jwt-vc-issuer`, with `x5c` rejected and `issuer` pinned to `iss` |
| Suppress a block by serving a stale or forged status list | Status-list token signature verified, issuer matched, URI pinned to the `iss` origin (§3.5) |
| Server-side request forgery via a fetched URL | URL validation, private-address refusal, bounded size and timeout (§3.6) |
| Hijack DNS | HTTPS required, DNSSEC where available and where a `prv` is relied on |
| Compromise a Trust Authority | HSM keys, several authorities, short lifetime, block, operational transparency |

A network attacker cannot break HTTPS or forge a signature. A compromised agent holds valid credentials but cannot alter their contents or extend their life. A malicious Trust Authority can issue and block its own credentials but cannot forge another's. A malicious Service Provider sees what is presented to it but cannot reuse it, because the presentation is bound to it by `aud` and to the holder by `cnf`.

---

## 5.4 Cryptographic Requirements

**Signature profile.** Every TSAI v1 protocol signature MUST use `ES256`: ECDSA over the NIST P-256 curve with SHA-256. This applies to issuer-signed credentials, key-binding JWTs, proof-of-control challenges, Status List Tokens, Trust Authority operational reports, and HSM attestations. Every signing JWK MUST use `kty` `EC` and `crv` `P-256`; a verifier MUST reject every other `alg`, key type, or curve. TSAI v1 performs no signature-algorithm negotiation.

**Hash profile.** TSAI v1 uses SHA-256 for SD-JWT disclosure digests and `sd_hash`, RFC 7638 JWK thumbprints, type-metadata and reputation-methodology integrity, and RFC 9530 request content digests. A verifier MUST reject another digest algorithm in these protocol fields.

**Key generation and use.** Keys and nonces MUST be generated with a cryptographically secure random source; P-256 keys provide at least a 128-bit security level, and nonces carry at least 128 bits of entropy. Implementations MUST use an established cryptographic library or HSM with secure ECDSA nonce generation; software signers SHOULD use deterministic ECDSA per RFC 6979. A TSAI signing key MUST be used only for signing and MUST NOT be reused for encryption or key agreement.

**Encryption.** TSAI v1 defines no JWE or other payload-encryption scheme. HTTPS supplies confidentiality in transit, with cipher-suite selection governed by the applicable TLS version; encryption at rest is an implementation concern outside the protocol.

**Algorithm migration.** Cryptographic agility is provided by a future protocol-version transition, not by accepting dormant alternatives in v1. A replacement algorithm MUST be introduced with a migration timeline and an explicit transition during which implementations can move to the new protocol version.

---

## 5.5 Credential Lifecycle Security

**Issuance (Trust Authority).** Signing keys are held in an HSM, key access is logged, and issuance is recorded for audit (§7.8) without storing credential contents. Contents match the evaluation (§7.4).

**The agent identity and binding keys.** Under ADR 017 the required `sub` is the persistent agent identity; `cnf` is the current proof-of-possession key. An agent MUST protect every registered private key and SHOULD hold it in hardware-backed storage (RFC 9901 §10.2). Distinct keys across contexts limit compromise and key-based linkage, although required `sub` remains globally correlatable. The operator is responsible for registration, rotation, and repudiation through the authenticated management channel. Detailed handling — memory hygiene, file permissions, backup encryption — is in the implementation guide.

**Transmission.** Credentials travel over HTTPS with TLS 1.2 or higher. The `TSAI-Credential` value MUST NOT be logged or placed in a URL, and proxies MUST NOT cache requests carrying it.

**Verification and caching (Service Provider).** Verification follows Section 3, and verification-result caching is bounded there (§3.7.3): a cached result MUST NOT outlive the credential's `exp`, the cache key includes the presented credential, and a positive result is not served across an observable status change. Reputation-methodology documents are obtained only out of band, integrity-checked, and cached by `(mtd, mtd#integrity)`; reputation policy is keyed by `(iss, typ, mtd)`. Request-time verification does not fetch a methodology or reveal the presenting agent.

---

## 5.6 Replay and Substitution

A presentation is bound to one Service Provider by `aud`, carries a fresh key-binding JWT with a bounded `iat` and a `nonce`, and, for a state-changing action, a `req` digest that binds the request (§3.4, ADR 014). A captured credential is unusable without the `cnf` key; a captured presentation is not usable against another Service Provider, and, where `req` is present, not against another action at this one. The freshness window, nonce policy, and request-binding rule are in Section 3.4. All parties keep time with NTP; a Service Provider monitors clock drift and returns its time on a stale rejection.

---

## 5.7 Privacy

**Agent correlation.** Every credential carries a required, persistent `sub`, so the same agent is correlatable across Service Providers by design. This enables agent-level allow/deny decisions and blocks that survive key rotation; TSAI v1 chooses that property over pairwise agent unlinkability. Distinct `cnf` keys still limit key-based linkage and compromise scope but do not hide `sub`. A `status` claim adds a second correlator through its stable `uri` and `idx`; omitting it removes that additional handle but does not make the agent unlinkable, and the TA block then cannot reach the credential within its 30-minute lifetime. An SP can always apply its local block by `sub`.

**What each party learns.** A Service Provider learns the persistent agent `sub`, operator identity, signals, and issuing Trust Authority, but not the agent's activity elsewhere from the protocol itself; cross-SP comparison of `sub` can correlate presentations. A Trust Authority learns which agents it registers and issues to and, under holder-directed issuance (ADR 015), their pattern of signal requests, but not which Service Provider an agent visits on the offline path. A status fetch reveals only that someone read a list, not which credential or Service Provider.

**Users** are out of scope; a credential carries no user identity, and a Service Provider MUST NOT conflate agent trust with user trust.

---

## 5.8 Trust Authority Security

Signing keys are held in an HSM with multi-person authorisation, restricted and audited access, and periodic rotation with old keys retained for verification. A verifier, not the Trust Authority, resolves `jwt-vc-issuer` to obtain the signing key, under the fetch hardening of Section 3.6; a Trust Authority resolves a `prv` when it verifies a certifier, over HTTPS and with DNSSEC-validated resolution where it relies on the result, since a hijacked DNS record could redirect that lookup. It publishes a compact-JWS operational report (§7.10) and HSM attestation (§7.11), both signed by the normal current TA signing key. On key compromise it rotates the key through the out-of-band path (§3.7.2), notifies Service Providers and the governance body, and re-issues; Service Providers can drop it from their trusted set. A Trust Authority is a legal entity accountable for what it issues.

---

## 5.9 Service Provider Responsibilities

Verification is Section 3. Beyond it, a Service Provider MUST NOT log credential contents or misrepresent a signal, MUST indicate and log degraded-mode operation within the bounds of §3.7.2, and decides which Trust Authorities to trust and how strongly to verify a given action. It combines TSAI with its own controls in defence in depth.

---

## 5.10 Protocol-Specific Security

Transport integration and its considerations for MCP, A2A, and HTTP are in Section 4, including exposure, replay and substitution, the payments boundary, and the one-hop limitation.

---

## 5.11 Limitations

TSAI does not protect against LLM-specific attacks, poor output quality, an agent's runtime behaviour after verification, a malicious operator holding a valid credential, social engineering, or vulnerabilities in the Service Provider's own systems. Beyond those, several limitations are inherent in the current design and are recorded so a reader does not assume otherwise:

- **`prv` is attribution, not proof.** A compliance or assurance `prv` names the third party the Trust Authority asserts stands behind a claim, without a signature from that party. A Service Provider relying on such a signal for a material decision verifies it out of band.
- **Signal currency.** The 30-minute lifetime bounds the binding and the presentation, not the assertions; a signal's currency is carried by `asof` (§2.5.1), and a Service Provider should read it rather than assume a freshly minted credential carries fresh facts.
- **Derived-type trust.** A derived `vct`, `aka_vcts`, or `extends` assertion does not authorise its issuer (SD-JWT VC §6.6). A Service Provider accepts a derived TSAI type only from an issuer it trusts and only after validating the integrity-pinned metadata and schema chain to the canonical TSAI type.
- **Reputation washing.** Agent-level reputation lets an operator register a new agent to shed a poor record; an operator-level reputation signal (`rep` with `scp: operator`, ADR 016) and the identity floor bound this, but do not close it. End-user-level Sybil resistance is deferred (ADR 008).
- **Agent key compromise.** A stolen registered binding key lets an attacker present existing credentials until they expire. It cannot register a new identity or key without the authenticated operator management channel. The operator repudiates the key; where issued credentials may be affected, the TA blocks the persistent agent `sub` (§7.6).
- **Operator-session compromise.** An agent host that holds both a binding key and the `operatorAuth` bearer session can request challenges, issuance, and refresh until that session is revoked. Operators SHOULD keep management and refresh credentials outside the agent runtime where practical; Trust Authorities SHOULD scope sessions to the required agent and operations, limit their lifetime, and support immediate revocation (§7.2).
- **Request substitution without `req`.** Where a presentation does not carry `req`, TSAI binds the presenter to the credential and the audience, not to the action; a Service Provider whose verifying and acting components differ must require `req` (§3.4).
- **Persistent-agent correlation.** Required global `sub` enables cross-SP correlation. TSAI v1 accepts this cost to support stable agent-level policy and blocking; omitting `status` removes only the additional status-index correlator (§5.7).
- **One hop.** In a multi-agent chain a service agent learns the immediately connecting agent's signals, not the originating agent's (§4.6).

---

## 5.12 Normative Requirements Summary

**Trust Authorities MUST** hold EC/P-256 signing keys in an HSM, use `ES256` for every TSAI signature, verify an agent and match contents to the evaluation before issuing (§7.4), keep the block current and publish the status list, support key repudiation (§7.6), and publish compact-JWS operational reports, HSM attestations, and evaluation criteria (§7.10–§7.11).

**Agents MUST** protect the `cnf` private key, present only over HTTPS, and present an unexpired credential.

**Service Providers MUST** verify per Section 3, not log credential contents, not misrepresent signals, bound degraded mode and caches (§3.7), and indicate degraded operation.

**All parties MUST** use HTTPS with TLS 1.2 or higher (TA APIs 1.3, §7.7), validate certificates, and keep time with NTP.

---

## References

- draft-ietf-oauth-sd-jwt-vc-18; RFC 9901 (§10.1 correlation, §10.2 key storage); draft-ietf-oauth-status-list-21
- RFC 7519, RFC 7518, RFC 7515, RFC 7638, RFC 8725, RFC 6979, RFC 9530; NIST SP 800-57
- ADR 007, ADR 014, ADR 016, ADR 017, ADR 018
