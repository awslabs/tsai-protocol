<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - References

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 6.1 Normative References

The following documents are required for conformance to this specification. Implementations MUST follow these standards.

**[SD-JWT-VC]**  
SD-JWT-based Verifiable Credentials  
IETF, draft-ietf-oauth-sd-jwt-vc  
https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc

**[SD-JWT]**  
Selective Disclosure for JWTs  
IETF, draft-ietf-oauth-selective-disclosure-jwt  
https://datatracker.ietf.org/doc/html/draft-ietf-oauth-selective-disclosure-jwt

**[STATUS-LIST]**  
Token Status List  
IETF, draft-ietf-oauth-status-list  
https://datatracker.ietf.org/doc/html/draft-ietf-oauth-status-list

**[RFC7638]**  
JSON Web Key (JWK) Thumbprint  
IETF RFC 7638, September 2015  
https://datatracker.ietf.org/doc/html/rfc7638

**[DID-WEB]**  
did:web Method Specification (referenced third parties)  
W3C CCG  
https://w3c-ccg.github.io/did-method-web/

**[RFC2119]**  
Key words for use in RFCs to Indicate Requirement Levels  
IETF RFC 2119, March 1997  
https://datatracker.ietf.org/doc/html/rfc2119

**[RFC8174]**  
Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words  
IETF RFC 8174, May 2017  
https://datatracker.ietf.org/doc/html/rfc8174

**[RFC7519]**  
JSON Web Token (JWT)  
IETF RFC 7519, May 2015  
https://datatracker.ietf.org/doc/html/rfc7519

**[RFC7515]**  
JSON Web Signature (JWS)  
IETF RFC 7515, May 2015  
https://datatracker.ietf.org/doc/html/rfc7515

**[RFC8259]**  
The JavaScript Object Notation (JSON) Data Interchange Format  
IETF RFC 8259, December 2017  
https://datatracker.ietf.org/doc/html/rfc8259

---

## 6.2 Informative References

The following documents provide helpful context but are not required for conformance.

### 6.2.1 TSAI Documents

**[TSAI-CONCEPT]**  
TSAI High-Level Concept  
TSAI Working Group, January 2026  
`concept/02-high-level-concept.md`

**[TSAI-ADR-001]**  
ADR 001: Agent Delegation Mechanism  
TSAI Working Group, January 2026  
`decisions/001-agent-delegation-mechanism.md`

**[TSAI-ADR-002]**  
ADR 002: Centralized Trust Authorities  
TSAI Working Group, January 2026  
`decisions/002-centralized-trust-authorities.md`

**[TSAI-ADR-003]**  
ADR 003: W3C Verifiable Credentials  
TSAI Working Group, January 2026  
`decisions/003-w3c-verifiable-credentials.md`

**[TSAI-ADR-004]**  
ADR 004: Tiered Trust Model  
TSAI Working Group, January 2026  
`decisions/004-tiered-trust-model.md`

**[TSAI-ADR-005]**  
ADR 005: Signaling vs Enforcement  
TSAI Working Group, January 2026  
`decisions/005-signaling-vs-enforcement.md`

**[TSAI-ADR-006]**  
ADR 006: DID Methods  
TSAI Working Group, January 2026  
`decisions/006-did-methods.md`

**[TSAI-ADR-007]**  
ADR 007: Short-Lived Credentials  
TSAI Working Group, January 2026  
`decisions/007-short-lived-credentials.md`

**[TSAI-ADR-008]**  
ADR 008: User Privacy and Sybil Prevention  
TSAI Working Group, January 2026  
`decisions/008-user-privacy-and-sybil-prevention.md`

**[TSAI-ADR-009]**  
ADR 009: Timestamp-Based Replay Prevention  
TSAI Working Group, January 2026  
`decisions/009-timestamp-based-replay-prevention.md`

**[TSAI-ADR-010]**  
ADR 010: Fail-Closed with Degraded Mode  
TSAI Working Group, January 2026  
`decisions/010-fail-closed-with-degraded-mode.md`

