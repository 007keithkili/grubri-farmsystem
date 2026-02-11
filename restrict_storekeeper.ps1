# restrict_storekeeper.ps1
# Run from project root (where app.py and templates/ live).
# Makes backups and:
#  - removes 'storekeeper' from role-checks inside task/supplies route functions
#  - hides links to task/supplies pages in templates for storekeeper
# Safe & idempotent: creates backups and tries not to double-wrap templates.

$ErrorActionPreference = 'Stop'

$appFile = ".\app.py"
$templatesDir = ".\templates"

if (-not (Test-Path $appFile)) {
    Write-Host "ERROR: app.py not found in current folder." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $templatesDir)) {
    Write-Host "WARNING: templates directory not found; template changes will be skipped." -ForegroundColor Yellow
}

# create backups of app.py and templates list (timestamped)
$timestamp = (Get-Date).ToString("yyyyMMddHHmmss")
$backupApp = "$appFile.bak.$timestamp"
Copy-Item -Path $appFile -Destination $backupApp -Force
Write-Host "Backup created: $backupApp"

# read app.py
$text = Get-Content -Path $appFile -Raw -Encoding UTF8

# list of route/function keywords to restrict (task/supply variations)
$keywords = @('task','tasks','task_list','tasks_list','supply','supplies','supply_list','supplies_list','delete_task','delete_supply')

# helper: remove 'storekeeper' token from role-check array literal
function Remove-StorekeeperFromRoleCheck($match) {
    # $match is the full match string like: getattr(current_user, 'role', None) not in ['admin','storekeeper','manager']
    $patternInner = "getattr\s*\(\s*current_user\s*,\s*['""]role['""]\s*,\s*None\s*\)\s*not\s*in\s*\[([^\]]*)\]"
    $m2 = [regex]::Match($match, $patternInner)
    if (-not $m2.Success) { return $match }
    $inner = $m2.Groups[1].Value
    # split items by comma
    $items = $inner -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
    # remove storekeeper variants (with or without quotes)
    $itemsClean = $items | Where-Object { ($_ -replace "'" , "") -replace '"' -ne 'storekeeper' -and $_ -ne "'storekeeper'" -and $_ -ne '"storekeeper"' }
    # ensure quotes and proper formatting
    $itemsClean = $itemsClean | ForEach-Object {
        $it = $_.Trim()
        if ($it -match "^[\"'].*[\"']$") { $it } else { ("'" + ($it -replace "['""]", "") + "'") }
    }
    if ($itemsClean.Count -eq 0) {
        # fallback to admin-only
        $newList = "['admin']"
    } else {
        $newList = "[" + ($itemsClean -join ", ") + "]"
    }
    $newExpr = "getattr(current_user, 'role', None) not in " + $newList
    return $newExpr
}

