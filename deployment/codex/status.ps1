[CmdletBinding()]
param(
    [string]$DestinationRoot = (Join-Path (Join-Path $HOME ".agents") "skills"),
    [switch]$SkipRemoteCheck
)

$ErrorActionPreference = "Stop"
$CanonicalRelativePath = "skill/hell-grind-aigc-skill"
$DefaultCodexSkillRoot = "$HOME/.agents/skills"
. (Join-Path $PSScriptRoot "common.ps1")

$targetPath = Join-Path $DestinationRoot "hell-grind-aigc-skill"

try {
    $repoRoot = Get-HellGrindRepoRoot
    $source = Get-SourceInfo -RepoRoot $repoRoot -SkipRemoteCheck:$SkipRemoteCheck -ReadOnly

    if (-not (Test-Path $targetPath -PathType Container)) {
        Write-Host "status=not-installed"
        Write-Host ("target={0}" -f $targetPath)
        exit 1
    }

    $manifest = Read-DeploymentManifest -TargetPath $targetPath
    $currentDigest = Get-DirectoryDigest -Path $targetPath
    if ($currentDigest -ne [string]$manifest.installed_digest) {
        Write-Host "status=local-drift"
        Write-Host ("installed_version={0}" -f $manifest.skill_version)
        Write-Host ("installed_commit={0}" -f $manifest.source_commit)
        Write-Host ("source_version={0}" -f $source.Version)
        Write-Host ("source_commit={0}" -f $source.Commit)
        exit 2
    }

    if ([string]$manifest.source_commit -eq $source.Commit) {
        Write-Host "status=current"
        $exitCode = 0
    }
    else {
        Write-Host "status=update-available"
        $exitCode = 1
    }

    Write-Host ("installed_version={0}" -f $manifest.skill_version)
    Write-Host ("installed_commit={0}" -f $manifest.source_commit)
    Write-Host ("source_version={0}" -f $source.Version)
    Write-Host ("source_commit={0}" -f $source.Commit)
    Write-Host ("target={0}" -f $targetPath)
    exit $exitCode
}
catch {
    Write-Error $_.Exception.Message
    exit 3
}
