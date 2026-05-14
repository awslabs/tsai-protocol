<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 008: User Privacy and Sybil Prevention

**Status:** Proposed  
**Date:** 2026-01-23  
**Deciders:** TSAI Working Group  
**Amended by:** [ADR 012 — Service Provider Terminology](./012-service-provider-terminology.md)

---

## Context

TSAI credentials identify **agent operators** (legal entities), not **end-users** (humans using agents). This creates a gap in addressing two critical concerns:

### 1. User Privacy
End-users want pseudonymity when agents interact with platforms on their behalf:
- Browsing products without revealing identity
- Preventing cross-platform tracking
- Revealing identity only when necessary (e.g., checkout with shipping address)

### 2. Sybil Prevention
Platforms need to prevent Sybil attacks where one person controls multiple agents to:
- Monopolize scarce resources (queue positions, limited inventory)
- Bypass rate limits
- Game reputation systems
- Commit fraud at scale

### The Fundamental Tension

**Privacy requires:** Unlinkable pseudonyms, minimal identity disclosure  
**Sybil prevention requires:** Verifiable uniqueness, one agent per human

**Additional complexity:** Once a user reveals PII (e.g., shipping address) to a platform, their pseudonym becomes linkable to their real identity on that platform. The challenge is preventing this linkage from extending across platforms or across sessions.

### Current TSAI Design

Agent credentials contain:
- Agent DID (identifies the agent instance)
- Operator identity (legal entity running the agent)
- Trust signals (reputation, economic stake, etc.)

**What's missing:**
- No mechanism to prove "this agent represents a unique verified human"
- No privacy-preserving user pseudonyms
- No cross-platform unlinkability guarantees

---

## Decision

**For TSAI v1.0:** User delegation is **out of scope**

**Rationale:**
- All viable solutions add significant complexity (ZK proofs, anonymous credentials, or TA operational burden)
- Privacy/Sybil trade-offs are application-specific (e-commerce vs. social media vs. APIs)
- Platforms already have user account systems that can address this
- Protocol should focus on operator accountability first

**For TSAI v2.0:** Revisit with one of the privacy-preserving options (likely Option 3 or 5)

**Guidance for v1.0 implementations:**
- Document the limitation clearly
- Provide recommendations for platform-level solutions
- Design credential structure to be extensible for future user delegation

---

## Options Considered

### Option 1: No User Delegation (Chosen for v1.0)

**Description:** TSAI credentials only identify agent operators. User identity and Sybil prevention are platform responsibilities.

**How it works:**
- Agent presents TSAI credential (operator identity + trust signals)
- Platform manages user identity through traditional means (accounts, sessions, OAuth)
- Platform enforces Sybil prevention through rate limiting, user accounts, behavioral analysis

**Pros:**
- Simple, keeps protocol focused
- No additional complexity or crypto requirements
- Platforms retain flexibility in user management
- Aligns with current web architecture (user accounts are standard)
- Faster time to market for v1.0

**Cons:**
- No protocol-level Sybil prevention
- No cross-platform privacy guarantees
- Inconsistent user experience across platforms
- Each platform must solve the problem independently

**Privacy implications:**
- User privacy depends on platform's account system
- No protocol-level protection against cross-platform tracking
- Operator identity is always visible to platform

**Sybil prevention:**
- Platform enforces through user accounts (one account per person)
- Rate limiting by operator credential
- Behavioral analysis and fraud detection

**Decision:** **Chosen for v1.0** - Defer to platforms, revisit in v2.0

---

### Option 2: TA-Issued Pairwise Credentials

**Description:** TA issues separate credentials for each (user, platform) pair. Each credential contains a platform-specific DID derived from user's master identity.

**How it works:**
1. User registers master identity with TA (KYC)
2. Agent requests credential for specific platform: "Issue credential for shop.example.com"
3. TA derives: `platformDID = derive(userID, "shop.example.com")`
4. TA checks: "Have I already issued credential for this (user, platform)?"
5. If yes: return existing credential; If no: issue new credential
6. Agent presents credential to platform
7. Platform verifies TA signature, enforces uniqueness by platformDID

