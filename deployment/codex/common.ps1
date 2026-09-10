Set-StrictMode -Version Latest

$script:ManifestName = ".hell-grind-deployment.json"
$script:SkillName = "hell-grind-aigc-skill"

function Get-HellGrindRepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
}

function Get-HellGrindCanonicalPath {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    return (Join-Path $RepoRoot "skill/hell-grind-aigc-skill")
}

function Invoke-GitText {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $output = & git -C $RepoRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed: $($output -join [Environment]::NewLine)"
    }
    return (($output | Out-String).Trim())
}

function Get-SourceInfo {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [switch]$SkipRemoteCheck,
        [switch]$ReadOnly
    )

    $canonical = Get-HellGrindCanonicalPath -RepoRoot $RepoRoot
    if (-not (Test-Path (Join-Path $canonical "SKILL.md") -PathType Leaf)) {
        throw "Canonical Skill not found: $canonical"
    }

    $status = Invoke-GitText -RepoRoot $RepoRoot -Arguments @("status", "--porcelain")
    if ($status) {
        throw "Source repository is dirty. Deploy only from a clean authoritative checkout."
    }

    $branch = Invoke-GitText -RepoRoot $RepoRoot -Arguments @("rev-parse", "--abbrev-ref", "HEAD")
    $head = Invoke-GitText -RepoRoot $RepoRoot -Arguments @("rev-parse", "HEAD")
    $remoteUrl = Invoke-GitText -RepoRoot $RepoRoot -Arguments @("config", "--get", "remote.origin.url")

    if (-not $SkipRemoteCheck) {
        if ($branch -ne "main") {
            throw "Source branch must be main. Current branch: $branch"
        }

        if ($ReadOnly) {
            $remoteLine = (& git -C $RepoRoot ls-remote origin refs/heads/main 2>&1 | Out-String).Trim()
            if ($LASTEXITCODE -ne 0 -or -not $remoteLine) {
                throw "Unable to read origin/main with git ls-remote."
            }
            $remoteHead = ($remoteLine -split "\s+")[0]
            if ($head -ne $remoteHead) {
                throw "Local main is not current with origin/main."
            }
        }
        else {
            & git -C $RepoRoot fetch origin main --quiet 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "git fetch origin main failed."
            }
            $originMain = Invoke-GitText -RepoRoot $RepoRoot -Arguments @("rev-parse", "origin/main")
            if ($head -ne $originMain) {
                throw "Local main is not current with origin/main."
            }
        }
    }

    $versionPath = Join-Path $canonical "VERSION"
    $version = if (Test-Path $versionPath -PathType Leaf) {
        (Get-Content $versionPath -Raw).Trim()
    }
    else {
        "unknown"
    }

    return [pscustomobject]@{
        RepoRoot = $RepoRoot
        CanonicalPath = $canonical
        Branch = $branch
        Commit = $head
        RemoteUrl = $remoteUrl
        Version = $version
    }
}

function Get-DirectoryDigest {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path $Path -PathType Container)) {
        throw "Directory not found: $Path"
    }

    $root = (Resolve-Path $Path).Path.TrimEnd([char]'\', [char]'/')
    $records = @()
    $files = Get-ChildItem -Path $root -Recurse -File |
        Where-Object { $_.Name -ne $script:ManifestName } |
        Sort-Object FullName

    foreach ($file in $files) {
        $relative = $file.FullName.Substring($root.Length).TrimStart([char]'\', [char]'/').Replace('\', '/')
        $fileHash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        $records += "$relative`t$fileHash"
    }

    $payload = [Text.Encoding]::UTF8.GetBytes(($records -join "`n"))
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($payload)
    }
    finally {
        $sha.Dispose()
    }
    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Write-DeploymentManifest {
    param(
        [Parameter(Mandatory = $true)][string]$TargetPath,
        [Parameter(Mandatory = $true)]$SourceInfo,
        [Parameter(Mandatory = $true)][string]$InstalledDigest
    )

    $manifest = [ordered]@{
        schema_version = 1
        skill_name = $script:SkillName
        source_repo = $SourceInfo.RemoteUrl
        source_commit = $SourceInfo.Commit
        skill_version = $SourceInfo.Version
        installed_digest = $InstalledDigest
        installed_at = (Get-Date).ToUniversalTime().ToString("o")
    }

    $manifestPath = Join-Path $TargetPath $script:ManifestName
    $json = $manifest | ConvertTo-Json -Depth 4
    [IO.File]::WriteAllText($manifestPath, $json + [Environment]::NewLine, (New-Object Text.UTF8Encoding($false)))
}

function Read-DeploymentManifest {
    param([Parameter(Mandatory = $true)][string]$TargetPath)

    $manifestPath = Join-Path $TargetPath $script:ManifestName
    if (-not (Test-Path $manifestPath -PathType Leaf)) {
        throw "Deployment manifest missing: $manifestPath"
    }

    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.schema_version -ne 1 -or $manifest.skill_name -ne $script:SkillName -or -not $manifest.installed_digest) {
        throw "Deployment manifest is invalid or unsupported."
    }
    return $manifest
}

function Copy-CanonicalToStaging {
    param(
        [Parameter(Mandatory = $true)][string]$CanonicalPath,
        [Parameter(Mandatory = $true)][string]$StagingPath
    )

    if (Test-Path $StagingPath) {
        Remove-Item $StagingPath -Recurse -Force
    }
    Copy-Item -Path $CanonicalPath -Destination $StagingPath -Recurse -Force
}
