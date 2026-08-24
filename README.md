# synapticTrack GitHub Pages Site

This directory contains the generated static site for the `synapticTrack` project.
The HTML pages are built from the consolidated project document in `docs/paper`.

Build order from the repository root:

```bash
python3 docs/paper/build_consolidated_document.py
python3 docs/site/build_split_site.py
```

The generated pages intentionally do not load `polyfill.io`; that external service
can trigger credential prompts or blocked requests. Math rendering still uses
MathJax from jsDelivr.

Suggested GitHub Pages source after review: publish this directory, or copy its
contents to the branch/directory selected in the repository Pages settings.

Deployment is a repository operation. Push only when explicitly intended and
verify the generated site locally before publishing.


## Synchronizing the Pages Checkout

After rebuilding the static site, synchronize it to the standalone Pages
repository with:

```bash
./docs/sync_site.sh
```

The default target is the sibling `../synapticTrack.github.io/` checkout. Pass a
target directory as the first argument to use a different local checkout. The
script preserves the target repository's `.git/` and `.github/` directories.
