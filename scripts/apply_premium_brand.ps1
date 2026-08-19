$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$htmlFiles = Get-ChildItem -Path $root -Recurse -File -Filter '*.html'
$link = '<link rel="stylesheet" href="/assets/css/ra-premium-brand-2026.css?v=20260819">'
$logo = '<img src="/assets/brand/current/ra-profile-black-circle-red-mark.png" alt="Revelation Agency" width="640" height="640">'
$changed = 0
foreach ($file in $htmlFiles) {
  $text = [IO.File]::ReadAllText($file.FullName)
  $next = $text
  if ($next -notmatch 'ra-premium-brand-2026\.css') {
    $next = $next -replace '(?i)</head>', "$link`r`n</head>"
  }
  $next = [regex]::Replace($next, '(?is)(<a\b[^>]*\bclass="ra-nav__logo"[^>]*>\s*)<img\b[^>]*>', ('$1' + $logo))
  # Repoint the two legacy footer/schema destinations that belonged to an unrelated agency.
  $next = $next.Replace('https://www.linkedin.com/company/revelation-agency', 'https://www.linkedin.com/company/reviiiagency')
  $next = $next.Replace('https://www.instagram.com/revelationagency/', 'https://www.instagram.com/reviiiagency/')
  if ($next -ne $text) {
    [IO.File]::WriteAllText($file.FullName, $next, [Text.UTF8Encoding]::new($false))
    $changed++
  }
}
Write-Output "Updated $changed HTML files."
