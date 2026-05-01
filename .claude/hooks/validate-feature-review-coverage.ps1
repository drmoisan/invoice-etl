<#
.SYNOPSIS
    SubagentStop hook that validates feature-review coverage verdicts against the branch diff.

.DESCRIPTION
    Runs when the feature-review subagent terminates. Cross-checks the most recent
    policy-audit.<timestamp>.md under docs/features/active/**/ against the PR context
    summary at artifacts/pr_context.summary.txt and against existing coverage artifacts.

    Validation rules:
      - Enumerate languages that have changed files in the branch diff:
          .ts / .tsx            -> TypeScript
          .py                   -> Python
          .ps1 / .psm1          -> PowerShell
          .cs                   -> CSharp
      - For each language with one or more changed files, the policy audit must contain
        a coverage-scoped row or line that states an explicit PASS or FAIL verdict for
        that language. Scope-narrowing phrases on those rows are treated as validation
        failures:
          "informational only", "context only", "out of plan scope", "out of scope",
          "not applicable", "N/A", "UNVERIFIED".
      - If the coverage artifact for a language is present, repo-wide line coverage is
        parsed and compared against the 80 percent floor. When repo-wide coverage is
        below 80 percent and the audit does not carry a FAIL verdict on a coverage row
        for that language, validation fails.

    Coverage artifact paths by language:
        TypeScript  coverage/lcov.info                          (LCOV text)
        Python      artifacts/python/lcov.info                  (LCOV text)
        PowerShell  artifacts/pester/powershell-coverage.xml    (JaCoCo XML)
        CSharp      artifacts/csharp/coverage.xml               (JaCoCo XML)

    On a validation failure the script writes a block decision to stdout and exits 1.
    Read-only: inspects artifacts on disk and never modifies state.

.NOTES
    Compatible with PowerShell 7+.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
    $start = (Get-Location).Path
    $current = $start
    while ($true) {
        if (Test-Path (Join-Path $current '.claude')) { return $current }
        $parent = Split-Path $current -Parent
        if (-not $parent -or $parent -eq $current) { break }
        $current = $parent
    }
    return $start
}

function Get-LatestPolicyAudit {
    [OutputType([System.IO.FileInfo])]
    param([string]$RepoRoot)

    $activeRoot = Join-Path $RepoRoot 'docs/features/active'
    if (-not (Test-Path $activeRoot)) { return $null }

    Get-ChildItem -Path $activeRoot -Recurse -File -Filter 'policy-audit.*.md' |
        Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
}

function Get-ChangedLanguageSet {
    [OutputType([System.Collections.Hashtable])]
    param([string]$RepoRoot)

    $prSummary = Join-Path $RepoRoot 'artifacts/pr_context.summary.txt'
    $langs = [ordered]@{}
    if (-not (Test-Path $prSummary)) { return $langs }

    foreach ($line in Get-Content -Path $prSummary) {
        if ($line -notmatch '^\s*-\s+(\S+)\s+\(\+\d+/-\d+\)\s*$') { continue }
        $path = $matches[1]
        $ext = [IO.Path]::GetExtension($path).ToLowerInvariant()
        switch -Regex ($ext) {
            '^\.(ts|tsx)$' { $langs['TypeScript'] = $true }
            '^\.py$' { $langs['Python']     = $true }
            '^\.(ps1|psm1)$' { $langs['PowerShell'] = $true }
            '^\.cs$' { $langs['CSharp']     = $true }
        }
    }
    return $langs
}

function Get-LcovRepoCoverage {
    [OutputType([Nullable[double]])]
    param([string]$Path)

    if (-not (Test-Path $Path)) { return $null }

    $totalFound = 0
    $totalHit = 0
    foreach ($line in Get-Content -Path $Path) {
        if ($line.StartsWith('LF:')) {
            $totalFound += [int]($line.Substring(3))
        }
        elseif ($line.StartsWith('LH:')) {
            $totalHit += [int]($line.Substring(3))
        }
    }
    if ($totalFound -le 0) { return $null }
    return [math]::Round(($totalHit * 100.0) / $totalFound, 2)
}

function Get-JacocoRepoCoverage {
    [OutputType([Nullable[double]])]
    param([string]$Path)

    if (-not (Test-Path $Path)) { return $null }

    [xml]$doc = Get-Content -Path $Path -Raw
    $counters = $doc.SelectNodes('//counter[@type="LINE"]')
    if (-not $counters -or $counters.Count -eq 0) { return $null }

    $missed = 0
    $covered = 0
    foreach ($counter in $counters) {
        $missed += [int]$counter.missed
        $covered += [int]$counter.covered
    }
    $total = $missed + $covered
    if ($total -le 0) { return $null }
    return [math]::Round(($covered * 100.0) / $total, 2)
}

