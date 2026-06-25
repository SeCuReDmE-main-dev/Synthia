# NSS Math Sources for Synthia

## Objective

This report records 20 public `fs.unm.edu` sources selected for Synthia's mathematical layer. Each entry explains why the source was selected and how Synthia should use it for `I_lexicon`, T/I/F, plithogenic contradiction, document filtration, lexicon switching, and graph memory.

## Synthia Math Context

The current canonical `I_lexicon` chain is:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

`I` is base indeterminacy. `I_system^S` is system-level indeterminacy inside the active lexicon set, task, corpus, and source context. `H_lex` is normalized lexicon entropy over candidate lexicons. `G_lex` is lexicon decision-gap uncertainty between the highest-ranked and second-highest-ranked lexicon. `I_lexicon` is the final context-preserving lexicon indeterminacy state used for classification, filtration, switching, and quarantine.

Plithogenic mathematics is treated here as a system-level method for multi-attribute contradiction, attribute-value reasoning, and multivariate indeterminacy. It supports `I_system^S` and helps compute contradiction load, but it is not a replacement for the `I_lexicon` chain.

## Source Selection Criteria

Sources were selected when they met at least one of these criteria:

- They are hosted on the public `fs.unm.edu` domain.
- They define or explain neutrosophy, T/I/F, neutrosophic logic, set, probability, statistics, or measure.
- They define plithogenic set, logic, probability, statistics, symbolic algebra, or hypersoft attribute structures.
- They can support Synthia modules such as `TIF`, `PlithogenicMatrix`, `I_lexicon`, HippoRAG graph trace, taxonomy review packets, or source-weighted document filtration.
- They are broad enough to serve as stable public citation anchors for future Synthia math development.

## 20 NSS / FS Source Ledger

### 1. NSS Journal Hub

- URL: https://fs.unm.edu/NSS/
- Classification: `foundation`
- Why selected: It is the public journal root for Neutrosophic Sets and Systems and provides the main source context for advanced studies in neutrosophy, neutrosophic sets, logic, probability, statistics, and related fields.
- How Synthia will use it: Public source root for the NSS math ledger and a stable citation base when adding future NSS references.

### 2. NSS Articles Index

- URL: https://fs.unm.edu/NSS/Articles.htm
- Classification: `foundation`
- Why selected: It is the public article index for discovering individual NSS papers and verifying source availability.
- How Synthia will use it: Discovery index for future source expansion, report refreshes, and public-source verification.

### 3. A Unifying Field in Logics: Neutrosophic Logic, Neutrosophy, Neutrosophic Set, Probability and Statistics

- URL: https://fs.unm.edu/eBook-Neutrosophics6.pdf
- Classification: `foundation`, `TIF`, `probability_statistics`
- Why selected: It is a broad foundational source for neutrosophy, neutrosophic logic, set, probability, and statistics.
- How Synthia will use it: Foundation for the public explanation of T/I/F, indeterminacy, and uncertainty-bearing probability/statistics.

### 4. Neutrosophic Set as a Generalization of the Intuitionistic Fuzzy Set

- URL: https://fs.unm.edu/IFS-generalized.pdf
- Classification: `foundation`, `TIF`
- Why selected: It supports indeterminacy as a component distinct from truth and falsity.
- How Synthia will use it: Source basis for keeping `I` separate from `T` and `F` in Synthia payloads and review packets.

### 5. Neutrosophic Logic as a Generalization of Intuitionistic Fuzzy Logic

- URL: https://fs.unm.edu/IFL-generalized.pdf
- Classification: `foundation`, `TIF`
- Why selected: It supports a logic model where propositions are not reduced to binary truth.
- How Synthia will use it: Logic foundation for interpreting classification assertions with T/I/F rather than only yes/no labels.

### 6. Introduction to Neutrosophic Logic

- URL: https://fs.unm.edu/IntrodNeutLogic.pdf
- Classification: `foundation`, `TIF`
- Why selected: It is an accessible public reference for neutrosophic logic.
- How Synthia will use it: Educational source for README-level and docs-level explanations of Synthia's T/I/F reasoning.

