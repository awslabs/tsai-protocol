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

### 5.1.1 What TSAI Trusts (Protocol Assumptions)

The TSAI protocol is built on the following trust assumptions:

**Trust Authorities:**
- TAs operate honestly and securely
- TAs perform claimed verification processes (KYC, reputation monitoring, stake verification)
- TAs protect their signing keys appropriately
- TAs issue credentials only to agents that meet stated criteria
- TAs maintain accurate revocation status

**Cryptographic Foundations:**
- Signature algorithms (ES256, EdDSA) are secure
- Key lengths provide adequate security (256-bit minimum)
- Random number generation has sufficient entropy
- Hash functions are collision-resistant

**Infrastructure:**
- DID resolution infrastructure (DNS, HTTPS) operates correctly
- Certificate authorities for HTTPS are trustworthy
- Systems use NTP or equivalent for clock synchronization
- Network transport (HTTPS) provides confidentiality and integrity

**Participants:**
- Service Providers verify credentials before granting access
- Service Providers interpret trust signals honestly
- Agents present credentials they legitimately obtained
- Users understand the trust model when interacting with Agents

### 5.1.2 What TSAI Does NOT Trust

**Agents:**
- Agents are the entities being verified (not trusted by default)
- Agent behavior must be constrained by Service Providers
- Agent outputs require validation
- Agents may attempt to misuse credentials

**Network:**
- Network infrastructure may be compromised (hence HTTPS requirement)
- DNS may be hijacked (hence DNSSEC recommendations for T0/T1, DNSSEC requirement for T2/T3)
- Man-in-the-middle attacks are possible (hence signature verification)

**Individual Trust Authorities:**
- No single TA is fully trusted (multiple TAs provide redundancy)
- TAs may be compromised (Service Providers choose which TAs to trust)
- TA evaluation methodologies may vary (Service Providers assess TA quality)

**Credential Holders:**
- Credentials may be stolen (hence short expiry)
- Credentials may be replayed (hence timestamp validation)
- Agents may present expired credentials (hence expiry checking)

### 5.1.3 Explicit Non-Goals (Out of Scope)

TSAI explicitly does NOT provide:

**Runtime Behavior Monitoring:**
- TSAI credentials are point-in-time trust signals
- Continuous monitoring of Agent behavior is a Service Provider responsibility
- Agents may behave differently after credential verification

**Content Validation:**
- TSAI does not verify Agent outputs are correct, safe, or appropriate
- Content quality and safety are application-specific concerns
- Service Providers must implement their own content validation

**LLM-Specific Security:**
- Prompt injection attacks are not prevented by TSAI
- Jailbreaking and adversarial inputs require separate mitigations
- LLM hallucinations and errors are not addressed by TSAI

**End-User Authentication:**
- TSAI verifies Agents, not end users
- User authentication is handled separately (OAuth, etc.)
- Trust between a User and a Service Provider is independent of trust between an Agent and a Service Provider

**Malicious Operators with Valid Credentials:**
- If a TA issues credentials to a malicious Operator, TSAI cannot prevent misuse
- TA evaluation quality is the trust anchor
- Defense in depth and Service Provider policies are essential

### 5.1.4 Centralization Risks and Mitigations

TSAI uses centralized Trust Authorities rather than decentralized web-of-trust. This design choice (see ADR 002) provides performance and reliability but introduces centralization risks.

**Risks of Centralized TAs:**

1. **Single Point of Failure**
   - Risk: TA outage prevents credential issuance/verification
   - Mitigation: Short credential expiry (2-4 hours) means T0/T1 verification works offline; Service Providers cache DID documents; multiple TAs provide redundancy

2. **TA Compromise**
   - Risk: Attacker gains access to TA signing keys, issues fraudulent credentials
   - Mitigation: HSM key storage with published attestation for T2/T3 (Section 7.8); multiple TAs (Service Providers choose which to trust); short credential expiry limits impact window; revocation for emergency invalidation; transparency logs (future consideration)

