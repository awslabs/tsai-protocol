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

This section specifies how Service Providers verify TSAI credentials presented by Agents. Verification ensures the credential was issued by a trusted TA, has not expired or been revoked, the Agent controls the DID in the credential, and the credential has not been replayed.

This section specifies T0/T1 verification, which uses offline verification with no TA runtime dependency. T2/T3 verification (challenge-response, real-time revocation) is deferred to TSAI 1.1.

---

## 3.2 DID Resolution Requirements

Service Providers MUST be able to resolve TA DIDs to obtain public keys for signature verification.

### 3.2.1 Supported DID Methods

**For Trust Authority DIDs:**
- Service Providers MUST support `did:web` resolution
- Example: `did:web:trust-authority.example:tsai:ta`

**For Agent DIDs:**
- Service Providers MUST support `did:key` resolution (MVP)
- Service Providers SHOULD support `did:web` resolution (production)

### 3.2.2 DID Resolution Process

Service Providers MUST resolve DIDs according to the W3C DID Resolution specification (see References).

**Key requirements:**
- Service Providers MUST validate DID document signatures where applicable
- Service Providers MUST verify DID document has not expired
- Service Providers MAY cache DID documents (caching policies are implementation-specific)

**Error handling:**
- If DID resolution fails, verification MUST fail (fail closed)
- Service Providers MAY implement retry logic with exponential backoff
- Service Providers operating in degraded mode (see Section 3.5) MAY accept cached DID documents beyond normal cache duration

---

## 3.3 Credential Verification (T0/T1)

T0 and T1 credentials use offline verification with no TA runtime dependency.

### 3.3.1 Verification Overview

Verification proceeds in two phases: first verify the VP-JWT envelope (proves the Agent controls the DID), then verify the enclosed VC-JWT (proves a trusted TA issued the credential). Section 3.3.5 specifies the canonical verification algorithm. Sections 3.3.2 and 3.3.4 provide supporting details on timestamp validation and Operator DID resolution.

### 3.3.2 Timestamp Validation

**Clock Skew Tolerance:**
- Service Providers MUST accept timestamps within ±30 seconds of the Service Provider's current time
- Assumes all systems use NTP synchronization
- Rationale: Prevents replay attacks while accommodating minor clock drift

**Timestamp Format:**
- All timestamps MUST be ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
- Timezone MUST be UTC (Z suffix)

**Validation:**
```
currentTime = the Service Provider's current UTC time
issuanceTime = parse(credential.issuanceDate)
expirationTime = parse(credential.expirationDate)

if (currentTime < issuanceTime - 30 seconds):
    reject "Credential not yet valid"

if (currentTime > expirationTime + 30 seconds):
    reject "Credential expired"

accept
```

### 3.3.4 Operator DID Resolution (Optional)

Service Providers MAY resolve Operator DIDs for discovery and additional verification.

**When to resolve:**
- Discovery: Find all Agents operated by this Operator
- Verification: Cross-check Operator information in credential
- Monitoring: Track the Operator's Agent ecosystem

**Resolution process:**
1. Extract Operator DID from `credentialSubject.operatedBy.id`
2. Resolve DID according to W3C DID Resolution specification
3. Verify DID document is valid and not expired
4. Extract Operator metadata (if present in DID document)

**What Operator DID resolution provides:**
- List of all Agents operated by this Operator (via service endpoints)
- Operator's public keys (for future use cases)
- Operator's service endpoints (website, support, etc.)
- Additional Operator metadata

**What Operator DID resolution does NOT provide:**
- Credential verification (credential contains all necessary information)
- Trust signals (all trust signals are in the credential)
- Required verification step (resolution is optional)

**Error handling:**
- If Operator DID resolution fails, verification SHOULD continue
- Credential contains all information needed for verification
- Resolution failure does not invalidate credential

**Example Operator DID document:**
```json
{
  "@context": ["https://www.w3.org/ns/did/v1"],
  "id": "did:web:acme-corp.com",
  "verificationMethod": [{
    "id": "did:web:acme-corp.com#key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:web:acme-corp.com",
    "publicKeyMultibase": "z6Mk..."
  }],
  "service": [{
    "id": "did:web:acme-corp.com#agents",
    "type": "AgentRegistry",
    "serviceEndpoint": "https://acme-corp.com/agents"
  }, {
    "id": "did:web:acme-corp.com#website",
    "type": "LinkedDomains",
    "serviceEndpoint": "https://acme-corp.com"
  }]
}
```

