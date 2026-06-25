# NSS Articles Indexation for I_lexicon

## Objective

Synthia uses the public NSS articles index at https://fs.unm.edu/NSS/Articles.htm as an evolving discovery surface for mathematical source selection. The index is not treated as a single theorem source. It helps Synthia find candidate article titles and PDF links that can support routing into the correct math lexicon before classification.

The default Synthia chain remains:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Role of the Articles Index

The NSS hub defines broad source families. The articles index supplies individual article records that can be scanned, normalized, deduplicated, and classified by mathematical family.

Synthia uses article-title evidence to estimate a lexicon distribution:

```text
P(L_i | d, S)
```

That distribution is then converted into `H_lex`, `G_lex`, and `I_lexicon`. The result is a candidate routing signal for document filtration, lexicon switching, source selection, and graph memory.

## Source Families

The indexation layer classifies records into families such as `TIF`, `probability_statistics`, `plithogenic`, `symbolic_algebra`, `hypersoft`, `neutroalgebra`, `neutrogeometry`, `topology`, `decision_making`, `graph_theory`, `physics`, and `future_math_lexicon`.

Plithogenic matches are treated as system-level multi-attribute contradiction support. Probability and statistics matches support the calculation of the lexicon distribution. Neutrogeometry and fractal terms remain specialized carriers and do not replace the default public `I_lexicon` chain.

## Public Boundary

Generated article ledgers and raw index snapshots belong in `Synthia_organisation/02_taxonomy_lexicon_model/`. The public repository stores the parser, scorer, tests, and small fixtures only.

Article-index classifications are candidates for routing and review. They do not claim that every Synthia formula is formally proven by every indexed NSS article, and they do not replace human mathematical judgment.

## Current Implementation

The first implementation is deterministic and explainable. It uses standard-library HTML parsing, public URL normalization, PDF deduplication, volume/article marking, and weighted keyword scoring. This keeps the system auditable and avoids adding runtime dependencies for the public repo.
