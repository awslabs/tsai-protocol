<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Credential Format

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## 2.1 Overview

A TSAI credential is an SD-JWT VC, as defined in draft-ietf-oauth-sd-jwt-vc. A Trust Authority issues it, binds it to the holder's key, and populates it with a flat list of trust signals. Every credential carries a minimum identity set, the identity floor (Section 2.5.3), so that it always names an accountable operator. The agent presents the credential with a key-binding JWT that proves possession of the bound key.

This section specifies the serialisation, the payload claims, the holder binding, the trust-signal structure and its categories, selective disclosure, status and lifetime, party identity, the type-metadata document, and versioning. The verification algorithm, the freshness and replay rules, and the policy for when a Service Provider fetches status are specified in Section 3.

Authorization and mandate, the constraints on what an agent is permitted to do, are not trust signals and are out of scope for this document (Section 2.12). The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

---

## 2.2 Serialisation

A credential in transit has the SD-JWT VC form

```
<issuer-signed JWT>~<disclosure 1>~...~<disclosure N>~<key-binding JWT>
```

where the disclosures are present only under selective disclosure (Section 2.6); the default form is `<issuer-signed JWT>~<key-binding JWT>`. A stored, unpresented credential is the issuer-signed JWT alone, with a trailing `~`.

---

## 2.3 Issuer-signed JWT

### 2.3.1 Header

```json
{ "alg": "EdDSA", "typ": "dc+sd-jwt", "kid": "key-1" }
```

- `alg` MUST be one of `EdDSA` (Ed25519), `ES256`, `ES384`, or `ES512`. A verifier MUST reject any other value, including `none` and RSA algorithms.
- `typ` MUST be `dc+sd-jwt`, the media type `application/dc+sd-jwt`.
- `kid` MUST identify the Trust Authority signing key within the issuer's key set (Section 2.8).

### 2.3.2 Payload

| Claim | Requirement | Meaning |
|---|---|---|
| `iss` | REQUIRED | The Trust Authority's HTTPS issuer identifier; keys discovered at `/.well-known/jwt-vc-issuer` (Section 2.8). |
| `vct` | REQUIRED | The verifiable credential type, a URL identifying the type and version, resolvable to a type-metadata document (Section 2.9). |
| `vct#integrity` | REQUIRED | Integrity metadata for the `vct` type-metadata document, per SD-JWT VC §5; lets a verifier cache the document indefinitely and detect substitution (Section 2.9). |
| `iat` | REQUIRED | Issuance time, seconds since the Unix epoch. |
| `exp` | REQUIRED | Expiry time, 30 minutes after `iat` (Section 2.7). |
| `sub` | OPTIONAL | A stable HTTPS identifier for the agent, operator-controlled; used for continuity across key rotation. |
| `cnf` | REQUIRED | The holder binding key, a JWK (Section 2.4). |
| `status` | OPTIONAL | A reference into a status list keyed to the agent or operator identity (Section 2.7). |
| `signals` | REQUIRED | The flat list of trust signals, carrying at least the identity floor (Sections 2.5, 2.5.3). |
| `_sd_alg` | CONDITIONAL | The disclosure digest algorithm; present only under selective disclosure (Section 2.6). |

---

## 2.4 Holder Binding

A TSAI credential is bound to a key the holder controls, carried in `cnf` and proven at presentation by a key-binding JWT (ADR 014).

`cnf` contains the holder's public key as a JWK:

```json
"cnf": { "jwk": { "kty": "OKP", "crv": "Ed25519", "x": "O8G5X-9Zichaemqq4fFOqQ3SyYI18A4INI1oWPWlLcc" } }
```

At presentation the holder signs a key-binding JWT with the private key matching `cnf`:

**Header:** `{ "alg": "EdDSA", "typ": "kb+jwt" }`

**Payload:**

