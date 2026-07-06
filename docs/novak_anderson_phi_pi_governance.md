# Novak-Anderson Phi/Pi Governance Case

Synthia governs the source and claim boundary for the FNP-QNN Novak-Anderson
phi/pi theorem layer. It does not reimplement the simulator math; it prepares a
source-linked review packet using the existing `scientific-governance` reviewer.

## Sources

| Source id | Source | Governance role |
| --- | --- | --- |
| `ANDERSON_NOVAK_PHI_PI_2008` | `https://hascmathart.weebly.com/uploads/7/6/8/7/7687070/a_connection_between_the_numbers_phi_and_pi_2.pdf` | Primary public mathematical source for pseudopi, inverse pseudopi, and pseudophi. |
| `ANDERSON_NOVAK_FIBONACCI_VECTOR_POLYGONS_2009` | `https://www.researchgate.net/profile/Stuart-Anderson-2/publication/228768410_Fibonacci_vector_sequences_and_regular_polygons/links/54b5ec8c0cf26833efd345f7/Fibonacci-vector-sequences-and-regular-polygons.pdf` | Primary public source for Fibonacci-vector recurrence and Golden Numbers. |
| `DANI_NOVAK_PHI_HIGHER_DIMENSIONS_SHEET_REDACTED` | `https://docs.google.com/spreadsheets/d/1LICbMOdp689MwMvwToTQJkKf0SQNVKMNoRMKeRP1WFw/edit` | Redacted private-provenance teaching Sheet. |
| `GENESIS_ECHOES_PAPER_I_DRIVE_DOC` | `https://docs.google.com/document/d/1kDqt3WML2ev0uBNH9OKseIb7XF5k6H9ScRzusJ47gf4/edit` | Interpretive Phi Framework document; not primary theorem proof. |
| `PRIVATE_DANI_NOVAK_GMAIL_PROVENANCE_REDACTED` | `[private Gmail provenance redacted]` | Provenance confirmation only; no private body, message id, attachment id, or display URL is stored. |
| `PHI_FRAMEWORK_RESEARCH_DRIVE_DOC` | `https://docs.google.com/document/d/10DNzmxVqZCvMNBN4tIvQpbkXwCLIIqbCnsx5TJlqj7s/edit` | Deferred interpretive Phi Framework source. |
| `PHI_CALCULUS_CHEATSHEET_DRIVE_DOC` | `https://docs.google.com/document/d/1sOi-vZhIZiyyOMPnu55S7eAuEKdI3lB8K4D5Z6zqJPw/edit` | Deferred phi calculus source. |
| `BRIDGE_CALCULUS_DRIVE_DOC` | `https://docs.google.com/document/d/14hBgjKn8QTjZjQUx0s8DuCNM7h12Q7zVQcgFM2MjA7Q/edit` | Deferred bridge calculus source. |
| `UNIFIED_FFED_CALCULI_DRIVE_DOC` | `https://docs.google.com/document/d/1lH3OTdklWpRcT4QxZEPguzFsq1fwqUpG527W7emCY2g/edit` | Deferred elemental calculi source. |
| `ANTI_ENTROPY_IMPERATIVE_DRIVE_DOC` | `https://docs.google.com/document/d/11f4kORbVcy3OmIRbQ00nxS76sPdw4V3orc0jffI7tA0/edit` | Deferred anti-entropy white-paper source. |

## CLI

```powershell
python -m synthia_core.cli scientific-governance novak-anderson
```

The command returns the same JSON shape as other `scientific-governance`
commands: `source_ids`, `evidence_sources`, `model_card`, `dataset_sheet`,
`operational_tif`, `human_review_required`, and authority boundaries.

## Boundary

The governed claim is narrow:

- the cited formulas and numerical convergence checks can be reviewed;
- source provenance is visible without exposing private correspondence;
- human review remains required;
- Synthia does not certify cosmology, cryptography, medicine, consciousness,
  production security, or autonomous scientific truth.
