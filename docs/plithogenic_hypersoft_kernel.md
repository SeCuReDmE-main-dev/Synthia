# Plithogenic Hypersoft Kernel

## Objective

This kernel implements Synthia phase 19 from the public NSS source:

https://fs.unm.edu/NSS/ExtensionOfSoftSetToHypersoftSet.pdf

It models attribute-value products, hypersoft mappings, neutrosophic membership payloads, and plithogenic hypersoft contradiction.

## Synthia Role

The hypersoft layer supports taxonomy filtering and multi-criteria document classification. It helps Synthia keep attribute-product context before reducing a classification into:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Interfaces

```text
synthia hypersoft explain
synthia hypersoft product --attributes <json>
synthia hypersoft classify --mapping <json>
```

## Implementation Boundary

The kernel reports unresolved attribute points and contradiction load. It prepares review-ready evidence rather than final scientific claims.