| Claim | Requirement | Meaning |
|---|---|---|
| `iat` | REQUIRED | Time the presentation was created. Its freshness is bounded per Section 3. |
| `aud` | REQUIRED | The Service Provider the presentation is addressed to: the HTTPS origin of the service (Section 2.8). On a transport with no HTTP origin, such as MCP over stdio, it is the stable audience identifier the server declares in its capability exchange (Section 4.2). The Service Provider MAY publish the expected value in its discovery documents. |
| `nonce` | REQUIRED | A value binding the presentation to a transaction. The agent generates it from a cryptographically secure source, at least 128 bits, fresh per presentation; where the risk of the action warrants, the Service Provider issues it as a challenge instead (Section 3). |
| `sd_hash` | REQUIRED | The digest over the issuer-signed JWT and any forwarded disclosures, computed per RFC 9901 §4.3.1. |
| `req` | OPTIONAL | A request binding (ADR 020): the request method and target URI, and, when the request has a body, a content digest of the body per RFC 9530. REQUIRED for a state-changing action and where the verifying and acting components differ (Section 3). |

`nonce` is REQUIRED in every key-binding JWT, per RFC 9901 §4.3; the escalation decision concerns who supplies it, not whether it is present. `req` is an added claim, adopted deliberately per ADR 020.

**Worked example.** The header is `{ "alg": "EdDSA", "typ": "kb+jwt" }`. The baseline claims set for a read, with an agent-generated `nonce`:

```json
{
  "iat": 1781863250,
  "aud": "https://service-provider.example",
  "nonce": "9b8f2c1a7e4d6f0b3a5c8e2d1f4a6b9c",
  "sd_hash": "X9Dd6l3aY8p2Qq7rT1uV0wZ2xN4mK6sB8cE0fH1gJ2k"
}
```

For a state-changing action, the `nonce` is the Service-Provider-issued single-use challenge and `req` binds the method, URI, and body digest:

```json
{
  "iat": 1781863250,
  "aud": "https://service-provider.example",
  "nonce": "c1f4a6b9c8e2d1f49b8f2c1a7e4d6f0b",
  "sd_hash": "X9Dd6l3aY8p2Qq7rT1uV0wZ2xN4mK6sB8cE0fH1gJ2k",
  "req": {
    "method": "POST",
    "uri": "https://service-provider.example/api/orders",
    "digest": "sha-256=:RjVcQo5Xk2n9pQ0rT1uV0wZ2xN4mK6sB8cE0fH1gJ2=:"
  }
}
```

---

## 2.5 Trust Signals

`signals` is a flat array (ADR 016). Each signal has a category, a type, and type-specific fields.

The field and type codes are abbreviated (`cat`, `typ`, `prv`, `org`, `dct`, and so on) because a credential is fetched every 30 minutes and sent on every request, so wire size matters; the human-readable labels live in the type metadata (Section 2.9), and the registry of categories and types is governance-maintained (Section 8).

Absence of a signal is not a negative assertion. It may mean the Trust Authority did not evaluate that category, not that it evaluated it unfavourably; TSAI carries no adverse signals, and the block is the sanctioned negative path. A Service Provider MUST NOT read the absence of a signal as an adverse finding, and a Trust Authority MAY indicate which categories it assessed so a Service Provider can tell silence from a gap.

### 2.5.1 Common fields

| Field | Requirement | Meaning |
|---|---|---|
| `cat` | REQUIRED | The category code (Sections 2.5.3–2.5.6). |
| `typ` | REQUIRED | The type code within the category. |
| `prv` | CONDITIONAL | The provider of a third-party signal, a `did:web` (Section 2.8); present on compliance and assurance, omitted where the Trust Authority is the source. |
| `asof` | CONDITIONAL | The time the Trust Authority established or last confirmed the fact, seconds since the epoch. REQUIRED for reputation, compliance, and assurance; RECOMMENDED for identity. It carries signal currency, which the 30-minute lifetime does not (Section 5.11). |

The schema is authoritative for each type's field list.

### 2.5.2 Categories

| `cat` | Category | Question |
|---|---|---|
| `idn` | Identity | Who is the agent and its operator? |
| `rep` | Reputation | How has the agent behaved? |
| `cmp` | Compliance | What third-party certifications does the operator hold? |
| `asr` | Assurance | What economic backing stands behind the agent? |

### 2.5.3 Identity (`idn`) and the identity floor

Attributes the Trust Authority verified; the provider is the Trust Authority, so `prv` is omitted. Types:

