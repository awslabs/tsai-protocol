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

A TSAI credential is an SD-JWT VC, as defined in draft-ietf-oauth-sd-jwt-vc-18. A Trust Authority issues it, binds it to the holder's key, and populates it with a flat list of trust signals. Every credential carries a minimum identity set, the identity floor (Section 2.5.3), so that it always names an accountable operator. The agent presents the credential with a key-binding JWT that proves possession of the bound key.

This section specifies the serialisation, the payload claims, the holder binding, the trust-signal structure and its categories, selective disclosure, status and lifetime, party identity, the type-metadata document, and versioning. The verification algorithm, the freshness and replay rules, and the policy for when a Service Provider fetches status are specified in Section 3.

Authorization and mandate, the constraints on what an agent is permitted to do, are not trust signals and are out of scope for this document (Section 2.12). The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

---

## 2.2 Serialisation

A credential in transit has the SD-JWT VC form

```
<issuer-signed JWT>~<disclosure 1>~...~<disclosure N>~<key-binding JWT>
```

where the disclosures are present only under selective disclosure (Section 2.6); the default form is `<issuer-signed JWT>~<key-binding JWT>`. A stored, unpresented credential is the SD-JWT without a key-binding JWT: it includes any issuer-provided disclosures and ends with a trailing `~`; without disclosures it is `<issuer-signed JWT>~`.

---

## 2.3 Issuer-signed JWT

### 2.3.1 Header

```json
{ "alg": "ES256", "typ": "dc+sd-jwt", "kid": "key-1" }
```

- `alg` MUST be `ES256`. A verifier MUST reject every other value. TSAI v1 does not negotiate signature algorithms.
- `typ` MUST be `dc+sd-jwt`, the media type `application/dc+sd-jwt`.
- `kid` MUST identify the Trust Authority signing key within the issuer's key set (Section 2.8).

### 2.3.2 Payload

| Claim | Requirement | Meaning |
|---|---|---|
| `iss` | REQUIRED | The Trust Authority's HTTPS issuer identifier; it may include a path but no query or fragment. Keys are discovered using the SD-JWT VC well-known insertion rule (Section 2.8). |
| `vct` | REQUIRED | The verifiable credential type, a URL identifying the type and version, resolvable to a type-metadata document (Section 2.9). |
| `vct#integrity` | REQUIRED | Integrity metadata for the `vct` Type Metadata document, per SD-JWT VC §5; selects the exact metadata that governs the credential (Section 2.9). |
| `aka_vcts` | CONDITIONAL | Additional credential types. REQUIRED on a derived TSAI type and MUST include the canonical TSAI `vct`; MUST NOT contain the credential's primary `vct` (Sections 2.5.7 and 2.9). |
| `iat` | REQUIRED | Issuance time, seconds since the Unix epoch. |
| `exp` | REQUIRED | Expiry time, 30 minutes after `iat` (Section 2.7). |
| `sub` | REQUIRED | The registered, persistent HTTPS identifier for the agent. Its hostname is a canonical lower-case ASCII DNS name in A-label form, with no trailing dot or port, and exactly matches a `dct`. The TA copies it from the authenticated agent record; it survives binding-key rotation and is not accepted from `IssueRequest`. |
| `cnf` | REQUIRED | The holder binding key, a JWK (Section 2.4). |
| `status` | OPTIONAL | A reference into a status list keyed to the agent or operator identity (Section 2.7). |
| `signals` | REQUIRED | The flat list of trust signals, carrying at least the identity floor (Sections 2.5, 2.5.3). |
| `_sd_alg` | CONDITIONAL | The disclosure digest algorithm; present only under selective disclosure (Section 2.6). |

---

## 2.4 Holder Binding

A TSAI credential is bound to a key the holder controls, carried in `cnf` and proven at presentation by a key-binding JWT (ADR 014).

`cnf` contains the holder's public key as a JWK:

```json
"cnf": { "jwk": { "kty": "EC", "crv": "P-256", "x": "TCAER19Zvu3OHF4j4W4vfSVoHIP1ILilDls7vCeGemc", "y": "ZxjiWWbZMQGHVWKVQ4hbSIirsVfuecCE6t4jT9F2HZQ" } }
```

