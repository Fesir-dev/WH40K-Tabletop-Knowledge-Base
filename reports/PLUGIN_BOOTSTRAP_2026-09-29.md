# WH40K Tabletop Platform plugin bootstrap — 2026-09-29

Created the first private ChatGPT plugin for the tabletop project.

## Identity

- name: `wh40k-tabletop-platform`
- display: **WH40K Tabletop Platform**
- version: `0.1.0`
- plugin ID: `plugins_6abb8bb6fa408191adc7d026078a6310`
- release ID: `pluginrel_6abb8bb83a38819186c8994218f7e81a`

## Design decision

The plugin deliberately does not embed a static copy of the knowledge base.

Instead it knows the canonical repository identity and mandatory bootstrap paths, then refreshes current `main` contracts before substantive work. This prevents the plugin from drifting every time source authority, analytics lineage or repository schemas evolve.

## Initial skills

1. project router/bootstrap;
2. promoted knowledge retrieval;
3. current rules/source research;
4. roster/meta analytics;
5. repository governance.

## Next likely plugin increments

After live use, evaluate dedicated skills for:

- physical collection engineering;
- hobby/paint/material workflows;
- automated source-monitor/update intake;
- New Recruit editor/runtime validation;
- exact faction-specific workflows if generic routing becomes too broad.
