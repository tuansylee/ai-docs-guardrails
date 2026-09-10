---
title: Reference IDs
description: How Beacon builds and validates request reference IDs.
status: published
---

# Reference IDs

Every request returns a reference ID of the form REF-<number>-<check>. The two
check digits are the number modulo 97, so a mistyped ID is easy to detect.

Examples of valid IDs:

- REF-100024-17
- REF-100025-18
- REF-250000-31
