param(
    [int]$TimeoutSeconds = 5
)

$ErrorActionPreference = "Stop"

function Write-CheckResult {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Message
    )

    $status = if ($Passed) { "PASS" } else { "FAIL" }
    Write-Host ("{0} {1} - {2}" -f $status, $Name, $Message)
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Uri,
        [hashtable]$Headers = @{}
    )

    try {
        $response = Invoke-WebRequest -Uri $Uri -Headers $Headers -TimeoutSec $TimeoutSeconds -UseBasicParsing
        $ok = [int]$response.StatusCode -ge 200 -and [int]$response.StatusCode -lt 400
        Write-CheckResult -Name $Name -Passed $ok -Message ("HTTP {0}" -f [int]$response.StatusCode)
        return $ok
    }
    catch {
        Write-CheckResult -Name $Name -Passed $false -Message $_.Exception.Message
        return $false
    }
}

$allPassed = $true
$masterKey = $env:LITELLM_MASTER_KEY
$authHeaders = @{}

if (-not $masterKey) {
    Write-Host 'Missing LITELLM_MASTER_KEY. Set it first:'
    Write-Host '$env:LITELLM_MASTER_KEY="sk-your-key"'
    $allPassed = $false
}
else {
    $authHeaders = @{ Authorization = "Bearer $masterKey" }
}

$allPassed = (Test-Endpoint -Name "vLLM tunnel" -Uri "http://127.0.0.1:8000/v1/models") -and $allPassed
$allPassed = (Test-Endpoint -Name "LiteLLM health" -Uri "http://127.0.0.1:4000/health" -Headers $authHeaders) -and $allPassed

if ($masterKey) {
    $allPassed = (Test-Endpoint -Name "LiteLLM models" -Uri "http://127.0.0.1:4000/v1/models" -Headers $authHeaders) -and $allPassed
}
else {
    Write-CheckResult -Name "LiteLLM models" -Passed $false -Message "missing LITELLM_MASTER_KEY"
}

$allPassed = (Test-Endpoint -Name "OpenWebUI homepage" -Uri "http://127.0.0.1:3000") -and $allPassed
$allPassed = (Test-Endpoint -Name "Platform exporter" -Uri "http://127.0.0.1:9108/healthz") -and $allPassed
$allPassed = (Test-Endpoint -Name "Dashboard API" -Uri "http://127.0.0.1:8088/api/healthz") -and $allPassed

if (-not $allPassed) {
    exit 1
}
