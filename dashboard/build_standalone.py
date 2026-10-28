"""대시보드 페이지(dashboard/index.html)와 데이터(outputs/v5/dashboard)를 합쳐
로그인 없이 볼 수 있는 단일 HTML(dashboard/standalone.html)을 만든다."""
import csv
import json
import os
import sys

repo = sys.argv[1]
dash_dir = os.path.join(repo, 'outputs', 'v5', 'dashboard')
page = open(os.path.join(repo, 'dashboard', 'index.html'), encoding='utf-8').read()
page = page.replace('<meta name="dash-one-writer">\n', '')

data = {}
for name in ['dongs', 'spots', 'kpi', 'actions', 'monthly', 'background', 'model']:
    with open(os.path.join(dash_dir, f'{name}.csv'), encoding='utf-8') as f:
        data[name] = list(csv.DictReader(f))
data['boundary'] = json.load(open(os.path.join(dash_dir, 'boundary.json'), encoding='utf-8'))
data_js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

head = r'''<title>제주 통과형 진단</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@400;600&display=swap">
<style>
  /* 지도·처방·진단·모니터링을 한 열로 쌓는 보고서형 대시보드. 제주 바다·현무암 톤 */
  :root {
    --color-bg: #f6f7f6; --color-panel: #ffffff; --color-fg: #1d2421; --color-fg-muted: #5c6863;
    --color-border-line: #dde3e0; --color-ok: #2f7d5b; --color-warn: #a56a12; --color-bad: #c2462d;
    --cds-chart-grid: #e8ecea; --cds-chart-axis: #b9c3be; --cds-chart-reference: #8c9893; --cds-chart-muted: #a7b2ad;
    --cds-surface-popover: #ffffff; --cds-border: #d3dad6; --cds-shadow-popover: 0 4px 16px rgba(20, 30, 25, .12);
    --cds-text-secondary: #5c6863;
    --font-anthropic-sans: 'Noto Sans KR', system-ui, -apple-system, 'Malgun Gothic', sans-serif;
    --font-anthropic-serif: 'Noto Serif KR', 'Nanum Myeongjo', Georgia, serif;
    --cds-font-size-caption: .8125rem; --cds-font-size-body: .9375rem; --cds-font-size-heading: 1.0625rem; --cds-font-size-title: 1.75rem;
    --cds-font-weight-medium: 600;
    --cds-gap-xs: .375rem; --cds-gap-sm: .625rem; --cds-gap-md: 1rem; --cds-gap-lg: 1.5rem; --cds-gap-xl: 2.25rem;
    --cds-pad-xs: .375rem; --cds-pad-sm: .625rem; --cds-pad-md: 1rem; --cds-pad-lg: 1.25rem;
    --cds-radius: 8px; --cds-dur-slow: .3s;
    --series-0: #2b6f8f; --series-1: #c2462d; --series-2: #3f8f5f; --series-3: #b07a1c; --series-4: #6f5aa8; --series-5: #3b8f8a; --series-6: #8a5a44; --series-7: #5f6f7a;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --color-bg: #141917; --color-panel: #1c2320; --color-fg: #e6ece9; --color-fg-muted: #9aa8a2;
      --color-border-line: #2e3833; --color-ok: #6cc49a; --color-warn: #e0a54a; --color-bad: #f07a5f;
      --cds-chart-grid: #26302b; --cds-chart-axis: #46524c; --cds-chart-reference: #7d8b85; --cds-chart-muted: #64716b;
      --cds-surface-popover: #222a26; --cds-border: #36423c; --cds-shadow-popover: 0 4px 16px rgba(0, 0, 0, .4);
      --cds-text-secondary: #9aa8a2;
      --series-0: #6fb2d2; --series-1: #f07a5f; --series-2: #78c492; --series-3: #e0a54a; --series-4: #a996e0; --series-5: #6cc4be; --series-6: #c99a82; --series-7: #9aaab5;
      color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --color-bg: #141917; --color-panel: #1c2320; --color-fg: #e6ece9; --color-fg-muted: #9aa8a2;
    --color-border-line: #2e3833; --color-ok: #6cc49a; --color-warn: #e0a54a; --color-bad: #f07a5f;
    --cds-chart-grid: #26302b; --cds-chart-axis: #46524c; --cds-chart-reference: #7d8b85; --cds-chart-muted: #64716b;
    --cds-surface-popover: #222a26; --cds-border: #36423c; --cds-shadow-popover: 0 4px 16px rgba(0, 0, 0, .4);
    --cds-text-secondary: #9aa8a2;
    --series-0: #6fb2d2; --series-1: #f07a5f; --series-2: #78c492; --series-3: #e0a54a; --series-4: #a996e0; --series-5: #6cc4be; --series-6: #c99a82; --series-7: #9aaab5;
    color-scheme: dark;
  }
  body { background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); font-size: var(--cds-font-size-body); }
  #dash-root { padding-block: 1.5rem 3rem; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
  #dash-root .jt-credit { margin-top: var(--cds-gap-lg); }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
  // 대시보드 런타임 대신 쓰는 최소 구현: 페이지에 넣은 데이터를 그대로 돌려준다
  (function () {
    const RAW = __DATA__;
    const calcs = {}, draws = {};
    const readColors = () => {
      const cs = getComputedStyle(document.documentElement);
      return [0, 1, 2, 3, 4, 5, 6, 7].map((i) => cs.getPropertyValue('--series-' + i).trim());
    };
    window.dash = {
      colors: readColors(),
      data(id) {
        if (calcs[id]) return { status: 'ok', data: calcs[id](), meta: [] };
        return RAW[id] ? { status: 'ok', data: RAW[id], meta: [] } : { status: 'missing', data: [], meta: [] };
      },
      calc(id, spec) {
        let memo = null;
        calcs[id] = () => memo || (memo = spec.fn(...spec.inputs.map((i) => window.dash.data(i).data)));
      },
      draw(name, fn) {
        if (typeof fn === 'function') draws[name] = fn;
        document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
          try { draws[name] && draws[name](el); } catch (e) { console.error(name, e); }
        });
      },
      onData(fn) { fn(); },
      params() { return {}; }, setParams() {}, resetParams() {}, setLink() {}, refresh() {},
    };
    let t = null;
    const redrawAll = () => { window.dash.colors = readColors(); Object.keys(draws).forEach((n) => window.dash.draw(n)); };
    window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(redrawAll, 150); });
    if (window.matchMedia) window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', redrawAll);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(redrawAll);
  })();
</script>
'''.replace('__DATA__', data_js)

credit = ('\n  <p class="jt-note jt-credit">동국대학교 BAF 마케팅팀 · 2026 제주 관광 데이터 활용사례 공모전 · '
          '분석 노트북과 데이터: github.com/DGU-BAF/BAF-26-2-marketing</p>\n</div>')
body = page.replace('<div class="jt">', '<div id="dash-root">\n<div class="jt">', 1)
# 맨 마지막 섹션 뒤 닫는 </div>(.jt)에 출처 줄을 붙이고 #dash-root를 닫음
idx = body.index('\n</div>\n\n<script>')
body = body[:idx] + '\n</div>' + credit + body[idx + len('\n</div>'):]

out = os.path.join(repo, 'dashboard', 'standalone.html')
open(out, 'w', encoding='utf-8').write(head + body)
print(out, os.path.getsize(out), 'bytes')
