#!/usr/bin/env python3
# Copyright Amazon.com Inc. or its affiliates.
# SPDX-License-Identifier: Apache-2.0
"""
TSAI specification checker.

Mechanises the artefact-agreement checks from the review process feedback:

  1. every JSON schema is a valid Draft 2020-12 schema;
  2. every JSON example embedded in the docs validates against the right schema;
  3. Type Metadata, credential schemas, reputation methodology documents, and
     their integrity bindings agree;
  4. the key-binding-JWT test vectors are schema-valid and their freshness verdict
     matches the Section 3.4 rule;
  5. no review-artefact tokens ([A-L].n) leak into the repository;
  6. the OpenAPI parses and declares a servers block;
  7. (warning only) every "Section n.n" / "§n.n" cross-reference resolves to a heading.

Run from anywhere: it locates the repository root relative to this file.
Exit status is non-zero if any check other than the cross-reference warning fails.

Requires: jsonschema, pyyaml, cryptography.
"""
import base64
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
ARCH = ROOT / "architecture"
SCHEMAS = ARCH / "schemas"
FORMAT_CHECKER = FormatChecker()
CLOCK_SKEW_SECONDS = 30
DOMAIN_FRESHNESS_SECONDS = 12 * 60 * 60

failures = []
warnings = []


def fail(msg):
    failures.append(msg)


def warn(msg):
    warnings.append(msg)


def load_json(path):
    with open(path) as f:
        return json.load(f)


# ---- 1. schemas are valid Draft 2020-12 -----------------------------------
schema_files = sorted(SCHEMAS.glob("*.schema.json"))
schemas = {}
schemas_by_id = {}
schema_paths_by_id = {}
for sf in schema_files:
    try:
        s = load_json(sf)
        Draft202012Validator.check_schema(s)
        schemas[sf.name] = s
        if "$id" in s:
            schemas_by_id[s["$id"]] = s
            schema_paths_by_id[s["$id"]] = sf
    except Exception as e:  # noqa: BLE001
        fail(f"[schema] {sf.name} is not a valid Draft 2020-12 schema: {e}")

CRED = schemas.get("tsai-credential.schema.json")
KB = schemas.get("key-binding-jwt.schema.json")
TM = schemas.get("tsai-type-metadata.schema.json")
REPUTATION_METHOD = schemas.get("tsai-reputation-methodology.schema.json")
A2A = schemas.get("a2a-agent-card-tsai.schema.json")
MCP = schemas.get("mcp-capability-tsai.schema.json")
TA_STATUS = schemas.get("tsai-ta-status.schema.json")
HSM = schemas.get("tsai-ta-hsm-attestation.schema.json")
REGISTERED_REPUTATION_TYPES = set(
    CRED.get("$defs", {})
    .get("reputationSignal", {})
    .get("properties", {})
    .get("typ", {})
    .get("enum", [])
) if CRED else set()

# a sub-schema over just the signals array, for the fragment examples
SIGNALS_SUB = None
reputation_fixture = None
if CRED:
    signals_fragment_schema = copy.deepcopy(CRED["properties"]["signals"])
    signals_fragment_schema["items"] = {"$ref": "#/$defs/registeredSignal"}
    SIGNALS_SUB = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["signals"],
        "properties": {"signals": signals_fragment_schema},
        "$defs": copy.deepcopy(CRED["$defs"]),
    }

    reputation_validator = Draft202012Validator(
        CRED["$defs"]["reputationSignal"],
        format_checker=FORMAT_CHECKER,
    )
    reputation_fixture = {
        "cat": "rep",
        "typ": "ecommerce",
        "asof": 1781800000,
        "mtd": "https://ta.example/reputation/test-vector/1",
        "mtd#integrity": "sha256-Td9FdWbwljmeY78DD/gKxGxPSjjV9vzvOU3oXPH4dJY=",
        "scr": 0.94,
        "cnt": 3518,
        "wdw": "P90D",
    }
    if list(reputation_validator.iter_errors(reputation_fixture)):
        fail("[reputation] valid score, methodology, and evidence context were rejected")
    for required_field in ("asof", "mtd", "mtd#integrity", "scr", "cnt", "wdw"):
        invalid_reputation = dict(reputation_fixture)
        invalid_reputation.pop(required_field)
        if not list(reputation_validator.iter_errors(invalid_reputation)):
            fail(f"[reputation] missing {required_field} was accepted")
    invalid_reputation = dict(reputation_fixture, band="established")
    if not list(reputation_validator.iter_errors(invalid_reputation)):
        fail("[reputation] removed band field was accepted")
    for invalid_score in (-0.01, 1.01):
        invalid_reputation = dict(reputation_fixture, scr=invalid_score)
        if not list(reputation_validator.iter_errors(invalid_reputation)):
            fail(f"[reputation] score outside [0, 1] was accepted: {invalid_score}")


def issuer_metadata_url(issuer):
    if any(character.isspace() for character in issuer):
        raise ValueError("issuer must not contain whitespace")
    parsed = urlsplit(issuer)
    if parsed.scheme != "https" or not parsed.netloc or parsed.hostname is None or parsed.query or parsed.fragment:
        raise ValueError("issuer must be an HTTPS URL without query or fragment")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("issuer authority must not contain user information")
    try:
        parsed.port
    except ValueError as error:
        raise ValueError("issuer contains an invalid port") from error
    path = parsed.path.rstrip("/")
    return f"https://{parsed.netloc}/.well-known/jwt-vc-issuer{path}"


