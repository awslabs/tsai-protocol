<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 006: DID Methods for TAs and Agents

**Status:** Accepted  
**Date:** 2026-01-22  
**Deciders:** TSAI Working Group

---

## Context

The protocol uses Decentralized Identifiers (DIDs) for both Trust Authorities and agents. Multiple DID methods exist with different properties:

- **did:web** - DNS-based, simple, centralized
- **did:key** - Self-contained, no infrastructure, no key rotation
- **did:peer** - Peer-to-peer, private, not suitable for public discovery
- **did:ion** - Bitcoin-anchored, decentralized, complex

The choice affects:
- Infrastructure requirements
- Key rotation capabilities
- Discovery mechanisms
- Interoperability
- Adoption barriers

---

## Options Considered

| Method | Infrastructure | Key Rotation | Discovery | Complexity | Cost |
|--------|---------------|--------------|-----------|------------|------|
| did:web | DNS + HTTPS | Yes | Simple | Low | Domain cost |
| did:key | None | No | N/A | Minimal | Free |
| did:peer | None | Yes | Private | Medium | Free |
| did:ion | Bitcoin | Yes | Public | High | Gas fees |

---

## Alternatives Considered

### Option 1: did:key for Everyone

**Description:** Both TAs and agents use did:key.

**Pros:**
- Simplest possible approach
- No infrastructure required
- Truly decentralized

**Cons:**
- No key rotation (critical for TAs)
- No service endpoints (needed for TA APIs)
- No discovery mechanism (how do platforms find TAs?)
- Not suitable for professional TAs

---

### Option 2: did:web for Everyone

**Description:** Both TAs and agents use did:web.

**Pros:**
- Consistent approach
- Key rotation for everyone
- Service endpoints for everyone

**Cons:**
- Requires domain ownership for all agents
- Higher barrier to entry for agents
- DNS dependency for everyone
- Overkill for simple agents

---

### Option 3: did:ion (Blockchain-based)

**Description:** Use Bitcoin-anchored DIDs for decentralization.

**Pros:**
- Truly decentralized
- No single point of control
- Censorship-resistant

**Cons:**
- Complex infrastructure
- Slower resolution
- Gas fees for updates
- Overkill for TSAI use case
- Doesn't align with centralized TA model

---

### Option 4: did:peer (Peer-to-peer)

**Description:** DIDs exchanged directly between parties.

**Pros:**
- Privacy-preserving
- No infrastructure
- Decentralized

**Cons:**
- Not suitable for public discovery
- TAs need to be publicly discoverable
- Complex for TSAI use case

---

### Option 5: Mixed Approach

**Description:**
- TAs use did:web (discovery, key rotation, service endpoints)
- Agents use did:key for MVP (simplicity)
- Agents use did:web for production (key rotation, service endpoints)
- Protocol supports multiple agent DID methods

**Pros:**
- Optimal for each use case
- Low barrier to entry (did:key for MVP)
- Production-ready path (did:web)
- Flexible (agents choose)

**Cons:**
- Platforms must support multiple DID methods
- More complex than single method

---

## Decision

**Mixed Approach** (Option 5):

**Trust Authorities:** `did:web` (mandatory)

**Agents:**
- **MVP:** `did:key` (simplest, no infrastructure)
- **Production:** `did:web` (enables key rotation, service endpoints)  
- **Protocol:** Supports multiple agent DID methods including `did:wba` (platforms must handle all)

**Rationale:**

### Trust Authorities: did:web

TAs already have domains and HTTPS infrastructure. Governance body maintains TA registry with `did:web` identifiers. Platforms can resolve TA DIDs via HTTPS. TAs can update DID documents for key rotation. DID document includes TA API endpoints for real-time verification and revocation status lists.

### Agents: did:key (MVP)

DID derived directly from public key. No infrastructure required. No registration process. Fastest possible verification (key embedded in DID). Acceptable trade-off: no key rotation (agents can migrate to `did:web` later).

### Agents: did:web (Production)

Enables key rotation without changing DID. Agent can publish API endpoints. Agent identity tied to domain (operator controls). Acceptable trade-offs: requires domain ownership, DNS dependency.

### Agents: did:wba Support

TSAI explicitly supports `did:wba` for W3C AI Agent Protocol compatibility. Agents using W3C AI Agent Protocol can obtain TSAI credentials using their `did:wba` identifiers.

---

## Consequences

### Positive