### 7. Single Valued Neutrosophic Sets

- URL: https://fs.unm.edu/SingleValuedNeutrosophicSets.pdf
- Classification: `TIF`
- Why selected: It provides a bounded practical form of neutrosophic values.
- How Synthia will use it: Mathematical support for the current Python `TIF` representation where values are bounded and serializable.

### 8. Introduction to Neutrosophic Measure, Integral, and Probability

- URL: https://fs.unm.edu/NeutrosophicMeasureIntegralProbability.pdf
- Classification: `probability_statistics`, `I_lexicon`
- Why selected: It gives measure and probability background for systems where events or spaces carry indeterminacy.
- How Synthia will use it: Source support for uncertainty-bearing source scoring, document filtration, and future probability-calibrated lexicon decisions.

### 9. Introduction to Neutrosophic Statistics

- URL: https://fs.unm.edu/NeutrosophicStatistics.pdf
- Classification: `probability_statistics`
- Why selected: It treats statistics where data can contain indeterminacy.
- How Synthia will use it: Statistical basis for indeterminate data, uncertain classification outputs, and human-review packet scoring.

### 10. The Neutrosophic Statistical Distribution

- URL: https://fs.unm.edu/NSS/TheNeutrosophicStatisticalDistribution.pdf
- Classification: `probability_statistics`, `future_math_lexicon`
- Why selected: It connects neutrosophic statistics to distribution-level modeling.
- How Synthia will use it: Future support for calibrated uncertainty distributions around `H_lex`, `G_lex`, and `I_lexicon`.

### 11. Neutrosophic Random Variables

- URL: https://fs.unm.edu/NSS/NeutrosophicRandomVariables4.pdf
- Classification: `probability_statistics`, `I_lexicon`
- Why selected: It gives a path for modeling uncertain quantities as neutrosophic random variables.
- How Synthia will use it: Future model for lexicon probabilities and source evidence as indeterminate random variables.

### 12. Practical Applications of the Independent Neutrosophic Components

- URL: https://fs.unm.edu/NSS/PracticalIndependentNeutrosophic36.pdf
- Classification: `TIF`
- Why selected: It supports treating neutrosophic components as independent rather than collapsed.
- How Synthia will use it: Direct support for keeping T, I, and F independent in Synthia JSON payloads, CLI output, and graph memory.

### 13. Introduction to the MultiNeutrosophic Set

- URL: https://fs.unm.edu/NSS/MultiNeutrosophicSet.pdf
- Classification: `TIF`, `taxonomy_filtering_support`
- Why selected: It supports evaluation by many sources or experts.
- How Synthia will use it: Source basis for multi-source review, expert-weighted evidence, and source-weighted lexicon state.

### 14. Plithogenic Set, an Extension of Crisp, Fuzzy, Intuitionistic Fuzzy, and Neutrosophic Sets

- URL: https://fs.unm.edu/NSS/PlithogenicSetAnExtensionOfCrisp.pdf
- Classification: `plithogenic`
- Why selected: It is the main public source for plithogenic attributes, attribute values, dominant values, and contradiction degree.
- How Synthia will use it: Core source for `PlithogenicMatrix`, contradiction scoring, and attribute-value reasoning in lexicon classification.

### 15. Introduction to Plithogenic Logic

- URL: https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf
- Classification: `plithogenic`, `I_lexicon`
- Why selected: It supports plithogenic logic as a multi-attribute and multivariate reasoning layer.
- How Synthia will use it: Mathematical source for treating plithogenic classification as a system-level method for organizing indeterminacy.

### 16. Plithogenic Probability and Statistics

- URL: https://fs.unm.edu/NSS/PlithogenicProbabilityStatistics20.pdf
- Classification: `plithogenic`, `probability_statistics`, `I_lexicon`
- Why selected: It connects plithogenic work to multivariate probability, statistics, and indeterminate variables.
- How Synthia will use it: Source support for aggregating many lexicon signals before computing `H_lex`, `G_lex`, and final `I_lexicon`.