_issuer_cases = {
    "https://ta.example": "https://ta.example/.well-known/jwt-vc-issuer",
    "https://ta.example/": "https://ta.example/.well-known/jwt-vc-issuer",
    "https://ta.example/tenant/acme": "https://ta.example/.well-known/jwt-vc-issuer/tenant/acme",
    "https://ta.example/tenant/acme/": "https://ta.example/.well-known/jwt-vc-issuer/tenant/acme",
}
for issuer, expected in _issuer_cases.items():
    if issuer_metadata_url(issuer) != expected:
        fail(f"[issuer] metadata URL mismatch for {issuer}")
    if CRED and list(Draft202012Validator(CRED["properties"]["iss"], format_checker=FORMAT_CHECKER).iter_errors(issuer)):
        fail(f"[issuer] credential schema rejects valid issuer {issuer}")
for issuer in (
    "http://ta.example",
    "https://user@ta.example/path",
    "https://ta.example:invalid/path",
    "https://ta.example:99999/path",
    "https://ta.example/path with-space",
    "https:///missing-host",
    "https://ta.example/path?x=1",
    "https://ta.example/path#fragment",
):
    try:
        issuer_metadata_url(issuer)
        fail(f"[issuer] invalid issuer accepted by URL construction: {issuer}")
    except ValueError:
        pass
    if CRED and not list(Draft202012Validator(CRED["properties"]["iss"], format_checker=FORMAT_CHECKER).iter_errors(issuer)):
        fail(f"[issuer] credential schema accepts invalid issuer {issuer}")


CANONICAL_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)"
    r"(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$"
)


def canonical_hostname(value):
    if not isinstance(value, str):
        return None
    hostname = urlsplit(value).netloc if "://" in value else value
    return hostname if CANONICAL_HOSTNAME.fullmatch(hostname) else None


for valid_hostname in ("acme.example", "xn--bcher-kva.example"):
    if canonical_hostname(valid_hostname) != valid_hostname:
        fail(f"[identity] canonical hostname was rejected: {valid_hostname}")
for invalid_hostname in ("Acme.example", "acme.example.", "bücher.example", "-acme.example"):
    if canonical_hostname(invalid_hostname) is not None:
        fail(f"[identity] non-canonical hostname was accepted: {invalid_hostname}")


def credential_identity_errors(instance):
    errors = []
    sub = instance.get("sub")
    sub_host = canonical_hostname(sub) if isinstance(sub, str) else None
    if sub_host is None:
        return ["sub is missing or has no valid hostname"]
    iat = instance.get("iat")
    matching = [
        signal
        for signal in instance.get("signals", [])
        if isinstance(signal, dict)
        and signal.get("cat") == "idn"
        and signal.get("typ") == "dct"
        and canonical_hostname(signal.get("val")) == sub_host
    ]
    if not matching:
        return ["sub hostname does not match any dct"]
    if not isinstance(iat, int):
        return ["credential iat is not an integer"]
    if not any(
        isinstance(signal.get("asof"), int)
        and signal["asof"] <= iat + CLOCK_SKEW_SECONDS
        and iat - signal["asof"] <= DOMAIN_FRESHNESS_SECONDS
        for signal in matching
    ):
        errors.append("matching dct is outside the domain-freshness window")
    return errors


def validate(instance, schema, label):
    if schema is None:
        warn(f"[example] {label}: no schema loaded to validate against")
        return
    errs = sorted(Draft202012Validator(schema, format_checker=FORMAT_CHECKER).iter_errors(instance), key=str)
    for e in errs:
        loc = "/".join(str(p) for p in e.absolute_path) or "(root)"
        fail(f"[example] {label}: {loc}: {e.message}")


def sri(path):
    digest = hashlib.sha256(path.read_bytes()).digest()
    return "sha256-" + base64.b64encode(digest).decode()


def methodology_semantic_errors(methodology):
    score = methodology.get("score", {})
    errors = []
    if score.get("minimum") != 0:
        errors.append("score.minimum must be 0")
    if score.get("maximum") != 1:
        errors.append("score.maximum must be 1")
    if score.get("direction") != "higher-better":
        errors.append("score.direction must be higher-better")
    return errors


METHODOLOGY_VECTOR_PATH = ARCH / "test-vectors" / "reputation-methodology.json"
METHODOLOGY_FIXTURE = load_json(METHODOLOGY_VECTOR_PATH)
METHODOLOGY_FIXTURE_INTEGRITY = sri(METHODOLOGY_VECTOR_PATH)
validate(METHODOLOGY_FIXTURE, REPUTATION_METHOD, "reputation methodology test vector")
for error in methodology_semantic_errors(METHODOLOGY_FIXTURE):
    fail(f"[reputation-methodology] test vector: {error}")
methodologies_by_id = {METHODOLOGY_FIXTURE["id"]: METHODOLOGY_FIXTURE}
methodology_integrities_by_id = {
    METHODOLOGY_FIXTURE["id"]: METHODOLOGY_FIXTURE_INTEGRITY,
}


def reputation_methodology_errors(signal):
    errors = []
    methodology_id = signal.get("mtd")
    methodology = methodologies_by_id.get(methodology_id)
    methodology_integrity = methodology_integrities_by_id.get(methodology_id)
    if methodology is None or methodology_integrity is None:
        return [f"methodology {methodology_id!r} is unavailable"]
    if signal.get("mtd#integrity") != methodology_integrity:
        errors.append("mtd#integrity does not match methodology bytes")
    value = signal.get("scr")
    if isinstance(value, (int, float)) and not 0 <= value <= 1:
        errors.append("scr is outside the normalized range [0, 1]")
    return errors


