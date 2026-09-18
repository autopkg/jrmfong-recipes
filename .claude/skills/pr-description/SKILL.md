---
name: pr-description
description: Write a short what, why and how pull request description for this repo (autopkg/jrmfong-recipes). Name the app in the title, and name the identifier, the download URL and the Team ID a reviewer has to check. Use when asked to create a PR, open a pull request, or write or update a PR description.
user-invocable: true
---

# PR description

Write a short, scannable pull request title and body. A reviewer should get the
point in about 30 seconds.

Write the title and every bullet in the house style:
[[plain-technical-english]]. That means sentence case, active voice, everyday
words, one idea per bullet and ASCII only.

This repo has no ticket tracker. A pull request stands on its own body, so the
Why section carries the whole reason for the change.

## 1. Gather context, read only

None of these commands change anything:

```sh
git rev-parse --abbrev-ref HEAD          # current branch
git log --oneline main..HEAD             # commits on this branch
git status --short                       # uncommitted work
git diff --stat main...HEAD              # files touched
```

Check 3 things before you write:

- if the branch is `main`, stop. The work belongs on a feature branch
- if the changes are not committed, describe the working tree. Say they need
  committing before a pull request can open
- if a pull request already exists for the branch, update it rather than opening
  another

## 2. Naming in this repo

The remote is `autopkg/jrmfong-recipes`. Branches are kebab-case and say what
the change does, such as `add-snowsql-recipe`, `add-veracrypt-pkg-recipe` and
`create-burp-suite-pkg`. Take the title from the branch or the commits.

Write the title in sentence case and the imperative, under about 70 characters.
Name the app, because most changes here add or fix the recipes for one app, and
the app name is what a reviewer looks for.

This repo has no GitHub issue integration. Never add a `Closes #` line or a
`Fixes #` line.

## 3. Body: what, why and how

```markdown
## What

- <what changed, one bullet per logical change>

## Why

- <the reason: the bug, the risk, or the goal - not the implementation>

## How

- <approach and main decisions - not every file touched>
```

Name the identifier, the download URL, the processor order and the Team ID a
reviewer needs to check. A recipe review is mostly a check of those 4 things, so
put them in the body rather than leaving them in the diff.

Say where `EndOfCheckPhase` sits when you add or move a download step. The
marker decides whether a CI run can reuse a cached download, and a reviewer
cannot see that from a diff of one file. See step 5 of
[[create-autopkg-recipes]].

End the body with the attribution line this session asks you to add, copied
exactly. It is a fixed string, so the ASCII rule and the emoji rule do not apply
to it. Add nothing else after it.

## 4. Commits

This repo merges pull requests rather than squashing them, so every commit
reaches `main`. A commit message is the permanent record in `git log main`, and
a title and body live only in GitHub. Write the message accordingly:

```
add the snowsql download and pkg recipes

SnowSQL ships a signed pkg behind a download page, so the download recipe
pulls the real URL with URLTextSearcher and pins the installer authority.
```

Rules for a commit:

- write the subject in the imperative and lowercase, under about 70 characters
- name the app in the subject
- end the message with the attribution trailer this session asks you to add,
  copied exactly

## Guidelines

- keep it scannable, with bullets and short phrases rather than paragraphs. If a
  bullet runs past one line, split it
- one idea per bullet, and 2 to 5 bullets per section. One bullet is fine
- what changed goes in What. The reason goes in Why. The approach goes in How.
  Do not repeat yourself across the 3
- use backticks for code references, such as `SnowSQL.download.recipe.yaml`,
  `CodeSignatureVerifier` and `com.github.jrmfong.download.SnowSQL`
- lead with the why when the what does not make it obvious
- be specific, and never write "various improvements" or "update recipes". Name
  the app, the file or the processor

## Anti-patterns

Avoid all of these:

- walls of text, or a bullet-by-bullet retelling of the diff
- a list of every file changed. The reviewer can read the diff, so explain the
  approach instead
- a `Closes #` line, as this repo has no GitHub issue integration
- pasting a whole recipe into the body. Link the file and name what changed
- pasting a code signature requirement string into the body. Name the Team ID
  and the bundle identifier instead
- secrets in the description, such as API keys, tokens or webhook URLs

## Apply

Show the title and body to the user for approval first. Then use `gh` if it is
available:

```sh
gh pr create --title "<summary>" --body "<body>"     # new PR
gh pr edit   --title "<summary>" --body "<body>"     # existing PR
```

If `gh` is missing or not authenticated, print the final title and body. The
user can then paste them into GitHub, or run `gh` themselves with a `!` command.

## Example

For the branch `add-snowsql-recipe`:

> Title: Add the SnowSQL download and pkg recipes
>
> Body:
>
> ## What
>
> - add `snowflake/SnowSQL.download.recipe.yaml` and
>   `snowflake/SnowSQL.pkg.recipe.yaml`, under
>   `com.github.jrmfong.download.SnowSQL`
>
> ## Why
>
> - the data team asked for SnowSQL in Self Service, and no public recipe takes
>   the arm64 build
>
> ## How
>
> - read the real pkg URL off the downloads page with `URLTextSearcher`, because
>   the vendor publishes no appcast
> - pin the installer authority for Snowflake Computing INC. (W4NT6CRQ7U) with
>   strict and deep verification on
> - keep `EndOfCheckPhase` straight after the download, so a CI run can reuse a
>   cached download

## Related

- house style for every word of prose you write: [[plain-technical-english]]
- authoring the recipes themselves, and where the marker goes:
  [[create-autopkg-recipes]]
