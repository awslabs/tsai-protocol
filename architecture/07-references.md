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

**[VC-DATA-MODEL-2.0]**  
W3C Verifiable Credentials Data Model 2.0  
W3C Recommendation, May 2025  
https://www.w3.org/TR/vc-data-model-2.0/

**[VC-JOSE-COSE]**  
W3C Securing Verifiable Credentials using JOSE and COSE  
W3C Recommendation, May 2025  
https://www.w3.org/TR/vc-jose-cose/

**[DID-CORE]**  
W3C Decentralized Identifiers (DIDs) v1.0  
W3C Recommendation, July 2022  
https://www.w3.org/TR/did-core/

**[DID-RESOLUTION]**  
W3C DID Resolution  
W3C Working Draft, January 2026  
https://w3c-ccg.github.io/did-resolution/

**[BitstringStatusList]**  
W3C Bitstring Status List v1.0  
W3C Candidate Recommendation, December 2023  
https://www.w3.org/TR/vc-bitstring-status-list/

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
https://github.com/agentpayments/ap2

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
- Sections 1-6 complete
- Ready for working group review

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