**Credential structure:**
```json
{
  "credentialSubject": {
    "agentDID": "did:key:agent123",
    "operatorIdentity": { ... },
    "userDelegation": {
      "platformDID": "did:key:user_platform_specific",
      "platform": "shop.example.com",
      "taAttestation": "This platformDID represents a verified unique human"
    }
  }
}
```

**Pros:**
- Simple to implement (no exotic crypto)
- Strong Sybil prevention (TA enforces one DID per user per platform)
- Cross-platform unlinkability (different DIDs per platform)
- TA can revoke if user misbehaves
- Works with existing VC infrastructure

**Cons:**
- TA learns which platforms user visits (privacy leak to TA)
- TA must track (user, platform) pairs (operational burden)
- User must request new credential for each platform
- TA becomes bottleneck for new platform access
- Within-platform linkability after PII disclosure (acceptable trade-off)

**Privacy implications:**
- TA knows: user identity, which platforms user has credentials for
- TA doesn't know: what user does on platforms, when they visit
- Platform knows: user's platform-specific DID, behavior on their platform
- Platform doesn't know: user's real identity (until PII disclosure), user's master DID, activity on other platforms
- Cross-platform tracking prevented (different DIDs)

**Sybil prevention:**
- Strong: TA enforces one platformDID per verified human per platform
- Platform can trust uniqueness based on TA attestation

**Complexity:**
- Low: Standard VC issuance, no special crypto
- TA operational burden: Medium (must track pairwise credentials)

---

### Option 3: Blind Derivation with ZK Proofs

**Description:** User derives platform-specific DIDs locally. Agent proves to TA that derivation is correct without revealing master DID or platform. TA issues attestation that can be verified by platform.

**How it works:**
1. User registers master DID with TA (KYC)
2. TA issues "derivation capability" credential
3. Agent derives: `platformDID = derive(masterDID, "shop.example.com")`
4. Agent generates ZK proof: "platformDID is correctly derived from a TA-verified masterDID"
5. Agent requests TA to sign attestation (TA verifies ZK proof without learning platform)
6. Agent presents platformDID + attestation to platform
7. Platform verifies attestation, enforces uniqueness

**Credential structure:**
```json
{
  "credentialSubject": {
    "agentDID": "did:key:agent123",
    "operatorIdentity": { ... },
    "userDelegation": {
      "derivedDID": "did:key:platform_specific",
      "zkProof": "...",  // Proves correct derivation
      "taAttestation": "This derivedDID is from a verified unique human",
      "blindedUserID": "hash(userID)"  // For uniqueness enforcement
    }
  }
}
```