- **TA Discovery:** Governance body registry with did:web identifiers
- **Agent Simplicity:** did:key for MVP (no infrastructure)
- **Production Ready:** did:web for production agents (key rotation)
- **Flexibility:** Agents choose DID method based on needs

### Negative

- **Platform Complexity:** Must support multiple agent DID methods
- **Agent Migration:** Agents may need to migrate from did:key to did:web
- **DNS Dependency:** did:web relies on DNS (centralization)

### Neutral

- **Ecosystem Evolution:** Agents start with did:key, migrate to did:web as they mature
- **DID Method Support:** Protocol can add support for new DID methods in future

### Future Considerations

- **Signature algorithms:** TSAI 1.0 supports EdDSA (Ed25519) and ES256/ES384/ES512 (via JsonWebSignature2020). Future versions may add secp256k1 support for blockchain-native agents (Ethereum wallets as agent identities) if demand materializes.
- **Additional DID methods:** did:ethr or did:pkh could complement secp256k1 support for blockchain ecosystems.

---

## Implementation Notes

### Trust Authorities

**DID Method:** `did:web` (mandatory)

**DID Format:** `did:web:{domain}:tap:ta`

**Resolution:** HTTPS GET to `https://{domain}/.well-known/did.json`

**DID Document Must Include:**
- Verification methods (public keys for signing credentials)
- Service endpoints (credential issuance API, revocation status list, real-time verification API)

**Example:**
```json
{
  "@context": ["https://www.w3.org/ns/did/v1"],
  "id": "did:web:trust-authority.example:tap:ta",
  "verificationMethod": [{
    "id": "did:web:trust-authority.example:tap:ta#key-1",
    "type": "JsonWebKey2020",
    "controller": "did:web:trust-authority.example:tap:ta",
    "publicKeyJwk": { ... }
  }],
  "service": [{
    "id": "did:web:trust-authority.example:tap:ta#credential-issuance",
    "type": "TAPCredentialIssuance",
    "serviceEndpoint": "https://api.trust-authority.example/tap/credentials"
  }]
}
```

---

### Agents (MVP)

**DID Method:** `did:key` (recommended for MVP)

**DID Format:** `did:key:{multibase-encoded-public-key}`

**Resolution:** No resolution needed (key embedded in DID)

**Example:**
```
did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH
```

**Key Generation:**
- Agent generates Ed25519 key pair
- Derives DID from public key
- No registration required

---

### Agents (Production)

**DID Method:** `did:web` (recommended for production)

**DID Format:** `did:web:{domain}:agents:{agent-id}`

**Resolution:** HTTPS GET to `https://{domain}/agents/{agent-id}/did.json`

**DID Document Must Include:**
- Verification methods (public keys for signing VPs)
- Optional: Service endpoints (agent APIs for agent-to-agent communication)

**Example:**
```json
{
  "@context": ["https://www.w3.org/ns/did/v1"],
  "id": "did:web:agent-operator.com:agents:agent123",
  "verificationMethod": [{
    "id": "did:web:agent-operator.com:agents:agent123#key-1",
    "type": "JsonWebKey2020",
    "controller": "did:web:agent-operator.com:agents:agent123",
    "publicKeyJwk": { ... }
  }]
}
```

---

### Platform Implementation

**Must Support:**
- `did:web` resolution (for TAs and production agents)
- `did:key` resolution (for MVP agents)

**DID Resolution:**
- Use standard DID resolution libraries
- Cache DID documents (reduce latency)
- Handle resolution failures gracefully

**Verification:**
- Resolve DID to get public key
- Verify credential signature with public key
- Verify VP signature with agent's public key

---

## Migration Path

### Phase 1 (MVP)

- TAs use `did:web`
- Agents use `did:key`
- Simple, low barrier to entry

### Phase 2 (Production)

- TAs continue using `did:web`
- Agents migrate to `did:web` (optional)
- Agents can keep `did:key` if preferred

### Phase 3 (Ecosystem Maturity)

- Most production agents use `did:web`
- `did:key` still supported for simple agents
- Protocol may add support for additional DID methods

---

## References

- [W3C DID Core Specification](https://www.w3.org/TR/did-core/)
- [W3C DID Resolution](https://w3c-ccg.github.io/did-resolution/)
- [did:web Method Specification](https://w3c-ccg.github.io/did-method-web/)
- [did:key Method Specification](https://w3c-ccg.github.io/did-method-key/)
- TSAI High-Level Concept (concept/02-high-level-concept.md)