- `org` — the operator's legal entity name. `val` is the name.
- `jur` — the operator's jurisdiction. `val` is an ISO 3166-1 alpha-2 code.
- `kyc` — the depth of identity verification. `val` is one of:
  - `basic` — legal name, address, and business registration verified;
  - `enhanced` — basic, plus beneficial ownership and financial checks;
  - `institutional` — enhanced, plus regulatory-compliance checks and audits.
- `dct` — a domain the operator controls, verified by DNS challenge or email. `val` is the domain.
- `dag` — the age of that domain. `val` is an ISO 8601 duration; `asof` fixes the measurement time.

**The identity floor (ADR 019).** A Trust Authority MUST NOT issue a credential unless `signals` contains, as identity signals, the operator's legal name (`org`), jurisdiction (`jur`), verification depth (`kyc`), and at least one verified controlled domain (`dct`). These four are `mandatory` in the type metadata (Section 2.9), and the schema enforces their presence. The floor is not a tier and defines no ordering.

### 2.5.4 Reputation (`rep`)

The agent's behavioural record, observed by the Trust Authority; `prv` is omitted, since the Trust Authority is the source (ADR 021). Fields:

- `band` — a portable ordinal, one of `insufficient-history`, `established`, or `strong`. Comparable across Trust Authorities; each authority publishes how it maps its own scale (Section 2.9, Section 7.10).
- `scr` — a TA-specific score, not comparable across authorities.
- `cnt` — the number of interactions behind the record. REQUIRED whenever `band` or `scr` is present.
- `wdw` — the observation window, an ISO 8601 duration; with `asof` (the window end) it is computable. REQUIRED whenever `band` or `scr` is present.
- `scp` — the scope of the record, `agent` (the default) or `operator`. An `operator` record aggregates across the operator's agents; a Service Provider evaluating a thin agent-level record reads the operator-level one (Section 5.11, ADR 021).

`typ` names the domain of the record, for example `ecommerce`. Reputation signals at both scopes are `sd: never` in the type metadata (Section 2.9), so an agent cannot withhold a record it holds, including the operator-level one a washed agent would most want to hide.

### 2.5.5 Compliance (`cmp`)

