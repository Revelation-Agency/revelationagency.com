$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$out = Join-Path $root 'assets\brand\social\premium-2026'
$backgroundPath = Join-Path $out 'approved-node-orbit-background-1983x793.png'
$approvedMasterPath = Join-Path $out 'approved-master-1983x793.png'
$markPath = Join-Path $root 'assets\brand\current\ra-mark-red.png'

foreach ($required in @($backgroundPath, $approvedMasterPath, $markPath)) {
  if (-not (Test-Path -LiteralPath $required)) { throw "Required brand source is missing: $required" }
}

$red = [Drawing.ColorTranslator]::FromHtml('#C91C1D')
$ink = [Drawing.ColorTranslator]::FromHtml('#171717')
$paper = [Drawing.ColorTranslator]::FromHtml('#F6F3EE')
$background = [Drawing.Image]::FromFile($backgroundPath)
$mark = [Drawing.Image]::FromFile($markPath)
$fonts = [Drawing.Text.PrivateFontCollection]::new()
$fonts.AddFontFile('C:\Windows\Fonts\BebasNeue Regular.otf')
$fonts.AddFontFile('C:\Windows\Fonts\HelveticaNeueCyr-Roman.otf')
$headFamily = $fonts.Families | Where-Object Name -Match 'Bebas' | Select-Object -First 1
$bodyFamily = $fonts.Families | Where-Object Name -Match 'Helvetica' | Select-Object -First 1

function Save-Png([Drawing.Bitmap]$bitmap, [string]$path) {
  $bitmap.Save($path, [Drawing.Imaging.ImageFormat]::Png)
  $bitmap.Dispose()
}

function Set-Quality([Drawing.Graphics]$graphics) {
  $graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $graphics.CompositingQuality = [Drawing.Drawing2D.CompositingQuality]::HighQuality
  $graphics.TextRenderingHint = [Drawing.Text.TextRenderingHint]::AntiAliasGridFit
}

function New-RoundedPath([Drawing.RectangleF]$rect, [single]$radius) {
  $diameter = $radius * 2
  $path = [Drawing.Drawing2D.GraphicsPath]::new()
  $path.AddArc($rect.Left, $rect.Top, $diameter, $diameter, 180, 90)
  $path.AddArc($rect.Right - $diameter, $rect.Top, $diameter, $diameter, 270, 90)
  $path.AddArc($rect.Right - $diameter, $rect.Bottom - $diameter, $diameter, $diameter, 0, 90)
  $path.AddArc($rect.Left, $rect.Bottom - $diameter, $diameter, $diameter, 90, 90)
  $path.CloseFigure()
  return $path
}

function New-Profile([int]$size, [string]$name) {
  $bitmap = [Drawing.Bitmap]::new($size, $size)
  $graphics = [Drawing.Graphics]::FromImage($bitmap)
  Set-Quality $graphics
  $graphics.Clear($red)
  $blackBrush = [Drawing.SolidBrush]::new($ink)
  $diameter = [int]($size * .76)
  $graphics.FillEllipse($blackBrush, [int](($size - $diameter) / 2), [int](($size - $diameter) / 2), $diameter, $diameter)
  $markSize = [int]($diameter * .58)
  $graphics.DrawImage($mark, [Drawing.Rectangle]::new([int](($size - $markSize) / 2), [int](($size - $markSize) / 2), $markSize, $markSize))
  $blackBrush.Dispose()
  $graphics.Dispose()
  Save-Png $bitmap (Join-Path $out $name)
}

function Draw-ApprovedBackground([Drawing.Graphics]$graphics, [int]$width, [int]$height) {
  $scale = [Math]::Max($width / [double]$background.Width, $height / [double]$background.Height)
  $drawWidth = [int][Math]::Ceiling($background.Width * $scale)
  $drawHeight = [int][Math]::Ceiling($background.Height * $scale)
  $drawX = $width - $drawWidth
  $drawY = [int](($height - $drawHeight) / 2)
  $graphics.DrawImage($background, [Drawing.Rectangle]::new($drawX, $drawY, $drawWidth, $drawHeight))
  return @{ Scale = $scale; X = $drawX; Y = $drawY }
}

