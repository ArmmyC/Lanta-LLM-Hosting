from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_watchdog_has_safe_operating_modes():
    script = (ROOT / "scripts" / "watch-lanta-job.ps1").read_text(encoding="utf-8")

    assert '[string]$Preset = "qwen36-35b-a3b"' in script
    assert "[switch]$Once" in script
    assert "[switch]$DryRun" in script
    assert "PENDING,RUNNING" in script
    assert "CANCEL_EXISTING=0 bash scripts/submit-preset.sh" in script
    assert "scancel" not in script


def test_lanta_watchdog_is_foreground_and_policy_aware():
    script = (ROOT / "lanta" / "scripts" / "watch-preset.sh").read_text(
        encoding="utf-8"
    )

    assert "set -euo pipefail" in script
    assert "PRESET=${PRESET:-qwen36-35b-a3b}" in script
    assert "PENDING,RUNNING" in script
    assert 'CANCEL_EXISTING=0 bash scripts/submit-preset.sh "$PRESET"' in script
    assert "cluster policy" in script
    assert "nohup" not in script
    assert "scancel" not in script
