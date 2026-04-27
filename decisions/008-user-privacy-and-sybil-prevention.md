<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 008: User Privacy and Sybil Prevention

**Status:** Proposed  
**Date:** 2026-01-23  
**Deciders:** TSAI Working Group

---

## Context

TSAI credentials identify **Agent Operators** (legal entities), not **end-users** (humans using Agents). This creates a gap in addressing two critical concerns:

### 1. User Privacy
End-users want pseudonymity when Agents interact with Service Providers on their behalf:
- Browsing products without revealing identity
- Preventing tracking across Service Providers
- Revealing identity only when necessary (e.g., checkout with shipping address)

### 2. Sybil Prevention
Service Providers need to prevent Sybil attacks where one person controls multiple Agents to:
- Monopolize scarce resources (queue positions, limited inventory)
- Bypass rate limits
- Game reputation systems
- Commit fraud at scale

### The Fundamental Tension

**Privacy requires:** Unlinkable pseudonyms, minimal identity disclosure  
**Sybil prevention requires:** Verifiable uniqueness, one Agent per human

**Additional complexity:** Once a User reveals PII (e.g., shipping address) to a Service Provider, their pseudonym becomes linkable to their real identity with that Service Provider. The challenge is preventing this linkage from extending to other Service Providers or across sessions.

### Current TSAI Design

Agent credentials contain:
- Agent DID (identifies the Agent instance)
- Operator identity (legal entity running the Agent)
- Trust signals (reputation, economic stake, etc.)

**What's missing:**
- No mechanism to prove "this Agent represents a unique verified human"
- No privacy-preserving User pseudonyms
- No unlinkability guarantees across Service Providers

---

## Decision

**For TSAI v1.0:** User delegation is **out of scope**

**Rationale:**
- All viable solutions add significant complexity (ZK proofs, anonymous credentials, or TA operational burden)
- Privacy/Sybil trade-offs are application-specific (e-commerce vs. social media vs. APIs)
- Service Providers already have user account systems that can address this
- Protocol should focus on Operator accountability first

**For TSAI v2.0:** Revisit with one of the privacy-preserving options (likely Option 3 or 5)

**Guidance for v1.0 implementations:**
- Document the limitation clearly
- Provide recommendations for solutions at the Service Provider layer
- Design credential structure to be extensible for future user delegation

---

## Options Considered

### Option 1: No User Delegation (Chosen for v1.0)

**Description:** TSAI credentials only identify Agent Operators. User identity and Sybil prevention are the Service Provider's responsibility.

**How it works:**
- Agent presents TSAI credential (Operator identity + trust signals)
- The Service Provider manages user identity through traditional means (accounts, sessions, OAuth)
- The Service Provider enforces Sybil prevention through rate limiting, user accounts, behavioral analysis

**Pros:**
- Simple, keeps protocol focused
- No additional complexity or crypto requirements
- Service Providers retain flexibility in user management
- Aligns with current web architecture (user accounts are standard)
- Faster time to market for v1.0

**Cons:**
- No protocol-level Sybil prevention
- No unlinkability guarantees across Service Providers
- Inconsistent user experience across Service Providers
- Each Service Provider must solve the problem independently

**Privacy implications:**
- User privacy depends on the Service Provider's account system
- No protocol-level protection against tracking across Service Providers
- Operator identity is always visible to the Service Provider

**Sybil prevention:**
- The Service Provider enforces through user accounts (one account per person)
- Rate limiting by Operator credential
- Behavioral analysis and fraud detection

**Decision:** **Chosen for v1.0** - Defer to Service Providers, revisit in v2.0

---

### Option 2: TA-Issued Pairwise Credentials

**Description:** The TA issues separate credentials for each (User, Service Provider) pair. Each credential contains a Service-Provider-specific DID derived from the User's master identity.

**How it works:**
1. User registers master identity with TA (KYC)
2. Agent requests credential for a specific Service Provider: "Issue credential for shop.example.com"
3. TA derives: `serviceProviderDID = derive(userID, "shop.example.com")`
4. TA checks: "Have I already issued a credential for this (User, Service Provider)?"
5. If yes: return existing credential; If no: issue new credential
6. Agent presents credential to the Service Provider
7. The Service Provider verifies the TA signature and enforces uniqueness by serviceProviderDID

**Credential structure:**
```json
{
  "credentialSubject": {
    "agentDID": "did:key:agent123",
    "operatorIdentity": { ... },
    "userDelegation": {
      "serviceProviderDID": "did:key:user_sp_specific",
      "serviceProvider": "shop.example.com",
      "taAttestation": "This serviceProviderDID represents a verified unique human"
    }
  }
}
```

