param(
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [string]$TeamName = '奶娃工程'
)

$ErrorActionPreference = 'Stop'
$edgeCandidates = @(
  "$env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe"
)
$edge = $edgeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw '未找到 Microsoft Edge 或 Google Chrome，无法无头打印 PDF。' }

python "$PSScriptRoot\make-diagrams.py"
if ($LASTEXITCODE -ne 0) { throw '图示生成失败。' }
python "$PSScriptRoot\markdown-to-html.py" "$Root\system-design.md" "$Root\system-design.html" '系统设计说明书'
if ($LASTEXITCODE -ne 0) { throw '系统设计 HTML 生成失败。' }
python "$PSScriptRoot\markdown-to-html.py" "$Root\database-design.md" "$Root\database-design.html" '数据库设计说明书'
if ($LASTEXITCODE -ne 0) { throw '数据库设计 HTML 生成失败。' }

$outDir = Join-Path $Root 'pdf'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$safeTeamName = $TeamName -replace '[<>:"/\\|?*]', '_'
$htmlFiles = @(
  @{ Source = "$Root\system-design.html"; Output = "$outDir\${safeTeamName}_系统设计说明书.pdf" },
  @{ Source = "$Root\database-design.html"; Output = "$outDir\${safeTeamName}_数据库设计说明书.pdf" }
)

foreach ($item in $htmlFiles) {
  $source = (Resolve-Path $item.Source).Path
  $output = [IO.Path]::GetFullPath($item.Output)
  if (Test-Path $output) { Remove-Item -Force $output }
  & $edge --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$output" "file:///$($source.Replace('\','/'))" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "浏览器打印失败：$source" }
  if (-not (Test-Path $output)) { throw "PDF 生成失败：$output" }
  Write-Host "created $output"
}
