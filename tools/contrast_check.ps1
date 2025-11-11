$cssPath = 'c:\Users\HP\Desktop\fullstack-app\frontend\style.css'
$css = Get-Content $cssPath -Raw
$varPattern = '--([a-z0-9\-]+)\s*:\s*([^;\n]+);'
$vars = @{}
[regex]::Matches($css, $varPattern) | ForEach-Object {
    $name = $_.Groups[1].Value
    $val = $_.Groups[2].Value.Trim()
    $vars[$name] = $val
}
function HexToRgb($hex) {
    $h = $hex.TrimStart('#')
    return [int]::Parse($h.Substring(0,2), 'HexNumber'), [int]::Parse($h.Substring(2,2), 'HexNumber'), [int]::Parse($h.Substring(4,2), 'HexNumber')
}
function SrgbToLinear($c) {
    $c = $c / 255.0
    if ($c -le 0.03928) { return $c/12.92 }
    return ([math]::Pow((($c+0.055)/1.055), 2.4))
}
function Luminance($rgb) {
    $r = $rgb[0]
    $g = $rgb[1]
    $b = $rgb[2]
    return 0.2126 * (SrgbToLinear $r) + 0.7152 * (SrgbToLinear $g) + 0.0722 * (SrgbToLinear $b)
}
function Contrast($c1,$c2) {
    $l1 = Luminance $c1
    $l2 = Luminance $c2
    $L1 = [math]::Max($l1,$l2)
    $L2 = [math]::Min($l1,$l2)
    return ($L1 + 0.05)/($L2 + 0.05)
}
function ResolveColor($val){
    if (-not $val) { return $null }
    $val = $val.Trim()
    if ($val -like 'var(*)') {
        $inner = $val.Substring(4,$val.Length-5).Trim()
        if ($inner.StartsWith('--')) { $key = $inner.Substring(2); return ResolveColor($vars[$key]) }
    }
    if ($val -like 'rgb(*)') {
        $nums = [regex]::Matches($val, '\d+') | ForEach-Object { [int]$_.Value }
        return $nums[0],$nums[1],$nums[2]
    }
    $m = [regex]::Match($val, '#([0-9a-fA-F]{6})')
    if ($m.Success) { return HexToRgb('#'+$m.Groups[1].Value) }
    return $null
}

$keys = @('primary-color','brown-600','brown-700','brown-800','cream-50','cream-100','white','cream-300')
Write-Host 'Parsed variables (sample):'
foreach ($k in $keys) { Write-Host ("  --{0}: {1}" -f $k, $vars[$k]) }

$tests = @(
    @{name='body text'; fg=ResolveColor($vars['brown-700']); bg=ResolveColor($vars['cream-50'])},
    @{name='heading (h1) text'; fg=ResolveColor($vars['brown-800']); bg=ResolveColor($vars['cream-50'])},
    @{name='card text'; fg=ResolveColor($vars['brown-600']); bg=ResolveColor($vars['cream-100'])},
    @{name='btn-primary (text on primary)'; fg=ResolveColor($vars['white']); bg=ResolveColor($vars['primary-color'])},
    @{name='footer text'; fg=ResolveColor($vars['cream-300']); bg=ResolveColor($vars['brown-800'])}
)

Write-Host "`nContrast checks: (ratio, pass >=4.5 normal text, >=3 large)"
$failed = @()
foreach ($t in $tests) {
    $fg = $t.fg; $bg = $t.bg
    if (-not $fg -or -not $bg) { Write-Host "  $($t.name): color not found (fg=$fg, bg=$bg)"; $failed += $t; continue }
    # print resolved RGBs
    Write-Host ("  {0} -> fg: {1}, bg: {2}" -f $t.name, ($fg -join ','), ($bg -join ','))
        $lfg = Luminance $fg
        $lbg = Luminance $bg
        Write-Host ("    luminance fg={0}, bg={1}" -f $lfg, $lbg)
        # compute ratio directly to avoid earlier function issues
        $L1 = [math]::Max($lfg, $lbg)
        $L2 = [math]::Min($lfg, $lbg)
        $ratio = [math]::Round((($L1 + 0.05)/($L2 + 0.05)),2)
    $pass = $ratio -ge 4.5
    if ($pass) { Write-Host "  $($t.name): $ratio - PASS" } else { Write-Host "  $($t.name): $ratio - FAIL"; $failed += $t }
}

if ($failed.Count -eq 0) { Write-Host "`nAll tested items passed AA contrast for normal text."; exit 0 }

Write-Host "`nSuggestions:" 
foreach ($t in $failed) {
    $name = $t.name
    if ($name -like '*btn*') { Write-Host ((" - {0}: consider using --white or --soft-white for button text or darken --primary-color.") -f $name) }
    else { Write-Host ((" - {0}: consider darkening text color or lightening background to meet contrast.") -f $name) }
}
exit 0
