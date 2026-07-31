<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# TSAI Architecture Specification - Protocol Integration

**Version:** 1.0 (Draft)  
**Date:** January 2026  
**Status:** Working Group Draft

---

## 4.1 Overview

This section specifies how TSAI integrates with agentic protocols to carry trust signals. TSAI is additive, transport-agnostic, complementary to existing authentication and authorization mechanisms such as OAuth, and adoptable incrementally. It does not modify the semantics of the protocols it sits beside.

A TSAI presentation is a credential (SD-JWT VC, Section 2) with a key-binding JWT appended, in the compact form `<issuer-signed JWT>~<key-binding JWT>`. Across the transports below it travels in a `TSAI-Credential` header or an equivalent field. Verification follows Section 3.

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119.

---

## 4.2 MCP Integration

### 4.2.1 Context

MCP uses a host, a client, and a server. The host verifies the agent before allowing server connections. Transports are stdio (local) and Streamable HTTP (remote). Authorization uses OAuth 2.1. TSAI answers who the agent is; OAuth answers what the user has authorised.

### 4.2.2 HTTP transport

The agent carries its presentation in a header:

```http
POST /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer <oauth-access-token>
TSAI-Credential: <issuer-signed JWT>~<key-binding JWT>
MCP-Protocol-Version: 2025-11-25

{ "jsonrpc": "2.0", "method": "initialize", "params": { "...": "..." } }
```

The `TSAI-Credential` header carries the compact presentation. A server verifies it before initialization and, because credentials are short-lived, on each request. On failure it returns a JSON-RPC error with a `tsaiError` code from Section 3.5.

### 4.2.3 Capability declaration

A server declares TSAI support in the initialization response. Schema: [`schemas/mcp-capability-tsai.schema.json`](schemas/mcp-capability-tsai.schema.json).

```json
{
  "capabilities": {
    "tsai": {
      "required": true,
      "trustedAuthorities": [
        "https://trust-authority-a.example",
        "https://trust-authority-b.example"
      ]
    }
  }
}
```

`required` states whether a credential is mandatory; `trustedAuthorities` lists the accepted Trust Authority issuers as HTTPS identifiers. What a server requires of the signals themselves, and how it weighs them, is its own policy (Section 3.4).

### 4.2.4 stdio transport

Without HTTP headers, the agent includes the presentation in the initialization message as `tsaiCredential`. The server verifies it during initialization, and MAY request a fresh one as expiry approaches.

### 4.2.5 OAuth 2.1 coexistence

TSAI and OAuth serve different purposes and run together: TSAI establishes agent identity and trust, OAuth establishes user authorization. A request may carry both, the `TSAI-Credential` header and the OAuth bearer token. A server verifies the TSAI presentation first, then the OAuth token.

---

## 4.3 A2A Integration

### 4.3.1 Context

A2A has a client agent and a server agent, with discovery through an Agent Card at `/.well-known/agent-card.json`. The server verifies the client before processing a task.

### 4.3.2 Agent Card

A server declares TSAI in the Agent Card with an `HTTPAuthSecurityScheme`. Schema: [`schemas/a2a-agent-card-tsai.schema.json`](schemas/a2a-agent-card-tsai.schema.json).

```json
{
  "securitySchemes": {
    "tsai": {
      "httpAuthSecurityScheme": {
        "scheme": "bearer",
        "bearerFormat": "dc+sd-jwt",
        "description": "A TSAI credential presentation",
        "trustedAuthorities": [
          "https://trust-authority-a.example"
        ]
      }
    }
  },
  "security": [ { "tsai": [] } ]
}
```

`bearerFormat` is `dc+sd-jwt`, the SD-JWT VC media type. `trustedAuthorities` lists accepted issuers as HTTPS identifiers.

### 4.3.3 Transports

Over HTTP+JSON the presentation travels in the `TSAI-Credential` header; over gRPC in the `tsai-credential` metadata key. In both, the value is the compact presentation, verified before a task is created or retrieved. Failures return a protocol-appropriate error carrying a `tsaiError` code.

### 4.3.4 Task authorization

A server verifies the presentation before creating a task and associates the task with the presenting agent, identified by its `cnf` key. On retrieval it confirms the same agent. Whether the signals justify the requested operation is the server's policy over the signals (Section 3.4), not a tier check.

### 4.3.5 Push notifications

When a server delivers a webhook, it MAY present its own TSAI credential so the client can confirm the notification comes from the expected agent. This is the same presentation and verification in the reverse direction.

---

## 4.4 General HTTP Integration

A service that is not covered above carries the presentation in a `TSAI-Credential` header on requests that require trust verification, over HTTPS.

A service MAY advertise its requirements at a well-known URI:

```http
GET /.well-known/tsai-config.json
```