### 3.3.5 Verifiable Presentation Verification

Agents prove possession of credentials by wrapping them in a VP-JWT (JWT-encoded Verifiable Presentation) signed with the Agent's DID private key. This is consistent with the VC-JWT encoding used for credentials (per W3C VC-JOSE-COSE).

**JSON Schema:** [`schemas/verifiable-presentation.schema.json`](schemas/verifiable-presentation.schema.json)

**VP-JWT Structure:**

```
Header:
{
  "alg": "EdDSA",
  "typ": "JWT",
  "kid": "did:web:acme-corp.com:agents:agent123#key-1"   // Agent's key
}

Payload:
{
  "vp": {
    "@context": ["https://www.w3.org/ns/credentials/v2"],
    "type": ["VerifiablePresentation"],
    "verifiableCredential": ["<VC-JWT>"]
  },
  "iss": "did:web:acme-corp.com:agents:agent123",
  "aud": "https://service-provider.example",
  "iat": 1706961330,
  "exp": 1706961390,
  "nonce": "a1b2c3d4..."
}

Signature: <EdDSA signature over header.payload>
```

**Key distinction:** The VP-JWT `kid` identifies the **Agent's** signing key (used to verify the VP). The enclosed VC-JWT `kid` identifies the **TA's** signing key (used to verify the credential). These are different keys from different parties.

**VP-JWT Claims:**

- `iss` (REQUIRED): Agent DID. MUST match `credentialSubject.id` in the enclosed VC.
- `aud` (REQUIRED): Service Provider identifier. Prevents replay against a different Service Provider.
  - HTTP transport: Request URL origin (e.g., `https://service-provider.example`)
  - MCP stdio transport: Server identifier from MCP initialization
  - Push notifications: Webhook URL origin
- `iat` (REQUIRED): Issued-at timestamp (Unix seconds). Service Providers MUST validate within ±30 seconds of current time.
- `exp` (REQUIRED): Expiration timestamp (Unix seconds). MUST be no more than 60 seconds after `iat`. This is the VP expiry (seconds), distinct from the enclosed VC expiry (hours).
- `nonce` (OPTIONAL for T0/T1, REQUIRED for T2/T3): Nonce provided by the Service Provider. When present, eliminates the replay window entirely. When absent, Service Providers rely on `iat` ±30 seconds for freshness.
- `vp.verifiableCredential` (REQUIRED): MUST contain exactly one TSAI credential (VC-JWT). VPs with zero or more than one credential MUST be rejected.

**Verification steps:**
1. Decode VP-JWT and verify structure
2. Resolve Agent DID from `iss` to get the Agent's public key (referenced by `kid` in VP-JWT header)
3. Verify VP-JWT signature using the Agent's public key
4. Verify `aud` matches the Service Provider's own identifier
5. Verify `iat` is within ±30 seconds of current time
6. Verify `exp` is no more than 60 seconds after `iat` and has not passed
7. If `nonce` is present, verify it matches a nonce issued by the Service Provider (and has not been used before)
8. Extract VC-JWT from `vp.verifiableCredential[0]`
9. Verify `iss` matches `credentialSubject.id` in the enclosed VC
10. Decode VC-JWT header and payload
11. Resolve TA DID from `issuer` claim; extract public key referenced by `kid` in VC-JWT header
12. Verify VC-JWT signature using TA's public key
13. Validate `issuanceDate` and `expirationDate` (±30 seconds clock skew tolerance, see Section 3.3.2)
14. Validate `credentialSubject` fields: Agent DID format, Operator DID format (MUST be `did:web`); optionally resolve Operator DID (see Section 3.3.4)
15. If `credentialStatus` is present, check revocation (see Section 3.4)

If any step fails, reject the credential. If all steps succeed, the credential is valid.

**Replay Prevention:**
- `aud` binds the VP to a specific Service Provider, preventing replay against a different one
- `iat` ±30 seconds limits freshness window for T0/T1
- `nonce` (when present) eliminates replay entirely for T2/T3
- `exp` caps VP lifetime at 60 seconds regardless of other checks