3. **TA Misbehavior**
   - Risk: TA issues credentials to unqualified Agents, lowers standards for profit
   - Mitigation: TA operational status reports enable anomaly detection (Section 7.7); TA accreditation requirements; Service Providers choose which TAs to trust; reputation damage incentivizes honest operation; legal liability for TAs

4. **Oligopoly Formation**
   - Risk: Small number of TAs (3-10 globally) creates market power concentration
   - Mitigation: Low barriers to entry on the Service Provider side (any Service Provider can verify); Agents can switch TAs; governance body prevents anti-competitive behavior; open protocol enables new TA entry

5. **Vendor Lock-In**
   - Risk: Agents become dependent on specific TA
   - Mitigation: Portable credentials (W3C VC standard); Agents can obtain credentials from multiple TAs; Service Providers accept credentials from any recognized TA; no proprietary formats

6. **Regulatory Capture**
   - Risk: TAs become subject to government pressure, compromise Agent privacy
   - Mitigation: Multiple TAs in different jurisdictions; Agents choose TA based on jurisdiction; Service Providers can reject credentials from compromised TAs; protocol doesn't require TA to track credential usage

**Why Centralization is Acceptable:**

- **Performance:** T0/T1 verification <5ms requires offline verification (no distributed consensus)
- **Reliability:** 99.9%+ uptime requires professional operation (not volunteer networks)
- **Accountability:** Legal entities with liability (not anonymous nodes)
- **Regulatory Compliance:** SOC 2, insurance, audits require established organizations
- **Redundancy:** Multiple competing TAs (not single central authority)

**Distributed Trust Despite Centralized TAs:**

- Service Providers choose which TAs to trust (no mandatory TA)
- Agents choose which TA to use (no monopoly)
- Multiple TAs compete on methodology, price, and reputation
- Open protocol enables new TA entry
- Governance body is multi-stakeholder (not TA-controlled)

---

## 5.2 Protocol vs Implementation Boundaries

### 5.2.1 Protocol Requirements (Normative)

The following are protocol-level requirements that implementations MUST follow:

**Credential Format:**
- W3C Verifiable Credentials structure
- VC-JWT encoding
- Required claims by tier
- Signature algorithms

**Verification:**
- Signature verification against TA public keys
- Timestamp validation with ±30 second tolerance
- DID resolution for TAs and Agents
- Revocation checking for T2/T3
- Fail closed on security errors

**Transmission:**
- HTTPS mandatory for credential transmission
- Credential header format
- Error response structures

**Trust Signal Semantics:**
- Meaning of each claim (operatorIdentity, reputation, etc.)
- Tier definitions (T0, T1, T2, T3)
- Credential expiry by tier

### 5.2.2 Implementation Decisions (Non-Normative)

The following are Service Provider policy decisions, NOT protocol requirements:

