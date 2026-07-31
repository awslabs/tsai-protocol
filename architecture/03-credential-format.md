<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Credential Format

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 2.1 Overview

A TSAI credential is an SD-JWT VC, as defined in draft-ietf-oauth-sd-jwt-vc. A Trust Authority issues it, binds it to the holder's key, and populates it with a flat list of trust signals. The agent presents it with a key-binding JWT that proves possession of the bound key.

This section specifies the serialisation, the payload claims, the holder binding, the trust-signal structure and its categories, selective disclosure, status and lifetime, and party identity. The verification algorithm, the freshness and replay rules, and the policy for when a Service Provider fetches status are specified in Section 3 (Verification), not here.

Authorization and mandate, the constraints on what an agent is permitted to do, are not trust signals and are out of scope for this document. They belong with delegation (see ADR 001).

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

---

## 2.2 Serialisation

TSAI credentials use the SD-JWT VC serialisation. A credential in transit has the form

```
<issuer-signed JWT>~<disclosure 1>~...~<disclosure N>~<key-binding JWT>
```

where the disclosures are present only when selective disclosure is used (Section 2.6). In the default case there are no disclosures, and the form is

```
<issuer-signed JWT>~<key-binding JWT>
```

The issuer-signed JWT carries the credential. The key-binding JWT is added by the holder at presentation time (Section 2.4). A stored, unpresented credential is the issuer-signed JWT alone, with a trailing `~`.

---

## 2.3 Issuer-signed JWT

### 2.3.1 Header

```json
{
  "alg": "EdDSA",
  "typ": "dc+sd-jwt",
  "kid": "key-1"
}
```

- `alg` MUST be a supported signature algorithm. TSAI 1.0 supports `EdDSA` (Ed25519) and `ES256`, `ES384`, `ES512`.
- `typ` MUST be `dc+sd-jwt`, the media type `application/dc+sd-jwt`.
- `kid` MUST identify the Trust Authority signing key within the issuer's key set (Section 2.8).

### 2.3.2 Payload

The following claims are defined.

| Claim | Requirement | Meaning |
|---|---|---|
| `iss` | REQUIRED | The Trust Authority's HTTPS issuer identifier. Its keys are discovered at `/.well-known/jwt-vc-issuer` (Section 2.8). |
| `vct` | REQUIRED | The verifiable credential type, a URL identifying the TSAI credential type and its version. |
| `iat` | REQUIRED | Issuance time, seconds since the Unix epoch. |
| `exp` | REQUIRED | Expiry time. A credential is short-lived (Section 2.7). |
| `sub` | OPTIONAL | A stable identifier for the agent, an HTTPS identifier the operator controls. Used for continuity across key rotation; the binding itself is `cnf`. |
| `cnf` | REQUIRED | The holder binding key, a JWK (Section 2.4). |
| `status` | OPTIONAL | A reference into a status list, keyed to the agent or operator (Section 2.7). |
| `signals` | REQUIRED | The flat list of trust signals (Section 2.5). |
| `_sd_alg` | CONDITIONAL | The disclosure digest algorithm. Present only when selective disclosure is used (Section 2.6). |

---

## 2.4 Holder Binding

A TSAI credential is bound to a key the holder controls. The binding is carried in `cnf` and proven at presentation time by a key-binding JWT (ADR 014).

`cnf` contains the holder's public key as a JWK:

```json
"cnf": {
  "jwk": {
    "kty": "OKP",
    "crv": "Ed25519",
    "x": "O8G5X-9Zichaemqq4fFOqQ3SyYI18A4INI1oWPWlLcc"
  }
}
```

At presentation the holder signs a key-binding JWT with the private key matching `cnf`:

**Header**
```json
{ "alg": "EdDSA", "typ": "kb+jwt" }
```

**Payload**
```json
{
  "iat": 1781863260,
  "aud": "https://shop.example",
  "nonce": "9f2b",
  "sd_hash": "<hash of the issuer-signed JWT and any disclosures>"
}
```

- `aud` MUST be the Service Provider the presentation is addressed to.
- `nonce` is a value that binds the presentation to a request.
- `sd_hash` MUST be the digest of the presented issuer-signed JWT and its disclosures, so the key-binding signature covers exactly what is presented.

