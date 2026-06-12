#!/bin/bash
# Serve the training dashboard. Always rooted at the repo, port 8788.
cd "$(dirname "$0")"
lsof -ti :8788 | xargs kill 2>/dev/null
exec python3 -m http.server 8788
