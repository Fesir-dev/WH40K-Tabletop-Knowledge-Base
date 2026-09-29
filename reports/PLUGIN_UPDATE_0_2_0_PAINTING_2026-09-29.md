# WH40K Tabletop Platform plugin update — 0.2.0 — 2026-09-29

## Release

- plugin ID: `plugins_6abb8bb6fa408191adc7d026078a6310`
- version: `0.2.0`
- release ID: `pluginrel_6abb9106a710819188b1bd87744fe098`

## Added

`wh40k-hobby-painting`

The skill routes painting questions to the normalized repository authority under `hobby/painting/`.

It explicitly separates:

- physical paint/material inventory;
- recipe/technique knowledge;
- active painting-project state;
- dated economics/pricing;
- manufacturer specifications/provenance.

The project router and knowledge-retrieval skill were also updated so painting work starts from `hobby/painting/current.json` rather than a stale workbook assumption.

## Repository baseline

This plugin update follows painting KB migration commit `e811540a5fcce900be253a0e60ca88e5a66023fc`, whose CI completed successfully.
