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

This section specifies how TSAI integrates with agentic protocols to provide trust signaling. TSAI complements existing protocols without replacing their authentication, authorization, or communication mechanisms.

TSAI is additive (adds trust signals without modifying protocol semantics), transport-agnostic (works across different protocol bindings), complementary (coexists with existing auth mechanisms like OAuth and API keys), and optional (protocols can adopt TSAI incrementally).

Covered protocols: Model Context Protocol (MCP) in Section 4.2, Agent2Agent Protocol (A2A) in Section 4.3, and general HTTP-based protocols in Section 4.4.

---

## 4.2 MCP Integration

### 4.2.1 MCP Architecture Context

MCP uses a three-party architecture: host (LLM application like Claude Desktop or VS Code), client (connector within host), and server (capability provider for tools, resources, prompts). The host verifies client/agent credentials before allowing server connections.

MCP supports stdio transport (local) and HTTP/SSE transport (remote). Authorization uses OAuth 2.1 with Client ID Metadata Documents. Session management is stateful with capability negotiation. The host enforces explicit user consent.

### 4.2.2 Integration Approach

**TSAI role:** Verify agent/client identity and trustworthiness before OAuth flow.

**Integration pattern:**
```
User → Host (verifies agent via TSAI) → Client (authorized via OAuth) → Server
```

**Separation of concerns:**
- **TSAI:** Agent identity and trust signals (who is the agent?)
- **OAuth 2.1:** User authorization and resource access (what can the user do?)

### 4.2.3 HTTP Transport Integration

For MCP servers using Streamable HTTP transport:

**Credential Presentation:**

Agents include TSAI credentials in HTTP headers:

```http
POST /mcp HTTP/1.1
Host: mcp.example.com
Content-Type: application/json
Authorization: Bearer <oauth-access-token>
TSAI-Credential: <vp-jwt>
MCP-Protocol-Version: 2025-11-25
MCP-Session-Id: <session-id>

{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {...},
    "clientInfo": {...}
  }
}
```

**Header specification:**
- `TSAI-Credential` (REQUIRED for TSAI-enabled servers): Verifiable Presentation JWT
- Value format: Base64url-encoded VP-JWT
- Included on every HTTP request (similar to OAuth bearer token)

**Verification timing:**

Servers SHOULD verify TSAI credentials:
1. **Before initialization:** Verify agent identity before capability exchange
2. **Per-request:** Validate credential on each HTTP request (credentials are short-lived)

**Error responses:**

If TSAI verification fails:

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "TSAI credential verification failed",
    "data": {
      "tsaiError": "SIGNATURE_INVALID",
      "details": "Credential signature could not be verified"
    }
  }
}
```

### 4.2.4 Capability Declaration

MCP servers declare TSAI support in initialization response:

**JSON Schema:** [`schemas/mcp-capability-tsai.schema.json`](schemas/mcp-capability-tsai.schema.json)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "tools": {...},
      "resources": {...},
      "tsai": {
        "required": true,
        "minimumTier": "T1",
        "trustedAuthorities": [
          "did:web:trust-authority-a.example:tsai:ta",
          "did:web:trust-authority-b.example:tsai:ta"
        ]
      }
    },
    "serverInfo": {...}
  }
}
```

**TSAI capability fields:**
- `required` (boolean): Whether TSAI credentials are mandatory
- `minimumTier` (string): Minimum trust tier accepted (T0, T1, T2, T3)
- `trustedAuthorities` (array): List of accepted TA DIDs

**Client behavior:**
- If `tsai.required: true` and client lacks credential: Fail initialization
- If `tsai.required: false`: TSAI is optional, proceed without credential
- Client SHOULD request credential at appropriate tier before connecting

### 4.2.5 stdio Transport Integration

For local MCP servers using stdio transport:

**Challenge:** No HTTP headers available for credential transmission.