A Service Provider verifies three things: the issuer signature against the Trust Authority key, the key-binding signature against `cnf`, and that `sd_hash` matches the presented material. The freshness and replay rules on `iat`, `aud`, and `nonce` are specified in Section 3.

---

## 2.5 Trust Signals

`signals` is a flat array. Each signal is an object with a category, a type, and type-specific fields (ADR 016).

### 2.5.1 Common fields

| Field | Requirement | Meaning |
|---|---|---|
| `cat` | REQUIRED | The category code (Sections 2.5.3 to 2.5.6). |
| `typ` | REQUIRED | The type code within the category. |
| `prv` | CONDITIONAL | The provider of the signal, where it is a third party. A `did:web` (Section 2.8). Omitted when the Trust Authority itself is the source. |

Further fields depend on the type. The schema is authoritative for the field list of each type.

### 2.5.2 Categories

TSAI 1.0 defines four categories, distinguished by the question the signal answers for the Service Provider.

| `cat` | Category | Question |
|---|---|---|
| `idn` | Identity | Who is the agent and its operator? |
| `rep` | Reputation | How has the agent behaved? |
| `cmp` | Compliance | What third-party certifications does the operator hold? |
| `asr` | Assurance | What economic backing or recourse stands behind the agent? |

### 2.5.3 Identity (`idn`)

Attributes the Trust Authority verified about the agent and its operator. The provider is the Trust Authority, so `prv` is omitted.

Representative types:

- `dct` — a domain the operator controls. `val` is the domain.
- `dag` — the age of that domain. `val` is an ISO 8601 duration.
- `jur` — the operator's jurisdiction. `val` is an ISO 3166-1 alpha-2 code.
- `kyc` — the depth of identity verification. `val` is `basic`, `enhanced`, or `institutional`.

### 2.5.4 Reputation (`rep`)

The agent's behavioural track record, observed by the Trust Authority over a window.

Representative fields on a reputation signal:

- `scr` — a score. TA-specific and not comparable across Trust Authorities.
- `cnt` — the number of interactions the score is based on.
- `wdw` — the observation window, an ISO 8601 duration.

The `typ` names the domain of the record, for example `ecommerce`.

### 2.5.5 Compliance (`cmp`)

A third-party certification the operator holds. `prv` is the certifier's `did:web`.

Representative types are the certification names, for example `iso27001`, `soc2`, `pci-dss`. An `exp` field MAY carry the certification's own expiry.

### 2.5.6 Assurance (`asr`)

Economic backing or recourse that stands behind the agent. `prv` is the backer's `did:web`.

Representative types:

- `insurance` — liability cover. `cvr` is the coverage, an object with `val` and `cur` (an ISO 4217 code).
- `collateral` — funds held in escrow. `cvr` carries the amount.

An assurance signal MAY carry an `lei`, the legal-entity identifier of the liable party, where the party has one.

### 2.5.7 Extension

A Trust Authority MAY define signal types beyond the registered set. A custom type is a short code scoped to the credential's `iss`; it MUST NOT embed a domain name. Because every signal in a credential shares one issuer, the issuer disambiguates the code, and no signal carries a namespace string.

A Service Provider that recognises the issuing Trust Authority MAY act on its custom types. A Service Provider MUST ignore a type it does not recognise. A custom type MUST NOT duplicate or contradict a registered type.

---

## 2.6 Selective Disclosure

Selective disclosure is optional. By default a credential carries its signals in clear, and there are no disclosures.

When it is used, the issuer replaces a signal in `signals` with a digest object `{"...": "<digest>"}`, emits the corresponding disclosure alongside the credential, and sets `_sd_alg` to the digest algorithm. At presentation the holder forwards only the disclosures it chooses to reveal, and the `sd_hash` in the key-binding JWT covers the issuer-signed JWT together with the forwarded disclosures. A Service Provider reconstructs a revealed signal from its disclosure and ignores any signal it was not given.

---

## 2.7 Status and Lifetime

### 2.7.1 Lifetime

A TSAI credential is short-lived. `exp` MUST be 30 minutes after `iat`. A flow that outlives the credential obtains a fresh one; the lifetime is the re-issue cadence, not the replay window. Replay is prevented per presentation by the key-binding JWT (Section 2.4), on a separate clock.

