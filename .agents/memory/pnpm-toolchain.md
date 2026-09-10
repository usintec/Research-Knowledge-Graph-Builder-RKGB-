---
name: pnpm toolchain
description: Environment-specific guidance for reproducible pnpm installs in this workspace
---

When the workspace declares a pnpm version that is not already available, Corepack may repeatedly
try to download it and make `pnpm install` appear hung. Keep `packageManager` aligned with the
installed pnpm version unless the environment is intentionally being provisioned for another
version.

**Why:** The initial install stalled because Corepack attempted to fetch a declared older pnpm
version even though a newer pnpm binary was already available locally.

**How to apply:** Check `pnpm --version` before changing the package manager declaration or
diagnosing an install timeout as a dependency problem.
