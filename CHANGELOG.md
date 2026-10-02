# Changelog

## [Unreleased]

### Changed

- Migrate MCP server from `FastMCP` (mcp 1.x) to `MCPServer` (mcp 2.x).
  The `mcp.server.fastmcp.FastMCP` entry point was removed in mcp 2.0;
  the server now constructs `MCPServer(name, version=...)`, passing the
  version through the constructor instead of the removed private
  `_mcp_server.version` attribute. Tool decorators and `run()` are
  unchanged.

### Fixed

- Action pin comments now state the version actually pinned. The SHA is
  the security control, but the comment is the only part a human reads,
  so a wrong one hides a stale pin from every review — how
  `gh-action-pypi-publish` broke punt-kit's 0.12.0 release. Labels
  resolved against the GitHub API, and no SHA was changed.
- `markdownlint-cli2-action` is repinned from an unreleased commit on the
  action's default branch — ahead of every release tag including v24.2.0 —
  to the v24.2.0 release commit, and its `# v22` comment corrected. The
  workflow was already running code past v24.2.0 while the comment claimed
  v22; the pin now names an immutable released artifact rather than a
  moving branch head.

### Added

- `OPENROUTER_API_KEY` wired up in `.envrc` (canonical envrc rollout).

- Initial scaffolding for langlearn-imagegen.
- Added ROADMAP.md and refreshed README/DESIGN documentation.