**Solution:** Include TSAI credential in initialization message:

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {...},
    "clientInfo": {...},
    "tsaiCredential": "<vp-jwt>"
  }
}
```

**Verification:**
- Server verifies `tsaiCredential` during initialization
- Credential remains valid for session duration (within expiry time)
- Server MAY request credential refresh if expiry approaches

### 4.2.6 OAuth 2.1 Coexistence

TSAI and OAuth 2.1 serve different purposes:

| Aspect | TSAI | OAuth 2.1 |
|--------|------|-----------|
| **Purpose** | Agent identity & trust | User authorization & resource access |
| **Issued by** | Trust Authority | Authorization Server |
| **Verifies** | Agent operator legitimacy | User consent & permissions |
| **Lifetime** | 30 min - 4 hours | Hours to days (with refresh) |
| **Scope** | Agent-level trust signals | Resource-specific permissions |

**Combined flow:**

1. **Agent obtains TSAI credential** from Trust Authority
2. **Agent presents TSAI credential** to MCP server
3. **Server verifies agent identity** via TSAI
4. **Server initiates OAuth flow** for user authorization
5. **User grants permissions** via OAuth consent screen
6. **Agent receives OAuth access token**
7. **Agent makes requests** with both TSAI credential and OAuth token

**Example request:**
```http
POST /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer <oauth-access-token>
TSAI-Credential: <vp-jwt>

