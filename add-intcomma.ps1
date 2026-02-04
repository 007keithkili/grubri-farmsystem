# add-intcomma.ps1
# Adds a jinja filter 'intcomma' to app.py so templates can use |intcomma
# Run from project root where app.py lives.

$appPath = "app.py"

if (-not (Test-Path $appPath)) {
    Write-Error "Could not find $appPath in the current directory ($(Get-Location)). Run this script from your Flask project root."
    exit 1
}

# Backup original
$time = (Get-Date).ToString("yyyyMMddHHmmss")
$backupPath = "$appPath.bak.$time"
Copy-Item -Path $appPath -Destination $backupPath -ErrorAction Stop
Write-Host "Backup created: $backupPath"

# Read file
$content = Get-Content $appPath -Raw -ErrorAction Stop

# Avoid duplicate installation
if ($content -match "app\.jinja_env\.filters\[['""]intcomma['""]\]") {
    Write-Host "intcomma filter already registered in $appPath. No changes made."
    exit 0
}

# Regex: find the first line where app is created: app = Flask(...)
$pattern = '(?m)^\s*app\s*=\s*Flask\([^\)]*\).*$'

# Replacement: keep the matched line ($&) and insert the filter after it.
$replacement = '$&' + "`r`n`r`n# --- added by add-intcomma.ps1: intcomma jinja filter ---`r`ndef intcomma_filter(value):`r`n    \"\"\"Return a number with commas as thousands separators.`r`n    If value can\'t be converted to int, return it unchanged.\"\"\"`r`n    try:`r`n        return \"{:,}\".format(int(value))`r`n    except Exception:`r`n        return value`r`r`napp.jinja_env.filters['intcomma'] = intcomma_filter`r`n# --- end added ---`r`n"

# Try to replace the first occurrence
$newContent = [regex]::Replace($content, $pattern, $replacement, [System.Text.RegularExpressions.RegexOptions]::Multiline, 1)

if ($newContent -eq $content) {
    # pattern not found; append at end
    Write-Warning "Could not find 'app = Flask(...)' line. Appending intcomma filter to end of file instead."
    $newContent = $content + "`r`n`r`n# --- added by add-intcomma.ps1: intcomma jinja filter (app line not found) ---`r`ndef intcomma_filter(value):`r`n    \"\"\"Return a number with commas as thousands separators.`r`n    If value can\'t be converted to int, return it unchanged.\"\"\"`r`n    try:`r`n        return \"{:,}\".format(int(value))`r`n    except Exception:`r`n        return value`r`r`n# Attempt to register filter if 'app' exists in module`r`ntry:`r`n    app.jinja_env.filters['intcomma'] = intcomma_filter`r`nexcept Exception:`r`n    # If 'app' isn't defined at import time, it may be created later; nothing to do now`r`n    pass`r`n# --- end added ---`r`n"
}

# Write back
Set-Content -Path $appPath -Value $newContent -Encoding UTF8 -ErrorAction Stop

Write-Host "Inserted intcomma filter into $appPath."

Write-Host "`nDone. Please restart your Flask server. If you run into issues, restore the backup:"
Write-Host "`tCopy-Item -Path $backupPath -Destination $appPath -Force"
