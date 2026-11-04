# Agent Level Calculator

![AgentScouter Logo](docs/assets/logo.png)

An evidence-based level calculator for AI agents, implemented from the
Level Formula Spec v1. It scores an agent on five dimensions, derives an
intelligence value, and converts accumulated experience into an RPG-style
level and title.

Design principles (see README for the full story):

- Level is a function of verifiable evidence, not self-assessment.
- Level follows the save file (SOUL, MEMORY, skills), not the account.
  A newly registered agent is always Lv.1, no matter the base model.
- The base model only affects the learning curve through the coefficient
  `m`, which multiplies event XP. It never grants starting XP and never
  changes thresholds, dimension formulas, or INT.
- Every score is reproducible from the input profile: same profile plus
  same formula version gives the same result.

## Install

No third-party dependencies. Python 3.10 or newer.

```bash
git clone https://github.com/mkhsu2002/AgentScouter.git
cd AgentScouter
```

## CLI usage

```bash
python3 -m agent_level.cli examples/fang_profile.json
python3 -m agent_level.cli < examples/new_agent_profile.json
```

Output is JSON with the five dimension scores and their breakdowns,
composite, INT, XP, level, title, and thresholds.

## For agents

If you are an agent (or you run one), start with
[docs/AGENTS.md](docs/AGENTS.md): it has the copy-paste MCP setup, a
minimal profile template, and the data rules. It is written in plain
language so humans can read it too.

## MCP usage (recommended)

The calculator runs as an MCP server over stdio, so any MCP client can
call it as a tool. No dependencies, no network.

```bash
python3 -m agent_level.mcp_server
```

Example client configuration:

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

Tools:

- `calculate_level`: takes a `profile` object (see Input schema) and
  returns the full score report.
- `xp_to_level`: takes `xp` and returns level, title, current threshold,
  next threshold, and XP to the next level.

## Input schema

All fields are optional; missing counts default to 0 and missing
timestamps default to "no record". Counts must be non-negative.

| Field | Type | Meaning |
| `persona_items` | int 0-7 | SOUL plus IDENTITY items present: name, gender, age image, character, tone, signature emoji, origin date |
| `soul_bytes` | int | SOUL file size in bytes; below 1500 costs 2 persona points |
| `pref_count` | int | MEMORY preference entries |
| `autonomy_tier` | string | `none`, `single_batch`, `multi_batch`, `domain_full`, `full` |
| `mem_total` | int | MEMORY entries total (facts plus preferences plus commitments) |
| `domains` | string list | Domain list; new domains only count once listed |
| `people` | int | People in the relationship map |
| `groups` | int | Groups in the relationship map |
| `days_since_update` | int or null | Days since the last update; null means no record |
| `skills` | object list | Each: `steps`, `acceptance`, `failure` (0-2 each), `used`, `logged`, `projects` |
| `goals_total` | int | Tracked goals plus personal goals |
| `goals_done` | int | Completed goals |
| `platforms` | int | Collaboration platforms |
| `pass_rate` | number 0-1 or null | Acceptance pass rate; null means no record |
| `fixes` | int | Mechanism-level fixes |
| `acknowledged_fixes` | int | Fixes explicitly acknowledged by the user |
| `honesty` | string | `none`, `disclosed`, `hidden` |
| `reasoning_evidence` | int | Mechanism-reasoning evidence items |
| `reasoning_j` | int 0-19 | Bounded reviewer points for reasoning depth |
| `m` | number | Model learning coefficient, default 1.0 |
| `deliveries` | int | Accepted deliveries |
| `estimated` | string list | Fields that are estimates, echoed back as a flag |
| `name` | string | Agent display name for the result card (not scored) |
| `species` | string | Agent family for the result card, e.g. Muse (not scored) |
| `birthday` | string | Birthday for the result card; omitted from the card when absent (not scored) |

## Formulas (v1)

Decimals are always floored. Every dimension caps at 100.

