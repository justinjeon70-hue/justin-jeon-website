# Weekly Google Scholar stats update for drjustinjeon.com
# Registered in Windows Task Scheduler as "UpdateScholarStats" (Mondays 09:00).
$repo = "C:\Users\user\justin-jeon-website"
$log = Join-Path $env:LOCALAPPDATA "scholar_update.log"

function Log($msg) {
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg" | Add-Content $log
}

Set-Location $repo
Log "start"
git pull --rebase origin master 2>&1 | Add-Content $log
python scripts\update_scholar_stats.py 2>&1 | Add-Content $log

if (git diff --name-only scholar-stats.json) {
    git add scholar-stats.json
    git commit -m "Update Google Scholar stats" 2>&1 | Add-Content $log
    git push 2>&1 | Add-Content $log
    Log "pushed updated stats"
} else {
    Log "no changes"
}
