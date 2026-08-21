#!/usr/bin/env bash
# Machine headroom, measured correctly. Exists because the same reading was got wrong twice in one night.
#
# TRAP 1 -- THE PAGE SIZE IS NOT 4096 ON APPLE SILICON. It is 16384. A hand-written awk one-liner that captures
#   the page size and then hardcodes 4096 anyway is off by exactly 4x, in the CONSERVATIVE direction, which is
#   why it does not announce itself: it stands runs down instead of crashing them. Read the size, then USE it.
# TRAP 2 -- SWAP-USED IS A RESIDUAL, NOT AN ACTIVITY. macOS allocates swap eagerly and compresses aggressively;
#   1.3 GB of swap alongside 7 GB free is ordinary steady state, and after a large process exits it is mostly
#   evicted pages nobody has faulted back. The metric meaning "paging NOW" is the PAGEOUT RATE -- two samples.
#   A cumulative counter answers a question about history, not about now.
set -eu   # NOT pipefail: `| head` closing the pipe early is normal here, not an error
INTERVAL="${1:-10}"
PS=$(vm_stat | sed -n '1s/.*page size of \([0-9]*\) bytes.*/\1/p')
pg() { vm_stat | sed -n "s/^$1: *\([0-9]*\)\.*$/\1/p" | head -1; }
f=$(pg "Pages free"); i=$(pg "Pages inactive")
po1=$(pg "Pageouts"); sleep "$INTERVAL"; po2=$(pg "Pageouts")
awk -v ps="$PS" -v f="$f" -v i="$i" -v a="$po1" -v b="$po2" -v dt="$INTERVAL" -v ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
BEGIN{
  printf "%s  page size %d B\n", ts, ps
  printf "  free            %6.2f GB\n", f*ps/1073741824
  printf "  free+inactive   %6.2f GB   <- usable headroom\n", (f+i)*ps/1073741824
  printf "  pageout rate    %6d pages / %ds   %s\n", b-a, dt, ((b-a)>0 ? "PAGING" : "not paging")
}'
echo "  top consumers:"
ps -Ao rss,pid,args | sort -rn | head -4 | awk '{printf "    %6.0f MB  pid %-6s %.55s\n", $1/1024, $2, substr($0, index($0,$3))}'
