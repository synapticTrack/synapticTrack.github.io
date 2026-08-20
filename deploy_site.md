Use GitHub Pages to publish docs/site/.

  1. Create the repository synapticTrack/synapticTrack.github.io in your GitHub organization. GitHub
     Pages will serve it at:

  https://synaptictrack.github.io/

  2. Push the contents of local docs/site/ to that repository’s main branch. Do not push the docs/site
     directory itself, otherwise the site would be nested under /docs/site/.

  cd /home/cspark/Work/simulation_codes-working/synapticTrack/docs/site

  git init
  git branch -M main
  git add .
  git commit -m "Publish synapticTrack documentation site"
  git remote add origin git@github.com:synapticTrack/synapticTrack.github.io.git
  git push -u origin main

  3. On GitHub, open the new repository:
     Settings -> Pages -> Build and deployment -> select Deploy from a branch -> main -> /(root) -> Save.

  4. Ensure docs/site/index.html exists. It does, so GitHub Pages will use it as the homepage.

  For ongoing updates, from docs/site/:

  git add .
  git commit -m "Update documentation site"
  git push

  A cleaner long-term setup is a separate worktree or a GitHub Actions deployment workflow that rebuilds
  docs/site/ and publishes it automatically.

