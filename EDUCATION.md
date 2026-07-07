# Educational Use

Synthia is an educational research codebase for context-preserving lexicon
intelligence, taxonomy memory, uncertainty-aware classification, and
human-review boundaries.

## Neutrino Lexical Gate

The neutrino lexical gate is a public-safe classroom/research surface for
checking whether a neutrino-like simulation event is phrased safely before a
downstream simulator can use it.

It returns:

- `LexPacket_neutrino`;
- `Adm_lex`;
- `dL_lex`;
- a `Decision` status;
- a `RefusalPacket` with machine-readable reason codes.

The gate is deliberately lexical. It does not compute FNP-QNN friction and does
not produce `D_f`, `dF`, or `i_fractal`.

For neutrino teaching examples, the gate can also return a `chapter3_profile`
with separated carriers:

- `I_flavor`: flavor weak-state language;
- `I_mass`: mass propagation-state language;
- `I_phase`: distance/energy phase-evolution context;
- `I_interaction`: `weak_CC` or `weak_NC`;
- `I_secondary`: secondary detector products;
- `I_detector`: indirect detector projection.

For chapter-4 style exercises, the gate can also return `chapter4_profile`.
This is still lexical, not physical proof. It contains:

- `P_neutrino` and the `lex_neutrino` taxonomy;
- `H_lex`, `G_lex`, `I_lexicon`, and `dL_lex` as lexical metrics;
- `ProtectionPacket_neutrino` and `SynthiaGuard_neutrino`;
- `allowed_payload` and `excluded_payload` when a recoverable metaphor must be
  partitioned before FNP-QNN.

For chapter-5 style exercises, the gate can also return
`chapter5_intake_profile`. This is an intake request only. It prepares an
`E_FNP_neutrino_request`, `C_FNP_request`, lexical `T/I/F` seed request, scale
context request, and carrier request policy so FNP-QNN can validate the next
step. Synthia does not compute or return `D_f`, `D_f_hat`, `dF`,
`i_fractal`, or `i_fractal_candidate`.

For chapter-6 style exercises, the gate can also return
`chapter6_vector_profile`. This assembles `I_neutrino_vec` with ten carriers:
`I_source`, `I_flavor`, `I_mass`, `I_mix`, `I_phase`, `I_medium`,
`I_interaction`, `I_secondary`, `I_detector`, and `I_uncertainty`. The vector
is a public-safe chamber object for lexical review. It is not `dL_lex`, not
downstream FNP friction, not a detector signature, and not proof of detection.

For chapter-7 style exercises, the gate can also return
`chapter7_transition_profile`. This keeps `I_neutrino := I_neutrino_vec` as the
primary definition, records the toy passage state, and exposes the Synthia
reading that can approve the packet for FNP. This profile is still lexical:
`dL_lex` is not `dF`, `I_lexicon` is not `i_fractal`, and Synthia does not
return `D_f`, `D_f_hat`, `dF`, `i_fractal`, or `i_fractal_candidate`.

For chapter-8 style exercises, the gate can also return
`chapter8_run_profile`. This turns the first run into an explicit status:
`admissible_under_guardrails`, `suspended`, or `rejected`.
`permission_to_continue` is not proof, `simulation` is not detection, and a
`suspended` or `rejected` run must not be converted into a numeric shortcut.
The profile is still lexical/admission-only and does not compute FNP friction.

Use:

```powershell
python -m synthia_core.cli neutrino guardrail-check --input event.json --json
```

## Boundary

The maintained educational boundary is:

- educational simulation;
- simulation is not detection;
- flavor state is not mass propagation state;
- weak interaction primary guardrail;
- secondary detector response is not a primary strong-force interaction;
- Synthia classifies before FNP-QNN computes;
- `dL_lex != dF`;
- `I_lexicon != i_fractal`;
- candidate is not proof.

Do not use this gate as detector evidence, physics validation, medical evidence,
safety evidence, or autonomous scientific authority.
