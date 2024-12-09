mkdocs-decision-records
==

<p align="center">
	<img width="600" src="https://raw.githubusercontent.com/timo-reymann/mkdocs-decision-records/main/.github/images/demo.png">
    <br />
    Manage decision records with mkdocs in a customizable and minimal fashion.
</p>



## Features

- Customizable status colors and lifecycle
- Enforces information to be present for ADRs
- Allows description being kept as markdown

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
   status: proposed | rejected | accepted | deprecated | … | superseded by
   date: YYYY-MM-DD
   deciders:
      - decider 1
      - decider 2
   # Optional ticket
   ticket: FOO-1
   ---
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