```json
{
  "required": true,
  "trustedAuthorities": [ "https://trust-authority.example" ]
}
```

A service MAY expose a verification endpoint for testing that returns the verification outcome and the reconstructed signals:

```json
{
  "verified": true,
  "iss": "https://trust-authority.example",
  "sub": "https://acme-corp.example/agents/shopper-v3",
  "expiresAt": 1781865000,
  "signals": [
    { "cat": "idn", "typ": "jur", "val": "DE" },
    { "cat": "rep", "typ": "ecommerce", "prv": "did:web:rating-agency.example", "scr": 0.94, "cnt": 3518, "wdw": "P90D" }
  ]
}
```

---

## 4.5 Security Considerations

**Credential exposure.** Presentations travel over HTTPS. A server SHOULD NOT log the `TSAI-Credential` value, and proxies SHOULD NOT cache requests carrying it.

**Replay.** A presentation is bound to one Service Provider by `aud` and carries a fresh key-binding JWT per request, so a captured presentation is not usable elsewhere, and a captured credential is not usable at all without the holder's `cnf` private key. The freshness window and any nonce are specified in Section 3.4 and ADR 018.

**Credential theft.** A stored credential is unusable without the `cnf` private key, so an agent SHOULD hold that key in memory and, if it must persist it, protect it. The short lifetime bounds exposure.

**Trust Authority compromise.** Multiple Trust Authorities give redundancy, a Service Provider pins the issuers it trusts, and the governance body monitors Trust Authority behaviour.

---

## 4.6 Integration with the W3C AI Agent Protocol

### 4.6.1 Overview

The W3C AI Agent Protocol Community Group is standardising agent discovery, description, and agent-to-agent communication. TSAI is complementary: the W3C protocol handles discovery and communication, TSAI carries trust signals for those interactions.

### 4.6.2 Terminology

| W3C AI Agent Protocol | TSAI | Description |
|---|---|---|
| Personal Agent | Agent | Acts on behalf of a user |
| Service Agent | Service Provider | Receives and verifies credentials |
| Search Agent | Out of scope | Discovery service |

A single component can be a W3C Service Agent and a TSAI Service Provider at once, depending on which protocol is in view.

### 4.6.3 Identity layers are separate

The W3C protocol authenticates an agent with its own scheme, DIDWba, which uses a `did:wba` identifier and a signature over a nonce and timestamp. That proves the agent controls its W3C identity. TSAI does not use `did:wba`. A TSAI credential identifies the agent by the `cnf` key it is bound to and the Trust Authority by an HTTPS issuer (ADR 017).

The two layers are orthogonal and compose cleanly: the W3C DIDWba proof establishes control of the W3C identity, and the TSAI presentation establishes trust signals for that agent. A request can carry both, in the same way a TSAI presentation composes with Web Bot Auth (ADR 014).

### 4.6.4 Combined flow

A Service Agent that requires trust verification performs two checks on a request that carries both a DIDWba `Authorization` header and a `TSAI-Credential` header: the DIDWba proof for control of the W3C identity, and the TSAI presentation for the signals, per Section 3. If both hold, it proceeds, for example by issuing a session token for subsequent requests.

### 4.6.5 Declaring the requirement

A Service Agent MAY declare its TSAI requirement in its agent description:

```json
{
  "@type": "ad:AgentDescription",
  "name": "Hotel Booking Agent",
  "tsaiRequirements": {
    "required": true,
    "trustedAuthorities": [ "https://trust-authority-a.example" ]
  }
}
```

A Personal Agent obtains a credential from a Trust Authority, presents it alongside its DIDWba proof, and the Service Agent decides on the signals per its own policy.

---

## 4.7 Normative Requirements Summary

**Protocol servers MUST:**
- Declare TSAI support through the protocol's mechanism.
- Accept a presentation through the protocol's transport and verify it per Section 3.
- Return a protocol-appropriate error on failure.

**Protocol servers SHOULD:**
- Accept a fresh presentation mid-session as credentials expire.
- Avoid logging the `TSAI-Credential` value.

**Protocol clients MUST:**
- Obtain a credential and present it through the protocol's mechanism.
- Present a credential that has not expired, and prove possession of the `cnf` key.

**Protocol clients SHOULD:**
- Protect the `cnf` private key.
- Obtain a fresh credential before expiry.

Whether the signals justify a given operation is the Service Provider's policy over the signals (Section 3.4), not a tier.

---

## References

- W3C AI Agent Protocol: https://w3c-cg.github.io/ai-agent-protocol/protocol.html
- MCP Protocol Specification: https://github.com/modelcontextprotocol/modelcontextprotocol
- A2A Protocol Specification: https://github.com/a2aproject/A2A
- TSAI Credential Format: [Section 2](./03-credential-format.md)
- TSAI Verification: [Section 3](./04-verification.md)
