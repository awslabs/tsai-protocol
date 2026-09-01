<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Protocol Integration

**Version:** 1.0 (Draft)  
**Date:** 2026-08  
**Status:** Working Group Draft

---

## 4.1 Overview

This section specifies how TSAI integrates with agentic protocols. TSAI is additive, transport-agnostic, complementary to existing authentication, and adoptable incrementally; it does not modify the semantics of the protocols it sits beside.

A TSAI presentation is a credential (SD-JWT VC) with a key-binding JWT appended, in the compact form `<issuer-signed JWT>~<key-binding JWT>`. It travels in a `TSAI-Credential` header or an equivalent field, and verification follows Section 3. The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

### 4.1.1 Carrying more than one credential

An agent MAY present credentials from more than one Trust Authority, which is how the redundancy of §5.1.4 and ADR 002 is realised. The `TSAI-Credential` header MAY appear more than once, each occurrence carrying one compact presentation, all bound to the same `cnf` key. A Service Provider SHOULD accept more than one, MAY cap the number it will process, and MUST state its cap in its discovery document, since each additional credential costs a signature verification and possibly a fetch, and an agent needs to know the cap before it presents.

Where two credentials assert conflicting values for the same signal about the same operator, a Service Provider MUST NOT silently prefer one. Its policy resolves the conflict; absent a policy, it treats the disputed signal as unresolved and does not rely on it. This conflict rule is the substantive part of multi-Trust-Authority operation.

### 4.1.2 Error shape

When verification fails, the protocol-appropriate error carries the Section 3.7 code. The `tsaiError` object is `{ "code": "<Section 3.7 code>", "message": "<generic>" }`, placed in the transport's error-data field: the `data` of a JSON-RPC error for MCP and A2A JSONRPC, or the body for HTTP. The message MUST NOT leak issuer or algorithm detail (Section 3.7).

### 4.1.3 Issuer mismatch and discovery

An agent must present a credential from an issuer the Service Provider accepts. If it holds none, verification fails; there is no issuer negotiation in v1.0. An agent discovers the accepted issuers before connecting, from the Service Provider's `/.well-known/tsai-config.json`, the MCP capability, or the A2A extension params. Trust-Authority cross-recognition, by which one authority accepts another's evaluation so a single credential satisfies more Service Providers, is future work.

---

## 4.2 MCP Integration

### 4.2.1 Context

MCP has a host, a client, and a server, over stdio or Streamable HTTP, with OAuth 2.1 for authorization. TSAI answers who the agent is; OAuth answers what the user authorised.

### 4.2.2 Discovery without circularity

A server declares its accepted Trust Authorities so an agent can present an acceptable credential. The declaration must be readable before the agent commits a presentation, which the initialization response cannot provide, because the agent would have to present before learning what is accepted. TSAI resolves this two ways, and the applicable one depends on the transport:

- A server on an HTTP transport MUST publish its TSAI requirement at `/.well-known/tsai-config.json` on its origin, so an agent reads the accepted issuers before connecting.
- A server on stdio, which has no HTTP origin, MUST expose an unauthenticated `initialize` that returns the TSAI capability together with a server-issued `nonce` and the server's audience identifier; the agent then sends an authenticated request carrying the presentation that echoes the `nonce` and sets `aud` to that identifier. An HTTP server MAY offer this as well, and doing so supplies the Service-Provider-issued nonce that Section 3.4 uses for state-changing actions.

The capability is `{ "required": <bool>, "trustedAuthorities": [<https issuer>, ...], "aud": <audience identifier> }`, per [`schemas/mcp-capability-tsai.schema.json`](schemas/mcp-capability-tsai.schema.json). The `aud` field carries the audience identifier a stdio server declares; an HTTP server omits it and the audience is its origin.

### 4.2.3 Transport

Over HTTP the presentation travels in the `TSAI-Credential` header on requests; over stdio it travels in a `tsaiCredential` field of the authenticated request following the unauthenticated capability exchange, with the key-binding JWT `aud` set to the audience identifier the capability exchange declared. A server verifies per Section 3 before acting, and on each request, since credentials are short-lived. What the signals justify is the server's policy over the signals (Section 3), not a tier.

---

## 4.3 A2A Integration

### 4.3.1 Context

A2A has a client agent and a server agent, with an Agent Card fetched unauthenticated at `/.well-known/agent-card.json`, so the accepted issuers are readable before connecting and A2A has no circularity.

### 4.3.2 Declaring TSAI as an extension

TSAI is declared as an A2A extension, not by adding fields to a built-in security scheme. A2A's `httpAuthSecurityScheme` defines only `scheme`, `bearerFormat`, and `description`, so the TSAI-specific fields go in `capabilities.extensions`, where each entry has a `uri`, an optional `description`, a `required` flag, and free-form `params`. Schema: [`schemas/a2a-agent-card-tsai.schema.json`](schemas/a2a-agent-card-tsai.schema.json).