function Get-LanguageRepoCoverage {
    [OutputType([Nullable[double]])]
    param(
        [string]$RepoRoot,
        [string]$Language
    )

    switch ($Language) {
        'TypeScript' { return Get-LcovRepoCoverage -Path (Join-Path $RepoRoot 'coverage/lcov.info') }
        'Python' { return Get-LcovRepoCoverage -Path (Join-Path $RepoRoot 'artifacts/python/lcov.info') }
        'PowerShell' { return Get-JacocoRepoCoverage -Path (Join-Path $RepoRoot 'artifacts/pester/powershell-coverage.xml') }
        'CSharp' { return Get-JacocoRepoCoverage -Path (Join-Path $RepoRoot 'artifacts/csharp/coverage.xml') }
    }
    return $null
}

function Test-LanguageCoverageRow {
    [OutputType([System.Collections.Hashtable])]
    param(
        [string]$AuditText,
        [string]$Language,
        [Nullable[double]]$RepoWidePct
    )

    $languageLabelMap = @{
        'TypeScript' = @('TypeScript', 'typescript')
        'Python'     = @('Python', 'python', 'pytest')
        'PowerShell' = @('PowerShell', 'powershell', 'pester')
        'CSharp'     = @('C#', 'CSharp', 'csharp', '\.NET', 'dotnet')
    }

    $labels = $languageLabelMap[$Language]
    $labelPattern = '(?i)(' + (($labels | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')'

    $lines = $AuditText -split "`r?`n"
    $languageLines = $lines | Where-Object { $_ -match $labelPattern }

    if (-not $languageLines -or $languageLines.Count -eq 0) {
        return @{
            Ok     = $false
            Reason = "$Language has changed files on the branch but the policy-audit does not mention $Language."
        }
    }

    $coverageLines = $languageLines | Where-Object { $_ -match '(?i)(coverage|lcov|line[s]?\s+hit|pester)' }
    if (-not $coverageLines -or $coverageLines.Count -eq 0) {
        return @{
            Ok     = $false
            Reason = "$Language has changed files on the branch but no coverage-scoped row in the policy-audit mentions $Language."
        }
    }

    $narrowingPattern = '(?i)(informational only|context only|out of plan scope|out of scope|not applicable|\bN/A\b|\bUNVERIFIED\b)'
    $narrowing = $coverageLines | Where-Object { $_ -match $narrowingPattern }
    if ($narrowing -and $narrowing.Count -gt 0) {
        $first = ($narrowing | Select-Object -First 1).ToString().Trim()
        return @{
            Ok     = $false
            Reason = "$Language has changed files on the branch but a coverage-scoped row narrows scope: '$first'. Scope narrowing is not permitted for languages with changed files."
        }
    }

    $verdictLines = $coverageLines | Where-Object { $_ -match '\b(PASS|FAIL)\b' }
    if (-not $verdictLines -or $verdictLines.Count -eq 0) {
        return @{
            Ok     = $false
            Reason = "$Language coverage rows contain neither a PASS nor a FAIL verdict."
        }
    }

    if ($null -ne $RepoWidePct -and $RepoWidePct -lt 80.0) {
        $failLines = $coverageLines | Where-Object { $_ -match '\bFAIL\b' }
        if (-not $failLines -or $failLines.Count -eq 0) {
            return @{
                Ok     = $false
                Reason = ("{0} repo-wide coverage is {1}% (below the 80% floor) but the policy-audit contains no FAIL verdict on a coverage row for {0}." -f $Language, $RepoWidePct)
            }
        }
    }

    return @{ Ok = $true; Reason = $null }
}

function Write-BlockDecision {
    param([string]$Reason)

    $payload = [ordered]@{
        decision = 'block'
        reason   = $Reason
    } | ConvertTo-Json -Compress
    Write-Output $payload
}

try {
    $repoRoot = Get-RepoRoot
    $audit = Get-LatestPolicyAudit -RepoRoot $repoRoot
    if (-not $audit) {
        # No audit to validate. The existing SubagentStop artifact-presence hook covers this case.
        exit 0
    }

    $auditText = Get-Content -Path $audit.FullName -Raw
    $changedLanguages = Get-ChangedLanguageSet -RepoRoot $repoRoot

    if ($changedLanguages.Count -eq 0) {
        exit 0
    }

    $failures = [System.Collections.Generic.List[string]]::new()

    foreach ($lang in $changedLanguages.Keys) {
        $repoPct = Get-LanguageRepoCoverage -RepoRoot $repoRoot -Language $lang
        $result = Test-LanguageCoverageRow -AuditText $auditText -Language $lang -RepoWidePct $repoPct
        if (-not $result.Ok) {
            $failures.Add($result.Reason)
        }
    }

    if ($failures.Count -gt 0) {
        $header = "Feature-review coverage validation failed against branch diff."
        $body   = "  - " + ($failures -join "`n  - ")
        $footer = "Audit file: $($audit.FullName)`nFix the policy-audit to carry an explicit PASS or FAIL verdict per language with changed files, and reflect repo-wide coverage below 80% as FAIL."
        Write-BlockDecision -Reason ("{0}`n{1}`n{2}" -f $header, $body, $footer)
        exit 1
    }

    exit 0
}
catch {
    Write-BlockDecision -Reason ("Feature-review coverage validator error: {0}" -f $_.Exception.Message)
    exit 1
}

