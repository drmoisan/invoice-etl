<#
.SYNOPSIS
    Pre-tool-use hook that blocks Bash promotion-script bypass attempts.

.DESCRIPTION
    This script is invoked by the Claude Code PreToolUse hook before any Bash
    command runs. It reads the tool input from the CLAUDE_TOOL_INPUT environment
    variable, inspects the attempted command text, and blocks direct promotion
    script execution that would bypass the repository's MCP-only promotion path.

    Forbidden command tokens:
      - new-potential-entry.ps1
      - new_potential_bug_entry
      - potential_to_issue
      - new_active_feature_folder

    The hook is read-only: it inspects the attempted command and emits a JSON
    allow-or-block decision without mutating the command text.

.NOTES
    Compatible with PowerShell 7+.
#>
[CmdletBinding()]
param()

$script:PromotionMcpOnlyBlockedReason = 'PROMOTION_MCP_ONLY_BLOCKED: Direct Bash promotion-script execution is not allowed in agent sessions. Use the drmCopilotExtension MCP promotion tools instead.'

function Get-PromotionMcpOnlyBlockedReason {
    <#
    .SYNOPSIS
        Return the canonical deny message for promotion-script bypass attempts.
    .OUTPUTS
        System.String
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    return $script:PromotionMcpOnlyBlockedReason
}

function Test-PromotionBypassToken {
    <#
    .SYNOPSIS
        Return $true when a Bash command contains a forbidden promotion token.
    .PARAMETER CommandText
        The Bash command text extracted from CLAUDE_TOOL_INPUT.
    .OUTPUTS
        System.Boolean
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory)]
        [string] $CommandText
    )

    # Inspect only the command text so the hook remains a narrow, non-mutating
    # policy gate for direct promotion-script bypass attempts.
    $forbiddenTokens = @(
        'new-potential-entry.ps1',
        'new_potential_bug_entry',
        'potential_to_issue',
        'new_active_feature_folder'
    )

    foreach ($token in $forbiddenTokens) {
        if ($CommandText.IndexOf($token, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            return $true
        }
    }

    return $false
}

function Get-PromotionMcpOnlyBlockDecision {
    <#
    .SYNOPSIS
        Construct the structured block decision for a forbidden Bash command.
    .OUTPUTS
        System.Collections.Specialized.OrderedDictionary
    #>
    [CmdletBinding()]
    [OutputType([System.Collections.Specialized.OrderedDictionary])]
    param()

    return [ordered]@{
        decision = 'block'
        reason   = (Get-PromotionMcpOnlyBlockedReason)
    }
}

function Invoke-PromotionMcpOnlyDecision {
    <#
    .SYNOPSIS
        Parse CLAUDE_TOOL_INPUT and return an allow-or-block decision.
    .PARAMETER ToolInputRaw
        The raw JSON tool payload supplied by Claude Code.
    .OUTPUTS
        System.Collections.Specialized.OrderedDictionary
    .NOTES
        Missing tool input or missing command text is treated as allow because
        non-Bash invocations or empty Bash requests cannot bypass promotion flow.
    #>
    [CmdletBinding()]
    [OutputType([System.Collections.Specialized.OrderedDictionary])]
    param(
        [string] $ToolInputRaw
    )

    if (-not $ToolInputRaw) {
        return [ordered]@{ decision = 'allow' }
    }

    try {
        $toolInput = $ToolInputRaw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "enforce-promotion-mcp-only hook received malformed JSON in CLAUDE_TOOL_INPUT: $_"
    }

    $commandText = $toolInput.command
    if (-not $commandText) {
        return [ordered]@{ decision = 'allow' }
    }

    if (Test-PromotionBypassToken -CommandText $commandText) {
        return Get-PromotionMcpOnlyBlockDecision
    }

    return [ordered]@{ decision = 'allow' }
}

# Allow dot-sourcing in tests without executing the entrypoint.
if ($MyInvocation.InvocationName -eq '.') {
    return
}

try {
    $decision = Invoke-PromotionMcpOnlyDecision -ToolInputRaw $env:CLAUDE_TOOL_INPUT
} catch {
    Write-Error $_
    exit 1
}

$decision | ConvertTo-Json -Compress | Write-Output

exit 0