```json
{
  "capabilities": {
    "extensions": [
      {
        "uri": "https://tsaiprotocol.org/a2a/ext/1",
        "required": true,
        "params": { "trustedAuthorities": ["https://trust-authority-a.example"] }
      }
    ]
  },
  "securitySchemes": {
    "tsai": { "httpAuthSecurityScheme": { "scheme": "bearer", "bearerFormat": "dc+sd-jwt" } }
  }
}
```

The `httpAuthSecurityScheme` entry stays a plain `bearer`/`dc+sd-jwt` declaration, which is valid A2A; the accepted issuers live in the extension params.

### 4.3.3 Transport and errors

Over HTTP+JSON the presentation travels in the `TSAI-Credential` header; over gRPC in the `tsai-credential` metadata key. A failure returns an A2A-appropriate error carrying the `tsaiError` object (Section 4.1.2).

### 4.3.4 Webhooks and direction

When a server delivers a webhook and presents its own TSAI credential so the client can confirm the sender, the `aud` of that presentation is the HTTPS origin of the client's webhook endpoint, since `aud` always names the party that verifies. The receiving client is not in a position to issue a challenge in advance, so the presentation carries an agent-generated `nonce` and, for a state-changing notification, a `req` digest over the notification payload (ADR 014).

---

## 4.4 General HTTP Integration

A service carries the presentation in a `TSAI-Credential` header over HTTPS, and MAY advertise its requirement at `/.well-known/tsai-config.json`:

```json
{ "required": true, "trustedAuthorities": ["https://trust-authority.example"] }
```

The `aud` a Service Provider expects is its HTTPS origin; a service reachable at several hostnames, or an MCP server on a path, publishes the exact expected `aud` value in this document so an agent constructs an acceptable presentation.

### 4.4.1 Soft-fail postures

Verification need not be all-or-nothing while a Service Provider builds confidence. A Service Provider advertises one of three postures, and the posture governs what it does with an absent or failing credential:

- **log-only** — verify and record the outcome, gate nothing;
- **annotate** — attach the verified signals to the request for downstream use, gate nothing;
- **enforce** — reject on an absent or failing credential where TSAI is required.

This lets a Service Provider run TSAI in observation before enforcing.

---

## 4.5 Security Considerations

**Exposure.** Presentations travel over HTTPS; a server SHOULD NOT log the `TSAI-Credential` value, and proxies SHOULD NOT cache requests carrying it.

**Replay and substitution.** A presentation is bound to one Service Provider by `aud` and carries a fresh key-binding JWT. Within the freshness window, a component that observes a presentation inside the audience's own boundary could attach it to a different action unless the presentation binds the request; for state-changing actions a Service Provider requires `req` (Section 3.4, ADR 014). A captured credential is unusable without the holder's `cnf` private key.

**Payments boundary.** Assurance says what backing stands behind an agent; it does not say the agent is authorised to spend a given amount. A mandate and its value limits ride on the payment protocol (AP2 or equivalent); TSAI carries identity, standing, and recourse. A payment request therefore carries both: the TSAI presentation for who the agent is and what backs it, and the payment protocol's mandate for what it may spend.

**Trust Authority compromise.** Several Trust Authorities give redundancy, a Service Provider pins the issuers it trusts, and the governance body monitors behaviour.

---

## 4.6 Integration with the W3C AI Agent Protocol

The W3C AI Agent Protocol handles agent discovery, description, and agent-to-agent communication, and authenticates an agent with its own DIDWba scheme, which uses a `did:wba` identifier. TSAI does not use `did:wba`; it identifies the agent by the key its credential is bound to. The layers are orthogonal: the W3C proof establishes control of the W3C identity, and the TSAI presentation carries the trust signals, as TSAI also composes with Web Bot Auth (ADR 014). A request may carry both.

**One hop.** Because `aud` binds a presentation to one Service Provider, a middle agent cannot forward an upstream agent's presentation, which is correct, and delegation is deferred (ADR 001). The consequence is that in a chain from a personal agent through an orchestrator to a service agent, the service agent learns the orchestrator's trust signals and nothing about the originating agent or the user. This is also recorded as a limitation in §5.11.

---

## 4.7 Normative Requirements Summary

**Protocol servers MUST:**
- Declare TSAI support, and for MCP publish accepted issuers at a well-known location so an agent can read them before presenting.
- Accept a presentation through the transport, accept more than one credential and state the cap, apply the conflict rule (Section 4.1.1), and verify per Section 3.
- Return an error carrying the `tsaiError` object without leaking issuer or algorithm detail.

**Protocol servers SHOULD:**
- Accept a fresh presentation mid-session as credentials expire, and not log the `TSAI-Credential` value.

**Protocol clients MUST:**
- Present a credential from an accepted issuer, that has not expired, with a key-binding JWT proving the `cnf` key, and `req` where the action requires it.

Whether the signals justify an operation is the Service Provider's policy over the signals (Section 3), not a tier.

---

## References

- W3C AI Agent Protocol; MCP 2025-11-25; A2A v1.0; AP2 (Agent Payments Protocol)
- TSAI Credential Format (Section 2), TSAI Verification (Section 3)