def validate_registered_reputation_signals(instance, label):
    for signal in instance.get("signals", []):
        if (
            isinstance(signal, dict)
            and signal.get("cat") == "rep"
            and signal.get("typ") in REGISTERED_REPUTATION_TYPES
        ):
            for error in reputation_methodology_errors(signal):
                fail(f"[reputation] {label}: {error}")


if reputation_fixture is not None:
    if reputation_fixture.get("mtd#integrity") != METHODOLOGY_FIXTURE_INTEGRITY:
        fail("[reputation] fixture integrity is not derived from methodology test-vector bytes")
    if reputation_methodology_errors(reputation_fixture):
        fail("[reputation] valid methodology binding was rejected")
    invalid_reputation = dict(reputation_fixture)
    invalid_reputation["mtd#integrity"] = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    if not reputation_methodology_errors(invalid_reputation):
        fail("[reputation] invalid methodology integrity was accepted")
    invalid_reputation = dict(reputation_fixture, scr=1.01)
    if not reputation_methodology_errors(invalid_reputation):
        fail("[reputation] out-of-range score was accepted")
for field, value in (("minimum", -1), ("maximum", 100), ("direction", "lower-better")):
    invalid_methodology = copy.deepcopy(METHODOLOGY_FIXTURE)
    invalid_methodology["score"][field] = value
    if not methodology_semantic_errors(invalid_methodology):
        fail(f"[reputation-methodology] invalid normalized score {field} was accepted")
    if not list(Draft202012Validator(REPUTATION_METHOD).iter_errors(invalid_methodology)):
        fail(f"[reputation-methodology] schema accepted invalid normalized score {field}")


# ---- 2. examples in the docs validate against the right schema ------------
FENCE = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)


def parse_block(block):
    for cand in (block, "{" + block + "}"):
        try:
            return json.loads(cand)
        except Exception:  # noqa: BLE001
            continue
    return None


def classify_and_validate(obj, label):
    if not isinstance(obj, dict):
        return
    if "attestationType" in obj:
        validate(obj, HSM, label + " (hsm-attestation)")
    elif "activeCredentials" in obj:
        validate(obj, TA_STATUS, label + " (ta-status)")
    elif "sd_hash" in obj:
        validate(obj, KB, label + " (kb-jwt)")
    elif "capabilities" in obj or "securitySchemes" in obj:
        validate(obj, A2A, label + " (a2a)")
    elif "claims" in obj and "vct" in obj:
        validate(obj, TM, label + " (type-metadata)")
    elif "iss" in obj and "vct" in obj and "signals" in obj:
        validate(obj, CRED, label + " (credential)")
        for error in credential_identity_errors(obj):
            fail(f"[example] {label} (credential identity): {error}")
        validate_registered_reputation_signals(obj, label)
    elif "signals" in obj and isinstance(obj["signals"], list):
        validate(obj, SIGNALS_SUB, label + " (signals-fragment)")
        validate_registered_reputation_signals(obj, label)
    elif "trustedAuthorities" in obj:
        validate(obj, MCP, label + " (mcp-capability)")
    # anything else (cnf snippet, status snippet, config) is not classifiable; skip


# ADRs are point-in-time records and may show superseded field names or
# illustrative pseudo-JSON, so their examples are not validated against the
# current schema. Token and cross-reference checks still cover them.
doc_dirs = [ARCH, ROOT / "concept"]
doc_files = [ROOT / "README.md"]
for d in doc_dirs:
    doc_files.extend(sorted(d.glob("*.md")))

for doc in doc_files:
    text = doc.read_text()
    for i, m in enumerate(FENCE.finditer(text)):
        obj = parse_block(m.group(1))
        if obj is None:
            continue
        classify_and_validate(obj, f"{doc.relative_to(ROOT)} block#{i+1}")


# ---- 3. type metadata, schemas, inheritance, and integrity ----------------
BASE_VCT = "https://tsaiprotocol.org/credential/tsai/1"
BASE_SCHEMA_ID = "https://tsaiprotocol.org/schemas/tsai-credential/1.json"


