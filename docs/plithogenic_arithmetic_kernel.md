# Plithogenic Arithmetic Kernel

## Objective

This kernel implements Synthia phase 18 from the public source:

https://fs.unm.edu/NidusIdearum5-v3.pdf

It extends symbolic plithogenic numbers with arithmetic traces for addition, subtraction, multiplication, and absorbance-style component laws.

## Synthia Role

Arithmetic output stays traceable. Each result includes its source pointer, law name, operands, result, and bounded projection into:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Interfaces

```text
synthia symbolic-plithogenic multiply --left <json> --right <json> --law absorbance
```

Addition and subtraction are exposed through:

```text
synthia symbolic-plithogenic operate --op add|subtract --left <json> --right <json>
```

## Implementation Boundary

The v1 arithmetic law is explicit and inspectable. Custom symbolic law expansion can be added later only with validation.
