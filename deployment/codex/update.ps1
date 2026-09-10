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
$backupPath = $null
$targetPath = Join-Path $DestinationRoot "hell-grind-aigc-skill"

try {
    $repoRoot = Get-HellGrindRepoRoot
    $source = Get-SourceInfo -RepoRoot $repoRoot -SkipRemoteCheck:$SkipRemoteCheck

    if (-not (Test-Path $targetPath -PathType Container)) {
        throw "Codex Skill target is not installed: $targetPath. Use install.ps1 first."
    }

    $manifest = Read-DeploymentManifest -TargetPath $targetPath
    $currentDigest = Get-DirectoryDigest -Path $targetPath
    if ($currentDigest -ne [string]$manifest.installed_digest) {
        throw "Installed Skill has local drift. Refusing to overwrite local changes."
    }

    if ([string]$manifest.source_commit -eq $source.Commit) {
        Write-Host "Hell Grind Codex Skill is already current."
        Write-Host ("version={0}" -f $source.Version)
        Write-Host ("source_commit={0}" -f $source.Commit)
        exit 0
    }

    $stagingPath = Join-Path $DestinationRoot (".hell-grind-aigc-skill.staging.{0}" -f $PID)
    $backupPath = Join-Path $DestinationRoot (".hell-grind-aigc-skill.backup.{0}" -f $PID)

    Copy-CanonicalToStaging -CanonicalPath $source.CanonicalPath -StagingPath $stagingPath
    $newDigest = Get-DirectoryDigest -Path $stagingPath
    Write-DeploymentManifest -TargetPath $stagingPath -SourceInfo $source -InstalledDigest $newDigest

    Move-Item -Path $targetPath -Destination $backupPath
    Move-Item -Path $stagingPath -Destination $targetPath
    $stagingPath = $null
    Remove-Item $backupPath -Recurse -Force
    $backupPath = $null

    Write-Host "Updated Hell Grind Codex Skill"
    Write-Host ("target={0}" -f $targetPath)
    Write-Host ("version={0}" -f $source.Version)
    Write-Host ("source_commit={0}" -f $source.Commit)
    exit 0
}
catch {
    if ($stagingPath -and (Test-Path $stagingPath)) {
        Remove-Item $stagingPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    if ($backupPath -and (Test-Path $backupPath) -and -not (Test-Path $targetPath)) {
        Move-Item -Path $backupPath -Destination $targetPath -ErrorAction SilentlyContinue
    }
    Write-Error $_.Exception.Message
    exit 1
}
