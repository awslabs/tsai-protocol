<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 003: W3C Verifiable Credentials as Credential Format

**Status:** Superseded  
**Date:** 2026-01-22  
**Deciders:** TAP Working Group  
**Superseded by:** [Credential Serialisation Format](./draft-xx2-credential-serialisation-format.md) (this branch)  
**Amended by:** [ADR 012 — Service Provider Terminology](./012-service-provider-terminology.md)

---

## Context

The protocol requires a credential format for TAs to issue trust signals to agents. The format must support:

- Cryptographic signatures (tamper-evident)
- Multiple claim types (identity, reputation, stake, constraints)
- Revocation mechanisms
- Privacy features (selective disclosure)
- Interoperability with broader identity ecosystem

---

## Options Considered

### Option 1: Custom JWT Format

**Description:** Define custom JWT structure with TSAI-specific claims.

**Pros:**
- Simple, well-understood format
- Existing libraries and tooling
- Compact encoding
- Fast verification

**Cons:**
- Not interoperable with broader VC ecosystem
- No selective disclosure support
- Custom revocation mechanism needed
- Reinventing standards (NIH syndrome)
- No future extensibility path

---

### Option 2: JSON Web Tokens (JWT) with Custom Claims

**Description:** Standard JWT with TSAI claims in payload.

**Pros:**
- Simplest option
- Maximum compatibility
- Smallest credential size
- Fastest verification

**Cons:**
- No VC semantics (issuer/holder/verifier model)
- No standard revocation mechanism
- No selective disclosure
- Not interoperable with VC ecosystem
- Limited extensibility

---

### Option 3: W3C Verifiable Credentials

**Description:** W3C VC Data Model 2.0 with VC-JWT encoding for MVP.

**Pros:**
- Standards-based (W3C Recommendation)
- Perfect conceptual fit (issuer/holder/verifier)
- Future-proof extensibility
- Selective disclosure support (BBS+)
- Existing libraries and tooling
- Interoperable with broader ecosystem
- BitstringStatusList for revocation
- Verifiable Presentations for binding

**Cons:**
- Slightly larger credentials (~2-3x JWT size)
- JSON-LD processing overhead (mitigated by VC-JWT)
- Less mature tooling than pure JWT (improving rapidly)

---

### Option 4: Custom Binary Format

**Description:** Optimized binary credential format for performance.

**Pros:**
- Smallest possible size
- Fastest possible verification
- Optimized for TSAI use case

**Cons:**
- No standards alignment
- No ecosystem interoperability
- Custom tooling required
- Maintenance burden
- No extensibility path

---

## Decision

Adopt **W3C Verifiable Credentials Data Model 2.0** (Option 3) as the credential format, with **VC-JWT** encoding for MVP.

**Rationale:**

### Standards Alignment

**W3C Recommendation:**
- Broad industry support (Microsoft, IBM, Spruce, etc.)
- Active ecosystem and tooling
- Future-proof (W3C maintenance and evolution)

**Perfect Conceptual Fit:**
- Issuer (TA) → Holder (Agent) → Verifier (Platform)
- Exactly matches TSAI's three-party model
- Native support for trust signal use case

**Interoperability:**
- Works with broader identity/trust ecosystems
- Agents can present TSAI credentials alongside other VCs
- Platforms can verify multiple credential types with same infrastructure

### Future-Proof Extensibility

**Multiple Proof Formats:**
- Data Integrity proofs (JSON-LD signatures)
- JWT proofs (VC-JWT)
- BBS+ signatures (selective disclosure)
- Algorithm-agnostic (add new signature types without protocol changes)

**Selective Disclosure:**
- BBS+ signatures enable privacy-preserving proofs
- Agent can prove "reputation > 80" without revealing exact score
- Important for GDPR compliance and privacy

**Extensible Claims:**
- Easy to add new trust signals
- Custom claim types in TSAI namespace
- Backward compatibility maintained

### Practical Benefits

**VC-JWT Encoding:**
- JWT performance with VC semantics
- Existing JWT libraries work with minimal changes
- Compact serialization (smaller than JSON-LD)
- Good for T0/T1 offline verification