**[TSAI-ADR-011]**  
ADR 011: TA Operational Transparency  
TSAI Working Group, January 2026  
`decisions/011-ta-operational-transparency.md`

**[TSAI-ADR-012]**  
ADR 012: Service Provider Terminology  
TSAI Working Group, April 2026  
`decisions/012-service-provider-terminology.md`

**[TSAI-ADR-013]**  
ADR 013: VP-JWT Claim Structure (superseded by ADR 015)  
TSAI Working Group, June 2026  
`decisions/013-vp-jwt-claim-structure.md`

**[TSAI-ADR-014..018]**  
Follow-on ADRs: Holder Binding (ADR 014), Credential Serialisation Format (ADR 015, supersedes 003), Trust Signal Structure (ADR 016, supersedes 004), Party Identity (ADR 017, supersedes 006), Verification Strength and Replay (ADR 018, amends 007 and 009)  
TSAI Working Group  
`decisions/`

### 6.2.2 Protocol Specifications

**[MCP]**  
Model Context Protocol Specification  
Version 2025-11-25  
https://github.com/modelcontextprotocol/modelcontextprotocol

**[A2A]**  
Agent2Agent Protocol Specification  
Version 0.3.0  
https://github.com/a2aproject/A2A

**[AP2]**  
Agent Payments Protocol  
https://github.com/google-agentic-commerce/AP2

**[ERC-8004]**  
ERC-8004: Trustless Agents  
Ethereum Improvement Proposal  
https://eips.ethereum.org/EIPS/eip-8004

### 6.2.3 Security Standards

**[NIST-SP-800-57]**  
NIST Special Publication 800-57: Recommendation for Key Management  
National Institute of Standards and Technology  
https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final

**[OWASP-TOP-10]**  
OWASP Top 10 Web Application Security Risks  
OWASP Foundation  
https://owasp.org/www-project-top-ten/

**[RFC8615]**  
Well-Known Uniform Resource Identifiers (URIs)  
IETF RFC 8615, May 2019  
https://datatracker.ietf.org/doc/html/rfc8615

### 6.2.4 Standards and Formats

**[ISO-3166-1]**  
ISO 3166-1: Codes for the representation of names of countries and their subdivisions  
International Organization for Standardization  
https://www.iso.org/iso-3166-country-codes.html

**[ISO-4217]**  
ISO 4217: Codes for the representation of currencies  
International Organization for Standardization  
https://www.iso.org/iso-4217-currency-codes.html

**[ISO-8601]**  
ISO 8601: Date and time format  
International Organization for Standardization  
https://www.iso.org/iso-8601-date-and-time-format.html

**[RFC3986]**  
Uniform Resource Identifier (URI): Generic Syntax  
IETF RFC 3986, January 2005  
https://datatracker.ietf.org/doc/html/rfc3986

---

## 6.3 Document History

**Version 1.0 (Draft) - January 2026**
- Initial architecture specification

**Version 1.0 (Draft), revised - 2026-07**
- Moved the credential to SD-JWT VC with a key-binding JWT, replaced the T0–T3 tiers with a flat four-category signal list, and moved party identity to an HTTPS issuer, the `cnf` key, and `did:web` for third parties (ADRs 014–018)

---

## 6.4 Acknowledgments

This specification was developed by the TSAI Working Group, comprising European software vendors under AWS EMEA ISV team leadership.

**Contributing Organizations:**
- Amazon Web Services
- [Additional contributors to be listed]

**Special Thanks:**
- W3C Verifiable Credentials Working Group for foundational standards
- Model Context Protocol community for integration insights
- Agent2Agent Protocol community for collaboration patterns

---

## 6.5 Copyright and License

Copyright © 2026 TSAI Working Group. All rights reserved.

This document is made available under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

**You are free to:**
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose

**Under the following terms:**
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made

---

**End of TSAI Architecture Specification v1.0 (Draft)**
