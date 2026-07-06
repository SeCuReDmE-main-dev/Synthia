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

Use:

```powershell
python -m synthia_core.cli neutrino guardrail-check --input event.json --json
```

## Boundary

The maintained educational boundary is:

- educational simulation;
- simulation is not detection;
- weak interaction primary guardrail;
- Synthia classifies before FNP-QNN computes;
- `dL_lex != dF`;
- `I_lexicon != i_fractal`;
- candidate is not proof.

Do not use this gate as detector evidence, physics validation, medical evidence,
safety evidence, or autonomous scientific authority.
