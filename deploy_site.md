For each website update:

  cd /home/cspark/Work/simulation_codes-working/synapticTrack
  python3 docs/paper/build_consolidated_document.py
  python3 docs/site/build_split_site.py

  touch docs/site/.nojekyll

  rsync -a --delete --exclude='.git/' \
    docs/site/ \
    ../synapticTrack.github.io/