**Existing Libraries:**
- Veramo, SpruceID, MATTR, Trinsic
- Reduces implementation burden
- Battle-tested code

**BitstringStatusList:**
- Efficient revocation mechanism (W3C standard)
- More efficient than custom revocation lists
- Privacy-preserving (doesn't reveal which credential was checked)

**Verifiable Presentations:**
- Native support for credential binding (prevents theft)
- Domain binding (prevents replay)
- Challenge-response patterns

### Privacy Advantages

**Pseudonymous Identifiers:**
- Agent DID (not user identity)
- Reputation aggregated (not individual transactions)
- No user PII in credentials

**Selective Disclosure:**
- Prove claims without revealing all data
- Better GDPR compliance
- User privacy protection

**Data Minimization:**
- Only necessary claims in credentials
- Purpose limitation built-in
- Retention limits (credentials expire)

---

## Migration Path

### Phase 1: VC-JWT (MVP)

- Use VC-JWT encoding (JWT-compatible)
- Minimal disruption for platforms
- Leverage existing JWT libraries
- Good performance for T0/T1

### Phase 2: Add DIDs

- Migrate to DID-based identifiers
- `did:web` for TAs
- `did:key` or `did:web` for agents
- Enables key rotation and service endpoints

### Phase 3: BitstringStatusList

- Implement W3C BitstringStatusList for revocation
- More efficient than custom mechanisms
- Privacy-preserving

### Phase 4: Selective Disclosure

- Enable BBS+ signatures for T2/T3
- Agents can prove claims without revealing all data
- Better privacy for sensitive operations

---

## Trade-offs Accepted

### Credential Size

**Impact:** VC credentials ~2-3x larger than pure JWT

**Mitigation:**
- VC-JWT compact serialization
- Compression for transport
- Caching at platforms
- Acceptable for trust use case (not high-frequency data)

### JSON-LD Processing

**Impact:** JSON-LD processing overhead for Data Integrity proofs

**Mitigation:**
- Use VC-JWT for T0/T1 (no JSON-LD processing)
- Cache JSON-LD contexts
- Use Data Integrity only for T2/T3 when needed
- Tooling improvements over time

### Tooling Maturity

**Impact:** VC tooling less mature than pure JWT

**Mitigation:**
- Ecosystem improving rapidly (2024-2026)
- Multiple production-ready libraries available
- Worth investment for long-term benefits
- Standards-based approach reduces risk

---

## Consequences

### Positive

- **Standards-based:** W3C Recommendation with broad support
- **Interoperable:** Works with broader VC ecosystem
- **Future-proof:** Extensible, algorithm-agnostic
- **Privacy:** Selective disclosure support
- **Proven:** Battle-tested in production systems

### Negative

- **Complexity:** More complex than pure JWT
- **Size:** Larger credentials than pure JWT
- **Learning curve:** Teams must learn VC concepts

### Neutral

- **Tooling:** Requires VC libraries (Veramo, SpruceID, etc.)
- **Migration:** Phased approach from VC-JWT to full VC features

---

## Implementation Notes

**MVP (VC-JWT):**
- Use VC-JWT encoding for credentials
- Standard JWT libraries with VC semantics
- Offline verification for T0/T1
- Simple revocation (expiry-based)

**Production:**
- Add BitstringStatusList for revocation
- Implement Verifiable Presentations
- Support multiple proof formats
- Enable selective disclosure for T2/T3

**Libraries:**
- Veramo (TypeScript/JavaScript)
- SpruceID (Rust, Go, Python)
- MATTR (commercial, enterprise)
- Trinsic (commercial, developer-friendly)

---

## References

- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [W3C VC-JOSE-COSE](https://www.w3.org/TR/vc-jose-cose/)
- [W3C BitstringStatusList](https://www.w3.org/TR/vc-bitstring-status-list/)
- TAP Design Considerations (concept/archive/01-design-considerations.md)
- TAP High-Level Concept (concept/02-high-level-concept.md)
