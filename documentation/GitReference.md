### Git Basics
#### Forking the Repo
1. To work on the repository, you'll have to create a GitHub account and fork
   the repository.  Navigate to https://github.com/NERSC/CompactCori and click
   the `Fork` button in the upper right hand corner.  This will create a public
   copy of the CompactCori repository on your GitHub account
2. Clone the repository to Edison.  SSH to Edison by running `ssh
   [your_username]@edison.nersc.gov`.  Run `git clone
   git@github.com:[your_github_username]/CompactCori`
3. Create an upstream remote for your repository.  `cd` into the `CompactCori`
   directory and add the upstream remote: `git remote add upstream
   https://github.com/NERSC/CompactCori.git`

#### Working with Branches
You should never make changes directly on the `master` branch.  All changes
should be done on a separate branch from master ( unless you have some
compelling reason to branch off of a branch that's not master).  Remember that
the work on master is considered production -- that is, that there aren't bugs
or issues with it.  This is called "branch per feature" in agine software
engineering.

1. First, make sure you're on the master branch using `git status`.
1. If you're on another branch, `checkout` to master: `git checkout master`
2. To create a new branch, run `git checkout -b [branchname]` where you replace
   [branchname] with a hyphenated descriptive name for your new branch
3. To switch between branches, run `git checkout [branchname]` where
   [branchname] is the name of the branch you want to switch to

#### Committing Files
1. Run `git add [filename(s)]` to **stage** the file.  This is equivalent to
   telling Git "When I commit, please include any changes made to this file"
2. Run `git commit` to commit all the files you added.  In the resulting commit
   message, write a short (<50 charachter) summary of what changes the commit
   contains.  You should also write your subject line in the imperative mood.  A
   great way to test to see if you're doing things right is to prepend "Applying
   this commit will [your summary here]".  Note that this works for the above
   commit message: "Applying this commit will fix list and force calculation".
   If the commit summary read "Fixed particle list and force calculation", the
   sentence would read "Applying this commit will fixed particle list and force
   calculation", which is obviously grammatically incorrect.  Then write the
   body of the commit -- a more detailed (perhaps  bulleted) more detailed list
   of changes.  Be sure that your text is wrapped at 72 characters and that you
   leave a blank line between the summary and body.  For example:
   ```
   Fix particle list and force calculation

   - Make particles a static class variable
   - Check if particle is self
   - Fix division by zero error in calculate_force

   ```
3. Run `git pull --rebase` to make sure your code is up-to-date with what's
   already on GitHub.  Fix conflicts as necessary (feel free to ask me for help
   if you need help)
4. Run `git push origin [branchname]` to push your changes to GitHub so everyone
   else can see your work

#### Updating to Upstream and Opening a Pull Request
Before you create a Pull Request to merge your code back into the NERSC Git
repository, you'll want to make sure your branches are up-to-date.  You can do
this by updating your master branch off of the upstream remote we set up
earlier, and then rebasing your code off of your updated master before pull
requesting.

1. Run `git fetch upstream` to fetch all the branches in the upstream repository
2. Run `git checkout master` to change to the master branch
3. Rebase your master branch on the upstream branch by running `git rebase
   upstream/master`.  If there are merge conflicts, resolve them (or ask me for
   help if you're unsure of what's going on)
4. Rebase your working branches on your newly updated master branch: `git
   checkout [branchname]; git rebase master`.  Again, resolve merge conflicts if
   necessary (or ask for help)
5. Push your working branch back to GitHub.  Since you rebased which changed the
   commit history of the branch, if you do a regular `git push` you'll probably
   get a message about the push being unsuccessful.  Run a `git push --force` to
   force push your changes to your branch.  Be careful when doing this; make
   sure you're on the correct branch
6. Create a pull request by navigating to GitHub, clicking on the Pull Requests
   icon, and clicking the green button to create a new PR.  Choose the branch
   you want to merge back into the NERSC repo, add a description, and submit the
   PR for a code review.
