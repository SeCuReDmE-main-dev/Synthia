# Neutrosophic Logic Kernel

## Objective

This document records Synthia phases 5 and 6 for public use. The logic kernel interprets proposition-level truth, indeterminacy, and falsity before any document is lifted into Synthia's lexicon chain:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Sources

- Phase 5 source: [Neutrosophic Logic as a Generalization of Intuitionistic Fuzzy Logic](https://fs.unm.edu/IFL-generalized.pdf)
- Phase 6 source: [Introduction to Neutrosophic Logic](https://fs.unm.edu/IntrodNeutLogic.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.neutrosophic_logic`. It classifies propositions as relative, absolute, incomplete, paraconsistent, paradoxist, IFL-compatible, or general neutrosophic logic.

The IFL comparison is diagnostic only. Synthia preserves the full neutrosophic proposition when an input is not compatible with intuitionistic fuzzy logic.

## Public CLI

```text
synthia nss logic explain
synthia nss logic classify --T <value> --I <value> --F <value> --text <text>
synthia nss logic compare-ifl --T <value> --I <value> --F <value>
```

## Boundary

This kernel does not claim a proof for a user document. It provides a deterministic public-source classification surface that can be reviewed by humans and later stored in Synthia's graph memory.
