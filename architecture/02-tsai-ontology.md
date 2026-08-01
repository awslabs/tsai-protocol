<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Domain Model

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## Overview

TSAI models the relationship between an operator, the legal entity, and an agent, the program it runs. This document defines that relationship and how signals attach to each. The wire form is the flat signal list of the credential (Section 2); this is the model behind it.

---

## Operator

The legal entity, a company, organisation, or individual, that runs agents and is legally accountable for them. Within a credential the operator is identified by its identity signals, its legal name, jurisdiction, and a verified domain, rather than by a minted identifier (ADR 017). It carries the signals shared across all of its agents: identity, compliance, and assurance.

## Agent

The program that makes requests on behalf of an operator. It is identified by the key its credential is bound to, the `cnf` key, and it may carry a stable HTTPS name for continuity (ADR 017). It carries its own reputation.

## The operatedBy relationship

Each agent has exactly one operator. One operator can run several agents, each building its own reputation while sharing the operator's identity, compliance, and assurance. One operator per agent keeps accountability clear; a joint venture names one party as the operator.

---

## Signal Attribution

Each signal in the flat list is about either the operator or the agent.

- **Operator-level**, shared across the operator's agents: identity (legal name, jurisdiction, verification depth, controlled domain and its age), compliance (certifications), and assurance (economic backing).
- **Agent-level**, specific to the one agent: reputation (its behavioural record).

Authorization, the constraints on what an agent may do, is delegation rather than a signal, and is out of scope here (ADR 001).

---

## Example

A flat signal list carrying operator-level and agent-level signals:

```json
"signals": [
  { "cat": "idn", "typ": "jur", "val": "DE" },
  { "cat": "idn", "typ": "dct", "val": "acme-corp.example" },
  { "cat": "cmp", "typ": "iso27001", "prv": "did:web:cert-corp.example" },
  { "cat": "rep", "typ": "ecommerce", "scr": 0.94, "cnt": 3518, "wdw": "P90D" }
]
```

The identity and compliance signals describe the operator; the reputation signal describes the agent. The credential binds them to the agent's `cnf` key and to the operator's identity.

---

## Design Rationale

**One operator per agent.** A single accountable party per agent keeps the trust model simple and the responsibility unambiguous.

**The operator is identified by verified attributes, not a minted identifier.** An identifier a Trust Authority mints for the operator would not be consistent across Trust Authorities. The operator's legal identity and verified domain are what a Service Provider needs, and they are decided outside any single TA (ADR 017).

**The agent is identified by the key it holds.** The `cnf` key is self-authenticating and is what the holder proves possession of at presentation, so the agent needs no separate identifier for verification (ADR 014).

---

## References

- draft-ietf-oauth-sd-jwt-vc — SD-JWT-based Verifiable Credentials
- TSAI ADR 014 (Holder Binding), ADR 016 (Trust Signal Structure), ADR 017 (Party Identity)
- TSAI Credential Format (architecture/03-credential-format.md)
