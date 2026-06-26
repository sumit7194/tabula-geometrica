#!/bin/bash
# Bounded VM retry-launcher (2026-06-26 overnight): the L4 is stocked out; poll for capacity (~4h), and the moment it
# returns, ship + run the queued GPU job(s), pull results, then STOP the VM (so it never idles). Honors the user's
# "run as much as you can on the VM, shut down if nothing left" while they sleep. Fully logged; bounded; self-stopping.
set -u
ZONE=us-east1-d; VM=alphaludo-l4
LREPO=/Users/sumit/Github/SpaceTime/curvature
RREPO='~/spacetime/tabula-geometrica/curvature'
LOG=/tmp/vm_retry_launcher.log
say(){ echo "$(date '+%H:%M:%S') $*" | tee -a "$LOG"; }

say "launcher start (retry up to 16x / ~4h)"
for i in $(seq 1 16); do
  if gcloud compute instances start "$VM" --zone="$ZONE" >>"$LOG" 2>&1; then
    say "VM STARTED on retry $i -- shipping + launching queue"
    sleep 40
    # ship the new/required scripts (disk persists 136/collapse across stop, but re-ship to be safe)
    for f in scripts/137_choptuik_pinn_v2.py scripts/136_choptuik_pinn.py; do
      gcloud compute scp "$LREPO/$f" "$VM:$RREPO/scripts/" --zone="$ZONE" >>"$LOG" 2>&1
    done
    gcloud compute scp "$LREPO/hailmary/collapse.py" "$VM:$RREPO/hailmary/" --zone="$ZONE" >>"$LOG" 2>&1
    # verify GPU is actually free (do NOT contend with Ludo); only launch if free
    FREE=$(gcloud compute ssh "$VM" --zone="$ZONE" --command='nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l' 2>/dev/null)
    if [ "${FREE:-1}" != "0" ]; then
      say "GPU NOT free (Ludo?) -- not contending; stopping VM and giving up"
      gcloud compute instances stop "$VM" --zone="$ZONE" >>"$LOG" 2>&1; exit 0
    fi
    # launch the PINN-improve job (137: subcritical + supercritical + Fourier ablation) on CUDA, detached
    gcloud compute ssh "$VM" --zone="$ZONE" --command="cd $RREPO; setsid ./.venv/bin/python scripts/137_choptuik_pinn_v2.py --device cuda >/tmp/137.out 2>&1 </dev/null & sleep 6; echo launched 137" >>"$LOG" 2>&1
    say "137 launched -- monitoring (up to ~2h)"
    for j in $(seq 1 24); do
      sleep 300
      R=$(gcloud compute ssh "$VM" --zone="$ZONE" --command='pgrep -f 137_choptuik >/dev/null && echo R || echo D' 2>/dev/null | tail -1)
      [ "$R" = "D" ] && { say "137 finished after ~$((j*5))min"; break; }
    done
    # pull results back to the Mac (uncommitted -- documented on next engage)
    for ext in json png; do
      gcloud compute scp "$VM:$RREPO/results/137_choptuik_pinn_v2.$ext" "$LREPO/results/" --zone="$ZONE" >>"$LOG" 2>&1
    done
    say "results pulled. tail of 137 output:"; gcloud compute ssh "$VM" --zone="$ZONE" --command='grep -vE "Warning|warn" /tmp/137.out | tail -12' >>"$LOG" 2>&1
    gcloud compute instances stop "$VM" --zone="$ZONE" >>"$LOG" 2>&1
    say "VM STOPPED. launcher DONE."
    exit 0
  fi
  say "stockout (retry $i/16) -- sleeping 15min"
  sleep 900
done
say "gave up: stockout persisted ~4h. VM stays stopped (no cost). jobs remain queued for the user."
