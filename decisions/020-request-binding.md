<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 020: Request Binding

**Status:** Accepted  
**Date:** 2026-08-01  
**Deciders:** TSAI Working Group  
**Relationship to ADR 014:** amends [ADR 014 — Holder Binding and Web Bot Auth Integration](./014-holder-binding-and-web-bot-auth-integration.md); corrects its criterion-1 analysis

---

## Context

The key-binding JWT binds a presentation to a credential (`sd_hash`), to one Service Provider (`aud`), to a time (`iat`), and, when one is issued, to a challenge (`nonce`). It does not bind the request the presentation accompanies: not the method, not the target URI, not the body.

Within the freshness window, any party that observes a presentation and can reach the same `aud` may attach it to a different request against that audience. This is substitution, and it is distinct from replay to another Service Provider, which `aud` already prevents. A single-use nonce does not close it, because there is one presentation and one use; the substitution happens on that single use.

Three settings make it concrete. When the verifying component and the acting component differ — an edge verifier forwarding to an origin, which §1.3 and §4.4 document — a component in between can swap the request. On the JSON-RPC transports TSAI most expects, MCP and A2A's JSONRPC binding, the method and target URI are the same for every call, so signing them is vacuous and only a body digest distinguishes one `tools/call` from another. And on a push notification (§4.3.5) the receiver cannot issue a challenge in advance, so only a payload digest binds the notification.

ADR 014 rated variant 1a's binding strength "strong" and did not account for request substitution; on that specific property a conformant Web Bot Auth signature, which signs the request components, binds the request and variant 1a does not.

---

## Decision

Add an OPTIONAL `req` claim to the key-binding JWT: a digest over the request, computed as a content digest of the body per RFC 9530, together with the method and target URI. The body digest is the essential component, because on JSON-RPC transports the method and URI carry no distinction.

`req` is OPTIONAL at baseline and REQUIRED where the risk of the action warrants it, which is the escalation vocabulary ADR 018 already defines; a Service Provider whose verifying and acting components differ requires it for state-changing actions. This closes substitution inside the freshness window for those actions, and it makes ADR 018's window defensible: a read is exposed only to replay, which `aud` and the window bound, and a state-changing action is bound to its request.

`req` is an added key-binding JWT claim, which RFC 9901 §4.3 discourages absent a compelling reason. Request binding for state-changing actions is such a reason, and the claim carries an established RFC 9530 mechanism inside the artefact TSAI controls rather than depending on an external signature being present and correctly profiled. This is variant 1a's own logic applied to one more property, so the deviation is consistent with ADR 014.

---

## Consequences

- Substitution is closed for state-changing actions that carry `req`; reads remain exposed only to bounded replay.
- The key-binding JWT carries a claim beyond the RFC 9901 set, recorded here as a deliberate deviation.
- A Service Provider that separates verification from action MUST require `req` for state-changing actions; §5.3 and §5.11 state the residual risk for the case where it is absent.
- ADR 014's criterion-1 comparison is corrected: variant 1a does not bind the request, and `req` supplies the property without adopting the RFC 9421 acceptance path ADR 014 rejected.

---

## References

- [ADR 014 — Holder Binding and Web Bot Auth Integration](./014-holder-binding-and-web-bot-auth-integration.md)
- [ADR 018 — Verification Strength, Replay, and Lifetime without Tiers](./018-verification-strength-and-replay.md)
- [RFC 9530 — Digest Fields](https://www.rfc-editor.org/rfc/rfc9530)
- [RFC 9421 — HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
- [RFC 9901 — SD-JWT](https://www.rfc-editor.org/rfc/rfc9901) §4.3
