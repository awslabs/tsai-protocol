<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Credential Verification

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 3.1 Overview

This section specifies how a Service Provider verifies a TSAI credential presented by an agent. A presentation is an SD-JWT VC (Section 2) with a key-binding JWT appended. Verification establishes four things: that a trusted Trust Authority issued the credential, that the credential has not expired, that the presenter holds the bound key, and that the presentation is addressed to this Service Provider.

The base path is offline. It needs the Trust Authority's published signing key and nothing from the Trust Authority at request time. Freshness, replay prevention, the use of a nonce, and when a Service Provider fetches status are specified in Section 3.4 and ADR 018. The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

---

## 3.2 Key Discovery and Identity

Verification resolves keys and identities per ADR 017.

### 3.2.1 Trust Authority key

The Trust Authority is identified by the `iss` claim, an HTTPS identifier. Its signing keys are published at `iss` joined with `/.well-known/jwt-vc-issuer`, and the `kid` in the issuer-signed JWT header selects one. A Service Provider MUST obtain the issuer key from that endpoint and MAY cache it. There is no DID resolution for the Trust Authority.

A Service Provider verifies against a set of Trust Authority issuers it trusts, configured directly or from a registry. If `iss` is not a trusted issuer, or the key cannot be obtained, verification fails closed.

### 3.2.2 Agent key

The agent is not resolved. Its key is the `cnf` JWK inside the credential, and the key-binding JWT is verified against it directly.

### 3.2.3 Third-party identifiers

A compliance or assurance signal names its provider by a `did:web` in `prv`. A Service Provider resolves that DID only if it independently checks the provider, which is optional; the credential carries the signal as asserted by the Trust Authority.

---

## 3.3 Verification Algorithm

Given a presentation of the form `<issuer-signed JWT>~<disclosure 1>~...~<disclosure N>~<key-binding JWT>`, where disclosures are present only under selective disclosure:

1. Split the presentation on `~` into the issuer-signed JWT, any disclosures, and the key-binding JWT.
2. Check the issuer-signed JWT header has `typ` `dc+sd-jwt`. Read `iss` and confirm it is a trusted Trust Authority. Obtain the key named by `kid` from the issuer's `jwt-vc-issuer` metadata and verify the issuer signature.
3. Confirm `vct` is a recognised credential type.
4. Check the lifetime: `exp` has not passed and `iat` is not in the future, within the skew tolerance set in Section 3.4.
5. If disclosures are present, verify each against its digest in `signals` and reconstruct the revealed signals. Ignore any signal not disclosed.
6. Check the key-binding JWT header has `typ` `kb+jwt`. Verify its signature against the `cnf` JWK.
7. Confirm `aud` is this Service Provider, and that `sd_hash` matches the presented issuer-signed JWT together with the forwarded disclosures.
8. Apply the freshness, nonce, and status rules of Section 3.4.

If any step fails, reject the presentation. Ignore signal types that are not recognised, per Section 2.5.7.

---

## 3.4 Freshness, Replay, and Status

Verification strength follows the risk of the action, as specified in ADR 018, over the mechanisms below.

`aud` binds a presentation to one Service Provider, and each presentation carries its own key-binding JWT with a fresh `iat` and an optional `nonce`, on a clock independent of the 30-minute credential lifetime. A credential MAY carry a `status` reference keyed to the agent or operator identity (Section 2.7.2).

**Baseline.** A Service Provider MUST confirm `aud`, and SHOULD reject a key-binding JWT whose `iat` is more than 2 minutes old, allowing 30 seconds of clock skew. This is the offline path and needs nothing from the Trust Authority at request time.

**Escalation.** Where the risk of the action warrants, a Service Provider issues a `nonce` as a challenge, which the agent echoes in the key-binding JWT and which closes the freshness window, and fetches the agent or operator status list to honour a block. Which action calls for which addition is the Service Provider's policy over the signals, not a tier.

---

## 3.5 Error Handling

### 3.5.1 Fail closed

The following MUST result in rejection: an invalid or unsupported issuer or key-binding signature, an `iss` that is not trusted, an unrecognised `vct`, an expired credential, a key-binding JWT whose `aud` does not match or whose `sd_hash` does not match the presented material, and a malformed presentation.

Standard error codes:

- `SIGNATURE_INVALID` — an issuer or key-binding signature failed.
- `ISSUER_UNTRUSTED` — `iss` is not a trusted Trust Authority.
- `EXPIRED` — the credential lifetime has passed.
- `BINDING_INVALID` — the key-binding JWT failed, whether signature, `aud`, or `sd_hash`.
- `UNKNOWN_TYPE` — `vct` is not recognised.
- `MALFORMED` — the presentation could not be parsed.

A Service Provider SHOULD return a structured error without issuer identifiers or algorithm details, and SHOULD log the detail server-side.

```json
{ "verified": false, "error": { "code": "BINDING_INVALID", "message": "Verification failed" } }
```

### 3.5.2 Degraded mode

If the issuer metadata is temporarily unreachable, a Service Provider MAY continue with a cached issuer key, and MUST indicate the degraded trust level and log it. Degraded mode MUST NOT relax any cryptographic, lifetime, or binding check. The interaction between degraded mode and the risk policy of Section 3.4 is specified in ADR 018.

---

## 3.6 Normative Requirements Summary

**Service Providers MUST:**
- Obtain the Trust Authority key from `iss` and `/.well-known/jwt-vc-issuer` and verify the issuer signature.
- Verify the key-binding JWT against the credential's `cnf` key, and confirm `aud` and `sd_hash`.
- Check the credential lifetime.
- Reject a credential whose `iss` is untrusted or whose `vct` is unrecognised.
- Ignore signal types they do not recognise.
- Fail closed on any signature, lifetime, or binding failure.

**Service Providers SHOULD:**
- Confirm `aud` and bound the age of the key-binding JWT to 2 minutes, allowing 30 seconds of clock skew, per ADR 018.

**Service Providers MAY:**
- Cache issuer keys.
- Fetch the agent or operator status list where risk warrants (policy per ADR 018).
- Continue in degraded mode on infrastructure failure, clearly indicated.

The freshness window, nonce policy, and status-fetch policy are specified in ADR 018.

---

## References

- draft-ietf-oauth-sd-jwt-vc — SD-JWT-based Verifiable Credentials
- draft-ietf-oauth-status-list — Token Status List
- SD-JWT VC Issuer Metadata (`/.well-known/jwt-vc-issuer`)
- RFC 7519 (JSON Web Token), RFC 7515 (JSON Web Signature)
- RFC 7638 (JWK Thumbprint)
