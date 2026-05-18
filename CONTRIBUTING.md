# Contributing to ClusterShell

Contributions are welcome via [GitHub pull requests](https://github.com/clustershell/clustershell/pulls).
For bug reports and feature requests, please open a [GitHub issue](https://github.com/clustershell/clustershell/issues).

For project roles, decision-making, and maintainer information, see [GOVERNANCE.md](GOVERNANCE.md).
This project also adheres to a [Technical Charter](https://clustershell.readthedocs.io/en/latest/CHARTER.html), which defines its governance model, decision-making process, and contribution requirements.

## Developer Certificate of Origin (DCO)

All commits must include a `Signed-off-by` line certifying that you have the
right to submit the contribution under the project's license, per the
[Developer Certificate of Origin](https://developercertificate.org/). If you
are contributing on behalf of your employer, your sign-off attests that your
employer has authorized the contribution under the DCO.

Add it with the `-s` flag:

```
git commit -s -m "Your commit message"
```

This produces a line like:

```
Signed-off-by: Your Name <your.email@example.com>
```

The name and email must match your Git configuration (`git config user.name`
and `git config user.email`). Pull requests with missing sign-offs will be
blocked by an automated check.

To fix a missing sign-off on the last commit:

```
git commit --amend -s
```

To sign off multiple commits at once:

```
git rebase HEAD~N --signoff   # sign off the last N commits
```