**Pros:**
- Simple to implement (no exotic crypto)
- Strong Sybil prevention (TA enforces one DID per User per Service Provider)
- Unlinkability across Service Providers (different DIDs per Service Provider)
- TA can revoke if User misbehaves
- Works with existing VC infrastructure

**Cons:**
- TA learns which Service Providers the User visits (privacy leak to TA)
- TA must track (User, Service Provider) pairs (operational burden)
- User must request new credential for each Service Provider
- TA becomes bottleneck for new Service Provider access
- Linkability within a single Service Provider after PII disclosure (acceptable trade-off)

**Privacy implications:**
- TA knows: User identity, which Service Providers the User has credentials for
- TA doesn't know: what the User does on Service Providers, when they visit
- The Service Provider knows: the User's Service-Provider-specific DID, behavior on their own system
- The Service Provider doesn't know: the User's real identity (until PII disclosure), the User's master DID, activity with other Service Providers
- Tracking across Service Providers is prevented (different DIDs)

**Sybil prevention:**
- Strong: TA enforces one serviceProviderDID per verified human per Service Provider
- The Service Provider can trust uniqueness based on TA attestation

**Complexity:**
- Low: Standard VC issuance, no special crypto
- TA operational burden: Medium (must track pairwise credentials)

---

### Option 3: Blind Derivation with ZK Proofs

**Description:** The User derives Service-Provider-specific DIDs locally. The Agent proves to the TA that derivation is correct without revealing the master DID or the Service Provider. The TA issues an attestation that the Service Provider can verify.

**How it works:**
1. User registers master DID with TA (KYC)
2. TA issues "derivation capability" credential
3. Agent derives: `derivedDID = derive(masterDID, "shop.example.com")`
4. Agent generates ZK proof: "derivedDID is correctly derived from a TA-verified masterDID"
5. Agent requests TA to sign attestation (TA verifies ZK proof without learning the Service Provider)
6. Agent presents derivedDID + attestation to the Service Provider
7. The Service Provider verifies the attestation and enforces uniqueness

**Credential structure:**
```json
{
  "credentialSubject": {
    "agentDID": "did:key:agent123",
    "operatorIdentity": { ... },
    "userDelegation": {
      "derivedDID": "did:key:sp_specific",
      "zkProof": "...",
      "taAttestation": "This derivedDID is from a verified unique human",
      "blindedUserID": "hash(userID)"
    }
  }
}
```