### 17. Symbolic Plithogenic Algebraic Structures

- URL: https://fs.unm.edu/NSS/SymbolicPlithogenicAlgebraic39.pdf
- Classification: `plithogenic`, `symbolic_algebra`
- Why selected: It supports symbolic plithogenic structures and notation.
- How Synthia will use it: Public math source for future symbolic notation, algorithm rendering, and plithogenic math language.

### 18. Nidus Idearum V

- URL: https://fs.unm.edu/NidusIdearum5-v3.pdf
- Classification: `symbolic_algebra`, `future_math_lexicon`
- Why selected: It contains background related to symbolic plithogenic numbers and algebraic structures.
- How Synthia will use it: Future source for symbolic plithogenic number language and math-lexicon expansion.

### 19. Extension of Soft Set to Hypersoft Set, and then to Plithogenic Hypersoft Set

- URL: https://fs.unm.edu/NSS/ExtensionOfSoftSetToHypersoftSet.pdf
- Classification: `taxonomy_filtering_support`, `plithogenic`
- Why selected: It formalizes attribute and parameter structures that can generalize multi-criteria classification.
- How Synthia will use it: Support for taxonomy filtering, multi-criteria document routing, and structured lexicon attributes.

### 20. NeutroAlgebra is a Generalization of Partial Algebra

- URL: https://fs.unm.edu/NeutroAlgebra.pdf
- Classification: `future_math_lexicon`
- Why selected: It supports operations, functions, and axioms that can be well-defined, indeterminate, or outer-defined.
- How Synthia will use it: Future math-lexicon source for partially defined, indeterminate, or outer-defined transformations in graph memory and lexicon switching.

## How These Sources Map To Synthia Modules

- `TIF`: Sources 3, 4, 5, 6, 7, 12, and 13 support the public mathematical basis for truth, indeterminacy, and falsity.
- `PlithogenicMatrix`: Sources 14, 15, 16, 17, and 19 support attribute values, contradiction degree, multivariate reasoning, and symbolic plithogenic structures.
- `I_lexicon`: Sources 8, 11, 15, and 16 support uncertainty-bearing probability, system-level indeterminacy, and lexicon probability distributions.
- `H_lex`: Sources 8, 9, 10, 11, and 16 support probability and statistics needed for entropy-like lexicon uncertainty.
- `G_lex`: Sources 8, 9, 11, and 16 support score-distribution reasoning needed to compare the strongest and second-strongest lexicon candidates.
- HippoRAG graph trace: Sources 13, 14, 16, 19, and 20 support multi-source evidence, attribute structure, contradiction, and partially defined graph operations.
- Taxonomy memory review packets: Sources 3, 7, 12, 13, 14, and 19 support public-safe evidence scoring, human review, and multi-attribute classification context.

## Implementation Recommendations

- Keep the public canonical chain as:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

- Use plithogenic math as a system-level aggregation and contradiction layer before final lexicon selection.
- Treat source reliability, taxonomy coherence, semantic similarity, and contradiction degree as evidence channels for `P(L_i | d, S)`.
- Store source IDs from this report in public code or payloads only when the cited source directly supports the emitted value.
- Keep future math lexicons modular. A specialized math branch may introduce its own symbols, but it must not replace the public `I_lexicon` chain unless explicitly reviewed.

## Risks / Boundaries

- This report is a source map, not a proof that every Synthia formula is already formally established in the cited papers.
- `H_lex` and `G_lex` are Synthia engineering variables derived for lexicon classification; they should be presented as Synthia variables, not as NSS terminology.
- Plithogenic contradiction degree should remain visible as its own signal and should not be hidden inside a single confidence number.
- Public documentation should cite only public sources and avoid private correspondence or local-only evidence.
- Human experts remain responsible for scientific, taxonomic, and nomenclatural authority.