A third-party certification the operator holds. `prv` is the certifier's `did:web`. Types are certification names, for example `iso27001`, `soc2`, `pci-dss`. A `vld` field MAY carry the certification's own validity end (renamed from the earlier `exp` to avoid collision with the credential's `exp`); `asof` carries when the Trust Authority confirmed it.

A `prv` is attribution, not proof: it names the third party the Trust Authority asserts stands behind the claim, without a signature from that party (Section 5.11). A Service Provider relying on a compliance signal for a material decision verifies it out of band.

### 2.5.6 Assurance (`asr`)

Economic backing or recourse. `prv` is the backer's `did:web`. Types:

- `insurance` — liability cover. Fields: `cvr` (the coverage, an object with `val` and `cur`, an ISO 4217 code), `basis` (`per-incident` or `aggregate`), `scope` (what is covered), `vld` (the cover's validity end), and an optional `lei` for the liable legal entity.
- `collateral` — funds held in escrow. `cvr` carries the amount, `bal` an optional remaining balance.

As with compliance, `prv` is attribution and not proof; a Service Provider relying on assurance for a material decision confirms the arrangement out of band (Section 5.11).

### 2.5.7 Extension

A Trust Authority MAY define types beyond the registered set. A custom type is a short code scoped to the credential's `iss` and MUST NOT embed a domain name; the issuer disambiguates it. A Service Provider MAY act on a custom type from an issuer it recognises and MUST ignore a type it does not recognise; a custom type MUST NOT duplicate or contradict a registered type.

---

## 2.6 Selective Disclosure

Selective disclosure is optional and off by default. When used, the issuer replaces a signal in `signals` with a digest object `{"...": "<digest>"}`, emits the disclosure alongside the credential, and sets `_sd_alg`. A signal marked `sd: never` in the type metadata (Section 2.9), reputation among them, MUST NOT be made disclosable by the issuer. A withheld signal remains visible to the verifier as a digest object until reconstruction, so the verifier can count how many were withheld; the verifier surfaces that count and MAY fail closed above a policy threshold (Section 3, ADR 022).

The `sd` control is a TSAI extension to type metadata (Section 2.9), so a generic SD-JWT VC consumer does not enforce it; a TSAI verifier enforces `sd: never` explicitly (Section 3.3). This is a known property of the design, not an omission.

---

## 2.7 Status and Lifetime

### 2.7.1 Lifetime

`exp` MUST be 30 minutes after `iat`. A flow that outlives the credential obtains a fresh one; the lifetime is the re-issue cadence, and presentation freshness is a separate clock (Section 2.4, Section 3).

### 2.7.2 Status

An individual short-lived credential is not revoked; the control is a block on the agent or operator (ADR 018). A Trust Authority MUST publish an agent-and-operator status list, so a Service Provider can depend on the mechanism existing. A credential normally carries a `status` claim referencing it, keyed to the agent or operator identity, so that blocking one identity invalidates all of its credentials:

```json
"status": { "status_list": { "idx": 94567, "uri": "https://trust-authority.example/tsai/status/agents/1" } }
```

A credential MAY omit `status` only where the agent requires unlinkability across Service Providers, accepting that no block can reach it within the lifetime (Section 5.7). When a Service Provider fetches and how it verifies the status list are specified in Section 3.

---

## 2.8 Party Identity

Identity and key discovery follow ADR 017.

- **Trust Authority.** Identified by the HTTPS `iss`, an origin with no path, query, fragment, or trailing slash, with signing keys at `/.well-known/jwt-vc-issuer`; `kid` selects one. The absence of a path is deliberate: SD-JWT VC §3 forms the metadata location by inserting the well-known segment between the host and the path of `iss`, so forbidding a path makes that location coincide with the simple join. This is the only key-discovery mechanism: a credential carrying an `x5c` header MUST be rejected, and the verifier MUST confirm that the metadata's `issuer` equals `iss` (Section 3).
- **Agent.** Identified by the `cnf` key; an optional `sub` gives a stable HTTPS name, not a DID.
- **Referenced third parties.** A certifier (`cmp`) or a backer (`asr`) is identified by its own `did:web` in `prv`; an assurance party MAY additionally carry an `lei`.

---

## 2.9 Type Metadata

Each `vct` resolves to a type-metadata document (ADR 022) that carries display rules and per-claim controls. Two controls are load-bearing:

- `mandatory` — the claim MUST be present. The identity-floor signals (`org`, `jur`, `kyc`, `dct`) are `mandatory`.
- `sd` — whether the claim may be selectively disclosed. Reputation is `sd: never`.

**Deviation from SD-JWT VC claim addressing.** SD-JWT VC §4.6 addresses a claim by `path`, an ordered array that selects by position. TSAI signals are array elements distinguished by content rather than position, so the document addresses each control by a `signal` selector `{cat, typ}` rather than by `path`. This is a deliberate TSAI extension. Its consequence is that a generic SD-JWT VC consumer, which per SD-JWT VC §4.2 ignores properties it does not understand, ignores every `signal` entry and with it every `mandatory` and `sd` control; the controls are therefore enforced by TSAI-specific processing (Sections 2.6 and 3.3), not by a generic consumer. The document otherwise follows SD-JWT VC §4, including `locale` for display objects.

**Integrity and caching.** The credential carries a `vct#integrity` claim (Section 2.3.2) whose value is the integrity metadata of this document, per SD-JWT VC §5. A Service Provider MUST obtain the type-metadata document out of band or from cache and MUST NOT fetch it on the verification path. The cache is content-addressed: a Service Provider keys each type-metadata document by its `vct#integrity` value, and a credential's `vct#integrity` selects the document that applies to it. Documents from before and after an in-place change (Section 2.10) therefore coexist in the cache, and a credential keeps matching the document it was issued against, which is why the document may be cached indefinitely (SD-JWT VC §4.3.4 and §6.4). If a Service Provider does not hold the document a credential's `vct#integrity` names, it MUST fail the current presentation (Section 3.7.1) and SHOULD refresh the document out of band, after which later presentations that reference it verify. Substitution is caught the same way: an integrity value that no authentic published document matches never verifies, which is why the check is on the base verification path (Section 3.3).

The schema for the type-metadata document is [`schemas/tsai-type-metadata.schema.json`](schemas/tsai-type-metadata.schema.json).

---

## 2.10 Versioning

`vct` identifies the type and its version. A type evolves in place while it stays backward compatible, and a new `vct` is minted only for an incompatible change (SD-JWT VC §2.2.2.1). A Service Provider MUST reject a credential whose `vct` it does not recognise.

An in-place change alters the type-metadata document, so its `vct#integrity` changes: credentials issued before and after the change reference different documents under the same `vct`. This is not a flag day, because a Service Provider caches type-metadata documents by their integrity value (Section 2.9) and keeps the earlier one for credentials still in flight; the only cost is a one-time out-of-band refresh, per Service Provider, to obtain the new document. A change a Service Provider could not apply without breaking credentials already in flight is by definition incompatible and takes a new `vct` instead.

---

## 2.11 Worked Example

An issued credential, flat, before presentation:

```json
{
  "iss": "https://trust-authority.example",
  "vct": "https://tsaiprotocol.org/credential/tsai/1",
  "vct#integrity": "sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=",
  "iat": 1781863200,
  "exp": 1781865000,
  "sub": "https://acme-corp.example/agents/shopper-v3",
  "cnf": { "jwk": { "kty": "OKP", "crv": "Ed25519", "x": "O8G5X-9Zichaemqq4fFOqQ3SyYI18A4INI1oWPWlLcc" } },
  "status": { "status_list": { "idx": 94567, "uri": "https://trust-authority.example/tsai/status/agents/1" } },
  "signals": [
    { "cat": "idn", "typ": "org", "val": "Acme Corporation GmbH" },
    { "cat": "idn", "typ": "jur", "val": "DE" },
    { "cat": "idn", "typ": "kyc", "val": "enhanced" },
    { "cat": "idn", "typ": "dct", "val": "acme-corp.example" },
    { "cat": "idn", "typ": "dag", "val": "P850D", "asof": 1781000000 },
    { "cat": "rep", "typ": "ecommerce", "band": "established", "scr": 0.94, "cnt": 3518, "wdw": "P90D", "asof": 1781800000 },
    { "cat": "cmp", "typ": "iso27001", "prv": "did:web:cert-corp.example", "vld": 1981863200, "asof": 1780000000 },
    { "cat": "asr", "typ": "insurance", "prv": "did:web:cyber-insurance.example", "lei": "WDIFANOQF6AW1CXRCR17", "cvr": { "val": 100000, "cur": "EUR" }, "basis": "aggregate", "scope": "third-party liability", "vld": 1790000000, "asof": 1780000000 }
  ]
}
```

The first four identity signals are the floor. Presented, the holder appends a key-binding JWT carrying `iat`, `aud`, `nonce`, `sd_hash`, and, for a state-changing action, `req`.

---

## 2.12 Out of Scope

Authorization and mandate — value limits, permitted operations, rate limits, a human-in-loop requirement — are not trust signals. They are delegation (ADR 001) and are specified separately.

---

## 2.13 Normative Requirements Summary

**Trust Authorities MUST:**
- Issue SD-JWT VC credentials with `typ` `dc+sd-jwt`, `alg` in the permitted set, and `exp` 30 minutes after `iat`.
- Carry a `vct#integrity` claim binding the credential to its type-metadata document (Section 2.9).
- Include the identity floor (`org`, `jur`, `kyc`, `dct`) in every credential (ADR 019).
- Include `cnt` and the observation window whenever a reputation signal carries `band` or `scr` (ADR 021).
- Not make an `sd: never` signal, reputation among them, selectively disclosable.
- Publish signing keys at `/.well-known/jwt-vc-issuer`, a type-metadata document per `vct`, and an agent-and-operator status list.

**Agents MUST:**
- Present a credential that has not expired, with a key-binding JWT carrying `iat`, `aud`, `nonce`, and `sd_hash`, and `req` where the action and topology require it.

**Service Providers MUST:**
- Verify per Section 3, reject an unrecognised `vct` or `alg` or an `x5c` header, and ignore unrecognised signal types.
- Obtain type metadata out of band or from cache, never on the verification path, and check `vct#integrity` (Section 2.9).
