<#
.SYNOPSIS
  Incremental backup of this project and its Claude session history to company OneDrive.

.DESCRIPTION
  Copies only new and changed files into <OneDrive>\Liminality-french-swap-spreads-backup-current\.
  Same design as tools\backup-to-onedrive.ps1 in C:\Liminality-put-writing-strategy, which has
  run hourly since 2026-09-22.

  COPY-ONLY, NEVER DELETE. There is deliberately no /MIR or /PURGE: if a file disappears from
  this machine it must NOT disappear from the backup on the next run, since that is the exact
  failure this exists to insure against. The cost is that files deleted on purpose linger.

  Paths come from environment variables where possible, so there is no user-specific text here.

.NOTES
  Excluded: .venv (rebuildable Python packages, see requirements.txt), __pycache__,
  .pytest_cache, and analysis\_cache (regenerable script caches).
  Included: exports\ (built decks and workbooks), docs\drafts\, analysis\data\, .git.
  Scheduled task: "Liminality french-swap-spreads backup to OneDrive", hourly.
#>

$ErrorActionPreference = 'Stop'

$od = if ($env:OneDriveCommercial) { $env:OneDriveCommercial } else { $env:OneDrive }
if (-not $od -or -not (Test-Path $od)) { Write-Error "OneDrive folder not found"; exit 1 }

$project  = 'C:\Liminality-french-swap-spreads'
$sessions = Join-Path $env:USERPROFILE '.claude\projects\C--Liminality-french-swap-spreads'
$dest     = Join-Path $od 'Liminality-french-swap-spreads-backup-current'
$log      = Join-Path $dest 'backup.log'

New-Item -ItemType Directory -Force -Path $dest | Out-Null
Add-Content -Path $log -Encoding utf8 -Value ("`r`n===== {0} =====" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))

# /E every subdir, /XO skip when the destination copy is newer, /FFT+/DST tolerate timestamp
# granularity across filesystems, /R:1 /W:1 so a locked file costs a second rather than minutes.
$common = @('/E', '/XO', '/R:1', '/W:1', '/NFL', '/NDL', '/NP', '/NJH', '/FFT', '/DST',
            '/XD', '.venv', '__pycache__', '.pytest_cache', '_cache')

$worst = 0
foreach ($job in @(
    @{ From = $project;  To = (Join-Path $dest 'project');         Name = 'project' },
    @{ From = $sessions; To = (Join-Path $dest 'claude-sessions'); Name = 'transcripts + memory' }
)) {
    if (-not (Test-Path $job.From)) {
        Add-Content -Path $log -Encoding utf8 -Value ("  SKIP {0}: source missing" -f $job.Name)
        continue
    }
    $null = & robocopy $job.From $job.To @common 2>&1 | Out-String
    $code = $LASTEXITCODE
    if ($code -gt $worst) { $worst = $code }
    # robocopy: 0 = nothing to do, 1 = files copied, <8 = benign, >=8 = a real failure
    $verdict = if ($code -ge 8) { 'FAILED' } elseif ($code -eq 0) { 'no change' } else { 'copied' }
    Add-Content -Path $log -Encoding utf8 -Value ("  {0,-22} {1} (rc={2})" -f $job.Name, $verdict, $code)
}

if ($worst -ge 8) {
    Add-Content -Path $log -Encoding utf8 -Value "  RESULT: FAILED"
    exit 1
}
Add-Content -Path $log -Encoding utf8 -Value "  RESULT: ok"
exit 0
