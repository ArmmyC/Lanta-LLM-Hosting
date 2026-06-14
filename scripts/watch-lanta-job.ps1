[CmdletBinding()]
param(
    [ValidateSet(
        "qwen36-27b",
        "qwen36-35b-a3b",
        "qwen3-coder-30b-a3b",
        "qwen25-coder-32b",
        "deepseek-coder-v2-lite"
    )]
    [string]$Preset = "qwen36-35b-a3b",

    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$RemoteHost = "lanta",

    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$RemoteUser = "ub127",

    [ValidatePattern('^/[A-Za-z0-9._/-]+$')]
    [string]$RemoteRoot = "/project/zz992000-zdevb/zz992005/ub127/SiliconCraft",

    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$JobName = "vllm-model",

    [ValidateRange(30, 86400)]
    [int]$CheckEverySeconds = 300,

    [switch]$Once,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Write-WatchLog {
    param([Parameter(Mandatory)][string]$Message)

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Invoke-LantaSsh {
    param([Parameter(Mandatory)][string]$Command)

    $output = & ssh $RemoteHost $Command 2>&1
    $exitCode = $LASTEXITCODE
    return [pscustomobject]@{
        ExitCode = $exitCode
        Output = @($output)
    }
}

function Test-LantaJob {
    Write-WatchLog "Checking Lanta job $JobName on $RemoteHost..."
    $checkCommand = "squeue -u $RemoteUser -h -n $JobName -t PENDING,RUNNING -o '%i|%T|%M|%N'"
    $result = Invoke-LantaSsh -Command $checkCommand

    if ($result.ExitCode -ne 0) {
        $detail = ($result.Output | Out-String).Trim()
        if ($detail) {
            Write-WatchLog "SSH or Slurm check failed: $detail"
        } else {
            Write-WatchLog "SSH or Slurm check failed with exit code $($result.ExitCode)."
        }
        return [pscustomobject]@{ Success = $false; ActiveJob = $null }
    }

    $activeJob = $result.Output |
        ForEach-Object { $_.ToString().Trim() } |
        Where-Object { $_ -match '^[0-9_.+]+\|(PENDING|RUNNING)\|' } |
        Select-Object -First 1

    return [pscustomobject]@{ Success = $true; ActiveJob = $activeJob }
}

function Submit-LantaPreset {
    if ($DryRun) {
        Write-WatchLog "DRY RUN: would submit preset $Preset from $RemoteRoot."
        return $true
    }

    Write-WatchLog "No active job found. Submitting preset $Preset..."
    $submitCommand = "cd '$RemoteRoot' && CANCEL_EXISTING=0 bash scripts/submit-preset.sh '$Preset'"
    $result = Invoke-LantaSsh -Command $submitCommand

    if ($result.ExitCode -ne 0) {
        $detail = ($result.Output | Out-String).Trim()
        if ($detail) {
            Write-WatchLog "Submission failed: $detail"
        } else {
            Write-WatchLog "Submission failed with exit code $($result.ExitCode)."
        }
        return $false
    }

    $detail = ($result.Output | Out-String).Trim()
    if ($detail) {
        Write-WatchLog "Submit output: $detail"
    }
    Write-WatchLog "Submit command completed. Waiting for the next scheduled check before any further action."
    return $true
}

Write-WatchLog "Starting Lanta job watchdog (preset=$Preset, interval=${CheckEverySeconds}s, once=$Once, dry-run=$DryRun)."

while ($true) {
    try {
        $check = Test-LantaJob
        if (-not $check.Success) {
            if ($Once) { exit 1 }
        } elseif ($check.ActiveJob) {
            Write-WatchLog "Active job found: $($check.ActiveJob)"
        } else {
            $submitted = Submit-LantaPreset
            if (-not $submitted -and $Once) { exit 1 }
        }
    } catch {
        Write-WatchLog "Watchdog check failed: $($_.Exception.Message)"
        if ($Once) { exit 1 }
    }

    if ($Once) { exit 0 }

    Write-WatchLog "Next check in $CheckEverySeconds seconds. Press Ctrl+C to stop."
    Start-Sleep -Seconds $CheckEverySeconds
}
