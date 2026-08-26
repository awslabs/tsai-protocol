#!/usr/bin/env python3
# Copyright Amazon.com Inc. or its affiliates.
# SPDX-License-Identifier: Apache-2.0
"""
TSAI specification checker.

Mechanises the artefact-agreement checks from the review process feedback:

  1. every JSON schema is a valid Draft 2020-12 schema;
  2. every JSON example embedded in the docs validates against the right schema;
  3. the type-metadata instance validates against its schema;
  4. the key-binding-JWT test vectors are schema-valid and their freshness verdict
     matches the Section 3.4 rule;
  5. no review-artefact tokens ([A-L].n) leak into the repository;
  6. the OpenAPI parses and declares a servers block;
  7. (warning only) every "Section n.n" / "§n.n" cross-reference resolves to a heading.

Run from anywhere: it locates the repository root relative to this file.
Exit status is non-zero if any check other than the cross-reference warning fails.

Requires: jsonschema, pyyaml.
"""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
ARCH = ROOT / "architecture"
SCHEMAS = ARCH / "schemas"

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
for sf in schema_files:
    try:
        s = load_json(sf)
        Draft202012Validator.check_schema(s)
        schemas[sf.name] = s
    except Exception as e:  # noqa: BLE001
        fail(f"[schema] {sf.name} is not a valid Draft 2020-12 schema: {e}")

CRED = schemas.get("tsai-credential.schema.json")
KB = schemas.get("key-binding-jwt.schema.json")
TM = schemas.get("tsai-type-metadata.schema.json")
A2A = schemas.get("a2a-agent-card-tsai.schema.json")
MCP = schemas.get("mcp-capability-tsai.schema.json")
TA_STATUS = schemas.get("tsai-ta-status.schema.json")
HSM = schemas.get("tsai-ta-hsm-attestation.schema.json")

# a sub-schema over just the signals array, for the fragment examples
SIGNALS_SUB = None
if CRED:
    SIGNALS_SUB = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["signals"],
        "properties": {"signals": CRED["properties"]["signals"]},
    }


def validate(instance, schema, label):
    if schema is None:
        warn(f"[example] {label}: no schema loaded to validate against")
        return
    errs = sorted(Draft202012Validator(schema).iter_errors(instance), key=str)
    for e in errs:
        loc = "/".join(str(p) for p in e.absolute_path) or "(root)"
        fail(f"[example] {label}: {loc}: {e.message}")


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
    elif "reportTimestamp" in obj or "activeCredentials" in obj:
        validate(obj, TA_STATUS, label + " (ta-status)")
    elif "sd_hash" in obj:
        validate(obj, KB, label + " (kb-jwt)")
    elif "capabilities" in obj or "securitySchemes" in obj:
        validate(obj, A2A, label + " (a2a)")
    elif "claims" in obj and "vct" in obj:
        validate(obj, TM, label + " (type-metadata)")
    elif "iss" in obj and "vct" in obj and "signals" in obj:
        validate(obj, CRED, label + " (credential)")
    elif "signals" in obj and isinstance(obj["signals"], list):
        validate(obj, SIGNALS_SUB, label + " (signals-fragment)")
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


# ---- 3. type-metadata instance --------------------------------------------
tm_instance = ARCH / "type-metadata" / "tsai-1.json"
if tm_instance.exists():
    validate(load_json(tm_instance), TM, "type-metadata/tsai-1.json")
else:
    fail("[type-metadata] tsai-1.json is missing")


# ---- 4. key-binding-JWT test vectors: schema + freshness rule -------------
def freshness_verdict(iat, now):
    # Section 3.4: reject if iat > now + 30 or iat < now - 90
    if iat > now + 30 or iat < now - 90:
        return "STALE_PRESENTATION"
    return "OK"


for vec in sorted((ARCH / "test-vectors").glob("kb-jwt-*.json")):
    v = load_json(vec)
    validate(v["kb"], KB, f"test-vectors/{vec.name} (kb-jwt)")
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
