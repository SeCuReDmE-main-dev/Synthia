# Book II Final Evidence - Synthia

## Scope

This public-safe register maps the software contracts used by *Fractal
NeutroGeometry: Mapping the Invisible Infinite*, Chapters 8-14. It records
software evidence only. The manuscript and private research corpus are not
part of this repository.

## Non-negotiable boundaries

```text
maximum_proof_state = P2_internal_repeatability
physical_model_validated = false
simulation != detection
candidate != proof
dL_lex != dF
PenroseRulePacket != physical_substrate
```

Synthia owns lexical classification, source-object admission, partition,
suspension, and refusal. It does not calculate downstream `D_f`, `D_f_hat`,
`dF`, or `i_fractal_candidate`.

## Chapter map

| Chapter | Synthia surface | Public status |
| --- | --- | --- |
| 8 | first-run permission gate | documented software contract |
| 9 | source-choice and T2K-like framing gate | documented; not T2K reproduction |
| 10 | chamber/container contract | documented contract only |
| 11 | two-path passage packet | preserved lexical evidence |
| 12 | ten-carrier intensive-validation profile | `P2_internal_repeatability` ceiling |
| 13 | four-run distributed-validation profile | 4 x 67 worker contracts admitted through Synthia |
| 14 | source and threshold admission gate | ready for bounded FNP matrix calculation |

## Reproduction commands

```powershell
python -m synthia_core.cli neutrino guardrail-check --input tests/fixtures/neutrino_chapter12_valid_event.json --json
python -m synthia_core.cli neutrino guardrail-check --input tests/fixtures/neutrino_chapter13_valid_event.json --json
python -m synthia_core.cli neutrino chapter14-threshold-check --input tests/fixtures/neutrino_chapter14_valid_event.json --json
python -m pytest -q
```

## Frozen evidence summary

| Chapter | Result | Evidence SHA-256 |
| --- | --- | --- |
| 12 | 128/128 E2B tasks, 32 workers; deterministic and seeded replay passed | `b719a00baeb2588be9ec0f15b69f704be9509fb2d7c812931ea2a595f03549d2` |
| 13 | 4 complete runs x 67 sandbox lifecycles; 1072 task results; expected outcomes matched | `ac2bf96322110a89d91eaf083a70cd191b7c17923e70a15f15d54b9e6a127428` |
| 14 | 245 Synthia tests passed at commit `4baed83189ee11bd2bcee92f2f36fb983315fe2f` | `a58583b16fd56fd60fcabd500cd4d47c42a2ed8e5eb3bdeedd9c360d1cc77876` |

The hashes identify private audit reports retained by the project. They allow
integrity comparison without publishing private conversations, cloud IDs, or
the full manuscript.

## Chapter 14 decision boundary

The chapter-14 gate requires a public-safe source object, exactly ten declared
carriers, bounded transition fields, and explicit false values for physical
validation, substrate validation, and real-detection claims. A valid packet is
admitted only for FNP-QNN threshold calculation. Invalid scientific upgrades
are rejected; incomplete mathematical context is suspended.

## Interim release note

The public websites are intentionally unchanged during this release. A website
sweep is planned separately. Until then, this file and the repository README
are the maintained public description of the Book II software evidence.