**Trust Authority Selection:**
- Which TAs to trust (the Service Provider's choice)
- How to evaluate TA quality (the Service Provider's assessment)
- When to add/remove TAs from trusted list (the Service Provider's policy)

**Trust Signal Interpretation:**
- How to use reputation scores (risk assessment)
- What reputation threshold to require (the Service Provider's policy)
- How to weight different signals (the Service Provider's algorithm)

**Constraint Enforcement:**
- Whether to enforce T3 authorization limits (the Service Provider's choice)
- How to handle constraint violations (the Service Provider's policy)
- What operations require which tiers (the Service Provider's risk model)

**Operational Policies:**
- Caching policies (DID documents, verification results, status lists)
- Monitoring and logging strategies (what to log, retention)
- Degraded mode policies (when to allow, duration limits)
- Incident response procedures (compromised credentials, TA issues)

**Core Principle:** TSAI signals, Service Providers decide.

---

## 5.3 Threat Model

### 5.3.1 Attacker Goals

**Primary Goals:**
- Impersonate a legitimate Agent to gain unauthorized access
- Bypass trust verification to access restricted resources
- Steal credentials to impersonate Agents
- Forge credentials to appear trustworthy
- Disrupt trust infrastructure to cause denial of service

**Secondary Goals:**
- Correlate Agent activities across Service Providers
- Extract information from credentials
- Compromise Trust Authorities to issue fraudulent credentials
- Manipulate trust signals to appear more trustworthy

### 5.3.2 Attack Surfaces

**Credential Theft:**
- Steal credentials from Agent storage
- Intercept credentials during transmission
- Extract credentials from logs or caches
- Social engineering to obtain credentials

**Replay Attacks:**
- Capture and replay valid credentials
- Reuse credentials against a different Service Provider
- Replay within timestamp tolerance window

**Forgery:**
- Create fake credentials with forged signatures
- Modify existing credentials
- Impersonate Trust Authorities

**Infrastructure Attacks:**
- Compromise TA signing keys
- Hijack DID resolution (DNS poisoning)
- Man-in-the-middle attacks on HTTPS
- Compromise revocation infrastructure

**Trust Authority Compromise:**
- Gain access to TA systems
- Steal TA signing keys
- Manipulate TA evaluation processes
- Issue fraudulent credentials

### 5.3.3 Attacker Capabilities

**Network Attacker:**
- Can intercept network traffic
- Can modify unencrypted traffic
- Cannot break HTTPS encryption
- Cannot forge valid signatures without keys

**Compromised Agent:**
- Has valid credentials
- Can present credentials to Service Providers
- Cannot modify credential contents
- Cannot extend credential expiry

**Malicious Trust Authority:**
- Can issue valid credentials
- Can revoke credentials
- Cannot forge credentials from other TAs
- Cannot modify already-issued credentials

**Malicious Service Provider:**
- Can see credentials presented to it
- Can log and cache credentials
- Cannot use credentials against a different Service Provider (bearer token model)
- Cannot extend credential validity

---

## 5.4 Cryptographic Requirements

### 5.4.1 Signature Algorithms

**Required Support:**
- Implementations MUST support ES256 (ECDSA with P-256 and SHA-256)
- Implementations MUST support EdDSA (Ed25519)

**Optional Support:**
- Implementations MAY support ES384 (ECDSA with P-384 and SHA-384)
- Implementations MAY support ES512 (ECDSA with P-521 and SHA-512)

**Prohibited:**
- Implementations MUST NOT use RSA with key length < 2048 bits
- Implementations MUST NOT use algorithms with known vulnerabilities

**Rationale:**
- ES256 and EdDSA provide strong security with good performance
- Multiple algorithm support enables algorithm agility
- Consistent with W3C VC-JOSE-COSE recommendations

### 5.4.2 Key Management

**Trust Authority Keys:**
- Private keys MUST be stored in Hardware Security Modules (HSMs) or equivalent
- Key generation MUST use cryptographically secure random number generators
- Keys SHOULD be rotated periodically (recommended: annually)
- Old keys MUST be retained for signature verification during rotation period
- TAs issuing T2/T3 credentials MUST publish an HSM attestation statement (see Section 7.8)

**Agent Keys:**
- Private keys SHOULD be stored securely (encrypted or memory-only)
- Keys MAY be ephemeral (generated per-session for did:key)
- Keys SHOULD be unique per Agent (avoid key reuse)

**Key Lengths:**
- ECDSA: Minimum 256-bit curve (P-256 or equivalent)
- EdDSA: Ed25519 (256-bit security level)
- RSA (if used): Minimum 2048 bits (3072 bits recommended)

### 5.4.3 Entropy Requirements

**Random Number Generation:**
- Nonces and timestamps MUST use cryptographically secure RNG
- Key generation MUST use a secure RNG provided by the operating system or hardware
- Minimum entropy: 128 bits for security-critical values

**Timestamp Precision:**
- Timestamps MUST include seconds precision
- Millisecond precision RECOMMENDED for better replay prevention
- Microsecond precision MAY be used but is not required

### 5.4.4 Algorithm Agility

**Adding New Algorithms:**
- New algorithms MAY be added via protocol updates
- Implementations MUST reject unknown algorithms
- Algorithm negotiation is NOT supported (credentials specify algorithm)

**Deprecating Algorithms:**
- Deprecated algorithms MUST be announced with migration timeline
- Implementations SHOULD warn when using deprecated algorithms
- Credentials using deprecated algorithms SHOULD be rejected after sunset date

---

## 5.5 Credential Lifecycle Security

### 5.5.1 Issuance Security (TA Responsibility)

**Key Protection:**
- Signing keys MUST be stored in HSMs or equivalent secure hardware
- TAs issuing T2/T3 credentials MUST publish an HSM attestation statement (see Section 7.8)
- Key access MUST be logged and audited
- Key ceremonies MUST follow industry best practices

**Credential Generation:**
- Credentials MUST be generated in secure environment
- Credential contents MUST match TA evaluation results
- Issuance MUST be logged for audit trail

**Verification Before Issuance:**
- TAs MUST verify Agent identity before issuing credentials
- TAs MUST perform claimed verification processes (KYC, reputation checks)
- TAs MUST validate all claims in credential

**Audit Logging:**
- All credential issuances MUST be logged
- Logs MUST include: Agent DID, tier, timestamp, issuer
- Logs MUST be tamper-evident and retained per regulatory requirements

### 5.5.2 Storage Security (Agent Responsibility)

**Secure Storage:**
- Agents SHOULD store credentials in memory only (not persisted)
- If persisted, credentials MUST be encrypted at rest
- Encryption keys MUST be protected (OS keychain, secure enclave)

**Access Control:**
- Credential access MUST be restricted to authorized processes
- Credentials MUST NOT be world-readable
- File permissions MUST prevent unauthorized access

**Secure Deletion:**
- Expired credentials MUST be securely deleted
- Memory containing credentials SHOULD be zeroed after use
- Credential caches MUST be cleared on expiry

**Backup Considerations:**
- Credentials SHOULD NOT be included in backups (short-lived)
- If backed up, backups MUST be encrypted
- Backup access MUST be audited

### 5.5.3 Transmission Security (Protocol Requirement)

**HTTPS Mandatory:**
- Credentials MUST be transmitted over HTTPS
- TLS 1.2 or higher MUST be used
- Certificate validation MUST be performed

**Header Security:**
- `TSAI-Credential` header MUST NOT be logged by servers
- Proxies MUST NOT cache requests containing TSAI credentials
- Credentials MUST NOT be included in URLs (query parameters)

**Error Handling:**
- Verification errors MUST NOT leak credential contents
- Error messages SHOULD be generic (avoid detailed failure reasons)
- Detailed errors MAY be logged server-side for debugging

### 5.5.4 Verification Security (Service Provider Responsibility)

Verification requirements are specified normatively in Section 3 (04-verification.md). Service Providers MUST follow the verification algorithm defined there, including signature verification, timestamp validation, revocation checking, and fail-closed behavior.

**Caching (Implementation Decision):**
- Service Providers MAY cache verification results
- Cache duration MUST NOT exceed credential expiry
- Caches MUST be invalidated on revocation
- Cache keys MUST include credential hash and timestamp

---

## 5.6 Replay Attack Prevention

### 5.6.1 Timestamp-Based Prevention (T0/T1)

**Mechanism:**
- Verifiable Presentations include timestamp
- Service Providers verify timestamp is within ±30 seconds of current time
- Creates ~1 minute replay window

**Rationale:**
- Simple implementation (no state management)
- No TA runtime dependency
- Acceptable for low-stakes T0/T1 use cases
- Balances security and operational simplicity

**Limitations:**
- ~1 minute replay window exists
- Attacker can replay within tolerance window
- Requires clock synchronization (NTP)

**Mitigation:**
- Short credential expiry (2-4 hours) limits stolen credential lifetime
- Service Providers MAY track recently seen VP signatures to prevent replay
- Higher tiers (T2/T3) use stronger mechanisms

### 5.6.2 Challenge-Response (T2/T3 - Future)

**Mechanism (Future Specification):**
- The Service Provider sends a random nonce (challenge)
- The Agent signs the nonce with its credential (response)
- The Service Provider verifies signature freshness
- Eliminates replay window

**Benefits:**
- No replay window
- Proves the Agent controls the private key
- Suitable for high-stakes operations

**Trade-offs:**
- Additional round-trip (latency)
- More complex implementation
- Requires state management

**Status:** Specified in future version for T2/T3 verification.

### 5.6.3 Clock Synchronization Requirements

**NTP Assumption:**
- All systems MUST use NTP or equivalent for time synchronization
- Clock drift MUST be monitored
- Systems SHOULD alert on NTP synchronization failures

**Risks of Clock Drift:**
- Expired credentials may be accepted
- Valid credentials may be rejected
- Replay window may expand

**Tolerance Rationale:**
- ±30 seconds accommodates minor clock drift
- Assumes NTP keeps clocks within ±10 seconds
- Provides buffer for network latency and processing time

---

## 5.7 Privacy Considerations

### 5.7.1 Agent Privacy

**DID Correlation:**
- Agents using same DID across Service Providers can be correlated
- Agents MAY use different DIDs for different Service Providers (pseudonymity)
- did:key enables anonymous Agents (no domain linkage)
- did:web links Agent to domain (less anonymous)

**Minimal Disclosure:**
- Credentials contain only required claims for tier
- No unnecessary personal information
- Reputation scores are aggregated (not individual interactions)

**Pseudonymity Options:**
- T0 supports did:key (fully pseudonymous)
- T1+ typically use did:web (domain-linked)
- Agents can create multiple DIDs for different contexts

**Recommendation:**
- Agents concerned about correlation SHOULD use different DIDs for different Service Providers
- Agents requiring domain verification MUST use did:web
- Service Providers SHOULD NOT require a specific DID method unless necessary

### 5.7.2 Service Provider Privacy

**What Service Providers Learn:**
- Agent identity (DID)
- Operator name and jurisdiction
- Trust signals (reputation, stake, certifications)
- Trust Authority that issued credential

**What Service Providers Don't Learn:**
- Agent interactions with other Service Providers
- Full history of Agent behavior (only aggregated reputation)
- Other credentials the Agent holds
- User identity (TSAI is Agent-to-Service-Provider, not User-to-Service-Provider)

**Tracking Across Service Providers:**
- Service Providers cannot track Agents across other Service Providers (unless the Agent uses the same DID)
- TAs do not inform Service Providers about other Service Providers the Agent accesses
- Credentials are bearer tokens (no callback to TA on use)

### 5.7.3 User Privacy

**Separation of Concerns:**
- TSAI credentials verify Agents, not end users
- User authentication handled separately (OAuth, etc.)
- User data not included in TSAI credentials

**User-Agent Relationship:**
- Users authorize Agents to act on their behalf (out of TSAI scope)
- Agent credentials don't reveal which User is being represented
- User privacy protected by separation of Agent and User identity

**Service Provider Responsibility:**
- Service Providers MUST NOT conflate Agent trust with User trust
- Service Providers handle User authentication independently
- User consent for Agent actions is the Service Provider's responsibility

### 5.7.4 Trust Authority Privacy

**What TAs Learn:**
- Which Agents request credentials (operational necessity)
- Agent identity and verification data (KYC, reputation)
- Credential issuance frequency

**What TAs Don't Learn:**
- Which Service Providers Agents access (credentials are bearer tokens)
- How Service Providers use credentials
- Agent interactions with Service Providers

**TA Transparency Requirements:**
- TAs MUST disclose data collection practices
- TAs MUST disclose data retention policies
- TAs MUST disclose data sharing practices
- TAs SHOULD minimize data collection to operational necessity

**Privacy by Design:**
- Credentials don't callback to TA on use
- TAs don't track credential usage
- Service Providers verify credentials locally (no TA runtime dependency for T0/T1)

---

## 5.8 Trust Authority Security

### 5.8.1 TA Key Compromise

**Impact:**
- Attacker can issue fraudulent credentials
- All credentials from compromised TA are suspect
- Service Providers may need to revoke trust in TA

**Detection:**
- Anomalous patterns in TA operational status reports (Section 7.7)
- Reports of fraudulent credentials from Service Providers
- Security audits and monitoring
- Credential transparency logs (future consideration)

**Response:**
- TA MUST immediately revoke compromised key
- TA MUST notify Service Providers and governance body
- TA MUST issue new credentials with new key
- Service Providers SHOULD remove compromised TA from trusted list temporarily

**Mitigation:**
- Multiple TAs provide redundancy (no single point of failure)
- Service Providers can pin TA DID documents
- Short credential expiry limits impact window
- Key rotation reduces long-term exposure

### 5.8.2 TA Operational Security

**Key Management:**
- Private keys MUST be stored in HSMs
- TAs issuing T2/T3 credentials MUST publish HSM attestation (Section 7.8)
- Key access MUST be restricted and audited
- Key ceremonies MUST follow industry best practices
- Backup keys MUST be stored securely offline

**Access Controls:**
- Multi-person authorization for key operations
- Role-based access control for TA systems
- Audit logging for all administrative actions
- Regular access reviews

**Infrastructure Security:**
- Secure development practices
- Regular security audits and penetration testing
- Incident response procedures
- Business continuity and disaster recovery plans

**Monitoring:**
- Real-time monitoring of credential issuance
- Anomaly detection for unusual patterns
- Security event logging and analysis
- Regular security assessments

### 5.8.3 TA Governance and Accountability

**Governance Body Role:**
The governance body stewards the specification. It does not operate monitoring infrastructure or enforce TA compliance. TA accountability relies on protocol-level mechanisms and enforcement by Service Providers.

**Operational Transparency:**
- TAs MUST publish signed operational status reports (Section 7.7)
- Reports provide aggregate metrics (issuance counts, revocation rates, key rotation timestamps)
- Service Providers use status reports to assess TA health and detect anomalies
- This enables accountability driven by Service Providers without requiring an operational governance body

**Transparency:**
- TAs MUST publish evaluation criteria
- TAs MUST disclose verification processes
- TAs MUST publish operational status reports (Section 7.7)

**Accountability:**
- TAs are legally accountable for issued credentials
- TAs MUST have liability insurance or equivalent
- TAs MUST respond to security incidents promptly
- Service Providers enforce TA accountability by adding or removing TAs from their trusted lists based on observed behavior and status report data

---

## 5.9 Service Provider Security Responsibilities

### 5.9.1 Verification Requirements

Verification requirements (mandatory checks, recommended checks, prohibited actions) are specified normatively in Section 3 (04-verification.md). See Section 3.8 for the complete normative requirements summary.

### 5.9.2 Trust Signal Interpretation

**Service Provider Discretion:**
- Service Providers decide which TAs to trust
- Service Providers decide how to interpret trust signals
- Service Providers decide risk thresholds
- Service Providers decide which tiers to require

**Honest Interpretation:**
- Service Providers MUST NOT misrepresent signal meanings
- Service Providers MUST NOT claim signals mean more than specified
- Service Providers SHOULD document their interpretation policies
- Service Providers SHOULD be transparent about trust requirements

**Risk Assessment:**
- Service Providers assess risk based on use case
- Service Providers may require higher tiers for sensitive operations
- Service Providers may combine TSAI with other signals
- Service Providers implement defense in depth

### 5.9.3 Degraded Mode

Degraded mode requirements (when allowed, when prohibited, notification format) are specified normatively in Section 3.5.2 (04-verification.md).

---

## 5.10 Protocol-Specific Security

Protocol integration patterns and security requirements for MCP, A2A, and general HTTP are specified in Section 4 (05-protocol-integration.md), including credential transmission, error handling, and transport-specific considerations. Section 4.5 covers protocol-specific security considerations (credential exposure, replay attacks, credential theft, TA compromise).

---

## 5.11 Limitations and Non-Goals

### 5.11.1 What TSAI Does NOT Protect Against

**LLM-Specific Attacks:**
- Prompt injection: Attacker manipulates LLM via crafted inputs
- Jailbreaking: Attacker bypasses LLM safety constraints
- Adversarial inputs: Inputs designed to cause incorrect outputs
- Model extraction: Attacker extracts model weights or training data

**Rationale:** These are LLM implementation issues, not trust signaling issues. Require separate mitigations (input validation, output filtering, model security).

**Agent Output Quality:**
- Hallucinations: LLM generates false information
- Incorrect information: Agent provides wrong answers
- Biased outputs: Agent exhibits unwanted biases
- Harmful content: Agent generates inappropriate content

**Rationale:** Content quality is application-specific. Service Providers must implement content validation, fact-checking, and safety filters.

**Agent Runtime Behavior:**
- Malicious actions after verification
- Behavior changes over time
- Exploitation of Service Provider vulnerabilities
- Resource abuse (excessive requests, storage)

**Rationale:** TSAI provides point-in-time trust signals. Continuous monitoring is a Service Provider responsibility. Defense in depth required.

**Malicious Operators with Valid Credentials:**
- Operator passes TA evaluation but acts maliciously
- Operator's behavior degrades after credential issuance
- Operator exploits legitimate access for malicious purposes

**Rationale:** TA evaluation quality is the trust anchor. If a TA issues credentials to a malicious Operator, TSAI cannot prevent misuse. Service Providers must implement additional controls.

**Social Engineering:**
- Attacker tricks users into authorizing malicious Agents
- Phishing attacks targeting users
- Impersonation of legitimate services

**Rationale:** User education and Service Provider UX are primary defenses. TSAI helps users identify legitimate Agents but doesn't prevent social engineering.

**Service Provider Vulnerabilities:**
- SQL injection, XSS, CSRF
- Authentication bypass
- Authorization flaws
- Infrastructure vulnerabilities

**Rationale:** Service Provider security is the Service Provider's responsibility. TSAI provides trust signals but doesn't secure a Service Provider's implementation.

### 5.11.2 Why These Are Out of Scope

**TSAI is Identity and Trust Signaling:**
- Verifies who the Agent is and their trust level
- Does not monitor what the Agent does after verification
- Does not validate Agent outputs
- Does not prevent all possible attacks

**Runtime Security is a Service Provider Responsibility:**
- Service Providers must monitor Agent behavior
- Service Providers must validate Agent outputs
- Service Providers must implement rate limiting, abuse detection
- Service Providers must maintain their own security controls

**Content Validation is Application-Specific:**
- Different applications have different content requirements
- No universal content validation mechanism
- Service Providers must implement domain-specific validation

**LLM Vulnerabilities Require Different Mitigations:**
- Input sanitization and validation
- Output filtering and safety checks
- Model security and access controls
- Separate research area from trust signaling

### 5.11.3 Defense in Depth Required

**TSAI is One Layer:**
- Reduces risk but doesn't eliminate it
- Must be combined with other security measures
- Not a silver bullet for agent security

**Additional Layers Needed:**
- User authentication and authorization
- Content validation and safety filters
- Rate limiting and abuse detection
- Monitoring and anomaly detection
- Incident response procedures
- Legal agreements and liability

**Honest Positioning:**
- TSAI makes it harder for malicious Agents to operate
- TSAI provides accountability through TA evaluation
- TSAI enables risk-calibrated decisions
- TSAI does not guarantee Agent safety

---

## 5.12 Security Considerations for Future Extensions

### 5.12.1 Challenge-Response Protocols

**For T2/T3 verification:**
- Eliminate replay window
- Prove the Agent controls the private key
- Enable real-time verification

**Security considerations:**
- Nonce generation must be cryptographically secure
- Challenge must be unpredictable
- Response must be timely (timeout)
- State management must be secure

### 5.12.2 Credential Delegation

**For Agent-to-Agent delegation:**
- Agent A delegates authority to Agent B
- B acts on behalf of A with constraints
- Delegation chain is verifiable

**Security considerations:**
- Delegation must be explicit and constrained
- Revocation must cascade through chain
- Audit trail must be maintained
- Circular delegation must be prevented

### 5.12.3 Credential Transparency Logs

**For TA accountability:**
- All issued credentials logged publicly
- Enables detection of fraudulent issuance
- Provides audit trail

**Security considerations:**
- Privacy implications of public logs
- Log integrity and tamper-evidence
- Efficient verification of log inclusion
- Scalability of log infrastructure

### 5.12.4 Real-Time TA Verification APIs

**For T2/T3 verification:**
- The Service Provider queries the TA in real-time
- The TA confirms credential validity
- Enables immediate revocation

**Security considerations:**
- TA availability becomes critical
- Privacy implications of the TA learning which Service Provider is accessed
- Performance impact of additional round-trip
- Authentication of Service Provider to TA

---

## 5.13 Normative Requirements Summary

### 5.13.1 Trust Authorities MUST

**Cryptographic:**
- Use HSMs or equivalent for key storage
- Publish HSM attestation statements for T2/T3 credential issuance (Section 7.8)
- Support ES256 and EdDSA signature algorithms
- Generate keys with cryptographically secure RNG
- Rotate keys periodically

**Operational:**
- Verify agent identity before issuing credentials
- Perform claimed verification processes
- Log all credential issuances
- Maintain accurate revocation status
- Respond to security incidents promptly

**Transparency:**
- Publish evaluation criteria
- Disclose verification processes
- Disclose data collection and retention policies
- Publish signed operational status reports (Section 7.7)

### 5.13.2 Agents MUST

**Credential Handling:**
- Store credentials securely (encrypted or memory-only)
- Delete expired credentials
- Present credentials only over HTTPS
- Include credentials in protocol-specific manner

**Key Management:**
- Protect private keys
- Use secure RNG for key generation
- Avoid key reuse across contexts

### 5.13.3 Service Providers MUST

See Section 3.8 (04-verification.md) for verification requirements. Additional security requirements:

**Privacy:**
- NOT log credential contents
- NOT cache credentials inappropriately
- NOT misrepresent trust signal meanings

**Degraded Mode:**
- Clearly indicate degraded operation
- Log degraded mode events
- NOT allow degraded mode for T3 operations

**DID Resolution (T2/T3):**
- Use DNSSEC-validated resolution for TA DIDs

### 5.13.4 All Parties MUST

**Transport Security:**
- Use HTTPS for credential transmission
- Use TLS 1.2 or higher
- Validate certificates

**Clock Synchronization:**
- Use NTP or equivalent
- Monitor clock drift
- Alert on synchronization failures

---

## References

- W3C Verifiable Credentials Data Model 2.0
- W3C VC-JOSE-COSE
- W3C DID Core
- RFC 7519 (JSON Web Token)
- RFC 7515 (JSON Web Signature)
- NIST SP 800-57 (Key Management)
- OWASP Top 10
- TSAI ADR 007: Short-Lived Credentials
- TSAI ADR 009: Timestamp-Based Replay Prevention
- TSAI ADR 010: Fail-Closed with Degraded Mode
