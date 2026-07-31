<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Security and Privacy

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 5.1 Trust Model and Assumptions

### 5.1.1 What TSAI trusts

- **Trust Authorities** operate honestly, perform the verification they claim (identity, reputation, backing), protect their signing keys, issue only to agents that meet their criteria, and keep any block current.
- **Cryptography**: the signature algorithms (EdDSA, ES256) are sound, keys have adequate length, random generation has sufficient entropy, and hashes are collision-resistant.
- **Infrastructure**: HTTPS and DNS operate correctly, the certificate authorities behind HTTPS are trustworthy, and systems keep time with NTP.
- **Participants**: Service Providers verify before granting access and read the signals honestly; agents present credentials they legitimately hold.

### 5.1.2 What TSAI does not trust

- **Agents** are the subject of verification, not trusted by default. Their behaviour must be constrained by the Service Provider, and their outputs validated.
- **The network** may be compromised, so HTTPS is required, signatures are verified, and issuer metadata is fetched over HTTPS with DNSSEC where available.
- **Any single Trust Authority**: no one TA is fully trusted; several give redundancy, and a Service Provider chooses which to trust.
- **Credential holders**: a credential may be stolen, so it is short-lived and bound to the holder key; a presentation may be captured, so each carries a fresh key-binding JWT addressed to one Service Provider.

### 5.1.3 Non-goals

TSAI does not monitor runtime behaviour, validate agent outputs, prevent prompt injection or other LLM-specific attacks, authenticate end users, or prevent a malicious operator who holds a valid credential from misusing it. These are the Service Provider's responsibility or a separate concern; TSAI gives point-in-time trust signals and accountability, not behavioural guarantees.

### 5.1.4 Centralisation risks

TSAI uses professional Trust Authorities rather than a web of trust (ADR 002), which brings centralisation risks and their mitigations:

- **Outage**: the offline base path and the 30-minute lifetime let verification continue without the TA at request time, and several TAs give redundancy.
- **Key compromise**: keys sit in an HSM, several TAs limit blast radius, the short lifetime bounds the window, and a block gives emergency invalidation.
- **Misbehaviour**: signed operational reports (Section 7.7) let Service Providers detect anomalies and drop a TA.
- **Oligopoly and lock-in**: verification is open to any Service Provider, credentials are portable SD-JWT VCs, and an agent can hold credentials from more than one TA.
- **Regulatory capture**: TAs operate in different jurisdictions, and a Service Provider can reject a compromised one.

Distributed trust holds despite centralised TAs: Service Providers choose which to trust, agents choose which to use, and the governance body is multi-stakeholder.

---

## 5.2 Protocol and Implementation Boundaries

Normative at the protocol level: the SD-JWT VC credential format (Section 2), the verification algorithm and its checks (Section 3), HTTPS transmission, the credential header, and the meaning of each signal. What a Service Provider does with the signals is its own policy: which TAs to trust, how to weigh the signals, how strongly to verify a given action, and its caching, logging, and degraded-mode choices. The principle is that TSAI signals and the Service Provider decides.

---

## 5.3 Threat Model

**Attacker goals**: impersonate a legitimate agent, bypass verification, steal or forge credentials, disrupt the infrastructure, or correlate an agent's activity across Service Providers.

**Attack surfaces and the response:**

| Surface | Response |
|---|---|
| Steal a credential from storage or the wire | Useless without the `cnf` private key; short lifetime bounds exposure |
| Replay a captured presentation | `aud` binds it to one Service Provider; a fresh key-binding JWT per request (freshness rule per Section 3.4, ADR 018) |
| Forge a credential | Issuer signature verified against the TA key from `jwt-vc-issuer` |
| Hijack DNS or intercept HTTPS | HTTPS required, DNSSEC where available, signatures verified |
| Compromise a TA | HSM keys, several TAs, short lifetime, block, operational transparency |

**Attacker capabilities.** A network attacker can intercept but cannot break HTTPS or forge a signature. A compromised agent holds valid credentials but cannot alter their contents or extend their life. A malicious TA can issue and block its own credentials but cannot forge another TA's. A malicious Service Provider sees what is presented to it but cannot reuse it elsewhere, because the presentation is bound to it by `aud` and to the holder by `cnf`.

---

## 5.4 Cryptographic Requirements

- Implementations MUST support `EdDSA` (Ed25519) and `ES256`, and MAY support `ES384` and `ES512`.
- Implementations MUST reject unknown or weak algorithms. The credential names its algorithm; there is no negotiation.
- Keys are generated with a cryptographically secure random source, providing at least a 128-bit security level (Ed25519 and P-256).
- Nonces and other security-critical values use a cryptographically secure random source with at least 128 bits of entropy.

---

## 5.5 Credential Lifecycle Security

**Issuance (Trust Authority).** Signing keys are held in an HSM, key access is logged, and issuance is recorded for audit without storing credential contents. The TA verifies the agent before issuing and populates the signals from its evaluation.