def refs_in(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                yield child
            yield from refs_in(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs_in(child)


def json_pointer(document, fragment):
    if fragment in {"", "#"}:
        return document
    if not fragment.startswith("#/"):
        raise ValueError(f"unsupported JSON Reference fragment: {fragment}")
    current = document
    for token in fragment[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def inline_local_refs(value, current_schema_id, stack=()):
    """Resolve references from the already loaded local schema registry only."""
    if isinstance(value, dict):
        if "$ref" in value:
            ref = value["$ref"]
            uri, marker, suffix = ref.partition("#")
            target_id = uri or current_schema_id
            target_schema = schemas_by_id.get(target_id)
            if target_schema is None:
                raise ValueError(f"schema reference is not local: {ref}")
            fragment = "#" + suffix if marker else ""
            key = (target_id, fragment)
            if key in stack:
                raise ValueError(f"circular schema reference: {ref}")
            target = copy.deepcopy(json_pointer(target_schema, fragment))
            resolved = inline_local_refs(target, target_id, stack + (key,))
            siblings = {key_: child for key_, child in value.items() if key_ != "$ref"}
            if siblings:
                return {
                    "allOf": [
                        resolved,
                        inline_local_refs(siblings, current_schema_id, stack),
                    ]
                }
            return resolved
        return {
            key: inline_local_refs(child, current_schema_id, stack)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [inline_local_refs(child, current_schema_id, stack) for child in value]
    return value


def selector_matches(parent, child):
    if parent.get("cat") != child.get("cat"):
        return False
    return "typ" not in parent or parent.get("typ") == child.get("typ")


def required_signal_selectors(value):
    selectors = set()
    if isinstance(value, dict):
        contained = value.get("contains")
        if isinstance(contained, dict):
            props = contained.get("properties", {})
            cat = props.get("cat", {}).get("const") if isinstance(props.get("cat"), dict) else None
            typ = props.get("typ", {}).get("const") if isinstance(props.get("typ"), dict) else None
            if cat is not None and typ is not None:
                selectors.add((cat, typ))
        for child in value.values():
            selectors.update(required_signal_selectors(child))
    elif isinstance(value, list):
        for child in value:
            selectors.update(required_signal_selectors(child))
    return selectors


def signal_sd_errors(parent_entries, child_entries):
    errors = []
    for entry in child_entries:
        child_selector = entry.get("signal")
        if not child_selector:
            continue
        for parent_entry in parent_entries:
            parent_selector = parent_entry.get("signal")
            if not parent_selector or not selector_matches(parent_selector, child_selector):
                continue
            parent_sd = parent_entry.get("sd", "allowed")
            child_sd = entry.get("sd", "allowed")
            if parent_sd in {"always", "never"} and child_sd != parent_sd:
                errors.append(child_selector)
    return errors


def exact_signal_selectors(value):
    selectors = set()
    if isinstance(value, dict):
        props = value.get("properties", {})
        if isinstance(props, dict):
            cat = props.get("cat", {}).get("const") if isinstance(props.get("cat"), dict) else None
            typ = props.get("typ", {}).get("const") if isinstance(props.get("typ"), dict) else None
            if cat is not None and typ is not None:
                selectors.add((cat, typ))
        for child in value.values():
            selectors.update(exact_signal_selectors(child))
    elif isinstance(value, list):
        for child in value:
            selectors.update(exact_signal_selectors(child))
    return selectors


def chain_error(start_vct, registry, base_vct):
    seen = set()
    cursor = start_vct
    while cursor in registry:
        if cursor in seen:
            return f"circular extends chain at {cursor}"
        seen.add(cursor)
        cursor = registry[cursor].get("extends")
        if cursor is None:
            if base_vct not in seen:
                return f"chain for {start_vct} is not rooted in canonical TSAI vct"
            return None
    return f"parent {cursor!r} is unavailable"


tm_dir = ARCH / "type-metadata"
tm_paths = sorted(tm_dir.glob("*.json"))
metadata_by_vct = {}
metadata_paths_by_vct = {}
for tm_path in tm_paths:
    tm = load_json(tm_path)
    validate(tm, TM, f"type-metadata/{tm_path.name}")
    vct = tm.get("vct")
    if vct in metadata_by_vct:
        fail(f"[type-metadata] duplicate vct {vct}")
    metadata_by_vct[vct] = tm
    metadata_paths_by_vct[vct] = tm_path

if BASE_VCT not in metadata_by_vct:
    fail("[type-metadata] canonical TSAI metadata is missing")

base_claims_by_path = {
    tuple(claim.get("path", [])): claim
    for claim in metadata_by_vct[BASE_VCT].get("claims", [])
    if claim.get("path")
}
sub_claim_metadata = base_claims_by_path.get(("sub",))
if not sub_claim_metadata:
    fail("[type-metadata] canonical TSAI metadata is missing the sub claim control")
elif sub_claim_metadata.get("mandatory") is not True or sub_claim_metadata.get("sd") != "never":
    fail("[type-metadata] canonical TSAI sub must be mandatory and sd never")
if ("aka_vcts",) in base_claims_by_path:
    fail("[type-metadata] canonical TSAI metadata must not define an aka_vcts claim control")

for vct, tm in metadata_by_vct.items():
    tm_path = metadata_paths_by_vct[vct]
    tsai_schema_uri = tm.get("tsai_schema_uri")
    schema_path = schema_paths_by_id.get(tsai_schema_uri)
    if schema_path is None:
        fail(f"[type-metadata] {tm_path.name}: tsai_schema_uri {tsai_schema_uri!r} is not a local schema $id")
    elif tm.get("tsai_schema_uri#integrity") != sri(schema_path):
        fail(f"[type-metadata] {tm_path.name}: tsai_schema_uri#integrity does not match {schema_path.name}")

    schema = schemas_by_id.get(tsai_schema_uri, {})
    controls = {
        (entry["signal"].get("cat"), entry["signal"].get("typ")): entry
        for entry in tm.get("tsai_signal_metadata", [])
        if entry.get("signal", {}).get("typ") is not None
    }
    category_controls = {
        entry["signal"].get("cat"): entry
        for entry in tm.get("tsai_signal_metadata", [])
        if entry.get("signal", {}).get("typ") is None
    }
    for selector in required_signal_selectors(schema):
        control = controls.get(selector) or category_controls.get(selector[0])
        if control is None:
            fail(f"[type-metadata] {tm_path.name}: schema-required signal {selector} has no effective tsai_signal_metadata control")
        elif control.get("sd") != "never":
            fail(f"[type-metadata] {tm_path.name}: schema-required signal {selector} must be sd never")

    for claim in tm.get("claims", []):
        if "path" not in claim:
            fail(f"[type-metadata] {tm_path.name}: standard claims entry has no path")
        if claim.get("mandatory") is True and claim.get("sd") != "never":
            fail(f"[type-metadata] {tm_path.name}: mandatory standard claim must set sd to never")

    parent_vct = tm.get("extends")
    if parent_vct:
        parent_path = metadata_paths_by_vct.get(parent_vct)
        if parent_path is None:
            fail(f"[type-metadata] {tm_path.name}: parent {parent_vct!r} is unavailable")
            continue
        if tm.get("extends#integrity") != sri(parent_path):
            fail(f"[type-metadata] {tm_path.name}: extends#integrity does not match {parent_path.name}")
        parent = metadata_by_vct[parent_vct]
        parent_tsai_schema_uri = parent.get("tsai_schema_uri")
        if parent_tsai_schema_uri not in set(refs_in(schema)):
            fail(f"[type-metadata] {tm_path.name}: derived schema does not $ref parent schema {parent_tsai_schema_uri}")
        direct_parent = any(
            item == {"$ref": parent_tsai_schema_uri}
            for item in schema.get("allOf", [])
            if isinstance(item, dict)
        )
        if not direct_parent:
            fail(f"[type-metadata] {tm_path.name}: parent schema is not a direct top-level allOf member")

        child_exact_controls = {
            (entry["signal"].get("cat"), entry["signal"].get("typ"))
            for entry in tm.get("tsai_signal_metadata", [])
            if entry.get("signal", {}).get("typ") is not None
        }
        for selector in exact_signal_selectors(schema):
            if selector not in child_exact_controls:
                fail(f"[type-metadata] {tm_path.name}: schema-defined custom signal {selector} has no exact tsai_signal_metadata entry")

        parent_claims_by_path = {
            tuple(claim.get("path", [])): claim
            for claim in parent.get("claims", [])
            if claim.get("path")
        }
        for claim in tm.get("claims", []):
            inherited = parent_claims_by_path.get(tuple(claim.get("path", [])))
            if not inherited:
                continue
            if inherited.get("mandatory") is True and claim.get("mandatory") is False:
                fail(f"[type-metadata] {tm_path.name}: child weakens mandatory for path {claim['path']}")
            parent_sd = inherited.get("sd", "allowed")
            child_sd = claim.get("sd", "allowed")
            if parent_sd in {"always", "never"} and child_sd != parent_sd:
                fail(f"[type-metadata] {tm_path.name}: child weakens sd for path {claim['path']}")

        parent_entries = parent.get("tsai_signal_metadata", [])
        for selector in signal_sd_errors(parent_entries, tm.get("tsai_signal_metadata", [])):
            fail(f"[type-metadata] {tm_path.name}: child weakens sd for {selector}")

        error = chain_error(vct, metadata_by_vct, BASE_VCT)
        if error:
            fail(f"[type-metadata] {tm_path.name}: {error}")

# Exercise the inheritance helpers independently of the one concrete fixture.
_synthetic_chain = {
    BASE_VCT: {},
    "urn:example:middle": {"extends": BASE_VCT},
    "urn:example:leaf": {"extends": "urn:example:middle"},
}
if chain_error("urn:example:leaf", _synthetic_chain, BASE_VCT):
    fail("[type-metadata] three-level extends chain was rejected")
_synthetic_cycle = {
    BASE_VCT: {},
    "urn:example:a": {"extends": "urn:example:b"},
    "urn:example:b": {"extends": "urn:example:a"},
}
if not chain_error("urn:example:a", _synthetic_cycle, BASE_VCT):
    fail("[type-metadata] circular extends self-test was accepted")
_parent_sd = [{"signal": {"cat": "rep"}, "sd": "never"}]
_child_sd = [{"signal": {"cat": "rep", "typ": "risk"}, "sd": "allowed"}]
if not signal_sd_errors(_parent_sd, _child_sd):
    fail("[type-metadata] inherited sd weakening self-test was accepted")


# Validate the concrete derived credential against both its base and derived
# schemas, resolving the immutable base schema from the local registry.
derived_vector_path = ARCH / "test-vectors" / "derived-vct-credential.json"
if derived_vector_path.exists():
    derived_vector = load_json(derived_vector_path)
    for error in credential_identity_errors(derived_vector):
        fail(f"[derived-vector] identity: {error}")
    derived_vct = derived_vector.get("vct")
    derived_tm = metadata_by_vct.get(derived_vct)
    if derived_tm is None:
        fail(f"[derived-vector] no Type Metadata for {derived_vct}")
    else:
        derived_schema = schemas_by_id.get(derived_tm.get("tsai_schema_uri"))
        if derived_schema is None:
            fail("[derived-vector] derived schema is unavailable")
        else:
            try:
                resolved_derived_schema = inline_local_refs(
                    derived_schema,
                    derived_schema["$id"],
                )
            except (KeyError, TypeError, ValueError) as error:
                fail(f"[derived-vector] schema reference resolution failed: {error}")
                resolved_derived_schema = {"not": {}}
            errs = sorted(
                Draft202012Validator(resolved_derived_schema, format_checker=FORMAT_CHECKER).iter_errors(derived_vector),
                key=str,
            )
            for error in errs:
                loc = "/".join(str(part) for part in error.absolute_path) or "(root)"
                fail(f"[derived-vector] {loc}: {error.message}")
        if derived_vector.get("vct#integrity") != sri(metadata_paths_by_vct[derived_vct]):
            fail("[derived-vector] vct#integrity does not match derived Type Metadata")
        if BASE_VCT not in derived_vector.get("aka_vcts", []):
            fail("[derived-vector] aka_vcts does not include canonical TSAI vct")
        if derived_vct in derived_vector.get("aka_vcts", []):
            fail("[derived-vector] aka_vcts contains the primary vct")
        exact_selectors = {
            (entry["signal"].get("cat"), entry["signal"].get("typ"))
            for entry in derived_tm.get("tsai_signal_metadata", [])
            if entry.get("signal", {}).get("typ") is not None
        }
        vector_selectors = {
            (signal.get("cat"), signal.get("typ"))
            for signal in derived_vector.get("signals", [])
            if isinstance(signal, dict)
        }
        if not exact_selectors.issubset(vector_selectors):
            fail("[derived-vector] not every exact derived signal selector is represented")

        def must_reject(instance, validator, label):
            if not list(validator.iter_errors(instance)):
                fail(f"[derived-vector] negative case was accepted: {label}")

        derived_validator = Draft202012Validator(resolved_derived_schema, format_checker=FORMAT_CHECKER)

        rotated = copy.deepcopy(derived_vector)
        rotated_key = ec.derive_private_key(2, ec.SECP256R1()).public_key().public_numbers()
        rotated["cnf"]["jwk"]["x"] = base64.urlsafe_b64encode(
            rotated_key.x.to_bytes(32, "big")
        ).rstrip(b"=").decode()
        rotated["cnf"]["jwk"]["y"] = base64.urlsafe_b64encode(
            rotated_key.y.to_bytes(32, "big")
        ).rstrip(b"=").decode()
        if list(derived_validator.iter_errors(rotated)) or credential_identity_errors(rotated):
            fail("[derived-vector] valid key rotation with stable sub was rejected")
        if rotated["sub"] != derived_vector["sub"] or rotated["cnf"] == derived_vector["cnf"]:
            fail("[derived-vector] rotation did not preserve sub and change cnf")

        bad = copy.deepcopy(derived_vector)
        bad["signals"][-1]["level"] = "unknown"
        must_reject(bad, derived_validator, "custom enum")

        bad = copy.deepcopy(derived_vector)
        bad.pop("aka_vcts", None)
        must_reject(bad, derived_validator, "missing aka_vcts")

        bad = copy.deepcopy(derived_vector)
        bad.pop("sub", None)
        must_reject(bad, derived_validator, "missing sub")

        bad = copy.deepcopy(derived_vector)
        bad["sub"] = "https://other.example/agents/shopper-v3"
        if not credential_identity_errors(bad):
            fail("[derived-vector] sub/dct mismatch was accepted")

        bad = copy.deepcopy(derived_vector)
        for signal in bad["signals"]:
            if signal.get("cat") == "idn" and signal.get("typ") == "dct":
                signal["asof"] = bad["iat"] - DOMAIN_FRESHNESS_SECONDS - 1
        if not credential_identity_errors(bad):
            fail("[derived-vector] stale dct was accepted")

        skewed = copy.deepcopy(derived_vector)
        for signal in skewed["signals"]:
            if signal.get("cat") == "idn" and signal.get("typ") == "dct":
                signal["asof"] = skewed["iat"] + CLOCK_SKEW_SECONDS
        if credential_identity_errors(skewed):
            fail("[derived-vector] allowed dct clock skew was rejected")

        bad = copy.deepcopy(derived_vector)
        for signal in bad["signals"]:
            if signal.get("cat") == "idn" and signal.get("typ") == "dct":
                signal["asof"] = bad["iat"] + CLOCK_SKEW_SECONDS + 1
        if not credential_identity_errors(bad):
            fail("[derived-vector] excessive dct clock skew was accepted")

        bad = copy.deepcopy(derived_vector)
        bad["aka_vcts"].append(bad["vct"])
        must_reject(bad, derived_validator, "aka_vcts contains primary vct")

        bad = copy.deepcopy(derived_vector)
        bad["signals"].append({
            "cat": "rep", "typ": "undeclared", "level": "low", "asof": 1781800000
        })
        must_reject(bad, derived_validator, "undeclared custom signal")

        bad = copy.deepcopy(derived_vector)
        bad["vct"] = BASE_VCT
        bad.pop("aka_vcts", None)
        must_reject(
            bad,
            Draft202012Validator(schemas_by_id[BASE_SCHEMA_ID], format_checker=FORMAT_CHECKER),
            "custom signal under canonical vct",
        )
else:
    fail("[derived-vector] derived-vct-credential.json is missing")


# ---- 4. compact-JWS TA publication vectors -------------------------------
def b64url_decode(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hsm_lifetime_valid(payload):
    return (
        payload.get("attestationType") != "self-attestation"
        or payload.get("exp", 0) - payload.get("iat", 0) <= 30 * 24 * 60 * 60
    )


def verify_ta_jws_vector(filename, expected_typ, payload_schema, max_lifetime=None):
    path = ARCH / "test-vectors" / filename
    if not path.exists():
        fail(f"[ta-jws] missing {filename}")
        return
    vector = load_json(path)
    parts = vector.get("compactJws", "").split(".")
    if len(parts) != 3:
        fail(f"[ta-jws] {filename}: compact JWS must have three segments")
        return
    try:
        header = json.loads(b64url_decode(parts[0]))
        payload = json.loads(b64url_decode(parts[1]))
        signature = b64url_decode(parts[2])
    except (ValueError, json.JSONDecodeError) as error:
        fail(f"[ta-jws] {filename}: cannot decode compact JWS: {error}")
        return
    if header != vector.get("protectedHeader"):
        fail(f"[ta-jws] {filename}: protected header does not match vector")
    if payload != vector.get("payload"):
        fail(f"[ta-jws] {filename}: payload does not match vector")
    if payload.get("iss") != vector.get("trustedIssuer"):
        fail(f"[ta-jws] {filename}: payload issuer does not equal trusted issuer")
    if header.get("alg") != "ES256" or header.get("typ") != expected_typ or not header.get("kid"):
        fail(f"[ta-jws] {filename}: incorrect protected header")
    validate(payload, payload_schema, f"test-vectors/{filename} (payload)")
    now = vector.get("now")
    if not isinstance(now, int) or not (payload.get("iat", now + 1) <= now < payload.get("exp", now)):
        fail(f"[ta-jws] {filename}: vector time is outside iat/exp")
    if payload.get("exp", 0) <= payload.get("iat", 0):
        fail(f"[ta-jws] {filename}: exp must be after iat")
    if max_lifetime is not None and payload.get("exp", 0) - payload.get("iat", 0) > max_lifetime:
        fail(f"[ta-jws] {filename}: lifetime exceeds {max_lifetime} seconds")
    if expected_typ == "tsai-ta-hsm-attestation+jwt" and not hsm_lifetime_valid(payload):
        fail(f"[ta-jws] {filename}: self-attestation lifetime exceeds 30 days")
    jwk = vector.get("publicJwk", {})
    if jwk.get("kid") != header.get("kid") or jwk.get("kty") != "EC" or jwk.get("crv") != "P-256":
        fail(f"[ta-jws] {filename}: key does not match protected header")
        return
    try:
        x = int.from_bytes(b64url_decode(jwk["x"]), "big")
        y = int.from_bytes(b64url_decode(jwk["y"]), "big")
        public_key = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()
        if len(signature) != 64:
            raise ValueError("ES256 signature is not 64 octets")
        r = int.from_bytes(signature[:32], "big")
        s = int.from_bytes(signature[32:], "big")
        public_key.verify(
            encode_dss_signature(r, s),
            f"{parts[0]}.{parts[1]}".encode(),
            ec.ECDSA(hashes.SHA256()),
        )
    except (KeyError, ValueError, InvalidSignature) as error:
        fail(f"[ta-jws] {filename}: signature verification failed: {error}")
        return
    tampered_signature = bytearray(signature)
    tampered_signature[-1] ^= 1
    try:
        public_key.verify(
            encode_dss_signature(
                int.from_bytes(tampered_signature[:32], "big"),
                int.from_bytes(tampered_signature[32:], "big"),
            ),
            f"{parts[0]}.{parts[1]}".encode(),
            ec.ECDSA(hashes.SHA256()),
        )
        fail(f"[ta-jws] {filename}: tampered signature was accepted")
    except InvalidSignature:
        pass


if not hsm_lifetime_valid({"attestationType": "self-attestation", "iat": 0, "exp": 30 * 24 * 60 * 60}):
    fail("[ta-jws] 30-day self-attestation lifetime was rejected")
if hsm_lifetime_valid({"attestationType": "self-attestation", "iat": 0, "exp": 30 * 24 * 60 * 60 + 1}):
    fail("[ta-jws] overlong self-attestation lifetime was accepted")

_report_url_on_independent_audit = dict(
    load_json(ARCH / "test-vectors" / "ta-hsm-attestation-jws.json")["payload"],
    reportUrl="https://ta.example/reports/hsm.pdf?access=requested",
)
if HSM and not Draft202012Validator(HSM, format_checker=FORMAT_CHECKER).is_valid(
    _report_url_on_independent_audit
):
    fail("[ta-jws] reportUrl was rejected on independent-audit")

_report_url_on_self_attestation = {
    "iss": "https://ta.example",
    "iat": 0,
    "exp": 1,
    "version": "1.0",
    "attestationType": "self-attestation",
    "auditDate": "2026-01-01",
    "scope": "Signing-key storage",
    "reportUrl": "https://ta.example/report",
}
if HSM and Draft202012Validator(HSM, format_checker=FORMAT_CHECKER).is_valid(
    _report_url_on_self_attestation
):
    fail("[ta-jws] reportUrl was accepted on self-attestation")

verify_ta_jws_vector("ta-status-jws.json", "tsai-ta-status+jwt", TA_STATUS, 86400)
verify_ta_jws_vector("ta-hsm-attestation-jws.json", "tsai-ta-hsm-attestation+jwt", HSM)


# ---- 5. key-binding-JWT test vectors: schema + freshness rule -------------
def freshness_verdict(iat, now):
    # Section 3.4: reject if iat > now + 30 or iat < now - 90
    if iat > now + 30 or iat < now - 90:
        return "STALE_PRESENTATION"
    return "OK"


for vec in sorted((ARCH / "test-vectors").glob("kb-jwt-*.json")):
    v = load_json(vec)
    validate(v["kb"], KB, f"test-vectors/{vec.name} (kb-jwt)")
    if v.get("header") != {"alg": "ES256", "typ": "kb+jwt"}:
        fail(f"[vector] {vec.name}: header must be exactly alg ES256 and typ kb+jwt")
    got = freshness_verdict(v["kb"]["iat"], v["now"])
    if got != v["expect"]:
        fail(f"[vector] {vec.name}: freshness rule gave {got}, expected {v['expect']}")


# ---- 5. no leaked review-artefact tokens ----------------------------------
TOKEN = re.compile(r"(?<![A-Za-z0-9.])[A-L]\.\d{1,2}(?!\d)")
for d in [ARCH, ROOT / "decisions"]:
    for md in sorted(d.glob("*.md")):
        for n, line in enumerate(md.read_text().splitlines(), 1):
            for m in TOKEN.finditer(line):
                fail(f"[token] {md.relative_to(ROOT)}:{n}: leaked review token '{m.group(0)}'")


# ---- 6. OpenAPI parses and declares servers -------------------------------
for oa in sorted((ARCH / "openapi").glob("*.yaml")):
    try:
        doc = yaml.safe_load(oa.read_text())
    except Exception as e:  # noqa: BLE001
        fail(f"[openapi] {oa.name} does not parse: {e}")
        continue
    if not doc.get("servers"):
        fail(f"[openapi] {oa.name} declares no servers block")
    ta_metadata = doc.get("components", {}).get("schemas", {}).get("TAMetadata", {})
    required = set(ta_metadata.get("required", []))
    properties = ta_metadata.get("properties", {})
    if "credentialTypes" not in required or "credentialTypes" not in properties:
        fail(f"[openapi] {oa.name} TAMetadata must require credentialTypes")
    if "schemaUri" in properties or "schema_uri" in properties:
        fail(f"[openapi] {oa.name} TAMetadata duplicates schema location from Type Metadata")

    paths = doc.get("paths", {})
    challenge_path = paths.get("/challenges", {})
    challenge_post = challenge_path.get("post", {})
    if "get" in challenge_path or not challenge_post:
        fail(f"[openapi] {oa.name} challenges must use POST, not GET")
    if {"operatorAuth": []} not in challenge_post.get("security", []):
        fail(f"[openapi] {oa.name} challenge POST must require operatorAuth")
    component_schemas = doc.get("components", {}).get("schemas", {})
    challenge_request = component_schemas.get("ChallengeRequest", {})
    if set(challenge_request.get("required", [])) != {"kid"} or challenge_request.get("additionalProperties") is not False:
        fail(f"[openapi] {oa.name} ChallengeRequest must require only registered kid and reject unknown fields")
    cache_control = (
        challenge_post.get("responses", {})
        .get("201", {})
        .get("headers", {})
        .get("Cache-Control", {})
        .get("schema", {})
        .get("const")
    )
    if cache_control != "no-store":
        fail(f"[openapi] {oa.name} challenge response must require Cache-Control no-store")
    proof = component_schemas.get("ProofOfControl", {})
    proof_required = set(proof.get("required", []))
    proof_properties = proof.get("properties", {})
    if proof_required != {"kid", "challenge", "signature"} or "jwk" in proof_properties:
        fail(f"[openapi] {oa.name} ProofOfControl must use kid without raw jwk")
    issue_request = component_schemas.get("IssueRequest", {})
    if (
        set(issue_request.get("required", [])) != {"proofOfControl"}
        or "sub" in issue_request.get("properties", {})
        or issue_request.get("additionalProperties") is not False
    ):
        fail(f"[openapi] {oa.name} IssueRequest must require proof only and must not accept sub or unknown identity fields")

    for path_name in ("/.well-known/tsai-ta-status", "/.well-known/tsai-ta-hsm-attestation"):
        media = (
            doc.get("paths", {})
            .get(path_name, {})
            .get("get", {})
            .get("responses", {})
            .get("200", {})
            .get("content", {})
        )
        if "application/jwt" not in media:
            fail(f"[openapi] {oa.name} {path_name} must return application/jwt")


# ---- 7. cross-reference resolution (warning only) -------------------------
HEADING = re.compile(r"^#+\s+(\d+(?:\.\d+)+)\b")
heading_numbers = set()
for md in sorted(ARCH.glob("*.md")):
    for line in md.read_text().splitlines():
        m = HEADING.match(line)
        if m:
            heading_numbers.add(m.group(1))

REF = re.compile(r"(?:Section\s+|§)(\d+(?:\.\d+)+)")
STD = re.compile(r"RFC|SD-JWT|draft|NIST|VC\s")
for md in sorted(ARCH.glob("*.md")) + sorted((ROOT / "concept").glob("*.md")):
    for n, line in enumerate(md.read_text().splitlines(), 1):
        # skip reference-list entries citing external standards
        if line.lstrip().startswith("-") and STD.search(line):
            continue
        for m in REF.finditer(line):
            # skip a reference immediately preceded by a standard name
            if STD.search(line[max(0, m.start() - 12):m.start()]):
                continue
            num = m.group(1)
            if num not in heading_numbers:
                warn(f"[xref] {md.relative_to(ROOT)}:{n}: Section {num} has no matching heading")


# ---- report ----------------------------------------------------------------
print(f"schemas checked: {len(schemas)}")
print(f"doc files scanned: {len(doc_files)}")
if warnings:
    print(f"\nwarnings ({len(warnings)}):")
    for w in warnings:
        print("  " + w)
if failures:
    print(f"\nFAILURES ({len(failures)}):")
    for f_ in failures:
        print("  " + f_)
    sys.exit(1)
print("\nOK: all hard checks passed")