function New-Cover([hashtable]$spec) {
  $width = [int]$spec.Width
  $height = [int]$spec.Height
  $bitmap = [Drawing.Bitmap]::new($width, $height)
  $graphics = [Drawing.Graphics]::FromImage($bitmap)
  Set-Quality $graphics
  $graphics.Clear($paper)
  $transform = Draw-ApprovedBackground $graphics $width $height

  $orbitX = [int]($transform.X + (1648 * $transform.Scale))
  $orbitY = [int]($transform.Y + (396 * $transform.Scale))
  $markSize = [int](175 * $transform.Scale)
  $graphics.DrawImage($mark, [Drawing.Rectangle]::new([int]($orbitX - $markSize / 2), [int]($orbitY - $markSize / 2), $markSize, $markSize))

  $labelFont = [Drawing.Font]::new($bodyFamily, [single]$spec.LabelSize, [Drawing.FontStyle]::Bold)
  $headlineFont = [Drawing.Font]::new($headFamily, [single]$spec.HeadlineSize, [Drawing.FontStyle]::Regular)
  $urlFont = [Drawing.Font]::new($bodyFamily, [single]$spec.UrlSize, [Drawing.FontStyle]::Bold)
  $redBrush = [Drawing.SolidBrush]::new($red)
  $inkBrush = [Drawing.SolidBrush]::new($ink)
  $whiteBrush = [Drawing.SolidBrush]::new([Drawing.Color]::White)
  $rulePen = [Drawing.Pen]::new([Drawing.Color]::FromArgb(55, $ink), [single][Math]::Max(1, $spec.RuleThickness))
  $format = [Drawing.StringFormat]::new()
  $format.FormatFlags = [Drawing.StringFormatFlags]::NoClip

  $graphics.DrawString('REVELATION AGENCY', $labelFont, $redBrush, [single]$spec.X, [single]$spec.LabelY, $format)
  $graphics.FillRectangle($redBrush, [single]$spec.X, [single]$spec.AccentY, [single]$spec.AccentWidth, [single]$spec.AccentHeight)
  $lineY = [single]$spec.HeadlineY
  foreach ($line in @('WE HELP WITH', 'BRANDING, MARKETING,', 'AND SALES SYSTEMS')) {
    $graphics.DrawString($line, $headlineFont, $inkBrush, [single]$spec.X, $lineY, $format)
    $lineY += [single]$spec.LineGap
  }
  $graphics.DrawLine($rulePen, [single]$spec.X, [single]$spec.RuleY, [single]($spec.X + $spec.RuleWidth), [single]$spec.RuleY)
  $graphics.FillEllipse($redBrush, [single]($spec.X - $spec.DotRadius), [single]($spec.RuleY - $spec.DotRadius), [single]($spec.DotRadius * 2), [single]($spec.DotRadius * 2))
  $graphics.FillEllipse($redBrush, [single]($spec.X + $spec.RuleWidth - $spec.DotRadius), [single]($spec.RuleY - $spec.DotRadius), [single]($spec.DotRadius * 2), [single]($spec.DotRadius * 2))

  $buttonRect = [Drawing.RectangleF]::new([single]$spec.X, [single]$spec.CtaY, [single]$spec.CtaWidth, [single]$spec.CtaHeight)
  $buttonPath = New-RoundedPath $buttonRect ([single]($spec.CtaHeight / 2))
  $graphics.FillPath($redBrush, $buttonPath)
  $format.Alignment = [Drawing.StringAlignment]::Center
  $format.LineAlignment = [Drawing.StringAlignment]::Center
  $graphics.DrawString('REVELATIONAGENCY.COM', $urlFont, $whiteBrush, $buttonRect, $format)

  $buttonPath.Dispose(); $format.Dispose(); $rulePen.Dispose()
  $redBrush.Dispose(); $inkBrush.Dispose(); $whiteBrush.Dispose()
  $labelFont.Dispose(); $headlineFont.Dispose(); $urlFont.Dispose(); $graphics.Dispose()
  Save-Png $bitmap (Join-Path $out $spec.Name)
}

