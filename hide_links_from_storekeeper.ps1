# hide_links_from_storekeeper.ps1
# Run from project root (where templates/ folder lives).
$ErrorActionPreference = 'Stop'

$templatesDir = ".\templates"
if (-not (Test-Path $templatesDir)) {
    Write-Host "templates directory not found in project root. Aborting." -ForegroundColor Red
    exit 1
}

$ts = (Get-Date).ToString("yyyyMMddHHmmss")
$keywords = @('sales','production','task','tasks','supply','supplies','staff','breeding','medical','feed')

# Helper to check if a nearby window already contains a Jinja guard
function Has-JinjaGuardNearby {
    param($lines, $index, $windowSize)
    $start = [Math]::Max(0, $index - $windowSize)
    $end = [Math]::Min($lines.Count - 1, $index)
    $snippet = ($lines[$start..$end] -join " ").ToLower()
    return $snippet -like "*{%% if current_user.role*" -or $snippet -like "*{%% if not current_user.role*"
}

$changedFiles = @()

Get-ChildItem -Path $templatesDir -Filter *.html -Recurse | ForEach-Object {
    $file = $_.FullName
    $lines = Get-Content -Path $file -Encoding UTF8
    $original = $lines -join "`n"
    $modified = $false

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $lineLower = $lines[$i].ToLower()

        # Skip blank lines
        if ($lineLower.Trim() -eq "") { continue }

        # 1) if line already inside a Jinja guard, skip
        if (Has-JinjaGuardNearby -lines $lines -index $i -windowSize 3) { continue }

        # 2) check for anchor hrefs like /sales, /production, /tasks, /supply, etc.
        $found = $false
        foreach ($kw in $keywords) {
            if ($lineLower.Contains("/$kw") -or $lineLower.Contains("url_for('$kw") -or $lineLower.Contains("url_for(`"$kw") -or $lineLower.Contains("url_for(\"$kw")) {
                $found = $true
                break
            }
        }

        # 3) also detect delete icon/button lines (fa-trash)
        if (-not $found -and $lineLower.Contains("fa-trash")) { $found = $true }

        if ($found) {
            # wrap only this single line preserving indentation
            $indentMatch = [regex]::Match($lines[$i], '^\s*')
            $indent = $indentMatch.Value
            # ensure we don't change indentation of the original content
            $wrappedLine = $indent + "{% if current_user.role != 'storekeeper' %}`n" + $lines[$i] + "`n" + $indent + "{% endif %}"
            $lines[$i] = $wrappedLine
            $modified = $true
            # skip ahead a bit to avoid re-processing inserted lines
            $i += 2
        }
    }

    if ($modified) {
        # backup and write
        $bak = $file + ".bak." + $ts
        Copy-Item -Path $file -Destination $bak -Force
        Set-Content -Path $file -Value $lines -Encoding UTF8
        $changedFiles += $file
        Write-Host "Patched template:" $file "-> backup:" $bak -ForegroundColor Green
    }
}

if ($changedFiles.Count -eq 0) {
    Write-Host "No template links found that needed wrapping." -ForegroundColor Yellow
} else {
    Write-Host "Finished. Files updated:" -ForegroundColor Cyan
    $changedFiles | ForEach-Object { Write-Host " - $_" }
    Write-Host "Restart your Flask app and test storekeeper (links should be hidden)." -ForegroundColor Cyan
}
