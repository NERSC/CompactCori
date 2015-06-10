###GIT_README.md

This document outlines the Git style conventions used in this repository.

####Branch Per Feature
There are two main git style conventions used in this repository.  The first is
branch per feature.  This means that all changes to code are done on a branch
off of master, meaning that there shouldn't ever be any changes made directly to
the master branch.  This convention comes from the world of agile software
engineering.  Since there isn't any work being done on master, only
full-featured changes to master are made, and there aren't as any little
conflicts between little features.  Branching per feature is also useful for
keeping commits for separate features separate once they are merged into master
(see below for more information).

To create a branch:
- Checkout to master `git checkout master`
- Create a new branch `git checkout -b [branchname]` replacing [branchname] with
  a short, descriptive, hyphenated (if applicable) name for your branch
- Commit and push to the branch as usual
- Do not merge into master

#### Rebase, not Merge
The second git convention used in this repository is rebasing instead of
merging.  This means that instead of correcting merge conflicts when merging
back into master, we rebase work that is being merged into master off of master,
thereby resolving any conflicts on the branch before merging into master.  The
logic behind this is that we want the git history to be uncluttered and free of
unnecessary merge commits.  After rebasing off of master, it's a good idea to
`merge --no-ff` back into master.  This merges the branch into master without
fast-forwarding it, making it trivial to see where commits pertaining to a
specific feature start and end.  See [this
article](http://walkingthestack.blogspot.com/2012/05/why-you-should-use-git-merge-no-ff-when.html)
for an explanation as to why this is beneficial.  It's also generally a good idea to
run `git pull --rebase` instead of an ordinary `git pull`.

To rebase your changes off of master so that you can safely merge back into
master:
- Commit all your changes and push to GitHub
- Checkout to master: `git checkout master`
- Pull from GitHub: `git pull --rebase origin master`
- Checkout to your branch: `git checkout [branchname]`
- Rebase on master: `git rebase master`
- Fix conflicts if necessary, running `git rebase --continue` after fixing
  conflicts (if applicable)
- Once you've successfully rebased off of master, checkout to master and merge
  without fast-forwarding: `git checkout master; git merge --no-ff [branchname]`
- Check to make sure everything looks right by running `git log --graph
  --pretty=oneline --all`