$profileTargets = @(
  @{ Size = 2048; Name = 'revelation-agency-profile-master-2048.png' },
  @{ Size = 1080; Name = 'instagram-profile-1080.png' },
  @{ Size = 1080; Name = 'tiktok-profile-1080.png' },
  @{ Size = 1024; Name = 'revelation-agency-profile-1024.png' },
  @{ Size = 800; Name = 'youtube-channel-icon-800.png' },
  @{ Size = 720; Name = 'google-business-logo-720.png' },
  @{ Size = 512; Name = 'revelation-agency-profile-512.png' },
  @{ Size = 400; Name = 'x-profile-400.png' },
  @{ Size = 400; Name = 'google-business-profile-400.png' },
  @{ Size = 300; Name = 'linkedin-company-logo-300.png' }
)
foreach ($target in $profileTargets) { New-Profile $target.Size $target.Name }

$coverTargets = @(
  @{ Name='linkedin-page-banner-1128x191.png'; Width=1128; Height=191; X=70; LabelY=22; LabelSize=9; AccentY=42; AccentWidth=40; AccentHeight=2; HeadlineY=52; HeadlineSize=23; LineGap=27; RuleY=136; RuleWidth=410; RuleThickness=1; DotRadius=2; CtaY=149; CtaWidth=168; CtaHeight=26; UrlSize=8 },
  @{ Name='x-header-1500x500.png'; Width=1500; Height=500; X=110; LabelY=68; LabelSize=17; AccentY=98; AccentWidth=70; AccentHeight=4; HeadlineY=122; HeadlineSize=46; LineGap=55; RuleY=303; RuleWidth=520; RuleThickness=1.5; DotRadius=3; CtaY=340; CtaWidth=275; CtaHeight=48; UrlSize=14 },
  @{ Name='facebook-cover-1640x924.png'; Width=1640; Height=924; X=105; LabelY=155; LabelSize=20; AccentY=190; AccentWidth=78; AccentHeight=4; HeadlineY=230; HeadlineSize=58; LineGap=70; RuleY=460; RuleWidth=610; RuleThickness=2; DotRadius=4; CtaY=505; CtaWidth=320; CtaHeight=56; UrlSize=16 },
  @{ Name='google-business-cover-1024x576.png'; Width=1024; Height=576; X=64; LabelY=92; LabelSize=13; AccentY=115; AccentWidth=52; AccentHeight=3; HeadlineY=142; HeadlineSize=37; LineGap=45; RuleY=289; RuleWidth=385; RuleThickness=1.5; DotRadius=3; CtaY=321; CtaWidth=220; CtaHeight=40; UrlSize=11 },
  @{ Name='youtube-banner-2560x1440.png'; Width=2560; Height=1440; X=560; LabelY=548; LabelSize=20; AccentY=584; AccentWidth=82; AccentHeight=4; HeadlineY=617; HeadlineSize=50; LineGap=60; RuleY=813; RuleWidth=650; RuleThickness=2; DotRadius=4; CtaY=842; CtaWidth=320; CtaHeight=54; UrlSize=16 },
  @{ Name='premium-agency-graphic-refresh-x-1500x500.png'; Width=1500; Height=500; X=110; LabelY=68; LabelSize=17; AccentY=98; AccentWidth=70; AccentHeight=4; HeadlineY=122; HeadlineSize=46; LineGap=55; RuleY=303; RuleWidth=520; RuleThickness=1.5; DotRadius=3; CtaY=340; CtaWidth=275; CtaHeight=48; UrlSize=14 },
  @{ Name='premium-agency-graphic-refresh-facebook-1640x856.png'; Width=1640; Height=856; X=105; LabelY=135; LabelSize=20; AccentY=170; AccentWidth=78; AccentHeight=4; HeadlineY=210; HeadlineSize=56; LineGap=68; RuleY=432; RuleWidth=600; RuleThickness=2; DotRadius=4; CtaY=476; CtaWidth=310; CtaHeight=54; UrlSize=15 },
  @{ Name='premium-agency-graphic-refresh-google-business-1920x1080.png'; Width=1920; Height=1080; X=120; LabelY=175; LabelSize=23; AccentY=216; AccentWidth=92; AccentHeight=5; HeadlineY=255; HeadlineSize=67; LineGap=80; RuleY=517; RuleWidth=710; RuleThickness=2; DotRadius=5; CtaY=568; CtaWidth=365; CtaHeight=62; UrlSize=18 }
)
foreach ($target in $coverTargets) { New-Cover $target }

