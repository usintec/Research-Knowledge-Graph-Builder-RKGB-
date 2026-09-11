---
name: GitHub push authentication
description: Authentication behavior observed when pushing this workspace to its GitHub origin.
---

For Git pushes from this workspace, GitHub accepted the workspace `GITHUB_TOKEN`
when sent as Basic authentication using the `x-access-token` username, while
the equivalent bearer extra header was rejected. The same token was accepted by
the GitHub API.

**Why:** The repository's HTTPS Git transport and API transport did not accept
the same Authorization header form, which caused a valid token to appear
invalid during the first push attempt.

**How to apply:** Keep the token in Replit Secrets and use a temporary Git
extra header or credential helper; never print or paste the token into chat.