**Pros:**
- Strong privacy (TA doesn't learn which Service Providers the User visits)
- Strong Sybil prevention (TA attestation + blindedUserID)
- Unlinkability across Service Providers
- User controls derivation (no TA bottleneck)

**Cons:**
- Complex (requires ZK-SNARK or similar)
- Limited library support (emerging technology)
- Higher computational cost
- Not widely deployed in production
- Requires specialized TA infrastructure
- Verification complexity for Service Providers

**Privacy implications:**
- TA knows: User identity, that the User is deriving credentials
- TA doesn't know: which Service Providers, when, how often
- The Service Provider knows: derived DID, blindedUserID (for uniqueness)
- The Service Provider doesn't know: User identity, master DID, other Service Providers
- Strongest privacy guarantees

**Sybil prevention:**
- Strong: The Service Provider enforces uniqueness via blindedUserID
- TA attestation proves derivation from verified human

**Complexity:**
- High: Requires ZK proof infrastructure
- TA operational burden: Medium (verify proofs, issue attestations)
- Verification burden for Service Providers: Medium (verify ZK proofs)

---

### Option 4: Commitment-Based with Handshake

**Description:** The TA issues a credential with a commitment to the master DID (hash). During the handshake with the Service Provider, the Agent reveals the master DID for verification; the Service Provider derives a session DID and discards the master DID.

**How it works:**
1. User registers master DID with TA (KYC)
2. TA issues credential with: `commitment = hash(masterDID)`, `blindedUserID`
3. Agent-Service-Provider handshake:
   - The Service Provider sends challenge (nonce)
   - Agent derives: `sessionDID = derive(masterDID, serviceProviderID, nonce)`
   - Agent reveals: masterDID, sessionDID, TA credential
4. The Service Provider verifies:
   - `hash(masterDID) == commitment` in TA credential
   - `sessionDID` correctly derived
   - TA signature valid
5. The Service Provider stores: (sessionDID, blindedUserID) for session
6. The Service Provider discards masterDID after verification

**Credential structure:**
```json
{
  "credentialSubject": {
    "agentDID": "did:key:agent123",
    "operatorIdentity": { ... },
    "userDelegation": {
      "masterDIDCommitment": "hash(masterDID)",
      "blindedUserID": "hash(userID)",
      "taAttestation": "Commitment is to a verified unique human"
    }
  }
}
```

**Pros:**
- Moderate complexity (no ZK proofs)
- Strong Sybil prevention
- Unlinkability across Service Providers (if Service Providers are honest)
- User controls derivation
- Standard crypto (hashing, key derivation)

**Cons:**
- Requires the Service Provider to be honest (discard master DID after verification)
- Master DID temporarily exposed during handshake
- Trust model: honest-but-curious Service Providers
- A Service Provider could store the master DID and link across sessions
- No cryptographic guarantee of privacy

**Privacy implications:**
- TA knows: User identity, commitment (but not Service Providers)
- The Service Provider temporarily sees: master DID during handshake
- The Service Provider should store: only sessionDID and blindedUserID
- Privacy depends on the Service Provider's honesty

**Sybil prevention:**
- Strong: The Service Provider enforces uniqueness via blindedUserID
- TA attestation proves verified human

**Complexity:**
- Medium: Standard crypto, handshake protocol
- TA operational burden: Low (issue credentials once)
- Verification burden for Service Providers: Medium (handshake protocol)

---

### Option 5: Anonymous Credentials (BBS+, CL Signatures)

**Description:** The TA issues anonymous credentials using special signature schemes (BBS+, CL signatures) that allow selective disclosure and unlinkable presentations. The User can generate unlimited pseudonyms while proving "verified unique human."

**How it works:**
1. User registers with TA (KYC)
2. TA issues anonymous credential with claims: "verified unique human", attributes
3. User generates pseudonym for the Service Provider
4. User creates presentation proving: "I have a TA credential attesting verified human"
5. The Service Provider verifies the presentation (cryptographically unlinkable to other presentations)
6. The Service Provider enforces uniqueness through an additional mechanism (e.g., rate limiting by TA)

**Credential structure:**
```json
{
  "credentialSubject": {
    "agentDID": "did:key:agent123",
    "operatorIdentity": { ... },
    "userDelegation": {
      "anonymousCredential": "...",
      "presentation": "...",
      "claims": ["verified_human", "kyc_level_enhanced"]
    }
  }
}
```

**Pros:**
- Strongest privacy guarantees
- Cryptographically sound unlinkability
- Selective disclosure (reveal only necessary claims)
- Well-researched (Idemix, U-Prove, BBS+)
- User can generate unlimited pseudonyms

**Cons:**
- Very complex
- Limited library support (BBS+ is newer, CL signatures are older but complex)
- Not widely deployed in production
- Requires specialized TA infrastructure
- Sybil prevention requires additional mechanism (not inherent)
- Higher computational cost

**Privacy implications:**
- TA knows: User identity during issuance
- TA doesn't know: which presentations the User creates, which Service Providers
- The Service Provider knows: the User has a valid credential, nothing else
- Strongest unlinkability guarantees

**Sybil prevention:**
- Weak without additional mechanism
- User can generate unlimited pseudonyms
- Requires rate limiting by TA or other approach

**Complexity:**
- Very high: Specialized crypto, limited tooling
- TA operational burden: High (specialized infrastructure)
- Verification burden for Service Providers: High (specialized verification)

---

### Option 6: User Accounts Managed by the Service Provider (Out of Protocol)

**Description:** TSAI only handles Operator credentials. Service Providers manage User identity through traditional accounts, sessions, OAuth, etc. Sybil prevention is entirely the Service Provider's responsibility.

**How it works:**
1. Agent presents TSAI credential (Operator identity)
2. User authenticates to the Service Provider separately (OAuth, username/password, etc.)
3. The Service Provider links the Agent to the user account
4. The Service Provider enforces Sybil prevention through its account system

**Pros:**
- Keeps TSAI simple and focused on Operator accountability
- Service Providers already have account systems
- Maximum flexibility for Service Providers
- No protocol changes needed
- Aligns with current web architecture

**Cons:**
- No protocol-level Sybil prevention
- No unlinkability guarantees across Service Providers
- Inconsistent user experience
- Each Service Provider solves the problem independently
- No standardization

**Privacy implications:**
- Depends entirely on the Service Provider's account system
- No protocol-level privacy guarantees

**Sybil prevention:**
- Depends entirely on the Service Provider's account system
- No protocol-level guarantees

**Complexity:**
- None for the TSAI protocol
- Complexity for each Service Provider: existing (they already have account systems)

---

## Comparison Matrix

| Option | Privacy | Sybil Prevention | Complexity | TA Burden | Burden on Service Provider | Standards | Production Ready |
|--------|---------|------------------|------------|-----------|----------------------------|-----------|------------------|
| 1. No delegation | Low | Depends on Service Provider | None | None | High | N/A | Yes |
| 2. Pairwise credentials | Medium | Strong | Low | Medium | Low | W3C VC | Yes |
| 3. ZK proofs | High | Strong | High | Medium | Medium | Emerging | No |
| 4. Commitment handshake | Medium | Strong | Medium | Low | Medium | Standard crypto | Possible |
| 5. Anonymous credentials | Very High | Weak* | Very High | High | High | Research | No |
| 6. Service-Provider accounts | Depends on Service Provider | Depends on Service Provider | None | None | Existing | N/A | Yes |

*Requires additional mechanism for Sybil prevention

---

## Rationale

**Why Option 1 for v1.0:**

1. **Complexity vs. Value:** All privacy-preserving options add significant complexity. v1.0 should focus on core value: Operator accountability and trust signals.

2. **Ecosystem Maturity:** Privacy-preserving identity is an active research area. Waiting for ecosystem maturity (better libraries, standards, deployment experience) will result in better v2.0 design.

3. **Reality on the Service Provider side:** Service Providers already have user account systems. They can address Sybil prevention through existing mechanisms while TSAI handles Operator trust.

4. **Extensibility:** Credential structure can be designed to accommodate future user delegation without breaking changes.

5. **Incremental Adoption:** Operators can adopt TSAI v1.0 for accountability without requiring end-users to change behavior.

6. **Application-Specific Trade-offs:** Privacy/Sybil requirements vary by use case. E-commerce needs different solutions than social media or APIs. v1.0 lets Service Providers experiment.

**Why defer to v2.0:**

- **Option 2 (Pairwise)** is viable but TA learning Service Providers is a privacy concern
- **Option 3 (ZK proofs)** is ideal but tooling isn't mature enough
- **Option 4 (Commitment)** requires trusting Service Providers to discard the master DID
- **Option 5 (Anonymous)** is too complex and doesn't inherently solve Sybil

**v2.0 direction:** Likely Option 3 (ZK proofs) as tooling matures, or Option 2 (Pairwise) if privacy-to-TA is acceptable.

---

## Consequences

**Positive:**
- v1.0 remains simple and focused
- Faster time to market
- Service Providers retain flexibility
- No premature commitment to specific privacy approach
- Allows ecosystem to experiment and learn

**Negative:**
- No protocol-level Sybil prevention in v1.0
- No unlinkability guarantees across Service Providers
- Service Providers must solve user identity independently
- Inconsistent user experience across Service Providers
- May limit adoption for privacy-sensitive use cases

**Neutral:**
- User delegation becomes a v2.0 feature
- Service Providers can implement their own solutions in the meantime
- Working group can observe real-world requirements before standardizing

---

## Implementation Notes

**For v1.0:**

1. **Document the limitation clearly** in architecture spec:
   - TSAI credentials identify Operators, not end-users
   - User privacy and Sybil prevention are the Service Provider's responsibility
   - Provide guidance on solutions at the Service Provider layer

2. **Design for extensibility:**
   - Credential structure should allow future `userDelegation` claim
   - Keep claim namespace clean for future additions

3. **Provide guidance to Service Providers:**
   - Recommend user account systems for Sybil prevention
   - Suggest rate limiting by Operator credential
   - Document privacy considerations

4. **Example approaches on the Service Provider side:**
   - OAuth integration (User authenticates separately)
   - Session tokens (the Service Provider issues, the Agent presents both TSAI credential + session token)
   - Rate limiting (limit requests per Operator credential)

**For v2.0:**

1. **Research and prototype:**
   - Evaluate ZK proof libraries (zk-SNARKs, zk-STARKs)
   - Test BBS+ signature implementations
   - Gather feedback from v1.0 deployments

2. **Define user delegation extension:**
   - Choose privacy-preserving approach based on ecosystem maturity
   - Specify credential format with `userDelegation` claim
   - Define verification algorithms
   - Create test vectors

3. **Backward compatibility:**
   - v2.0 credentials with user delegation should be verifiable by v1.0 Service Providers (they ignore the claim)
   - v1.0 credentials without user delegation should remain valid

---

## Open Questions

1. Should we provide non-normative guidance on solutions at the Service Provider layer in v1.0?
2. Should we reserve the `userDelegation` claim namespace for v2.0?
3. Should we create a separate document exploring privacy-preserving options in detail?
4. Should we engage with privacy research community for v2.0 design?

---

## References

- W3C Verifiable Credentials Data Model 2.0
- W3C Decentralized Identifiers (DIDs)
- BBS+ Signatures: https://identity.foundation/bbs-signature/draft-irtf-cfrg-bbs-signatures.html
- Anonymous Credentials: Idemix, U-Prove
- Zero-Knowledge Proofs: zk-SNARKs, zk-STARKs
- TSAI High-Level Concept (concept/02-high-level-concept.md)
- TSAI Credential Format (architecture/03-credential-format.md)