---

## 3.4 Revocation Checking (Optional for T0/T1, Required for T2/T3)

TSAI uses W3C BitstringStatusList for credential revocation. T2/T3 revocation requirements described here are informative and become normative alongside the T2/T3 verification protocol in TSAI 1.1.

### 3.4.1 Revocation Check Algorithm

If credential includes `credentialStatus` field:

**Step 1: Extract Status Information**
```json
"credentialStatus": {
  "id": "https://trust-authority.example/tsai/status/1#94567",
  "type": "BitstringStatusListEntry",
  "statusPurpose": "revocation",
  "statusListIndex": "94567",
  "statusListCredential": "https://trust-authority.example/tsai/status/1"
}
```

**Step 2: Fetch Status List Credential**
- HTTP GET `statusListCredential` URL
- Verify status list credential signature (issued by TA)
- Extract compressed bitstring from credential

**Step 3: Check Revocation Bit**
- Decompress bitstring
- Check bit at `statusListIndex`
- If bit = 1: Credential is revoked
- If bit = 0: Credential is valid

**Step 4: Handle Result**
- If revoked: Reject credential
- If valid: Continue verification
- If fetch fails: See Section 3.5 (Error Handling)

### 3.4.2 Caching Status Lists

Service Providers MAY cache status list credentials to reduce network requests.

**Recommendations (non-normative):**
- Cache duration: 5-15 minutes
- Invalidate cache on TA DID document changes
- Use HTTP caching headers if provided by TA

---

## 3.5 Error Handling

Verification can fail for multiple reasons. Service Providers MUST handle errors securely while maintaining availability.

### 3.5.1 Verification Failures (Fail Closed)

The following errors MUST result in credential rejection:

**Signature Errors:**
- Invalid JWT signature
- Unsupported signature algorithm
- Missing or malformed signature

**Timestamp Errors:**
- Credential expired (beyond clock skew tolerance)
- Credential not yet valid (beyond clock skew tolerance)
- Invalid timestamp format

**DID Errors:**
- Invalid DID format
- DID method not supported
- DID document signature invalid

**VP Errors:**
- VP signature invalid
- VP timestamp outside tolerance window
- Holder DID mismatch

**Revocation Errors (T2/T3 only, informative until TSAI 1.1):**
- Credential is revoked
- Status list indicates revocation

### 3.5.2 Infrastructure Failures (Degraded Mode)

The following errors MAY allow degraded mode operation:

**DID Resolution Failures:**
- TA DID document unreachable
- Network timeout
- DNS resolution failure

**Revocation Check Failures (T0/T1 only):**
- Status list credential unreachable
- Network timeout
- Status list signature invalid

**Degraded Mode Requirements:**

If a Service Provider operates in degraded mode:
- The Service Provider MUST clearly indicate degraded trust level
- The Service Provider MUST log degraded mode operation
- The Service Provider SHOULD use cached DID documents if available
- The Service Provider SHOULD implement circuit breaker patterns

**Degraded mode indication:**
```json
{
  "verified": true,
  "degraded": true,
  "warnings": [
    "TA DID resolution failed, using cached DID document",
    "Revocation check skipped due to network failure"
  ],
  "cachedUntil": "2026-01-23T11:00:00Z"
}
```

Service Providers MUST NOT operate in degraded mode for:
- Signature verification failures
- Expired credentials
- Invalid VP signatures

### 3.5.3 Error Response Format

When verification fails, Service Providers SHOULD return structured error information. Error responses MUST NOT include issuer identifiers, algorithm details, or DID resolution information. Service Providers SHOULD log detailed error information server-side for debugging.

```json
{
  "verified": false,
  "error": {
    "code": "SIGNATURE_INVALID",
    "message": "Credential verification failed"
  }
}
```

**Standard error codes:**
- `SIGNATURE_INVALID` - Credential signature verification failed
- `EXPIRED` - Credential has expired
- `NOT_YET_VALID` - Credential issuance date is in the future
- `REVOKED` - Credential has been revoked
- `DID_RESOLUTION_FAILED` - Could not resolve DID
- `VP_INVALID` - Verifiable Presentation verification failed
- `UNSUPPORTED_ALGORITHM` - Signature algorithm not supported
- `MALFORMED_CREDENTIAL` - Credential structure is invalid

