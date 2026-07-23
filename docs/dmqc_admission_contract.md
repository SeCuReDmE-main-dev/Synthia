# DMQC Admission Contract

Status: internal research-software contract  
Input schema: `synthia.dmqc_admission_input.v1`  
Output schema: `synthia.dmqc_admission.v1`  
Policy: `synthia.dmqc_policy.v1`

## Purpose

The DMQC admission gate validates provenance, metadata, units, uncertainty,
contradictions, and requested claims before any downstream FNP-QNN work.
DMQC means **Data Mining of Quantum Calculations** in this benchmark.

Synthia is a traceability instrument under human review. It is not a materials
authority, a DFT validator, a crystal-growth experiment, or a quantum backend.

The gate preserves the lexical hierarchy:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

It never computes or returns physical or fractal descriptor keys.

## Input

The input must be a JSON object with:

- `schema_version = synthia.dmqc_admission_input.v1`
- `case_id`
- `source_type` and `domain`
- `method.name` and `method.category`
- `software.name` and `software.version`
- `input_parameters`
- `raw_result_reference.uri` and a 64-character SHA-256
- `provenance_reference.entity_id`, `activity_id`, and `agent_id`
- declared `units`
- `timestamp`
- `uncertainty_model.type` and `declared = true`
- `convergence_or_quality_flags`
- `licence_and_access`
- `requested_claims`
- `declared_contradictions`

The v1 benchmark accepts these units:

| Field | Unit |
|---|---|
| `formation_energy` | `eV/atom` |
| `growth_rate` | `normalized_benchmark_unit` |
| `branch_drift` | `dimensionless` |
| `surface_roughness` | `dimensionless` |
| `defect_density` | `dimensionless` |

An unsupported or dimensionally impossible unit is a hard rejection. A later
schema may add explicit conversion declarations without weakening this rule.

## Decision states

```text
received
  |
  v
validated
  |
  +-- accepted  -> normalized admitted -> route_to_fnp
  +-- suspended -> normalized suspended -> hold_for_review
  +-- rejected  -> normalized rejected -> block_fnp
```

Hard failures always reject. Missing but recoverable evidence suspends.
Contradictions increase indeterminacy and suspend without being re-labelled as
scientific falsity.

## Hard rejection codes

- `dmqc_invalid_input_schema`
- `dmqc_impossible_unit`
- `dmqc_simulation_claimed_as_experiment`
- `dmqc_validated_material_claim_without_evidence`
- `dmqc_quantum_hardware_claim_without_backend_evidence`
- `dmqc_fnp_output_in_synthia`
- `dmqc_raw_reference_hash_mismatch`

## Suspension codes

- `dmqc_missing_case_identity`
- `dmqc_missing_source_type`
- `dmqc_missing_method`
- `dmqc_missing_provenance`
- `dmqc_missing_software_version`
- `dmqc_missing_uncertainty_model`
- `dmqc_incomplete_quality_flags`
- `dmqc_missing_licence_or_access`
- `dmqc_recoverable_source_contradiction`
- `dmqc_missing_fractal_measurement_metadata`

## Evidence profile

The output exposes nine bounded experimental components:

| Component | Working meaning |
|---|---|
| `P` | minimal provenance completeness |
| `Q` | declared quality-flag completeness |
| `R` | replay metadata completeness |
| `U` | declared uncertainty load |
| `C` | contradiction load |
| `M` | recoverable metadata-gap load |
| `H` | hard-failure blocker |
| `V` | policy-violation blocker |
| `X` | requested-claim excess |

The pilot scores are:

```text
T = 0.40 P + 0.30 Q + 0.30 R
I = max(U, C, M)
F = max(H, V, X)
```

These are versioned policy scores. They are not canonical neutrosophic
mathematics, physical observables, or proof of plithogenic advantage. A hard
failure is evaluated before the scores and cannot be averaged away.

## Output

The output contains:

- a versioned decision and stable reason-code order;
- `ready_for_fnp`;
- `P/Q/R/U/C/M/H/V/X`;
- experimental `T/I/F`;
- permitted and forbidden claims;
- evidence references;
- reproducibility status;
- the policy version;
- an explicit authority and physical-computation boundary.

The following keys are forbidden recursively in Synthia input and output:

```text
D_crystal
dC
i_crystal
D_f
D_f_hat
dF
i_fractal
i_fractal_candidate
```

Their names may appear only as string values in
`boundary.forbidden_output_fields`, never as computed fields.

## Deterministic replay

Canonical JSON uses:

- UTF-8;
- sorted keys;
- compact separators;
- finite JSON numbers only;
- no NaN or Infinity.

`canonical_sha256()` hashes this representation. Reordering JSON object keys
must not alter the decision or the replay hash.

## CLI

```powershell
python -m synthia_core.cli dmqc admission-check `
  --input tests/fixtures/dmqc_admission/admitted_complete.json `
  --json
```

Exit code `0` means the packet is accepted and ready for FNP. Suspended and
rejected packets are still printed as JSON and return a non-zero exit code.

## Claim boundary

This contract may support claims about schema validation, fail-closed handling,
reason-code traceability, deterministic replay, and cross-repository packet
integrity.

It does not support claims of validated DFT, material discovery, physical
crystal growth, experimental fractal measurement, quantum advantage, or
universal plithogenic superiority.
