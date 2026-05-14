<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# Trust Signals for Agent Evaluation

**Version:** 1.0  
**Date:** January 2026  
**Status:** Working Group Draft

---

## Overview

This document catalogs potential trust signals available in an agent trust ecosystem. It serves as a comprehensive reference of possible signals, though not all will be included in the TSAI protocol specification. The architecture specification defines which signals are normative for each tier.

Trust signals fall into six categories: identity (who the Agent and Operator are), behavioral (how the Agent has performed), economic (what's at stake), authorization (what the Agent is allowed to do), technical (cryptographic proofs), and third-party (external endorsements). Each category provides different dimensions of trustworthiness that Service Providers can use to make risk-calibrated decisions.

---

## 1. Identity Signals

- **Persistent identifier** - DID or similar stable identifier
- **Operator identity** - Legal entity operating the agent
- **Operator jurisdiction** - Geographic location and legal framework
- **KYC level** - Verification depth (basic, enhanced, institutional)
- **Domain verification** - Verified control of domain name
- **Domain age** - How long domain has been registered
- **Domain reputation** - Clean history (not on spam/malware lists)
- **Organizational affiliation** - Parent organization or network membership
- **Industry certifications** - ISO 27001, SOC 2, FedRAMP, PCI-DSS, HIPAA, GDPR compliance
- **Regulatory approvals** - Government certifications or licenses

---

## 2. Behavioral Signals (Reputation)

- **Interaction count** - Total number of interactions
- **Success rate** - Percentage of successful completions
- **Task-specific success rates** - Success rates by category or domain
- **User satisfaction** - Ratings from end users
- **Complaint rate** - Frequency of reported issues
- **Time in operation** - How long agent has been active
- **Behavioral consistency** - Stability of performance over time (variance metrics)
- **Reputation score** - Aggregated trust score (e.g., 0-100)
- **Confidence level** - Statistical confidence in score (based on sample size)
- **Trend** - Improving, stable, or declining
- **Recovery patterns** - How agent responds to failures

---

## 3. Economic Signals

- **Posted collateral** - Funds held in escrow
- **Stake amount** - Value at risk for misbehavior
- **Insurance coverage** - Third-party liability insurance
- **Financial backing** - Capitalization of operator
- **Bond/guarantee** - Performance guarantees
- **Total transaction value** - Cumulative value processed
- **Payment reliability** - History of successful payments

---

## 4. Authorization Signals (Constraints)

- **Authorized operations** - Explicit list of allowed actions
- **Value limits** - Maximum transaction amounts
- **Rate limits** - Requests per time period
- **Data access permissions** - What data agent can access
- **Time bounds** - Temporal validity of permissions
- **Domain restrictions** - Which Service Providers or services
- **Geographic restrictions** - Where agent can operate
- **User consent scope** - What user authorized
- **Human-in-loop indicators** - Whether human oversight is required
- **Authorization chain** - Who authorized this agent and for what

---

## 5. Technical Signals (Proofs)

- **Digital signatures** - Proof of action authenticity
- **Tamper-evident logs** - Immutable action history (audit logs)
- **TEE attestations** - Trusted execution environment proofs
- **Zero-knowledge proofs** - Compliance proofs without revealing details
- **Code integrity proofs** - Hash of agent code
- **Sandbox attestation** - Proof of isolated execution
- **Resource limits** - Proven constraints on compute/memory
- **Device fingerprint** - Hardware/software environment characteristics
- **Network context** - Origin network and routing information

---

## 6. Third-Party Signals (Endorsements)

- **TA endorsement** - Certification from recognized Trust Authority
- **Multiple TA consensus** - Agreement across independent TAs
- **TA methodology** - How TA evaluates agents
- **Payment scheme certification** - Visa, Mastercard, etc. (for commerce agents)
- **Industry certifications** - Sector-specific standards (overlaps with identity signals)
- **Audit reports** - Third-party security audits
- **Compliance attestations** - GDPR, CCPA, sector-specific regulations