The `cnf` JWK MUST have `kty` `EC` and `crv` `P-256`, MUST contain the public `x` and `y` coordinates, and MUST NOT contain private key material. At presentation the holder signs a key-binding JWT with the private key matching `cnf`:

**Header:** `{ "alg": "ES256", "typ": "kb+jwt" }`

**Payload:**

| Claim | Requirement | Meaning |
|---|---|---|
| `iat` | REQUIRED | Time the presentation was created. Its freshness is bounded per Section 3. |
| `aud` | REQUIRED | The Service Provider the presentation is addressed to: the HTTPS origin of the service (Section 2.8). On a transport with no HTTP origin, such as MCP over stdio, it is the stable audience identifier the server declares in its capability exchange (Section 4.2). The Service Provider MAY publish the expected value in its discovery documents. |
| `nonce` | REQUIRED | A value binding the presentation to a transaction. The agent generates it from a cryptographically secure source, at least 128 bits, fresh per presentation; where the risk of the action warrants, the Service Provider issues it as a challenge instead (Section 3). |
| `sd_hash` | REQUIRED | The SHA-256 digest over the issuer-signed JWT and any forwarded disclosures, computed per RFC 9901 §4.3.1. |
| `req` | OPTIONAL | A request binding (ADR 014): the request method and absolute target URI, and, when the request has a body, a SHA-256 content digest of the body per RFC 9530. The URI MUST match the request target by exact string equality, without normalisation. REQUIRED for a state-changing action and where the verifying and acting components differ (Section 3). |

`nonce` is REQUIRED in every key-binding JWT, per RFC 9901 §4.3; the escalation decision concerns who supplies it, not whether it is present. `req` is an added claim, adopted deliberately per ADR 014. TSAI v1 defines the closed claim set shown above; a key-binding JWT MUST NOT contain additional claims.

**Worked example.** The header is `{ "alg": "ES256", "typ": "kb+jwt" }`. The baseline claims set for a read, with an agent-generated `nonce`:

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

The field and type codes are abbreviated (`cat`, `typ`, `prv`, `org`, `dct`, and so on) because a credential is fetched every 30 minutes and sent on every request, so wire size matters; the human-readable labels live in the type metadata (Section 2.9), and the canonical schema defines the registered categories and types.

Absence of a signal is not a negative assertion. It may mean the Trust Authority did not evaluate that category, not that it evaluated it unfavourably; TSAI carries no adverse signals, and the block is the sanctioned negative path. A Service Provider MUST NOT read the absence of a signal as an adverse finding, and a Trust Authority MAY indicate which categories it assessed so a Service Provider can tell silence from a gap.

### 2.5.1 Common fields

| Field | Requirement | Meaning |
|---|---|---|
| `cat` | REQUIRED | The category code (Sections 2.5.3–2.5.6). |
| `typ` | REQUIRED | The type code within the category. |
| `prv` | CONDITIONAL | The provider of a third-party signal, a `did:web` (Section 2.8); present on compliance and assurance, omitted where the Trust Authority is the source. |
| `asof` | CONDITIONAL | The time the Trust Authority established or last confirmed the fact, seconds since the epoch. REQUIRED for reputation, compliance, assurance, and `idn/dct`; RECOMMENDED for other identity signals. It carries signal currency, which the 30-minute lifetime does not (Section 5.11). |

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
- `dct` — the single hostname anchoring the agent `sub`, verified by DNS or HTTPS challenge. `val` is the canonical lower-case ASCII DNS name in A-label form, with no trailing dot; Unicode U-labels are not carried in a credential. `asof` is REQUIRED, and freshness follows the domain-freshness window below.
- `dag` — the optional age of that sole `dct`; it appears at most once. `val` is an ISO 8601 duration; `asof` fixes the measurement time.

**The identity floor (ADR 016).** A Trust Authority MUST NOT issue a credential unless `signals` contains exactly one of each identity-floor signal: the operator's legal name (`org`), jurisdiction (`jur`), verification depth (`kyc`), and the verified controlled domain (`dct`) anchoring `sub`. The schema enforces their presence, and `tsai_signal_metadata` marks them `sd: never` (Section 2.9). The floor is not a tier and defines no ordering.

