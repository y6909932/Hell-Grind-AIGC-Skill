[CmdletBinding()]
param(
    [string]$DestinationRoot = (Join-Path (Join-Path $HOME ".agents") "skills"),
    [switch]$SkipRemoteCheck
)

$ErrorActionPreference = "Stop"
$CanonicalRelativePath = "skill/hell-grind-aigc-skill"
$DefaultCodexSkillRoot = "$HOME/.agents/skills"
. (Join-Path $PSScriptRoot "common.ps1")

$stagingPath = $null
try {
    $repoRoot = Get-HellGrindRepoRoot
    $source = Get-SourceInfo -RepoRoot $repoRoot -SkipRemoteCheck:$SkipRemoteCheck

    if (-not (Test-Path $DestinationRoot -PathType Container)) {
        New-Item -ItemType Directory -Path $DestinationRoot -Force | Out-Null
    }

    $targetPath = Join-Path $DestinationRoot "hell-grind-aigc-skill"
    if (Test-Path $targetPath) {
        throw "Codex Skill target already exists: $targetPath. Use update.ps1 instead."
    }

    $stagingPath = Join-Path $DestinationRoot (".hell-grind-aigc-skill.staging.{0}" -f $PID)
    Copy-CanonicalToStaging -CanonicalPath $source.CanonicalPath -StagingPath $stagingPath
    $digest = Get-DirectoryDigest -Path $stagingPath
    Write-DeploymentManifest -TargetPath $stagingPath -SourceInfo $source -InstalledDigest $digest

    Move-Item -Path $stagingPath -Destination $targetPath
    $stagingPath = $null

    Write-Host "Installed Hell Grind Codex Skill"
    Write-Host ("target={0}" -f $targetPath)
    Write-Host ("version={0}" -f $source.Version)
    Write-Host ("source_commit={0}" -f $source.Commit)
    Write-Host "Restart Codex if the new Skill does not appear immediately."
    exit 0
}
catch {
    if ($stagingPath -and (Test-Path $stagingPath)) {
        Remove-Item $stagingPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Error $_.Exception.Message
    exit 1
}
