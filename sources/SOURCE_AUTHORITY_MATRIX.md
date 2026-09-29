# External Source Authority Matrix

The repository separates **what is legally/currently true in the game** from **how the community mirrors, implements, runs and analyses it**.

| Layer | Sources | Role | Can establish normative rule truth? |
|---|---|---|---|
| Normative | Games Workshop Core Rules, updates, FAQ/Errata, Faction Packs/Codex, MFM, official app, Event Companion | Current official rules/points | **Yes**, within scope/version |
| Current mirror | Wahapedia 11E | Readable current mirror, discovery, structured cross-check, drift detection | No |
| Structured implementation | BSData/wh40k-11e | Machine-readable roster implementation: units, options, constraints, categories, validation logic | No |
| Runtime projection | New Recruit app + Wiki | Shows how catalogue data behaves for actual users | No |
| Validation tooling | New Recruit Data Editor | Validate/edit BSData-compatible catalogues; future MCP/WebMCP integration candidate | No |
| Empirical analytics | BCP, Stat Check | Results, representation, matchups, event evidence | No |
| Expert analysis | Goonhammer / Ruleshammer / Competitive Innovations | Attributed interpretation, faction/list/meta analysis | No |
| Event overlay | WTC and specific event packs | Event-scoped rulings/terrain/format overlays | Only inside that event scope |
| Community intelligence | BSData issues, competitive communities | Early warning, bug reports, disputed interactions | No |
| Personal observation | User collection/hobby state | Physical ownership/build facts | Yes for personal collection state |

## Preferred source path by question

### Current rules wording

1. applicable current GW official source;
2. Wahapedia for readable discovery/cross-check;
3. BSData for implementation consequences;
4. New Recruit for runtime projection;
5. expert/community interpretation only as attributed analysis.

### Points / roster construction

1. current GW MFM / official app where applicable;
2. BSData implementation cross-check;
3. New Recruit runtime validation;
4. Wahapedia structured cross-check.

### Competitive strength / metagame

1. event/result datasets such as BCP;
2. aggregate analytics such as Stat Check;
3. expert analysis such as Goonhammer;
4. community discussion only as supplementary intelligence.

Analytics never changes a rules fact.

## Conflict handling

- **GW != any secondary source** → official controls normative truth; preserve drift evidence.
- **Wahapedia != BSData** → `SOURCE_CONFLICT`; check official source.
- **BSData != New Recruit projection** → `RUNTIME_PROJECTION_DRIFT`.
- **WTC != global matched play** → `EVENT_SCOPE_DIFFERENCE`, not a global overwrite.
- **secondary sources agree but official evidence is unavailable/unverified** → may be high-confidence secondary evidence, but not `CURRENT_VERIFIED` normative truth.