{...}
```

**Verification order:**
1. Verify TSAI credential (agent identity)
2. Verify OAuth token (user authorization)
3. Check both are valid and not expired
4. Process request

---

## 4.3 A2A Integration

### 4.3.1 A2A Architecture Context

A2A uses a client-server architecture:
- **A2A Client:** Agent initiating requests
- **A2A Server:** Remote agent providing capabilities

**Trust verification point:** Server verifies client credentials before processing tasks.

**Key characteristics:**
- Transport: HTTP with JSON-RPC, gRPC, or REST
- Discovery: Agent Cards at `/.well-known/agent-card.json`
- State management: Task-based with lifecycle
- Authentication: OAuth 2.0, Bearer tokens, API keys

### 4.3.2 Integration Approach

**TSAI role:** Verify client agent identity and trustworthiness before task processing.

**Integration pattern:**
```
User → A2A Client (verified via TSAI) → A2A Server (trusts client based on TSAI signals)
```

### 4.3.3 Agent Card Enhancement

A2A servers declare TSAI requirements in Agent Card using `HTTPAuthSecurityScheme`:

**JSON Schema for TSAI security scheme:** [`schemas/a2a-agent-card-tsai.schema.json`](schemas/a2a-agent-card-tsai.schema.json)

```json
{
  "protocolVersions": ["0.3"],
  "name": "Research Assistant Agent",
  "description": "AI agent for academic research",
  "supportedInterfaces": [
    {
      "url": "https://research-agent.example.com/a2a/v1",
      "protocolBinding": "HTTP+JSON"
    }
  ],
  "securitySchemes": {
    "oauth2": {
      "oauth2SecurityScheme": {
        "flows": {...}
      }
    },
    "tsai": {
      "httpAuthSecurityScheme": {
        "scheme": "bearer",
        "bearerFormat": "VP-JWT",
        "description": "TSAI Verifiable Presentation (T1+ required)",
        "minimumTier": "T1",
        "trustedAuthorities": [
          "did:web:trust-authority-a.example:tsai:ta",
          "did:web:trust-authority-b.example:tsai:ta"
        ]
      }
    }
  },
  "security": [
    {"oauth2": [], "tsai": []}
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [...]
}
```

**TSAI security scheme structure:**
- Uses A2A's `HTTPAuthSecurityScheme` (bearer token authentication)
- `scheme`: "bearer" (RFC7235)
- `bearerFormat`: "VP-JWT" (Verifiable Presentation JWT)
- `minimumTier`: Minimum trust tier required (TSAI extension)
- `trustedAuthorities`: Accepted TA DIDs (TSAI extension)

**Security combinations:**
- `{"oauth2": [], "tsai": []}` - Both required
- `{"tsai": []}` - TSAI only
- `{"oauth2": []}` - OAuth only (no TSAI)

### 4.3.4 HTTP Transport Integration

For A2A HTTP+JSON binding:

**Credential presentation:**

```http
POST /a2a/v1/message:send HTTP/1.1
Host: research-agent.example.com
Content-Type: application/a2a+json
Authorization: Bearer <oauth-token>
TSAI-Credential: <vp-jwt>
A2A-Version: 0.3

{
  "message": {
    "role": "user",
    "parts": [{"text": "Find research papers on AI safety"}],
    "messageId": "msg-uuid"
  }
}
```

**Header specification:**
- `TSAI-Credential`: Verifiable Presentation JWT
- Included on all A2A requests (SendMessage, GetTask, etc.)
- Verified before task creation or retrieval

**Error responses:**

```http
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{
  "type": "https://a2a-protocol.org/errors/tsai-verification-failed",
  "title": "TSAI Credential Verification Failed",
  "status": 403,
  "detail": "Agent credential could not be verified",
  "tsaiError": "EXPIRED",
  "minimumTier": "T1"
}
```

### 4.3.5 gRPC Transport Integration

For A2A gRPC binding:

**Credential presentation via metadata:**

```
TSAI-Credential: <vp-jwt>
```

**gRPC metadata:**
- Key: `tsai-credential`
- Value: Base64url-encoded VP-JWT
- Included in request metadata for all RPCs

**Error responses:**

```
Status: PERMISSION_DENIED
Message: "TSAI credential verification failed: SIGNATURE_INVALID"
Details: {
  "tsaiError": "SIGNATURE_INVALID",
  "minimumTier": "T1"
}
```

### 4.3.6 Task Authorization

TSAI credentials scope task access:

**Task creation:**
- Server verifies TSAI credential before creating task
- Task is associated with agent DID from credential
- Trust tier determines allowed operations

**Task retrieval:**
- Server verifies agent DID matches task owner
- Prevents cross-agent task access
- Trust tier may affect task visibility

**Example authorization logic:**
```
if (credential.tier < "T1"):
    reject "Insufficient trust tier for this operation"

if (credential.subject.id != task.ownerId):
    reject "Agent does not own this task"

if (credential.expired):
    reject "Credential expired"

allow
```

### 4.3.7 Discovery Integration

**Registry filtering:**

Agent registries can filter by trust tier:

```http
GET /registry/agents?minimumTier=T1&trustedAuthority=did:web:trust-authority.example:tsai:ta
```

**Agent Card serving:**

Servers MAY serve different Agent Cards based on client trust tier:

```http
GET /.well-known/agent-card.json
TSAI-Credential: <vp-jwt>
```

Response includes skills available to that trust tier.

### 4.3.8 Push Notification Security

For A2A push notifications:

**Webhook registration:**

Client provides TSAI credential when creating push notification config:

```http
POST /a2a/v1/tasks/{id}/pushNotificationConfigs
TSAI-Credential: <vp-jwt>

{
  "webhookUrl": "https://client.example.com/webhook",
  "events": ["status-update", "artifact-update"]
}
```

**Webhook delivery:**

Server includes TSAI credential when POSTing to webhook:

```http
POST /webhook HTTP/1.1
Host: client.example.com
Content-Type: application/a2a+json
TSAI-Credential: <server-vp-jwt>

{
  "statusUpdate": {...}
}
```

**Mutual verification:**
- Client verifies server's TSAI credential on webhook delivery
- Prevents spoofed notifications
- Ensures notifications come from legitimate agents

---

## 4.4 General HTTP Integration

For protocols not explicitly covered:

### 4.4.1 HTTP Header Pattern

**Standard approach:**

```http
<METHOD> <PATH> HTTP/1.1
Host: <host>
TSAI-Credential: <vp-jwt>
<other-headers>

<body>
```

**Header specification:**
- Name: `TSAI-Credential`
- Value: Base64url-encoded VP-JWT
- Included on requests requiring trust verification

### 4.4.2 Discovery Endpoint

Services MAY expose TSAI requirements at well-known URI:

```http
GET /.well-known/tsai-config.json
```

**Response:**
```json
{
  "tsaiVersion": "1.0",
  "required": true,
  "minimumTier": "T1",
  "trustedAuthorities": [
    "did:web:trust-authority.example:tsai:ta"
  ],
  "verificationEndpoint": "https://api.example.com/tsai/verify"
}
```

### 4.4.3 Verification Endpoint

Services MAY expose verification endpoint for testing:

```http
POST /tsai/verify
Content-Type: application/json

{
  "credential": "<vp-jwt>"
}
```

**Response:**
```json
{
  "verified": true,
  "tier": "T1",
  "agentDid": "did:web:acme-corp.com:agents:agent123",
  "operatorDid": "did:web:acme-corp.com",
  "issuer": "did:web:trust-authority.example:tsai:ta",
  "expiresAt": "2026-01-23T14:00:00Z",
  "signals": {
    "operator": {
      "name": "Acme Corporation GmbH",
      "jurisdiction": "DE",
      "kycLevel": "enhanced",
      "certifications": ["ISO27001", "SOC2"]
    },
    "agent": {
      "interactionCount": 1247,
      "successRate": 0.94
    }
  }
}
```

---

## 4.5 Security Considerations

### 4.5.1 Credential Exposure

**Risk:** TSAI credentials transmitted in HTTP headers may be logged or cached.

**Mitigation:**
- Always use HTTPS for credential transmission
- Servers SHOULD NOT log `TSAI-Credential` header values
- Proxies SHOULD NOT cache requests with TSAI credentials
- Credentials are short-lived (limits exposure window)

### 4.5.2 Replay Attacks

**Risk:** Attacker intercepts and replays credential.

**Mitigation:**
- VP timestamp limits replay window to ~1 minute
- Servers MAY track recently seen VP signatures
- Short credential expiry limits stolen credential lifetime
- T2/T3 use challenge-response (future specification)

### 4.5.3 Credential Theft

**Risk:** Attacker steals credential from client storage.

**Mitigation:**
- Clients SHOULD store credentials in memory only
- Clients SHOULD encrypt credentials if persisted
- Short expiry limits stolen credential lifetime
- Revocation provides emergency invalidation

### 4.5.4 Trust Authority Compromise

**Risk:** Compromised TA issues fraudulent credentials.

**Mitigation:**
- Multiple TAs provide redundancy
- Service Providers can pin trusted TA DIDs
- Governance body monitors TA behavior
- Credential transparency logs (future consideration)

---

## 4.6 Future Extensions

### 4.6.1 Challenge-Response Protocol

Future versions will specify challenge-response for T2/T3:

**Flow:**
1. Server sends random nonce
2. Agent signs nonce with credential
3. Server verifies signature freshness
4. Eliminates replay window

### 4.6.2 Credential Delegation

Future versions will specify agent-to-agent delegation:

**Use case:** Agent A delegates to Agent B to perform sub-task

**Mechanism:** ZCAP-LD or similar delegation credential

### 4.6.3 Protocol-Specific Extensions

Future versions may define protocol-specific extensions:
- MCP: Tool-level trust requirements
- A2A: Task-level trust escalation
- HTTP: Resource-specific trust policies

---

## 4.7 Integration with W3C AI Agent Protocol

### 4.7.1 Overview

The W3C AI Agent Protocol Community Group is developing standardized protocols for agent-to-agent (A2A) communication, focusing on identity, discovery, description, and interaction mechanisms. TSAI is complementary to the W3C AI Agent Protocol:

- **W3C AI Agent Protocol:** Handles agent discovery, description, and A2A communication
- **TSAI:** Provides trust signaling for those interactions

**Relationship:** TSAI adds trust verification to W3C protocol interactions without modifying the W3C protocol itself.

### 4.7.2 Terminology Mapping

The W3C AI Agent Protocol and TSAI use different terminology for similar concepts:

| W3C AI Agent Protocol | TSAI Equivalent | Description |
|----------------------|-----------------|-------------|
| Personal Agent | Agent | Serves individual users, acts on their behalf |
| Service Agent | Service Provider | Provides services to other Agents |
| Search Agent | Out of scope | Discovery service (not covered by TSAI) |

**Clarification on "Agent":** When discussing both protocols together, "Agent" may refer to either a W3C Personal Agent or a TSAI Agent. Context determines meaning.

**Clarification on "Service Agent" vs. "Service Provider":** These similar-sounding terms name distinct concepts. A W3C "Service Agent" is an Agent in the W3C sense; a TSAI "Service Provider" is the TSAI actor that receives and verifies credentials. When a W3C Service Agent receives a TSAI credential, it is acting as a TSAI Service Provider. The same physical component can therefore be a W3C Service Agent and a TSAI Service Provider simultaneously, depending on which protocol is being discussed.

### 4.7.3 Identity Layer Compatibility

**W3C AI Agent Protocol Identity:**
- Uses `did:wba` (Web-Based Agent DID method)
- Resolution: `did:wba:agent.example.com:alice` → `https://agent.example.com/alice/did.json`
- Authentication: DIDWba scheme with signature in Authorization header

**TSAI Identity:**
- Supports `did:web`, `did:key`, and `did:wba`
- All methods are W3C DID-compliant and interoperable
- Authorization: TSAI credentials (Verifiable Presentations) with trust signals

**Compatibility:** TSAI explicitly supports `did:wba` as a valid agent DID method. Agents using W3C AI Agent Protocol can obtain TSAI credentials using their `did:wba` identifiers.

### 4.7.4 Combined Authentication and Authorization Flow

When a Personal Agent (W3C protocol) interacts with a Service Agent that requires trust verification:

**Step 1: W3C Protocol Authentication**
```http
GET /api/booking HTTP/1.1
Host: hotel.example.com
Authorization: DIDWba did="did:wba:agent.example.com:alice", nonce="abc123", timestamp="2026-01-30T10:00:00Z", verification_method="key-1", signature="base64url(signature)"
TSAI-Credential: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Step 2: Service Agent Verification**

The Service Agent performs two verification steps:

1. **DIDWba Authentication (W3C Protocol):**
   - Verify timestamp is within ±1 minute
   - Verify nonce hasn't been used (replay prevention)
   - Resolve `did:wba:agent.example.com:alice` to get DID document
   - Verify signature using public key from DID document
   - **Result:** Proves Personal Agent controls the DID

2. **TSAI Authorization:**
   - Parse TSAI credential from `TSAI-Credential` header
   - Verify TA signature on credential
   - Verify agent signature on VP
   - Check credential hasn't expired
   - Check trust tier meets requirements (e.g., T1+)
   - **Result:** Proves Personal Agent has TA-issued trust credential

**Step 3: Access Token Issuance**

If both verifications succeed, Service Agent returns JWT access token:

```http
HTTP/1.1 200 OK
Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Step 4: Subsequent Requests**

Personal Agent uses access token for subsequent requests (no repeated DIDWba/TSAI verification):

```http
GET /api/booking/status HTTP/1.1
Host: hotel.example.com
Authorization: Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.7.5 Use Case: Hotel Booking with Trust Verification

**Scenario:** Alice's Personal Agent wants to book a hotel using W3C AI Agent Protocol. The hotel Service Agent requires T1 credentials to prevent spam and fraud.

**Process:**

1. **Discovery:** Alice's Personal Agent discovers hotel Service Agent via Search Agent or `.well-known/agent-descriptions`

2. **Agent Description:** Personal Agent retrieves hotel's agent description, which declares TSAI requirement:
```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "ad": "https://example.com/ad#"
  },
  "@type": "ad:AgentDescription",
  "name": "Hotel Booking Agent",
  "did": "did:wba:hotel.example.com:booking",
  "tsaiRequirements": {
    "required": true,
    "minimumTier": "T1",
    "trustedAuthorities": [
      "did:web:trust-authority-a.example:tsai:ta",
      "did:web:trust-authority-b.example:tsai:ta"
    ]
  },
  "interfaces": [...]
}
```

3. **Credential Acquisition:** Personal Agent obtains T1 TSAI credential from Trust Authority (if not already cached)

4. **Authentication:** Personal Agent sends request with both DIDWba authentication and TSAI credential

5. **Verification:** Hotel Service Agent verifies both (identity + trust)

6. **Booking:** Hotel Service Agent grants access, Personal Agent completes booking

**Value:** Hotel Service Agent gets both identity proof (W3C protocol) and trust signals (TSAI), enabling risk-calibrated access decisions.

### 4.7.6 Agent Description Extension for TSAI

Service Agents using W3C AI Agent Protocol can declare TSAI requirements in their agent description documents:

**Optional TSAI fields in agent description:**

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "ad": "https://example.com/ad#",
    "tsai": "https://tsai.example.org/credentials/v1"
  },
  "@type": "ad:AgentDescription",
  "name": "Service Agent Name",
  "did": "did:wba:service.example.com:agent",
  "tsaiRequirements": {
    "required": true,
    "minimumTier": "T1",
    "trustedAuthorities": [
      "did:web:trust-authority-a.example:tsai:ta"
    ]
  }
}
```

