<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# Trust Signals for Agentic Interactions (TSAI)

AI agents can authenticate requests to websites and APIs. However, authentication neither identifies the organisation accountable for an agent nor provides independent evidence about the agent's conduct and claims. Service Providers need that context when deciding whether to accept agentic traffic and what an agent may do.

Trust Signals for Agentic Interactions (TSAI) is an open protocol for carrying this evidence in verifiable credentials. It is stewarded by AWS together with industry partners. The [TSAI website](https://tsaiprotocol.org/) provides the broader overview, examples, and participation guidance, while this repository contains the working specification and machine-readable artefacts used to review and implement the protocol.

The TSAI protocol was partially inspired by [“Inter-Agent Trust Models: A Comparative Study of Brief, Claim, Proof, Stake, Reputation and Constraint in Agentic Web Protocol Design” (Hu and Rong, 2025)](https://arxiv.org/abs/2511.03434).

## How TSAI works

### Actors and relationships

The **Agent Operator**, shortened to **Operator** in the specification, is the legal entity that runs an agent and is accountable for it. The **agent** is the software entity that acts and presents a TSAI credential. A **Trust Authority** evaluates the Operator and agent, then issues the credential. A **Service Provider** receives the presentation, verifies it, and decides how to respond.

A **User** may direct the agent, but the TSAI credential does not identify that User or establish delegated authority. The Operator establishes its relationship with the Trust Authority before issuance, while the Service Provider independently chooses which Trust Authorities it accepts. The credential carries the resulting evidence between these parties without transferring the access decision to the Trust Authority.

### Identity and issuance

An Operator enrols with a Trust Authority, establishes its legal identity and controlled domains, and registers each agent under a persistent HTTPS identifier. The agent also registers a P-256 binding key. The identifier remains stable when that key rotates, so reputation, status, and Service Provider policy remain attached to the same agent.

The Trust Authority issues a short-lived [SD-JWT VC](https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-18.html) only after establishing the claims it contains. Every credential identifies the accountable Operator through a required identity floor: legal name, jurisdiction, verification depth, and a recently verified controlled domain.

### Credential and evidence

The credential carries a flat list of signals across identity, reputation, compliance, and assurance. The standard TSAI credential type defines the registered signal vocabulary and field shapes. An extension publishes a separate credential type and schema while retaining the TSAI base requirements; the specification calls this a derived type.

Reputation scores remain specific to the Trust Authority that issues them. Registered scores use a normalised value from 0 to 1, where higher values are more favourable under the referenced methodology. Each score pins an immutable, versioned methodology document, so a Service Provider or auditor can determine how it was produced without requiring every authority to share one evaluation model.

TSAI v1 mandates [ES256](https://www.rfc-editor.org/rfc/rfc7518.html#section-3.4) signatures, P-256 signing and binding keys, and [SHA-256](https://www.rfc-editor.org/rfc/rfc6234.html) protocol digests. Credentials expire after 30 minutes, while time-sensitive signals carry their own confirmation time.

### Presentation and verification

For each interaction, the agent presents the credential with a fresh [key-binding JWT](https://www.rfc-editor.org/rfc/rfc9901.html#section-4.3) signed by the private key associated with the credential. The proof binds the presentation to the receiving Service Provider and to the exact credential. State-changing actions also use a Service-Provider-issued single-use nonce and bind the method, target URI, and [request-body digest](https://www.rfc-editor.org/rfc/rfc9530.html).

The normal verification path uses previously obtained issuer keys and integrity-pinned credential definitions, so it does not depend on a request-time call to the Trust Authority. A verifier checks both signatures, credential type and schema, lifetime, identity continuity, audience, freshness, and any request binding required for the action. A Service Provider may add an online [Token Status List](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-status-list) check where its risk policy requires one.

### Policy and existing controls

The Service Provider chooses which Trust Authorities it accepts and how it uses the verified signals. TSAI standardises the evidence and its verification, while the access decision remains with the receiving service.

TSAI does not identify the end User, grant authority to act or spend, or guarantee future agent behaviour. OAuth, request authentication, account controls, payment mandates, application authorisation, output validation, and runtime abuse controls retain their existing responsibilities. TSAI complements MCP, A2A, HTTP request authentication, and payment protocols because these mechanisms establish different properties.

## Reading and implementing the specification

Begin with the [introduction](./architecture/01-introduction.md) for scope, terminology, and conformance. Implementers should then read the [credential format](./architecture/03-credential-format.md) and [verification algorithm](./architecture/04-verification.md). A Trust Authority implementation also needs the [operational requirements](./architecture/07-trust-authority-apis.md) and the [API definition](./architecture/openapi/trust-authority-api.yaml), written in [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html). Security reviewers should read the [security and privacy analysis](./architecture/06-security-privacy.md) alongside those sections.

[JSON Schemas](./architecture/schemas/) using [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12), [Type Metadata](./architecture/type-metadata/), and [test vectors](./architecture/test-vectors/) accompany the normative prose. These artefacts define concrete payloads and exercise integrity relationships that prose alone cannot test. The [architecture decisions](./decisions/) record the alternatives and trade-offs behind the current design. The [concept documents](./concept/) provide non-normative context and future considerations.

Implementers may choose their own libraries and deployment architecture as long as they satisfy the conformance requirements.

## Contributing

The working group develops TSAI through GitHub issues and pull requests. Use issues for design questions, protocol proposals, and problem reports. A pull request should explain its protocol effect and rationale. It should record material design decisions and update the normative text together with every affected machine-readable artefact. Changes to an integrity-pinned file also require regeneration of each dependent integrity value and vector.

### Validate the repository

Run the repository checker before submitting a change:

```bash
python3 tools/check.py
```

The checker requires Python 3 with `jsonschema`, `PyYAML`, and `cryptography`. It validates the schemas, documentation examples, Type Metadata inheritance, integrity pins, reputation-methodology bindings, signed vectors, and selected cross-document contracts.

## Status and stewardship

TSAI v1 is a Working Group Draft stewarded by AWS with industry partners. The protocol remains under active review and should not be treated as a final standard. The [TSAI website](https://tsaiprotocol.org/) provides working-group contact and participation information.

## License

This project is licensed under the [Apache License 2.0](./LICENSE).

## Disclaimer

Sample code, software libraries, command line tools, proofs of concept, templates, or other related technology are provided as AWS Content or Third-Party Content under the AWS Customer Agreement, or the relevant written agreement between you and AWS (whichever applies). You should not use this AWS Content or Third-Party Content in your production accounts, or on production or other critical data. You are responsible for testing, securing, and optimizing the AWS Content or Third-Party Content, such as sample code, as appropriate for production grade use based on your specific quality control practices and standards. Deploying AWS Content or Third-Party Content may incur AWS charges for creating or using AWS chargeable resources, such as running Amazon EC2 instances or using Amazon S3 storage.
