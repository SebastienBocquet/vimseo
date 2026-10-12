<!--
 Copyright 2021 IRT Saint Exupery, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# Information for maintainers

In the commands below, `upstream` is the remote of
[vimseo/vimseo](https://github.com/vimseo/vimseo) and `X.Y.Z` the version to release,
which follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release a version

The version of the package is computed by `setuptools_scm` from the git tags: a
release is a tag `X.Y.Z` on `main`, and nothing else in the code holds the version.

### Prepare the release

1. Create a branch `release/X.Y.Z` from `upstream/main`.
2. Compile the changelog fragments of `changelog/fragments/` into `CHANGELOG.md`
   with `towncrier build --version X.Y.Z --date MM/DD/YYYY`: it writes the section
   `# Version X.Y.Z (MM/DD/YYYY)` and deletes the fragments. Move the entries left in
   the section `# Unreleased`, if any, into this new section, remove the section
   `# Unreleased` and review the entries. Commit with the message
   `docs(changelog): release X.Y.Z`.
3. Open a pull request to `main`, titled `docs(changelog): release X.Y.Z`, and merge
   it once the tests pass.

### Tag the release

Tag the merge commit with an annotated tag, and push it:

```bash
git fetch upstream
git tag -a X.Y.Z -m "vimseo X.Y.Z" upstream/main
git push upstream X.Y.Z
```

### Publish on PyPI

Build the distribution from a clean checkout of the tag: `setuptools_scm` gives a
development version (e.g. `X.Y.(Z+1).dev0+g<sha>.d<date>`) to a checkout which is not
exactly on the tag or which has modified files.

```bash
git worktree add --detach ../vimseo-release X.Y.Z
cd ../vimseo-release
tox -e dist
```

`tox -e dist` builds the source distribution and the wheel in `dist/` and checks the
content of the wheel. Check that their names hold `X.Y.Z`, then upload them with a
[PyPI API token](https://pypi.org/help/#apitoken) of the project:

```bash
export UV_PUBLISH_TOKEN=pypi-...
tox -e dist-upload
```

Then check the published package: `tox -e pypi-py312` installs `vimseo[all]` from
PyPI and runs the tests of the checkout against it.

### Publish the GitHub release

Create the release `vimseo X.Y.Z` from the tag, with the section `X.Y.Z` of the
changelog as notes, for instance with the
[GitHub CLI](https://cli.github.com/), from a file holding this section:

```bash
gh release create X.Y.Z -R vimseo/vimseo --title "vimseo X.Y.Z" --notes-file notes.md
```

### Deploy the documentation of the release

Deploy the documentation of the tag as the latest version, from the same checkout, as
described in [Deploy the documentation](#deploy-the-documentation):

```bash
mike deploy --push --remote upstream --update-aliases X.Y.Z latest
```

Finally, remove the worktree with `git worktree remove ../vimseo-release`.

## Deploy the documentation

The documentation is published on GitHub Pages, from the `gh-pages` branch of
[vimseo/vimseo](https://github.com/vimseo/vimseo), and is versioned with
[mike](https://github.com/jimporter/mike):

- each release is published under its version, e.g.
  [`0.1.7`](https://vimseo.github.io/vimseo/0.1.7/);
- the last release is also published under the alias `latest`, to which
  [the root of the site](https://vimseo.github.io/vimseo/) redirects;
- the `main` branch is published under `develop`.

The version selector of the documentation lists the versions deployed in
`versions.json` at the root of `gh-pages`. The links from the README to the
documentation point to `latest`.

### Prerequisites

- The `doc` tox environment, created with `tox -e doc --notest`.
- A clean checkout of the revision to document, e.g. a git worktree: MkDocs publishes
  every file under `docs/`, including the untracked ones.
- A local `gh-pages` branch up to date with the remote one: `mike` commits on top of it.

### Deploy a version

From the root of the checkout of the revision to document, e.g. the tag `X.Y.Z`
created by `git worktree add --detach ../vimseo-release X.Y.Z`:

```bash
git fetch upstream gh-pages:gh-pages

# The settings and preparation steps of the doc tox environment.
export DOCSTRING_INHERITANCE_ENABLE=1 PLOTLY_RENDERER=sphinx_gallery MPLBACKEND=AGG
# mike runs mkdocs in a subprocess: the doc environment must be in the PATH
# (.tox/doc/bin on Linux).
export PATH="$PWD/.tox/doc/Scripts:$PATH"
rm -rf docs/generated site
python docs/modify_readme_image_url.py

# A release, which becomes the latest one:
mike deploy --push --remote upstream --update-aliases X.Y.Z latest
# The main branch:
mike deploy --push --remote upstream develop
```

`mike deploy` builds the documentation, commits it in the directory of the version on
`gh-pages` and pushes it. The build fails if one of the runnable examples fails.

The other useful commands:

- `mike list` lists the deployed versions;
- `mike delete --push --remote upstream <version>` deletes a version;
- `mike serve` serves `gh-pages` locally, with the version selector (`mkdocs serve`
  does not show it).

!!! note

    `mike` only writes the directories of the versions, `versions.json` and the
    `index.html` redirecting the root to `latest`. If the history of `gh-pages` was
    rewritten, it refuses to deploy until you pass `--ignore-remote-status`, and the
    push must be forced with `git push --force-with-lease upstream gh-pages`.
