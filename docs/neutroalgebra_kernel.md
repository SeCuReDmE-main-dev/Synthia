# NeutroAlgebra Kernel

## Objective

This kernel implements Synthia phase 20 from the public NSS source:

https://fs.unm.edu/NeutroAlgebra.pdf

It classifies operation tables as classical, partial, outer-defined, or indeterminate and provides axiom diagnostics.

## Synthia Role

NeutroAlgebra becomes a future math lexicon for graph and operation memory. It can describe operations that are not fully closed, not fully defined, or not fully decidable.

The public hierarchy remains:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Interfaces

```text
synthia neutroalgebra explain
synthia neutroalgebra classify --operation <json>
synthia neutroalgebra axiom --axiom associativity|commutativity --table <json>
```

## Implementation Boundary

The v1 kernel is diagnostic. It does not claim formal proof of every algebraic structure; it produces source-linked review packets for Synthia memory.
