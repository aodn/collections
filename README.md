# `collections`
Versioned controlled collections metadata.

## Quickstart
```python
from aodn_collections import CATALOG_V1

print(CATALOG_V1.as_table())
```

## Project Tooling: `uv`
`uv` is the package management tool of choice.

See [docs](https://docs.astral.sh/uv/).

### Package Management
To add a package:
```bash
uv add <package-name>
```
To remove a package:
```bash
uv remove <package-name>
```
To add/remove a package to a particular dependency group:
```bash
uv add --group <dependency-group> <package-name>
```
```bash
uv remove --group <dependency-group> <package-name>
```

### Building
```bash
uv build
```

## Development
### Running Flows
#### Local Server
To run a local server open a terminal window and run the server:
```bash
uv run prefect server start
```
#### Deployments
To test deployments, add flow deployment configuration to the [prefect.yaml](./prefect.yaml) file and run the deploy command:

```bash
make deploy
```

### Releases
Packages are built via GitHub workflows and triggered by tags.

#### Supported Tag Variations
| Segment Type | Synonyms / Keywords | New Version Result | Description / Notes |
| :--- | :--- | :--- | :--- |
| **release** | - | `1.0.0` | Keeps the current stable release version |
| **major** | - | `2.0.0` | Bumps the major version (breaking changes) |
| **minor** | - | `1.1.0` | Bumps the minor version (new features, backward-compatible) |
| **micro** / **patch** / **fix** | - | `1.0.1` | Bumps the patch version (backward-compatible bug fixes) |
| **alpha** | `a` | `1.0.0a0` | Initiates an alpha pre-release stream |
| **beta** | `b` | `1.0.0b0` | Initiates a beta pre-release stream |
| **rc** / **pre** / **preview** | `c` | `1.0.0rc0` | Initiates a release candidate / preview stream |
| **rev** / **post** | `r` | `1.0.0.post0` | Appends a post-release (typically for minor packaging fixes) |
| **dev** | - | `1.0.0.dev0` | Appends a development release tag |

#### Example Release Usage

| Step | Tag / Version | Type | Description |
| :--- | :--- | :--- | :--- |
| 1 | `1.0.0-rc0` | RC (Minor/Major) | First release candidate for the upcoming feature set |
| 2 | `1.0.0-rc1` | RC (Fixes) | Bug fixes applied to the release candidate stream |
| 3 | `1.0.0` | **Major** / **Minor** | The official stable production release |
| 4 | `1.1.0-rc0` | RC (Minor) | First release candidate for the next feature release |
| 5 | `1.1.0` | **Minor** | Next stable production release (backward-compatible features) |
| 6 | `2.0.0-rc0` | RC (Major) | First release candidate for the next breaking-change release |
| 7 | `2.0.0` | **Major** | Next stable major production release (breaking changes) |

To build a release candidate, move to the release branch, tag and push to origin:
```bash
git tag <tag>
```
```bash
git push origin tag <tag>
```

This will trigger the [release workflow](.github/workflows/release.yml).

### Commit Automation
`pre-commit` is [pre-configured](./.pre-commit-config.yaml) to:
#### Lint
Linting is run with `ruff` as it [built by astral](https://docs.astral.sh/ruff/),like `uv`, and integrates easily with `uv`.

#### Requirements.txt Export
The [requirements.txt](./requirements.txt) is updated when the pyproject.toml changes.

#### Testing
`pytest` is run whenever pushing to origin.

#### Static Type Analysis
TODO: Add static type analysis to commit automation using [ty](https://docs.astral.sh/ty/)


### Docker
TODO: Build tested images and release to AODN AWS ECR.