**Fields:**
- `tsaiRequirements.required` (boolean): Whether TSAI credentials are mandatory
- `tsaiRequirements.minimumTier` (string): Minimum trust tier accepted (T0, T1, T2, T3)
- `tsaiRequirements.trustedAuthorities` (array): List of accepted TA DIDs

**Discovery:** Personal Agents can filter Service Agents by TSAI requirements during discovery.

### 4.7.7 Error Handling

**DIDWba Authentication Failure:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer error="invalid_signature", error_description="DIDWba signature verification failed", nonce="xyz987"
```

**TSAI Authorization Failure:**

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "insufficient_trust",
  "error_description": "T1 or higher credential required",
  "required_tier": "T1",
  "provided_tier": "T0"
}
```

**Combined Failure (both invalid):**

Service Agent SHOULD return 401 (authentication takes precedence over authorization).

### 4.7.8 Implementation Guidance

**For Personal Agents (W3C Protocol Clients):**
- Obtain TSAI credentials from Trust Authority
- Include both DIDWba authentication and TSAI credential in requests
- Handle TSAI-specific errors (insufficient trust tier, untrusted TA)
- Cache TSAI credentials (within expiry) to reduce TA load

**For Service Agents (W3C Protocol Servers):**
- Declare TSAI requirements in agent description
- Verify both DIDWba authentication and TSAI authorization
- Return clear error messages for TSAI failures
- Support degraded mode (accept lower tiers) for infrastructure failures