**Holder key and storage (agent).** The agent holds the `cnf` private key, which is what a credential is bound to. It SHOULD keep that key in memory and, if it must persist it, protect it. A stored credential is unusable without the key, and the 30-minute lifetime bounds exposure.

**Transmission.** Credentials travel over HTTPS with TLS 1.2 or higher. The `TSAI-Credential` value MUST NOT be logged by servers or placed in a URL, and proxies MUST NOT cache requests carrying it.

**Verification (Service Provider).** Verification follows Section 3: the issuer signature, the key-binding signature against `cnf`, `sd_hash`, `aud`, and the lifetime, failing closed on any failure.

---

## 5.6 Replay Prevention

A presentation is bound to one Service Provider by `aud`, and each presentation carries its own key-binding JWT with a fresh `iat` and an optional `nonce`, on a clock independent of the 30-minute credential lifetime. A captured credential is unusable without the `cnf` key, and a captured presentation is not usable against another Service Provider.

Per ADR 018, a Service Provider rejects a key-binding JWT whose `iat` is more than 2 minutes old, allowing 30 seconds of clock skew, and where the risk of the action warrants it issues a `nonce` challenge that closes the window. All parties keep time with NTP; a Service Provider monitors clock drift and alerts on synchronisation failure.

---

## 5.7 Privacy

**Agent correlation.** An agent is identified by the `cnf` key its credential is bound to, and optionally by a stable `sub` name. An agent that reuses the same key or `sub` across Service Providers can be correlated across them; an agent that wants to avoid this uses a fresh key per Service Provider. The credential still reveals the operator's identity signals, which are shared across that operator's agents.

**What a Service Provider learns**: the operator's identity and the agent's signals, and which Trust Authority issued the credential. It does not learn the agent's activity with other Service Providers, since a credential does not call back to the TA on use.

**What a Trust Authority learns**: which agents it issues to, and their evaluation data. It does not learn which Service Provider an agent visits on the offline path. The exception is a status fetch: when a Service Provider reads the agent or operator status list, it accesses a list at the TA rather than reporting a specific credential or Service Provider, which keeps the leakage coarse.

**Users** are out of scope. TSAI verifies agents, not end users; a credential carries no user identity, and a Service Provider MUST NOT conflate agent trust with user trust.

---

## 5.8 Trust Authority Security

Signing keys are held in an HSM, with multi-person authorisation for key operations, restricted and audited access, and periodic rotation with old keys retained for verification during the transition. A TA publishes signed operational reports (Section 7.7) and, where it offers assurance about its key handling, an HSM attestation (Section 7.8). On key compromise a TA rotates the key, notifies Service Providers and the governance body, and re-issues; Service Providers can drop the TA from their trusted set. A TA is a legal entity, accountable for what it issues, and Service Providers enforce that accountability by their choice of whom to trust.

---

## 5.9 Service Provider Responsibilities

Verification is specified in Section 3. Beyond it, a Service Provider MUST NOT log credential contents or misrepresent what a signal means, MUST indicate and log degraded-mode operation, and decides for itself which TAs to trust, how to weigh the signals, and how strongly to verify a given action. It combines TSAI with its own controls in defence in depth.

---

## 5.10 Protocol-Specific Security

Transport integration and its security considerations for MCP, A2A, and general HTTP are in Section 4, including credential exposure, replay, theft, and TA compromise.

---

## 5.11 Limitations

TSAI does not protect against LLM-specific attacks (prompt injection, jailbreaking, adversarial inputs), poor output quality (hallucination, bias, harmful content), an agent's runtime behaviour after verification, a malicious operator holding a valid credential, social engineering of users, or vulnerabilities in the Service Provider's own systems. These need separate mitigations: input and output validation, monitoring and anomaly detection, rate limiting, kill switches, TA evaluation quality, user education, and ordinary application security. TSAI is one layer that gives identity, trust signals, and accountability, to be combined with the rest.

---

## 5.12 Normative Requirements Summary

**Trust Authorities MUST** hold signing keys in an HSM, support `EdDSA` and `ES256`, verify an agent before issuing, record issuances for audit without storing contents, keep any block current, and publish signed operational reports (Section 7.7).

**Agents MUST** protect the `cnf` private key, present only over HTTPS, and present a credential that has not expired.

**Service Providers MUST** verify per Section 3, not log credential contents, not misrepresent signals, and indicate degraded-mode operation.

**All parties MUST** use HTTPS with TLS 1.2 or higher, validate certificates, and keep time with NTP.

The freshness window, nonce policy, and status-fetch policy are specified in ADR 018.

---

## References

- draft-ietf-oauth-sd-jwt-vc — SD-JWT-based Verifiable Credentials
- draft-ietf-oauth-status-list — Token Status List
- RFC 7519 (JSON Web Token), RFC 7515 (JSON Web Signature), RFC 7638 (JWK Thumbprint)
- NIST SP 800-57 (Key Management)
- TSAI ADR 007: Short-Lived Credentials
- TSAI ADR 014: Holder Binding; ADR 017: Party Identity; ADR 018: Verification Strength and Replay
