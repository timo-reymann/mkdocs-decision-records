mkdocs-decision-records
===
[![PyPI version](https://badge.fury.io/py/mkdocs-decision-records.svg)](https://pypi.org/project/mkdocs-decision-records)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-decision-records)](https://pypi.org/project/mkdocs-decision-records)
[![LICENSE](https://img.shields.io/github/license/timo-reymann/mkdocs-decision-records)](https://github.com/timo-reymann/mkdocs-decision-records/blob/main/LICENSE)
[![CircleCI](https://circleci.com/gh/timo-reymann/mkdocs-decision-records.svg?style=shield)](https://app.circleci.com/pipelines/github/timo-reymann/mkdocs-decision-records)
[![codecov](https://codecov.io/gh/timo-reymann/mkdocs-decision-records/graph/badge.svg?token=EVgb1KIcjC)](https://codecov.io/gh/timo-reymann/mkdocs-decision-records)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=timo-reymann_mkdocs-decision-records&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=timo-reymann_mkdocs-decision-records)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=timo-reymann_mkdocs-decision-records&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=timo-reymann_mkdocs-decision-records)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=timo-reymann_mkdocs-decision-records&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=timo-reymann_mkdocs-decision-records)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=timo-reymann_mkdocs-decision-records&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=timo-reymann_mkdocs-decision-records)
[![Renovate](https://img.shields.io/badge/renovate-enabled-green?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzNjkgMzY5Ij48Y2lyY2xlIGN4PSIxODkuOSIgY3k9IjE5MC4yIiByPSIxODQuNSIgZmlsbD0iI2ZmZTQyZSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTUgLTYpIi8+PHBhdGggZmlsbD0iIzhiYjViNSIgZD0iTTI1MSAyNTZsLTM4LTM4YTE3IDE3IDAgMDEwLTI0bDU2LTU2YzItMiAyLTYgMC03bC0yMC0yMWE1IDUgMCAwMC03IDBsLTEzIDEyLTktOCAxMy0xM2ExNyAxNyAwIDAxMjQgMGwyMSAyMWM3IDcgNyAxNyAwIDI0bC01NiA1N2E1IDUgMCAwMDAgN2wzOCAzOHoiLz48cGF0aCBmaWxsPSIjZDk1NjEyIiBkPSJNMzAwIDI4OGwtOCA4Yy00IDQtMTEgNC0xNiAwbC00Ni00NmMtNS01LTUtMTIgMC0xNmw4LThjNC00IDExLTQgMTUgMGw0NyA0N2M0IDQgNCAxMSAwIDE1eiIvPjxwYXRoIGZpbGw9IiMyNGJmYmUiIGQ9Ik04MSAxODVsMTgtMTggMTggMTgtMTggMTh6Ii8+PHBhdGggZmlsbD0iIzI1YzRjMyIgZD0iTTIyMCAxMDBsMjMgMjNjNCA0IDQgMTEgMCAxNkwxNDIgMjQwYy00IDQtMTEgNC0xNSAwbC0yNC0yNGMtNC00LTQtMTEgMC0xNWwxMDEtMTAxYzUtNSAxMi01IDE2IDB6Ii8+PHBhdGggZmlsbD0iIzFkZGVkZCIgZD0iTTk5IDE2N2wxOC0xOCAxOCAxOC0xOCAxOHoiLz48cGF0aCBmaWxsPSIjMDBhZmIzIiBkPSJNMjMwIDExMGwxMyAxM2M0IDQgNCAxMSAwIDE2TDE0MiAyNDBjLTQgNC0xMSA0LTE1IDBsLTEzLTEzYzQgNCAxMSA0IDE1IDBsMTAxLTEwMWM1LTUgNS0xMSAwLTE2eiIvPjxwYXRoIGZpbGw9IiMyNGJmYmUiIGQ9Ik0xMTYgMTQ5bDE4LTE4IDE4IDE4LTE4IDE4eiIvPjxwYXRoIGZpbGw9IiMxZGRlZGQiIGQ9Ik0xMzQgMTMxbDE4LTE4IDE4IDE4LTE4IDE4eiIvPjxwYXRoIGZpbGw9IiMxYmNmY2UiIGQ9Ik0xNTIgMTEzbDE4LTE4IDE4IDE4LTE4IDE4eiIvPjxwYXRoIGZpbGw9IiMyNGJmYmUiIGQ9Ik0xNzAgOTVsMTgtMTggMTggMTgtMTggMTh6Ii8+PHBhdGggZmlsbD0iIzFiY2ZjZSIgZD0iTTYzIDE2N2wxOC0xOCAxOCAxOC0xOCAxOHpNOTggMTMxbDE4LTE4IDE4IDE4LTE4IDE4eiIvPjxwYXRoIGZpbGw9IiMzNGVkZWIiIGQ9Ik0xMzQgOTVsMTgtMTggMTggMTgtMTggMTh6Ii8+PHBhdGggZmlsbD0iIzFiY2ZjZSIgZD0iTTE1MyA3OGwxOC0xOCAxOCAxOC0xOCAxOHoiLz48cGF0aCBmaWxsPSIjMzRlZGViIiBkPSJNODAgMTEzbDE4LTE3IDE4IDE3LTE4IDE4ek0xMzUgNjBsMTgtMTggMTggMTgtMTggMTh6Ii8+PHBhdGggZmlsbD0iIzk4ZWRlYiIgZD0iTTI3IDEzMWwxOC0xOCAxOCAxOC0xOCAxOHoiLz48cGF0aCBmaWxsPSIjYjUzZTAyIiBkPSJNMjg1IDI1OGw3IDdjNCA0IDQgMTEgMCAxNWwtOCA4Yy00IDQtMTEgNC0xNiAwbC02LTdjNCA1IDExIDUgMTUgMGw4LTdjNC01IDQtMTIgMC0xNnoiLz48cGF0aCBmaWxsPSIjOThlZGViIiBkPSJNODEgNzhsMTgtMTggMTggMTgtMTggMTh6Ii8+PHBhdGggZmlsbD0iIzAwYTNhMiIgZD0iTTIzNSAxMTVsOCA4YzQgNCA0IDExIDAgMTZMMTQyIDI0MGMtNCA0LTExIDQtMTUgMGwtOS05YzUgNSAxMiA1IDE2IDBsMTAxLTEwMWM0LTQgNC0xMSAwLTE1eiIvPjxwYXRoIGZpbGw9IiMzOWQ5ZDgiIGQ9Ik0yMjggMTA4bC04LThjLTQtNS0xMS01LTE2IDBMMTAzIDIwMWMtNCA0LTQgMTEgMCAxNWw4IDhjLTQtNC00LTExIDAtMTVsMTAxLTEwMWM1LTQgMTItNCAxNiAweiIvPjxwYXRoIGZpbGw9IiNhMzM5MDQiIGQ9Ik0yOTEgMjY0bDggOGM0IDQgNCAxMSAwIDE2bC04IDdjLTQgNS0xMSA1LTE1IDBsLTktOGM1IDUgMTIgNSAxNiAwbDgtOGM0LTQgNC0xMSAwLTE1eiIvPjxwYXRoIGZpbGw9IiNlYjZlMmQiIGQ9Ik0yNjAgMjMzbC00LTRjLTYtNi0xNy02LTIzIDAtNyA3LTcgMTcgMCAyNGw0IDRjLTQtNS00LTExIDAtMTZsOC04YzQtNCAxMS00IDE1IDB6Ii8+PHBhdGggZmlsbD0iIzEzYWNiZCIgZD0iTTEzNCAyNDhjLTQgMC04LTItMTEtNWwtMjMtMjNhMTYgMTYgMCAwMTAtMjNMMjAxIDk2YTE2IDE2IDAgMDEyMiAwbDI0IDI0YzYgNiA2IDE2IDAgMjJMMTQ2IDI0M2MtMyAzLTcgNS0xMiA1em03OC0xNDdsLTQgMi0xMDEgMTAxYTYgNiAwIDAwMCA5bDIzIDIzYTYgNiAwIDAwOSAwbDEwMS0xMDFhNiA2IDAgMDAwLTlsLTI0LTIzLTQtMnoiLz48cGF0aCBmaWxsPSIjYmY0NDA0IiBkPSJNMjg0IDMwNGMtNCAwLTgtMS0xMS00bC00Ny00N2MtNi02LTYtMTYgMC0yMmw4LThjNi02IDE2LTYgMjIgMGw0NyA0NmM2IDcgNiAxNyAwIDIzbC04IDhjLTMgMy03IDQtMTEgNHptLTM5LTc2Yy0xIDAtMyAwLTQgMmwtOCA3Yy0yIDMtMiA3IDAgOWw0NyA0N2E2IDYgMCAwMDkgMGw3LThjMy0yIDMtNiAwLTlsLTQ2LTQ2Yy0yLTItMy0yLTUtMnoiLz48L3N2Zz4=)](https://renovatebot.com)

<p align="center">
	<img width="600" src="https://raw.githubusercontent.com/timo-reymann/mkdocs-decision-records/main/.github/images/demo.png">
    <br />
    Manage decision records with mkdocs in a customizable and minimal fashion.
</p>

## Features

- Customizable status colors and lifecycle
- Enforces information to be present for ADRs
- Allows description being kept as markdown

## Demo

[You can find a Demo on GitHub Pages](https://timo-reymann.github.io/mkdocs-decision-records/)

## Installation

1. Install `mkdocs-decision-records` from the PyPi registry using your favorite package manager
2. Configure your `mkdocs.yml`
   ```yaml
   plugins:
   - decision-records:
       # Folder where your decision records are located, defaults to adr
       decisions_folder: adr
       # Optional prefix to prepend to ticket numbers
       ticket_url_prefix: https://ticket.example.com/
       # Configure amount of required deciders
       required_deciders_count: 1
       # Configure available stages and the badge colors
       lifecycle_stages:
         {status}: {color}
   ```
3. Create your ADRs ensuring to add the frontmatter meta data:
   ```markdown
   ---
   id: 000
   status: proposed | rejected | accepted | deprecated | … | superseded
   [superseded_by: <id it has been replaced with>]
   date: YYYY-MM-DD
   deciders:
      - decider 1
      - decider 2
   # Optional ticket
   ticket: FOO-1
   ---

   ## Context and Problem Statement

   [Describe the context and problem statement, e.g., in free form using two to three sentences. You may want to articulate the problem in form of a question.]

   ## Decision Drivers <!-- optional -->

   * [driver 1, e.g., a force, facing concern, …]
   * [driver 2, e.g., a force, facing concern, …]
   * … <!-- numbers of drivers can vary -->

   ## Considered Options

   * [option 1]
   * [option 2]
   * [option 3]

   ## Decision Outcome

   Chosen option: "[option 1]",
   because [justification. e.g., only option, which meets k.o. criterion decision driver | which resolves force force | … | comes out best (see below)].

   ## Pros and Cons of the Options <!-- optional -->

   ### [option 1]

   [example | description | pointer to more information | …] <!-- optional -->

   * Good, because [argument a]
   * Good, because [argument b]
   * Bad, because [argument c]
   * … <!-- numbers of pros and cons can vary -->

   ### [option 2]

   [example | description | pointer to more information | …] <!-- optional -->

   * Good, because [argument a]
   * Good, because [argument b]
   * Bad, because [argument c]
   * … <!-- numbers of pros and cons can vary -->

   ### [option 3]

   [example | description | pointer to more information | …] <!-- optional -->

   * Good, because [argument a]
   * Good, because [argument b]
   * Bad, because [argument c]
   * … <!-- numbers of pros and cons can vary -->

   ## Links <!-- optional -->

   * [Link type] [Link to ADR] <!-- example: Refined by [ADR-0005](0005-example.md) -->
   * … <!-- numbers of links can vary -->
   ```

## Superseding ADRs

This plugin is opinionated about using `superseded` status.

When setting the status to `superseded`, make to sure also set `superseded_by` to the ADR id it has been replaced with.

```markdown
---
# adr details
status: superseded
superseded_by: 123
---
<!-- Deprecated ADR -->
```

## Motivation

I love ADRs and documenting decisions in general. This plugin makes it a bit easier, enforcing basic meta information
while keeping the format open enough so you can do your thing.

## Contributing

I love your input! I want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the configuration
- Submitting a fix
- Proposing new features
- Becoming a maintainer

To get started please read the [Contribution Guidelines](./CONTRIBUTING.md).

## Development

### Requirements

- Python 3.12+
- Poetry

### Build

````sh
poetry install
````

### Alternatives

- [mkdocs-material](https://pypi.org/project/mkdocs-material-adr/)
    - Needs to use the theme
    - ADR graph
- [mkdocs-macros-adr-summary](https://github.com/febus982/mkdocs-macros-adr-summary)
    - works entirely with macros
    - no metadata table at the top