**For Search Agents:**
- Index TSAI requirements from agent descriptions
- Enable filtering by trust tier ("find T2+ hotel agents")
- Rank results by trust tier (optional)

### 4.7.9 Benefits of Integration

**For Personal Agents:**
- Access to trust-sensitive Service Agents
- Portable trust across multiple Service Agents
- Reduced friction (one credential, many services)

**For Service Agents:**
- Reduced fraud and spam
- Risk-calibrated access decisions
- Legal accountability (know who to hold responsible)

**For the Ecosystem:**
- Interoperable trust infrastructure
- Standards-based (W3C DIDs, VCs, JSON-LD)
- Complementary protocols (discovery + trust)

### 4.7.10 Future Considerations

**Mutual Verification:**
- Currently: Personal Agent proves trust to Service Agent (one-way)
- Future: Service Agent could also present TSAI credential to Personal Agent (mutual)
- Use case: Personal Agent verifies hotel is legitimate before sharing payment info

**Search Agent Integration:**
- Search Agents could require TSAI credentials for registration
- Prevents spam agents from polluting discovery
- Enables trust-based ranking in search results

**Trust Authority Discovery:**
- W3C protocol uses `.well-known/agent-descriptions` for agent discovery
- TSAI could adopt `.well-known/trust-authorities` for TA discovery
- Aligns discovery patterns across protocols

