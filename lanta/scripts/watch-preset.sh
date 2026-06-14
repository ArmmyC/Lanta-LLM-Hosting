#!/bin/bash
set -euo pipefail

# Optional login-node polling helper. Long-running watchdogs must comply with
# cluster policy. Prefer the Windows watchdog when possible.

PRESET=${PRESET:-qwen36-35b-a3b}
CHECK_EVERY_SECONDS=${CHECK_EVERY_SECONDS:-300}
ROOT=${ROOT:-/project/zz992000-zdevb/zz992005/ub127/SiliconCraft}
JOB_NAME=${JOB_NAME:-vllm-model}
ONCE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/watch-preset.sh [--once] [--dry-run] [--preset PRESET] [--interval SECONDS]

This foreground polling helper must only be used when allowed by cluster policy.
Press Ctrl+C to stop it.
EOF
}

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

is_supported_preset() {
  case "$1" in
    qwen36-27b|qwen36-35b-a3b|qwen3-coder-30b-a3b|qwen25-coder-32b|deepseek-coder-v2-lite)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --once)
      ONCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --preset)
      [ "$#" -ge 2 ] || { echo "--preset requires a value" >&2; exit 2; }
      PRESET=$2
      shift 2
      ;;
    --interval)
      [ "$#" -ge 2 ] || { echo "--interval requires a value" >&2; exit 2; }
      CHECK_EVERY_SECONDS=$2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! is_supported_preset "$PRESET"; then
  echo "Unsupported preset: $PRESET" >&2
  exit 2
fi

if ! [[ "$CHECK_EVERY_SECONDS" =~ ^[0-9]+$ ]] || [ "$CHECK_EVERY_SECONDS" -lt 30 ]; then
  echo "Interval must be an integer of at least 30 seconds." >&2
  exit 2
fi

trap 'log "Watchdog stopped."; exit 0' INT TERM

log "Starting Lanta job watchdog (preset=$PRESET, interval=${CHECK_EVERY_SECONDS}s, once=$ONCE, dry-run=$DRY_RUN)."

while true; do
  log "Checking Slurm job $JOB_NAME for user $USER..."
  if ! queue_output=$(squeue -u "$USER" -h -n "$JOB_NAME" -t PENDING,RUNNING -o '%i|%T|%M|%N'); then
    log "Slurm check failed."
    [ "$ONCE" -eq 1 ] && exit 1
  else
    active_job=$(printf '%s\n' "$queue_output" | sed -n '/[^[:space:]]/{p;q;}')
    if [ -n "$active_job" ]; then
      log "Active job found: $active_job"
    elif [ "$DRY_RUN" -eq 1 ]; then
      log "DRY RUN: would submit preset $PRESET from $ROOT."
    else
      log "No active job found. Submitting preset $PRESET..."
      if (cd "$ROOT" && CANCEL_EXISTING=0 bash scripts/submit-preset.sh "$PRESET"); then
        log "Submit command completed. Waiting for the next scheduled check before any further action."
      else
        log "Submission failed."
        [ "$ONCE" -eq 1 ] && exit 1
      fi
    fi
  fi

  [ "$ONCE" -eq 1 ] && exit 0
  log "Next check in $CHECK_EVERY_SECONDS seconds. Press Ctrl+C to stop."
  sleep "$CHECK_EVERY_SECONDS"
done
