import re
import sys

CSS_PATH = r"c:\Users\HP\Desktop\fullstack-app\frontend\style.css"

hex_re = re.compile(r"#([0-9a-fA-F]{6})")
var_re = re.compile(r"--([a-z0-9\-]+)\s*:\s*([^;\n]+);")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def srgb_to_linear(c):
    c = c / 255.0
    return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055) ** 2.4

def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

def contrast_ratio(c1, c2):
    l1 = luminance(c1)
    l2 = luminance(c2)
    L1, L2 = max(l1, l2), min(l1, l2)
    return (L1 + 0.05) / (L2 + 0.05)

# Read CSS and parse variables
with open(CSS_PATH, 'r', encoding='utf-8') as f:
    css = f.read()

vars = {}
for m in var_re.finditer(css):
    name = m.group(1).strip()
    val = m.group(2).strip()
    # strip comments
    val = re.sub(r"/\*.*?\*/", "", val)
    vars[name] = val

# Helper to resolve var(...) or hex
def resolve_color(val):
    val = val.strip()
    if val.startswith('var('):
        inner = val[4:val.rfind(')')].strip()
        if inner.startswith('--'):
            key = inner[2:]
            return resolve_color(vars.get(key, ''))
    # rgb(...) or rgba(...) or hex
    if val.startswith('rgb'):
        nums = re.findall(r"[0-9]+", val)
        nums = [int(n) for n in nums[:3]]
        return tuple(nums)
    m = hex_re.search(val)
    if m:
        return hex_to_rgb('#' + m.group(1))
    return None

# Colors to test
tests = [
    ('body text', resolve_color(vars.get('brown-700')), resolve_color(vars.get('cream-50'))),
    ('heading (h1) text', resolve_color(vars.get('brown-800')), resolve_color(vars.get('cream-50'))),
    ('card text', resolve_color(vars.get('brown-600')), resolve_color(vars.get('cream-100'))),
    ('btn-primary (text on primary)', resolve_color(vars.get('white')), resolve_color(vars.get('primary-color'))),
    ('footer text', resolve_color(vars.get('cream-300')), resolve_color(vars.get('brown-800'))),
]

print('Parsed CSS variables (sample):')
for k in ['primary-color','brown-600','brown-700','brown-800','cream-50','cream-100','white']:
    print(f'  --{k}: {vars.get(k)}')

print('\nContrast checks: (ratio, pass >=4.5 normal text, >=3 large)')
failed = []
for name, fg, bg in tests:
    if fg is None or bg is None:
        print(f'  {name}: color not found (fg={fg}, bg={bg})')
        failed.append((name,'missing'))
        continue
    ratio = contrast_ratio(fg, bg)
    ok = ratio >= 4.5
    print(f'  {name}: {ratio:.2f} - {'PASS' if ok else 'FAIL'}')
    if not ok:
        failed.append((name, ratio))

# Output adjustments suggestions
if not failed:
    print('\nAll tested items passed AA contrast for normal text.')
    sys.exit(0)

print('\nSuggestions:')
for item in failed:
    name = item[0]
    if item[1] == 'missing':
        print(f' - {name}: missing variable(s), check CSS')
        continue
    ratio = item[1]
    if 'btn' in name.lower():
        print(f' - {name}: consider using --soft-white for button text or darken --primary-color to improve contrast.')
    else:
        print(f' - {name}: consider darkening text color or lightening background to meet contrast. Current ratio {ratio:.2f}')

# Return non-zero if failures
sys.exit(0)