### 2.7.2 Status

Because a credential is short-lived and bound to the holder key, an individual credential is not revoked. The control is a block on the agent or operator, for the case where a Trust Authority loses trust within the lifetime.

Where a Trust Authority offers this, the credential carries a `status` claim referencing an IETF Token Status List, with the index keyed to the agent or operator identity rather than to the individual credential. Blocking one agent flips one bit, which invalidates all of that agent's credentials.

```json
"status": {
  "status_list": {
    "idx": 94567,
    "uri": "https://trusted-shops.com/tsai/status/agents/1"
  }
}
```

When a Service Provider fetches the status list, if at all, is a policy decision specified in Section 3. The common path does not fetch it and stays offline.

---

## 2.8 Party Identity

Identity and key discovery follow ADR 017.

- **Trust Authority.** Identified by the HTTPS `iss`. Its signing keys are published at `/.well-known/jwt-vc-issuer`, and `kid` in the header selects one. Key rotation is publishing a new key there.
- **Agent.** Identified by the `cnf` key. An optional `sub` gives a stable HTTPS name for continuity; it is not a DID.
- **Referenced third parties.** A certifier (`cmp`) or a backer (`asr`) is identified by its own `did:web`, one canonical DID per party, carried in `prv`. An assurance party MAY additionally carry an `lei`.

---

## 2.9 Versioning

`vct` identifies the credential type and its version. A Service Provider MUST reject a credential whose `vct` it does not recognise. A minor version is backward compatible; a major version MAY break compatibility.

---

## 2.10 Worked Example

An issued credential, flat, before presentation:

```json
{
  "iss": "https://trusted-shops.com",
  "vct": "https://tsaiprotocol.org/credential/tsai/1",
  "iat": 1781863200,
  "exp": 1781865000,
  "sub": "https://acme-corp.example/agents/shopper-v3",
  "cnf": {
    "jwk": { "kty": "OKP", "crv": "Ed25519", "x": "O8G5X-9Zichaemqq4fFOqQ3SyYI18A4INI1oWPWlLcc" }
  },
  "status": {
    "status_list": { "idx": 94567, "uri": "https://trusted-shops.com/tsai/status/agents/1" }
  },
  "signals": [
    { "cat": "idn", "typ": "dct", "val": "acme-corp.example" },
    { "cat": "idn", "typ": "dag", "val": "P850D" },
    { "cat": "cmp", "typ": "iso27001", "prv": "did:web:cert-corp.example", "exp": 1981863200 },
    { "cat": "rep", "typ": "ecommerce", "prv": "did:web:rating-agency.example", "scr": 0.94, "cnt": 3518, "wdw": "P90D" },
    { "cat": "asr", "typ": "insurance", "prv": "did:web:cyber-insurance.example", "lei": "WDIFANOQF6AW1CXRCR17", "cvr": { "val": 100000, "cur": "EUR" } }
  ]
}
```

Presented, the holder appends a key-binding JWT, giving `<issuer-signed JWT>~<KB-JWT>`. The key-binding JWT is shown in Section 2.4.

---

## 2.11 Out of Scope

Authorization and mandate, the constraints on what an agent may do, such as value limits, permitted operations, rate limits, and a human-in-loop requirement, are not trust signals. They are the subject of delegation (ADR 001) and are specified separately, not as a signal category.

---

## 2.12 Normative Requirements Summary

**Trust Authorities MUST:**
- Issue credentials as SD-JWT VC with `typ` `dc+sd-jwt`.
- Include `iss`, `vct`, `iat`, `exp`, `cnf`, and `signals`, and set `exp` to 30 minutes after `iat`.
- Sign with a key published at `/.well-known/jwt-vc-issuer` and identified by `kid`.
- Publish their signing keys and, where offered, an agent or operator status list.

**Agents MUST:**
- Present a credential that has not expired.
- Prove possession of the `cnf` key with a key-binding JWT (Section 2.4).

**Service Providers MUST:**
- Verify the issuer signature against the Trust Authority key, the key-binding signature against `cnf`, and the `sd_hash`.
- Reject a credential whose `vct` they do not recognise.
- Ignore signal types they do not recognise.

The verification algorithm, freshness and replay rules, and status-fetch policy are specified in Section 3.