**Pros:**
- Strong privacy (TA doesn't learn which platforms user visits)
- Strong Sybil prevention (TA attestation + blindedUserID)
- Cross-platform unlinkability
- User controls derivation (no TA bottleneck)

**Cons:**
- Complex (requires ZK-SNARK or similar)
- Limited library support (emerging technology)
- Higher computational cost
- Not widely deployed in production
- Requires specialized TA infrastructure
- Verification complexity for platforms

**Privacy implications:**
- TA knows: user identity, that user is deriving credentials
- TA doesn't know: which platforms, when, how often
- Platform knows: derived DID, blindedUserID (for uniqueness)
- Platform doesn't know: user identity, master DID, other platforms
- Strongest privacy guarantees

**Sybil prevention:**
- Strong: Platform enforces uniqueness via blindedUserID
- TA attestation proves derivation from verified human

**Complexity:**
- High: Requires ZK proof infrastructure
- TA operational burden: Medium (verify proofs, issue attestations)
- Platform verification: Medium (verify ZK proofs)

---

### Option 4: Commitment-Based with Handshake

**Description:** TA issues credential with commitment to master DID (hash). During platform handshake, agent reveals master DID for verification, platform derives session DID and discards master DID.

**How it works:**
1. User registers master DID with TA (KYC)
2. TA issues credential with: `commitment = hash(masterDID)`, `blindedUserID`
3. Agent-Platform handshake:
   - Platform sends challenge (nonce)
   - Agent derives: `sessionDID = derive(masterDID, platformID, nonce)`
   - Agent reveals: masterDID, sessionDID, TA credential
4. Platform verifies:
   - `hash(masterDID) == commitment` in TA credential
   - `sessionDID` correctly derived
   - TA signature valid
5. Platform stores: (sessionDID, blindedUserID) for session
6. Platform discards masterDID after verification

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
- Cross-platform unlinkability (if platforms are honest)
- User controls derivation
- Standard crypto (hashing, key derivation)

**Cons:**
- Requires platform to be honest (discard master DID after verification)
- Master DID temporarily exposed during handshake
- Trust model: honest-but-curious platforms
- Platform could store master DID and link across sessions
- No cryptographic guarantee of privacy

**Privacy implications:**
- TA knows: user identity, commitment (but not platforms)
- Platform temporarily sees: master DID during handshake
- Platform should store: only sessionDID and blindedUserID
- Privacy depends on platform honesty

**Sybil prevention:**
- Strong: Platform enforces uniqueness via blindedUserID
- TA attestation proves verified human

**Complexity:**
- Medium: Standard crypto, handshake protocol
- TA operational burden: Low (issue credentials once)
- Platform verification: Medium (handshake protocol)

---

### Option 5: Anonymous Credentials (BBS+, CL Signatures)

**Description:** TA issues anonymous credentials using special signature schemes (BBS+, CL signatures) that allow selective disclosure and unlinkable presentations. User can generate unlimited pseudonyms while proving "verified unique human."

**How it works:**
1. User registers with TA (KYC)
2. TA issues anonymous credential with claims: "verified unique human", attributes
3. User generates pseudonym for platform
4. User creates presentation proving: "I have a TA credential attesting verified human"
5. Platform verifies presentation (cryptographically unlinkable to other presentations)
6. Platform enforces uniqueness through additional mechanism (e.g., rate limiting by TA)

**Credential structure:**
```json
{
  "credentialSubject": {
    "agentDID": "did:key:agent123",
    "operatorIdentity": { ... },
    "userDelegation": {
      "anonymousCredential": "...",  // BBS+ or CL signature
      "presentation": "...",  // Unlinkable proof
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
- TA knows: user identity during issuance
- TA doesn't know: which presentations user creates, which platforms
- Platform knows: user has valid credential, nothing else
- Strongest unlinkability guarantees

**Sybil prevention:**
- Weak without additional mechanism
- User can generate unlimited pseudonyms
- Requires rate limiting by TA or other approach

**Complexity:**
- Very high: Specialized crypto, limited tooling
- TA operational burden: High (specialized infrastructure)
- Platform verification: High (specialized verification)

---

### Option 6: Platform-Managed User Accounts (Out of Protocol)

**Description:** TSAI only handles operator credentials. Platforms manage user identity through traditional accounts, sessions, OAuth, etc. Sybil prevention is entirely platform responsibility.

**How it works:**
1. Agent presents TSAI credential (operator identity)
2. User authenticates to platform separately (OAuth, username/password, etc.)
3. Platform links agent to user account
4. Platform enforces Sybil prevention through account system

**Pros:**
- Keeps TSAI simple and focused on operator accountability
- Platforms already have account systems
- Maximum flexibility for platforms
- No protocol changes needed
- Aligns with current web architecture

**Cons:**
- No protocol-level Sybil prevention
- No cross-platform privacy guarantees
- Inconsistent user experience
- Each platform solves problem independently
- No standardization

**Privacy implications:**
- Depends entirely on platform's account system
- No protocol-level privacy guarantees

**Sybil prevention:**
- Depends entirely on platform's account system
- No protocol-level guarantees

**Complexity:**
- None for TSAI protocol
- Platform complexity: Existing (already have account systems)

---

## Comparison Matrix

| Option | Privacy | Sybil Prevention | Complexity | TA Burden | Platform Burden | Standards | Production Ready |
|--------|---------|------------------|------------|-----------|-----------------|-----------|------------------|
| 1. No delegation | Low | Platform-dependent | None | None | High | N/A | Yes |
| 2. Pairwise credentials | Medium | Strong | Low | Medium | Low | W3C VC | Yes |
| 3. ZK proofs | High | Strong | High | Medium | Medium | Emerging | No |
| 4. Commitment handshake | Medium | Strong | Medium | Low | Medium | Standard crypto | Possible |
| 5. Anonymous credentials | Very High | Weak* | Very High | High | High | Research | No |
| 6. Platform accounts | Platform-dependent | Platform-dependent | None | None | Existing | N/A | Yes |

*Requires additional mechanism for Sybil prevention

---

## Rationale

**Why Option 1 for v1.0:**

1. **Complexity vs. Value:** All privacy-preserving options add significant complexity. v1.0 should focus on core value: operator accountability and trust signals.

2. **Ecosystem Maturity:** Privacy-preserving identity is an active research area. Waiting for ecosystem maturity (better libraries, standards, deployment experience) will result in better v2.0 design.

3. **Platform Reality:** Platforms already have user account systems. They can address Sybil prevention through existing mechanisms while TSAI handles operator trust.

4. **Extensibility:** Credential structure can be designed to accommodate future user delegation without breaking changes.

5. **Incremental Adoption:** Operators can adopt TSAI v1.0 for accountability without requiring end-users to change behavior.

6. **Application-Specific Trade-offs:** Privacy/Sybil requirements vary by use case. E-commerce needs different solutions than social media or APIs. v1.0 lets platforms experiment.

**Why defer to v2.0:**

- **Option 2 (Pairwise)** is viable but TA learning platforms is a privacy concern
- **Option 3 (ZK proofs)** is ideal but tooling isn't mature enough
- **Option 4 (Commitment)** requires trusting platforms to discard master DID
- **Option 5 (Anonymous)** is too complex and doesn't inherently solve Sybil

**v2.0 direction:** Likely Option 3 (ZK proofs) as tooling matures, or Option 2 (Pairwise) if privacy-to-TA is acceptable.

---

## Consequences

**Positive:**
- v1.0 remains simple and focused
- Faster time to market
- Platforms retain flexibility
- No premature commitment to specific privacy approach
- Allows ecosystem to experiment and learn

**Negative:**
- No protocol-level Sybil prevention in v1.0
- No cross-platform privacy guarantees
- Platforms must solve user identity independently
- Inconsistent user experience across platforms
- May limit adoption for privacy-sensitive use cases

**Neutral:**
- User delegation becomes a v2.0 feature
- Platforms can implement their own solutions in the meantime
- Working group can observe real-world requirements before standardizing

---

## Implementation Notes

**For v1.0:**

1. **Document the limitation clearly** in architecture spec:
   - TSAI credentials identify operators, not end-users
   - User privacy and Sybil prevention are platform responsibilities
   - Provide guidance on platform-level solutions

2. **Design for extensibility:**
   - Credential structure should allow future `userDelegation` claim
   - Keep claim namespace clean for future additions

3. **Provide platform guidance:**
   - Recommend user account systems for Sybil prevention
   - Suggest rate limiting by operator credential
   - Document privacy considerations

4. **Example platform approaches:**
   - OAuth integration (user authenticates separately)
   - Session tokens (platform issues, agent presents both TSAI credential + session token)
   - Rate limiting (limit requests per operator credential)

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
   - v2.0 credentials with user delegation should be verifiable by v1.0 platforms (they ignore the claim)
   - v1.0 credentials without user delegation should remain valid

---

## Open Questions

1. Should we provide non-normative guidance on platform-level solutions in v1.0?
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
- TSAI Credential Format (architecture/02-credential-format.md)