Copy-Item -LiteralPath $approvedMasterPath -Destination (Join-Path $out 'premium-agency-graphic-refresh-linkedin-1983x793.png') -Force
Copy-Item -LiteralPath (Join-Path $out 'youtube-banner-2560x1440.png') -Destination (Join-Path $out 'premium-agency-graphic-refresh-youtube-2560x1440.png') -Force

$alternate = [Drawing.Bitmap]::new(1024, 1024)
$alternateGraphics = [Drawing.Graphics]::FromImage($alternate)
Set-Quality $alternateGraphics
$alternateGraphics.Clear($ink)
$redBrush = [Drawing.SolidBrush]::new($red)
$alternateGraphics.FillEllipse($redBrush, 123, 123, 778, 778)
$markSize = 451
$attributes = [Drawing.Imaging.ImageAttributes]::new()
$matrix = [Drawing.Imaging.ColorMatrix]::new(@(
  [single[]](0,0,0,0,0), [single[]](0,0,0,0,0), [single[]](0,0,0,0,0), [single[]](0,0,0,1,0), [single[]](.09,.09,.09,0,1)
))
$attributes.SetColorMatrix($matrix)
$alternateGraphics.DrawImage($mark, [Drawing.Rectangle]::new([int](512-$markSize/2), [int](512-$markSize/2), $markSize, $markSize), 0, 0, $mark.Width, $mark.Height, [Drawing.GraphicsUnit]::Pixel, $attributes)
$attributes.Dispose(); $redBrush.Dispose(); $alternateGraphics.Dispose()
Save-Png $alternate (Join-Path $out 'revelation-agency-alternate-red-circle-black-mark-1024.png')

$iconTargets = @(
  @{ Size = 32; Name = 'favicon-32.png' }, @{ Size = 180; Name = 'apple-touch-icon.png' },
  @{ Size = 192; Name = 'icon-192.png' }, @{ Size = 512; Name = 'icon-512.png' }
)
foreach ($target in $iconTargets) {
  New-Profile $target.Size ('__' + $target.Name)
  Move-Item -LiteralPath (Join-Path $out ('__' + $target.Name)) -Destination (Join-Path $root $target.Name) -Force
}
Copy-Item -LiteralPath (Join-Path $out 'revelation-agency-profile-512.png') -Destination (Join-Path $root 'assets\brand\current\ra-profile-black-circle-red-mark.png') -Force
$faviconBitmap = [Drawing.Bitmap]::FromFile((Join-Path $root 'favicon-32.png'))
$icon = [Drawing.Icon]::FromHandle($faviconBitmap.GetHicon())
$stream = [IO.File]::Open((Join-Path $root 'favicon.ico'), [IO.FileMode]::Create)
$icon.Save($stream)
$stream.Dispose(); $icon.Dispose(); $faviconBitmap.Dispose()
$background.Dispose(); $mark.Dispose(); $fonts.Dispose()
Write-Output "Created approved-master social assets in $out"
