---
name: doc-linter
description: Check a Markdown file against the house style before commit. Use on any doc a human wrote or an agent drafted. Returns line-level problems, or nothing when the file is clean.
---

# doc-linter

## When to use
Before committing any Markdown file. Cheap to run, so run it often.

## What it checks
- Em and en dashes, which should be commas or shorter sentences.
- Filler words that make prose read as machine-written.
- Tables whose Total row does not add up.

## Steps
1. Run the deterministic guards first. They are fast and never guess.
2. Only then ask a model for wording help, on the lines the guards left alone.
3. Keep the human as the last read before commit.

## Kill condition
If the guards never fire for a month, the rules are either perfect or unused.
Check which, then tighten them or remove them.

## Lesson
Checking the whole file, including frontmatter, produced false alarms on a
description that used a hyphenated term on purpose. Scope the check to the parts
that matter.