**Domain-freshness window.** The `dct` used to anchor `sub` MUST have been verified no more than 12 hours before credential issuance. A verifier allows `dct.asof` to be up to 30 seconds later than credential `iat` for clock skew between TA components (Section 3.4).

### 2.5.4 Reputation (`rep`)

The agent's behavioural record, observed by the Trust Authority; `prv` is omitted, since the Trust Authority is the source (ADR 016). The following shape applies to registered TSAI reputation types under the canonical `vct`; a derived `vct` may define a custom `rep` shape through its own schema and `tsai_signal_metadata`. Fields:

- `mtd` — a versioned HTTPS identifier for the immutable methodology document. REQUIRED.
- `mtd#integrity` — SHA-256 integrity metadata over the exact methodology-document bytes. REQUIRED.
- `scr` — the Trust Authority's normalised score in the inclusive range 0 to 1. REQUIRED. Higher values are more favourable under the referenced methodology. Its semantics, calculation, and evidence basis are defined by `mtd`; equal values MUST NOT be treated as equivalent across methodologies without Service-Provider calibration.
- `cnt` — the number of eligible interactions behind the score. REQUIRED.
- `wdw` — the observation window, an ISO 8601 duration; with `asof` (the window end) it is computable. REQUIRED.
- `scp` — the scope of the record, `agent` (the default) or `operator`. An `operator` record aggregates across the operator's agents; a Service Provider evaluating a thin agent-level record reads the operator-level one (Section 5.11, ADR 016).

The methodology document MUST conform to [`schemas/tsai-reputation-methodology.schema.json`](schemas/tsai-reputation-methodology.schema.json), its `id` MUST equal `mtd`, and its score object MUST declare `minimum` 0, `maximum` 1, and `direction` `higher-better`. It defines the normalised score's semantics, calculation method, eligible evidence, outcome classification, minimum history, and treatment of insufficient history. A material change to any of those properties requires a new `mtd`; methodology documents are immutable. A Trust Authority serves an HTTPS `mtd` document as `application/json`. A Service Provider obtains and caches it out of band, verifies `mtd#integrity`, and keys score policy by `(iss, typ, mtd)` (Section 3.3). An unknown or invalid methodology gives no favourable reputation result.

`typ` names the registered domain of the record. The canonical TSAI v1 type contains `ecommerce`; adding another registered domain requires a new canonical `vct` version, while a custom domain uses a derived `vct`. Reputation signals at both scopes are `sd: never` in the type metadata (Section 2.9), so an agent cannot withhold a record it holds, including the operator-level one a washed agent would most want to hide.

### 2.5.5 Compliance (`cmp`)

