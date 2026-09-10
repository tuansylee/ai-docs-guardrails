---
name: release-notes-drafter
description: Draft release notes from a list of merged changes. Use when a version is about to ship and you have the raw change list. Returns a grouped draft for a human to check, never the final text.
---

# release-notes-drafter

## When to use
A version is about to ship and you have the merged pull requests or commit
subjects. Do not use this for marketing copy.

## Steps
1. Group changes into Added, Changed, Fixed, Deprecated.
2. Write one plain sentence per change, in the past tense.
3. Flag anything that changes an interface, so a human decides whether it needs a
   migration note.
4. Stop. A person reads the draft and signs off. The agent is not the last gate.

## Kill condition
If the team stops reading the draft and writes raw notes by hand for two releases
in a row, delete this skill. It is not paying for itself.

## Lesson
An early version invented a "Security" section when there were no security
changes, because the template carried that heading. A template should carry
structure, not empty headings that invite made-up content.