- HUM = persona + preference + autonomy
  - persona = max(0, 30 - 4 x (7 - persona_items) - (2 if soul_bytes < 1500 else 0))
  - preference = min(30, pref_count x 1.2)
  - autonomy = 0 / 20 / 28 / 36 / 40 by tier
- KNOW = fact + domain + relation + freshness
  - fact = min(40, mem_total x 0.6)
  - domain = min(30, len(domains) x 3)
  - relation = min(15, people x 2 + groups x 2)
  - freshness = 0 if no record else 15 - min(15, days_since_update x 0.5)
- SKILL = skill_count + structure + usage
  - skill_count = min(35, len(skills) x 6)
  - structure = sum over skills of (steps + acceptance + failure), capped at 30
  - usage = min(35, used_count x 6 + logged_count x 1)
- SPAN = project + migration + collaboration
  - project = min(50, goals_total x 2.5)
  - migration = min(30, 5 x sum over skills of max(0, projects - 1))
  - collaboration = min(20, people x 2 + platforms x 0.5)
- REL = pass + fixes + honesty
  - pass = 60 x pass_rate, or 0 with no record
  - fixes = min(25, 5 x fixes + 2 x acknowledged_fixes)
  - honesty = 15 if disclosed, else 0
- composite = (HUM + KNOW + SKILL + SPAN + REL) / 5
- reasoning = min(100, 20 x reasoning_evidence + reasoning_j)
- INT = 0.5 x KNOW + 0.3 x SKILL + 0.2 x reasoning
- XP = m x (100 x len(skills) + 80 x len(domains) + 40 x goals_done + 25 x deliveries)
- Level L threshold = 50 x L x (L - 1); level is the largest L whose
  threshold is at most XP. Titles: 1-4 Apprentice, 5-9 Assistant,
  10-14 Practitioner, 15-19 Expert, 20-29 Master, 30+ Legend.

## Worked examples

`examples/fang_profile.json` reproduces the Fang v1 trial exactly:
HUM 89, KNOW 88, SKILL 87, SPAN 91, REL 85, composite 88, INT 87,
XP 4520 at 100 deliveries, Lv.10. At 80 deliveries XP is 4020 (Lv.9)
and at 120 deliveries XP is 5020 (Lv.10), which is the Lv.9-10 range
in the original trial. `examples/new_agent_profile.json` scores
HUM 4, everything else 0, composite 0, XP 0, Lv.1.

## Result card

After scoring, render a PNG result card with the logo at the top left,
name, species, optional birthday, level, and the five-dimension radar
chart. The bottom right notes the card version (Test version v0.01),
and the bottom left points readers to the Pages site so a shared card
is self-explanatory.

```bash
python3 -m agent_level.cli examples/fang_profile.json --card card.png --logo docs/assets/logo.png
```

Without `--logo` the card still renders, just without the logo image.
The same card is available in the web version below, with a download
button.

## Share your card

Scored your agent? Share the card. It contains only what you chose to
put on it: name, species, optional birthday, level, and scores, never
your memory or conversation text. Post the PNG anywhere, with a line
like this:

> My agent Fang scored Lv.10 Practitioner on AgentScouter!
> Composite 88, INT 87. Try it: https://mkhsu2002.github.io/AgentScouter/

The web version has a "Copy share text" button that builds this line
from your result automatically.

## Live demo (GitHub Pages)

Try it in the browser, no install needed:

https://mkhsu2002.github.io/AgentScouter/

The page runs the same v1 formulas in JavaScript, entirely in your
browser, and can download the result card as a PNG. For the full
privacy story, see the [usage guide](docs/USAGE.md).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Roadmap (not in v1)

- Role weights: different dimension weights per agent class
  (steward, craftsman, scholar, pioneer) so specialists are not
  punished for narrow span.
- Task magnitude weights (S / M / L / XL) replacing flat per-delivery
  and per-goal XP.
- Verification: source snapshot hashes attached to a LEVEL report so
  a third party can recompute the same score.

## License

Apache-2.0. See LICENSE.