---

## 4.8 Normative Requirements Summary

**Protocol Servers MUST:**
- Declare TSAI support via protocol-specific mechanism
- Accept credentials via protocol-specific transport
- Verify credentials according to Section 3
- Return protocol-specific error responses on verification failure
- Clearly indicate degraded mode operation

**Protocol Servers SHOULD:**
- Support credential refresh mid-session
- Cache verification results appropriately
- Log TSAI-related events for monitoring
- Implement circuit breakers for TA infrastructure

**Protocol Servers MAY:**
- Require specific trust tiers for operations
- Filter capabilities based on trust tier
- Operate in degraded mode for infrastructure failures

**Protocol Clients MUST:**
- Obtain credentials at appropriate tier
- Present credentials via protocol-specific mechanism
- Handle verification failures gracefully
- Refresh credentials before expiry

**Protocol Clients SHOULD:**
- Store credentials securely
- Monitor credential lifecycle
- Implement retry logic for transient failures

**Protocol Clients MAY:**
- Cache credentials (within expiry)
- Pre-fetch credentials for anticipated use
- Request multiple tiers for different operations

---

## References

- W3C AI Agent Protocol Specification: https://w3c-cg.github.io/ai-agent-protocol/protocol.html
- MCP Protocol Specification: https://github.com/modelcontextprotocol/modelcontextprotocol
- A2A Protocol Specification: https://github.com/a2aproject/A2A
- TSAI Credential Format: [Section 3](./03-credential-format.md)
- TSAI Verification: [Section 4](./04-verification.md)