---

## 3.6 Security Considerations

### 3.6.1 Replay Attack Prevention

**T0/T1 Protection:**
- `aud` claim binds the VP to a specific Service Provider, preventing replay against a different one
- `iat` ±30 seconds limits freshness window
- `exp` caps VP lifetime at 60 seconds
- Short credential expiry (2-4 hours) limits stolen credential lifetime

**T2/T3 Protection (targeted for TSAI 1.1):**
- `nonce` from the Service Provider's challenge eliminates replay window entirely
- Real-time revocation checks via BitstringStatusList

**Threat matrix:**

| Scenario | Impact | Mitigation |
|----------|--------|------------|
| Stolen VP-JWT (without Agent key) | Replay within 60s, single Service Provider only | `aud` binding + `exp` 60s max |
| Stolen VC-JWT (without Agent key) | Useless — attacker cannot create valid VP without the Agent's private key | VP signature proves key possession |
| Stolen Agent private key + VC-JWT | Full impersonation until VC expiry (2-4h) | Short credential lifetimes, key rotation, revocation (T2/T3) |

### 3.6.2 Clock Synchronization

**Critical assumption:** All systems use NTP synchronization

**Risks if clocks drift:**
- Expired credentials may be accepted
- Valid credentials may be rejected
- Replay window may expand

**Mitigation:**
- Service Providers SHOULD monitor clock drift
- Service Providers SHOULD alert on NTP synchronization failures
- ±30 second tolerance accommodates minor drift

### 3.6.3 DID Document Trust

**Trust model:**
- Service Providers trust TA DID documents obtained via did:web resolution
- did:web relies on DNS and HTTPS security
- For T0/T1: Service Providers SHOULD use DNSSEC where available
- For T2/T3: Service Providers MUST use DNSSEC-validated resolution for TA DIDs
- Service Providers MUST use HTTPS for did:web resolution

**Risks:**
- DNS hijacking could redirect to malicious DID document
- Compromised TA domain could serve malicious keys

**Mitigation:**
- DNSSEC mandatory for T2/T3 (eliminates DNS spoofing for high-stakes tiers)
- Multiple TAs provide redundancy
- Service Providers can pin TA DID documents
- Governance body maintains TA registry

### 3.6.4 Revocation Check Bypass

**Risk:** Service Providers operating in degraded mode may skip revocation checks

**Mitigation:**
- Degraded mode MUST be clearly indicated
- Service Providers SHOULD limit degraded mode duration
- Service Providers SHOULD implement circuit breakers
- T2/T3 MUST NOT skip revocation checks (fail closed)

---

## 3.7 Future Extensions

### 3.7.1 T2/T3 Verification Protocols

Future versions of this specification will define:
- Challenge-response protocols for replay prevention
- Real-time TA verification APIs
- Constraint validation mechanisms
- Enhanced revocation checking

### 3.7.2 Verification Result Caching

Service Providers MAY cache verification results to improve performance. Caching policies are implementation-specific and will be addressed in implementation guidance documents.

---

## 3.8 Normative Requirements Summary

**Service Providers MUST:**
- Support did:web resolution for TA DIDs
- Support did:key resolution for Agent DIDs (MVP)
- Verify credential signatures using TA public keys
- Validate timestamps with ±30 second tolerance
- Verify Verifiable Presentation signatures
- Fail closed on signature, timestamp, and VP errors
- Clearly indicate degraded mode operation

**Service Providers MUST (T2/T3):**
- Use DNSSEC-validated resolution for TA DIDs

**Service Providers SHOULD:**
- Support did:web resolution for Agent DIDs (production)
- Check revocation for T0/T1 credentials when available
- Implement retry logic for transient failures
- Monitor clock synchronization
- Use DNSSEC for did:web resolution (T0/T1)

**Service Providers MAY:**
- Cache DID documents
- Cache status list credentials
- Track VP signatures to prevent replay
- Operate in degraded mode for infrastructure failures
- Cache verification results

---

## References

- W3C Verifiable Credentials Data Model 2.0
- W3C VC-JOSE-COSE
- W3C DID Resolution
- W3C BitstringStatusList
- RFC 7519 (JSON Web Token)
- RFC 7515 (JSON Web Signature)