# For each keyword, attempt to find a function block (def <name>) or route decorator containing the keyword,
# then inside that function replace role-checks that include storekeeper.
$changesMade = @()
foreach ($kw in $keywords) {
    # try find by function name first
    $defToken = "def $kw"
    $idx = $text.IndexOf($defToken)
    if ($idx -lt 0) {
        # try find by @app.route containing keyword (simple search)
        $routePattern = "@app.route\([^\)]*['""][^'""]*$kw[^'""]*['""]"
        $rmatch = [regex]::Match($text, $routePattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        if ($rmatch.Success) {
            # find start of function defined after this decorator
            $startIndex = $rmatch.Index
            # find "def " after this position
            $defAfter = $text.IndexOf("def ", $startIndex)
            if ($defAfter -ge 0) { $idx = $defAfter }
        }
    }
    if ($idx -lt 0) { continue }

    # extract function block: from idx to next "def " at column start or next "@app.route" (simple heuristic)
    $sub = $text.Substring($idx)
    $endCandidates = @("`ndef ", "`n@app.route")
    $endRel = $null
    foreach ($c in $endCandidates) {
        $pos = $sub.IndexOf($c)
        if ($pos -ge 0) {
            if ($endRel -eq $null -or $pos -lt $endRel) { $endRel = $pos }
        }
    }
    if ($endRel -eq $null) {
        $funcText = $sub
        $prefix = $text.Substring(0, $idx)
        $suffix = ""
    } else {
        $funcText = $sub.Substring(0, $endRel)
        $prefix = $text.Substring(0, $idx)
        $suffix = $text.Substring($idx + $endRel)
    }

    # only attempt replace if function text contains storekeeper or role-check
    if ($funcText -match "storekeeper" -or $funcText -match "getattr\s*\(\s*current_user\s*,\s*['""]role['""]") {
        # find all role-check expressions inside function
        $rolePattern = "getattr\s*\(\s*current_user\s*,\s*['""]role['""]\s*,\s*None\s*\)\s*not\s*in\s*\[[^\]]*\]"
        $newFunc = [regex]::Replace($funcText, $rolePattern, { param($m) Remove-StorekeeperFromRoleCheck($m.Value) }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

        if ($newFunc -ne $funcText) {
            $text = $prefix + $newFunc + $suffix
            $changesMade += "Updated role-checks in function for keyword: $kw"
        }
    }
}

if ($changesMade.Count -gt 0) {
    # write back app.py with changes and backup was already created
    Set-Content -Path $appFile -Value $text -Encoding UTF8
    Write-Host "Patched app.py role-checks for:" -ForegroundColor Green
    $changesMade | ForEach-Object { Write-Host " - $_" }
} else {
    Write-Host "No role-checks needed patching for task/supplies functions." -ForegroundColor Yellow
}

# Now patch template files: hide links/buttons pointing to task/supplies from storekeeper
if (Test-Path $templatesDir) {
    $htmlFiles = Get-ChildItem -Path $templatesDir -Filter *.html -Recurse
    $tplChanges = @()
    foreach ($f in $htmlFiles) {
        $content = Get-Content -Path $f.FullName -Raw -Encoding UTF8
        $orig = $content

        # look for hrefs or url_for references pointing at task/supplies routes, e.g. /task, /tasks, url_for('task'), url_for('tasks')
        $linkPattern = '(?i)(href\s*=\s*["'"]\/(?:task|tasks|supply|supplies)[^"'"]*["'"])|url_for\(\s*["'`](?:task|tasks|supply|supplies)['"`]\s*\)'
        $matches = [regex]::Matches($content, $linkPattern)
        if ($matches.Count -gt 0) {
            # For each match, wrap the containing line/block with Jinja guard, but avoid double-wrapping.
            # Simplest safe approach: for each match, wrap the entire line if not already inside a Jinja guard.
            $lines = $content -split "(`r?`n)"
            $changed = $false
            for ($i=0; $i -lt $lines.Length; $i++) {
                $line = $lines[$i]
                if ($line -match $linkPattern) {
                    # skip if already contains a Jinja role check nearby
                    if ($line -match "{%\s*if\s+current_user\.role" -or ($i -gt 0 -and $lines[$i-1] -match "{%\s*if\s+current_user\.role")) {
                        continue
                    }
                    # wrap this line with guard that hides for storekeeper
                    $wrapped = "{% if current_user.role != 'storekeeper' %}`n" + $line + "`n{% endif %}"
                    $lines[$i] = $wrapped
                    $changed = $true
                }
            }
            if ($changed) {
                $newContent = ($lines -join "")
                # save backup for this file
                $bak = $f.FullName + ".bak.$timestamp"
                Copy-Item -Path $f.FullName -Destination $bak -Force
                Set-Content -Path $f.FullName -Value $newContent -Encoding UTF8
                $tplChanges += $f.FullName
            }
        }
    }

    if ($tplChanges.Count -gt 0) {
        Write-Host "Wrapped links to task/supplies in templates to hide them from storekeeper:" -ForegroundColor Green
        $tplChanges | ForEach-Object { Write-Host " - $_" }
    } else {
        Write-Host "No template links found that needed wrapping." -ForegroundColor Yellow
    }
}

Write-Host "Done. Restart your Flask app and test the storekeeper account. Backups have been created." -ForegroundColor Cyan