A third-party certification the operator holds. `prv` is the certifier's `did:web`. The canonical TSAI v1 registered types are `iso27001`, `soc2`, and `pci-dss`; adding another registered certification type requires a new canonical `vct` version, while a custom type uses a derived `vct`. A `vld` field MAY carry the certification's own validity end (renamed from the earlier `exp` to avoid collision with the credential's `exp`); `asof` carries when the Trust Authority confirmed it.

A `prv` is attribution, not proof: it names the third party the Trust Authority asserts stands behind the claim, without a signature from that party (Section 5.11). A Service Provider relying on a compliance signal for a material decision verifies it out of band.

### 2.5.6 Assurance (`asr`)

Economic backing or recourse. `prv` is the backer's `did:web`. Types:

- `insurance` — liability cover. Fields: `cvr` (the coverage, an object with `val` and `cur`, an ISO 4217 code), `basis` (`per-incident` or `aggregate`), `scope` (what is covered), `vld` (the cover's validity end), and an optional `lei` for the liable legal entity.
- `collateral` — funds held in escrow. `cvr` carries the amount, `bal` an optional remaining balance.

As with compliance, `prv` is attribution and not proof; a Service Provider relying on assurance for a material decision confirms the arrangement out of band (Section 5.11).

### 2.5.7 Extension

The canonical TSAI `vct` permits only the registered TSAI signal vocabulary. A Trust Authority that adds a signal type MUST issue a derived credential type rather than place an arbitrary type under the canonical `vct`.

The derived type has its own collision-resistant `vct`. Its Type Metadata MUST `extend` an existing TSAI type, MUST integrity-pin the parent metadata, and MUST reference an integrity-protected JSON Schema that composes the parent's immutable schema, transitively preserving the canonical TSAI constraints. A derived credential MUST carry the canonical TSAI `vct` in `aka_vcts`. A verifier accepts it as TSAI only after confirming the metadata inheritance and validating the credential against both schemas (Section 2.9).

Within a derived `vct`, custom signal types are short codes. They need neither an FQDN nor an `x-` prefix because `(vct, cat, typ)` is the semantic identifier. Every custom signal selector and its disclosure/display controls MUST be declared in `tsai_signal_metadata`, and its fields MUST be declared by the derived schema. Several Trust Authorities that share an extension use one community-owned derived `vct`; equal type strings under unrelated `vct` values have no implied equivalence.

---

## 2.6 Selective Disclosure

Selective disclosure is optional and off by default. When used, the issuer replaces a signal in `signals` with a digest object `{"...": "<digest>"}`, emits the disclosure alongside the credential, and sets `_sd_alg` to `sha-256`; a TSAI verifier MUST reject any other disclosure digest algorithm. A Trust Authority MUST NOT insert decoy digests under RFC 9901 §4.2.5, because TSAI exposes unmatched signal digests as the withheld-signal count. A signal marked `sd: never` in `tsai_signal_metadata` (Section 2.9), reputation among them, MUST NOT be made disclosable by the issuer. A withheld signal remains visible to the verifier as a digest object until reconstruction, so the verifier can count how many were withheld; the verifier surfaces that count and MAY fail closed above a policy threshold (Section 3, ADR 015).

`tsai_signal_metadata` is a TSAI Type Metadata extension because standard SD-JWT VC paths cannot select array elements by their `cat` and `typ` values. A generic consumer ignores this top-level extension; a TSAI verifier processes it and enforces its `sd` controls (Section 3.3).

---

## 2.7 Status and Lifetime

### 2.7.1 Lifetime

`exp` MUST be 30 minutes after `iat`. A flow that outlives the credential obtains a fresh one; the lifetime is the re-issue cadence, and presentation freshness is a separate clock (Section 2.4, Section 3).

### 2.7.2 Status

An individual short-lived credential is not revoked; the control is a block on the agent `sub` or operator (ADR 018). A Trust Authority MUST publish an agent-and-operator status list, so a Service Provider can depend on the mechanism existing. A credential normally carries a `status` claim referencing it, keyed to the persistent agent `sub` or operator identity, so that blocking one identity invalidates all of its credentials across key rotation. The Status List Token MUST be signed with ES256:

```json
"status": { "status_list": { "idx": 94567, "uri": "https://trust-authority.example/status/agents-1" } }
```

A credential MAY omit `status` to avoid the additional status-index correlator, accepting that a TA block cannot reach it within the lifetime. The required `sub` remains a stable cross-Service-Provider identifier, so omitting `status` does not provide agent unlinkability; an SP can still apply its local block by `sub` (Section 5.7). When a Service Provider fetches and how it verifies the status list are specified in Section 3.

---

## 2.8 Party Identity

Identity and key discovery follow ADR 017.

- **Trust Authority.** Identified by the HTTPS `iss`, which contains a host and may contain a port and path but no query or fragment. Signing keys are discovered by inserting `/.well-known/jwt-vc-issuer` between the origin and the issuer path, after removing a terminating slash from that path; for example, `https://ta.example/tenant/acme` resolves metadata at `https://ta.example/.well-known/jwt-vc-issuer/tenant/acme`. `kid` selects an EC/P-256 key. This is the only key-discovery mechanism: a credential carrying an `x5c` header MUST be rejected, and the verifier MUST confirm that the metadata's `issuer` exactly equals the original `iss` (Section 3).
- **Agent.** Identified persistently by required HTTPS `sub`, registered under an authenticated operator account and anchored to a current `dct`. `sub` has no port because `dct` is a hostname. The `cnf` JWK is the current holder-binding key; it may rotate without changing `sub`.
- **Referenced third parties.** A certifier (`cmp`) or a backer (`asr`) is identified by its own `did:web` in `prv`; an assurance party MAY additionally carry an `lei`.

---

## 2.9 Type Metadata

Each `vct` resolves to a Type Metadata document (ADR 015). SD-JWT VC Type Metadata carries display and per-claim controls, but it has carried no JSON Schema since draft `-12`; `extends` therefore inherits metadata, not field-level validation.

**Schema.** TSAI adds two required top-level properties: `tsai_schema_uri`, which identifies the JSON Schema for the complete credential payload, and `tsai_schema_uri#integrity`, which pins the exact schema bytes. The schema is authoritative for the permitted claims and signals, their field shapes, and required presence. A TSAI verifier processes these properties even though a generic SD-JWT VC consumer ignores them.

**Standard claim metadata.** When used, the standard `claims` array remains conformant to SD-JWT VC §4.6 and every entry is addressed by a `path`. TSAI does not add claim metadata for `aka_vcts`: SD-JWT VC already makes it non-disclosable, while the credential schema and verifier enforce its TSAI-specific content rules. The canonical TSAI metadata uses `claims` to mark `sub` as mandatory and non-disclosable because SD-JWT VC permits `sub` to be selectively disclosed, whereas TSAI requires the persistent agent identifier in every presentation.

**Signal metadata.** Standard claim paths cannot select array elements by their `cat` and `typ` values, so TSAI adds the top-level `tsai_signal_metadata` property. Each entry selects every signal in a category, or one exact category/type pair, and carries `sd` plus optional display metadata. It does not define presence: the JSON Schema does that. A parent category selector governs every signal in that category unless the child defines a more specific selector. A child may narrow `sd: allowed` to `always` or `never`, but MUST NOT change an inherited `always` or `never` value. A schema-required signal MUST have an effective `tsai_signal_metadata` rule of `sd: never`, so it remains available for payload validation after disclosure processing.

A derived TSAI type uses the standard `extends` and `extends#integrity` properties to inherit its parent metadata. Its schema MUST use JSON Schema `allOf` with a `$ref` to the parent's immutable schema, thereby composing the canonical TSAI base transitively. The child adds `tsai_signal_metadata` entries for its custom signals; `aka_vcts` is governed by the credential schema and verification rules.

```json
{
  "vct": "https://ta.example/credential/tsai/1",
  "extends": "https://tsaiprotocol.org/credential/tsai/1",
  "extends#integrity": "sha256-TlXnQgvmjbrYiaBBCe7CJr5u1kN8EKlAfJphROLDYBI=",
  "tsai_schema_uri": "https://ta.example/schemas/credential/tsai/1.json",
  "tsai_schema_uri#integrity": "sha256-H5gGR/iMLT9a4ajpGQBRXOEwR4E1fUMqZl1gtCuhvtQ=",
  "tsai_signal_metadata": [
    { "signal": { "cat": "rep", "typ": "risk" }, "sd": "never" }
  ]
}
```

This separation keeps any standard `claims` entries processable by generic SD-JWT VC consumers. A generic consumer ignores the unknown top-level `tsai_schema_uri` and `tsai_signal_metadata` properties; a TSAI-aware consumer processes them in addition to any standard metadata.

**Integrity and caching.** The credential carries a `vct#integrity` claim (Section 2.3.2) using SHA-256 integrity metadata for its Type Metadata document, per SD-JWT VC §5. Derived metadata additionally carries `extends#integrity`; every TSAI metadata document carries `tsai_schema_uri#integrity`. A Service Provider MUST obtain the complete metadata and schema chain out of band or from cache and MUST NOT fetch it on the verification path.

Both caches are content-addressed. A credential's `vct#integrity` selects its metadata; each metadata document's schema integrity selects its schema; and `extends#integrity` selects the parent metadata. Documents for different immutable `vct` versions coexist under their integrity values. If any required document is absent, mismatched, circular, or not rooted in the canonical TSAI type, the Service Provider MUST fail the current presentation and SHOULD refresh the chain out of band. The fetch hardening in Section 3.6 applies to metadata and schema retrieval.

The schema for the type-metadata document is [`schemas/tsai-type-metadata.schema.json`](schemas/tsai-type-metadata.schema.json). The canonical payload schema is [`schemas/tsai-credential.schema.json`](schemas/tsai-credential.schema.json).

---

## 2.10 Versioning

`vct` identifies one immutable credential-type definition. The Type Metadata and JSON Schema associated with a TSAI `vct` MUST NOT change in place. Any change to the registered vocabulary, field constraints, display metadata, mandatory controls, or selective-disclosure controls mints a new `vct`, even when the change would otherwise be backward compatible.

Versioned metadata and schema URIs remain available for as long as credentials or derived types reference them. Existing derived types continue to extend their immutable parent version; adopting a newer TSAI base requires a new derived `vct`. A Service Provider MUST reject a credential whose metadata and schema chain it does not recognise or cannot validate.

---

## 2.11 Worked Example

An issued credential, flat, before presentation:

```json
{
  "iss": "https://trust-authority.example",
  "vct": "https://tsaiprotocol.org/credential/tsai/1",
  "vct#integrity": "sha256-TlXnQgvmjbrYiaBBCe7CJr5u1kN8EKlAfJphROLDYBI=",
  "iat": 1781863200,
  "exp": 1781865000,
  "sub": "https://acme-corp.example/agents/shopper-v3",
  "cnf": { "jwk": { "kty": "EC", "crv": "P-256", "x": "TCAER19Zvu3OHF4j4W4vfSVoHIP1ILilDls7vCeGemc", "y": "ZxjiWWbZMQGHVWKVQ4hbSIirsVfuecCE6t4jT9F2HZQ" } },
  "status": { "status_list": { "idx": 94567, "uri": "https://trust-authority.example/status/agents-1" } },
  "signals": [
    { "cat": "idn", "typ": "org", "val": "Acme Corporation GmbH" },
    { "cat": "idn", "typ": "jur", "val": "DE" },
    { "cat": "idn", "typ": "kyc", "val": "enhanced" },
    { "cat": "idn", "typ": "dct", "val": "acme-corp.example", "asof": 1781860000 },
    { "cat": "idn", "typ": "dag", "val": "P850D", "asof": 1781000000 },
    { "cat": "rep", "typ": "ecommerce", "mtd": "https://ta.example/reputation/test-vector/1", "mtd#integrity": "sha256-Td9FdWbwljmeY78DD/gKxGxPSjjV9vzvOU3oXPH4dJY=", "scr": 0.94, "cnt": 3518, "wdw": "P90D", "asof": 1781800000 },
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
- Issue SD-JWT VC credentials with `typ` `dc+sd-jwt`, `alg` `ES256`, and `exp` 30 minutes after `iat`.
- Carry a SHA-256 `vct#integrity` claim binding the credential to its Type Metadata document, and publish an integrity-protected schema for that type (Section 2.9).
- Include the identity floor (`org`, `jur`, `kyc`, `dct`) in every credential (ADR 016).
- Include the registered agent `sub`, copy it from the authenticated agent record, and ensure its hostname exactly matches a `dct` within the domain-freshness window (Section 2.5.3, ADR 017).
- Include `mtd`, `mtd#integrity`, `scr`, `cnt`, `wdw`, and `asof` in every registered TSAI reputation signal, and constrain `scr` to the inclusive range 0 to 1 with higher values more favourable; derived `rep` signals follow their own integrity-pinned schema (ADR 016).
- Not insert decoy digests and not make an `sd: never` signal, reputation among them, selectively disclosable.
- Publish signing-key metadata at the URL produced by the `jwt-vc-issuer` well-known insertion rule and publish an agent-and-operator status list. The publisher that defines each `vct` publishes its immutable Type Metadata and JSON Schema; TSAI publishes the canonical artefacts, while a TA or community publishes the derived artefacts it defines.
- Advertise every `vct` the Trust Authority issues. For a derived TSAI type, extend and integrity-pin the parent metadata and schema, include the canonical base type in `aka_vcts`, and declare every custom signal.

**Agents MUST:**
- Present a credential that has not expired, with an ES256 key-binding JWT carrying `iat`, `aud`, `nonce`, and `sd_hash`, and `req` where the action and topology require it.

**Service Providers MUST:**
- Verify per Section 3, reject any `alg` other than `ES256`, reject an unrecognised `vct` or an `x5c` header, confirm `sub` matches a fresh `dct`, and, after successful derived-schema validation, MAY ignore declared extension signals not used in policy.
- Obtain the complete Type Metadata and schema chain out of band or from cache, never on the verification path, and verify every integrity value and inheritance rule (Section 2.9).
