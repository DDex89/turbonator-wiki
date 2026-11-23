# Publishes this checkout to the user's empty GitHub repository.
# Requires Git for Windows and an authenticated GitHub credential helper.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$repo = 'https://github.com/DDex89/turbonator-wiki.git'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git for Windows is required.' }
if (-not (Test-Path '.git')) { git init -b main; if ($LASTEXITCODE -ne 0) { throw 'git init failed' } }
$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) { git remote add origin $repo }
elseif ($existing.Trim() -ne $repo) { throw "Existing origin is $existing, expected $repo" }
git add -A
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { git commit -m 'Restore Turbonator Wiki with FCC and SBEC3 documentation'; if ($LASTEXITCODE -ne 0) { throw 'git commit failed (check user.name / user.email)' } }
git push -u origin HEAD:main
if ($LASTEXITCODE -ne 0) { throw 'Push failed: check GitHub authentication and repository permissions.' }
Write-Host 'Published: https://github.com/DDex89/turbonator-wiki'
