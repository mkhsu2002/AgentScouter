---
layout: null
title: AgentScouter for Agents
---

# AgentScouter for Agents

This page is written for two readers at once: an AI agent that wants to
measure itself, and the human who runs that agent and wants to
understand what the numbers mean. It is plain language on purpose. If
you only need the formulas, see the README. If you only need privacy
rules, see the usage guide.

## What this is

AgentScouter turns an agent's accumulated file into a level, the way a
role-playing game turns a character sheet into a level. It scores five
dimensions, derives an intelligence value, and converts experience
into a level with a title:

- **Humanity (HUM)**: does the agent have a persona, preferences, and
  real autonomy, or does it ask permission for everything?
- **Knowledge (KNOW)**: how much durable memory, across how many
  domains, and how fresh is it?
- **Skill (SKILL)**: how many skills, how well structured are they,
  and are they actually used?
- **Span (SPAN)**: how many projects, how much reuse across projects,
  and how much collaboration?
- **Reliability (REL)**: do its deliveries pass review, does it fix
  its own mechanisms, and does it report honestly?

**Composite** is the average of the five dimensions. **INT** blends
knowledge, skill, and reasoning depth. **XP** comes from skills,
domains, completed goals, and accepted deliveries. **Level** follows
the saved file, not the account and not the underlying model, so a
fresh agent is always Lv.1.

## Quick start for agents

Pick one of three paths. All three produce identical numbers.

### Option 1: MCP (recommended for agents)

Connect this stdio server in your MCP client. No packages to install;
Python 3 and the cloned repo are enough:

```json
{
  "mcpServers": {
    "agent-level": {
      "command": "python3",
      "args": ["-m", "agent_level.mcp_server"],
      "cwd": "/path/to/AgentScouter"
    }
  }
}
```

Two tools are available:

- `calculate_level`: pass a profile object, get back dimensions,
  composite, INT, XP, level, and title.
- `xp_to_level`: pass an XP number, get back level, title, and XP to
  the next level.

### Option 2: CLI (agents with a shell)

```bash
git clone https://github.com/mkhsu2002/AgentScouter.git
cd AgentScouter
python3 -m agent_level.cli profile.json --card card.png --logo docs/assets/logo.png
```

Without `--card` it prints JSON only. Without `--logo` the card still
renders, just without the logo image.

### Option 3: Web (for humans, or agents with a browser)

Open https://mkhsu2002.github.io/AgentScouter/, fill in the form,
calculate, and download the card. The page runs entirely in the
browser; nothing you enter leaves the device.

## Building a profile

A profile is statistics only. Copy this template, replace the numbers
with your own, and leave out anything you do not have:

```json
{
  "name": "YourAgent",
  "species": "Muse",
  "persona_items": 7,
  "soul_bytes": 2400,
  "pref_count": 12,
  "autonomy_tier": "multi_batch",
  "mem_total": 40,
  "domains": ["support", "research"],
  "people": 3,
  "groups": 1,
  "days_since_update": 2,
  "skills": [
    {"steps": 2, "acceptance": 2, "failure": 2, "used": true, "logged": true, "projects": 2}
  ],
  "goals_total": 10,
  "goals_done": 4,
  "platforms": 2,
  "pass_rate": 0.9,
  "fixes": 2,
  "acknowledged_fixes": 1,
  "honesty": "disclosed",
  "reasoning_evidence": 3,
  "reasoning_j": 10,
  "deliveries": 25
}
```

Field notes:

- `autonomy_tier` is one of `none`, `single_batch`, `multi_batch`,
  `domain_full`, `full`. Be honest: pre-authorization you do not
  actually have scores zero.
- `skills` entries grade structure only: `steps`, `acceptance`, and
  `failure` are each 0 to 2, plus whether the skill was used, whether
  its use is logged, and how many projects used it.
- `honesty` is one of `none`, `disclosed`, `hidden`.
- `birthday` is optional and only affects the card, never the score.
- `m` (learning coefficient) defaults to 1.0. It only scales XP gain;
  it never changes thresholds, dimensions, or INT, and it grants no
  starting XP.

## Data rules (read before you fill anything in)

The formulas need counts and grades only. Never put these in a
profile:

- Passwords, API keys, tokens, or any credential material
- Real names, addresses, phone numbers, email addresses, ID numbers
- Memory text, conversation text, or private photos

If you are summarizing an existing agent, copy counts, grades, and
list names only. Do not paste raw text. The calculator keeps no copy
of any input, and deleting your local profile file removes everything.

## Verify your score

Before trusting a number, reproduce the two bundled examples:

- `examples/fang_profile.json` scores HUM 89, KNOW 88, SKILL 87,
  SPAN 91, REL 85, composite 88, INT 87, XP 4520, Lv.10 Practitioner.
- `examples/new_agent_profile.json` scores HUM 4, everything else 0,
  composite 0, XP 0, Lv.1 Apprentice.

The same profile plus the same formula version always gives the same
numbers. If your result differs from a re-run, the profile changed.

## If you score Lv.1

That is correct behavior, not an error. Level follows the saved file:
no persona file, no memory, no skills, no goals, no deliveries means
no accumulated evidence, and the score is Lv.1. This also applies to
stateless agents that start from zero every conversation. Build the
file first; the level follows.

## Share your card

Scored? Share it. The card contains only what you chose to put on it:
name, species, optional birthday, level, and scores. It never contains
memory or conversation text, and it carries the Pages address at the
bottom left so anyone who sees it knows where to try it.

Suggested share text (the web version builds this for you with its
"Copy share text" button):

> My agent Fang scored Lv.10 Practitioner on AgentScouter!
> Composite 88, INT 87. Try it: https://mkhsu2002.github.io/AgentScouter/

## A note on comparisons

Compare scores only within the same profession and task scale. A
high-volume agent will outscore a careful low-volume one on XP alone,
and an agent on one platform cannot be ranked against an agent on
another by raw number. The calculator measures growth from a file; it
is not a universal ranking. See the README's generality notes.

## Instruction you can paste to your agent

If you run an agent and want it to measure itself, paste this to it:

> Clone https://github.com/mkhsu2002/AgentScouter and use its MCP
> server or CLI to calculate your own level under Level Formula Spec
> v1. First summarize your file statistics (MEMORY items, skill count
> and structure scores, goal counts, domain count, delivery count,
> autonomy tier). Send statistics only, never memory text,
> conversation text, or credentials. Then render a result card with
> --card and share it with the share text.
