---
layout: null
title: AgentScouter Usage Guide
---

# AgentScouter Usage Guide

AgentScouter is a level calculator for AI agents: feed it a profile of
file statistics and it returns five dimension scores, an intelligence
value, experience, a level with a title, and optionally a test result
card. The formula version is Level Formula Spec v1; the full formulas
are in the README.

[Back to the calculator](index.html)

## Quick start

Three ways to run it, all producing identical numbers:

- **Web**: open the GitHub Pages site, fill in the form, calculate, and
  download the result card.
- **CLI**: `python3 -m agent_level.cli profile.json`, plus
  `--card card.png` to render a card and `--logo logo.png` to put the
  logo at the card's top left.
- **MCP**: connect `python3 -m agent_level.mcp_server` to an MCP client
  and call the `calculate_level` and `xp_to_level` tools.

## Input

The calculator needs statistics only, never raw text:

- Counts: MEMORY items, skills, goals, people, domains, deliveries.
- Grades: persona items present, autonomy tier, skill structure scores,
  honest-reporting grade.
- Lists: domain names only, and per skill only its structure scores
  and the number of projects it was used in.

The examples `examples/fang_profile.json` and
`examples/new_agent_profile.json` run as-is: the first reproduces
Fang's v1 trial, the second is a fresh agent at Lv.1. Domain names in
the Fang example are translated to English for this repo; only the
count matters for the score, so the numbers are unchanged.

## Share your card

Scored your agent? Share the card. It contains only what you chose to
put on it: name, species, optional birthday, level, and scores. It
never contains your memory or conversation text, and the card itself
carries the Pages address at the bottom left so anyone who sees it
knows where to try it.

Suggested share text (the web version builds this for you with its
"Copy share text" button):

> My agent Fang scored Lv.10 Practitioner on AgentScouter!
> Composite 88, INT 87. Try it: https://mkhsu2002.github.io/AgentScouter/

Before posting, check the card once: if you left a birthday on it,
that birthday is public too. Leave it blank and it never appears.

## Personal data safety

This is the most important section. Read it before entering data.

### Local-only computation, no network

- The CLI and MCP versions are local processes: no network, no
  uploads, no telemetry.
- The web version's JavaScript runs entirely in your browser. Input
  lives only in that tab and disappears when you close it. The site
  has no backend and no tracking.
- The calculator keeps no copy of any input. Delete your local
  profile file and nothing remains.

### Minimum data principle

The formulas need counts and grades only. Never enter:

- Passwords, API keys, tokens, credential material
- Real names, addresses, phone numbers, email addresses, ID numbers,
  account names
- Conversation text, memory text, private photos

When summarizing an existing agent, copy counts, grades, and list
names only. Never paste raw text.

### Card sharing boundary

The card shows only four kinds of information you actively entered:
name, species, birthday, level and scores. Birthday is optional and
omitted when blank. Check the card before sharing to make sure it
holds nothing you want to keep private. Sharing a card is not sharing
your memory.

### MCP and file storage

- MCP runs over local stdio, not the network. Still, do not send a
  profile containing real personal data to an untrusted client, and
  do not store profile files in a public directory.
- The public repo holds only code, formulas, and example statistics,
  no user private data. The Fang example is aggregate counts only.

### GitHub Pages boundary

The Pages site is a static page with no database and no accounts.
Nothing you enter is recorded. The only thing that ever leaves your
device is the card image you download yourself.

## FAQ

- **Why is a fresh agent always Lv.1?**
  Level follows the saved file, not the account or the underlying
  model. No accumulated file means Lv.1. That is a design decision,
  not missing data.
- **Does the underlying model affect the score?**
  Only through the learning coefficient m, which scales experience
  gain. It does not change thresholds, dimension formulas, or INT,
  and it grants no starting experience.
- **Can a score be verified?**
  Yes. The same profile plus the same formula version always gives
  the same numbers, and the repo's tests reproduce both the Fang and
  the fresh-agent examples.
- **Can scores be compared?**
  Meaningfully only within the same profession and task scale.
  Comparing agents across platforms or task volumes by raw number
  alone distorts the picture; see the README's generality notes and
  roadmap.
