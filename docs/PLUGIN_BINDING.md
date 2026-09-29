# ChatGPT plugin binding

## Current project plugin

- Display name: **WH40K Tabletop Platform**
- Plugin package name: `wh40k-tabletop-platform`
- Plugin ID: `plugins_6abb8bb6fa408191adc7d026078a6310`
- Version: `0.2.0`
- Release ID: `pluginrel_6abb9106a710819188b1bd87744fe098`
- Created: 2026-09-29

## Authority boundary

The plugin is a **router and operating interface**, not the canonical knowledge store.

The live authority remains:

`Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Before substantive work, plugin skills are required to refresh current repository contracts rather than trusting bundled stale snapshots.

## Included skills

- `wh40k-project-router` — bootstrap, continuation and domain routing.
- `wh40k-knowledge-retrieval` — reuse promoted repository knowledge before reopening research.
- `wh40k-rules-research` — current rules/source revalidation, diff and promotion.
- `wh40k-roster-analytics` — patch-scoped competitive/meta + collection-aware roster analysis.
- `wh40k-repo-governance` — schemas, provenance, migrations, CI and repository integrity.\n- `wh40k-hobby-painting` — painting inventory, 540-recipe catalogue, substitutions, army pipelines and active painting projects.

## Update policy

When repository architecture changes materially, prefer updating the repository contract first. Update the plugin only when routing/bootstrap behavior, required contract paths, domain boundaries or tool integration changes.

Do not duplicate large repository datasets inside the plugin.
