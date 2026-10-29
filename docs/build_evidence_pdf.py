"""서식 5 증빙자료 PDF 생성: v5 노트북 산출물(outputs/v5)로 분석 보고서를 만든다.
실행: python docs/build_evidence_pdf.py .   (reportlab, pillow, pandas 필요, Windows 맑은 고딕 사용)"""
import os
import sys

import pandas as pd
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image as RLImage, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

REPO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
V5 = os.path.join(REPO, 'outputs', 'v5')
EV = os.path.join(V5, 'evidence')
OUT = os.path.join(REPO, 'docs', '서식5_증빙자료_분석보고서.pdf')
DASH_URL = 'https://dgu-baf.github.io/BAF-26-2-marketing/'
GIT_URL = 'https://github.com/DGU-BAF/BAF-26-2-marketing'

pdfmetrics.registerFont(TTFont('Malgun', r'C:\Windows\Fonts\malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBd', r'C:\Windows\Fonts\malgunbd.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('Malgun', normal='Malgun', bold='MalgunBd', italic='Malgun', boldItalic='MalgunBd')

INK, MUTED, ACCENT, LINE, BAND = (colors.HexColor(c) for c in ('#1d2421', '#5c6863', '#2b6f8f', '#dde3e0', '#eef3f1'))
S = {
    'title': ParagraphStyle('t', fontName='MalgunBd', fontSize=21, leading=29, textColor=INK, spaceAfter=6),
    'sub': ParagraphStyle('s', fontName='Malgun', fontSize=11.5, leading=17, textColor=MUTED),
    'h1': ParagraphStyle('h1', fontName='MalgunBd', fontSize=14.5, leading=20, textColor=ACCENT, spaceBefore=4, spaceAfter=6),
    'h2': ParagraphStyle('h2', fontName='MalgunBd', fontSize=11.5, leading=16, textColor=INK, spaceBefore=6, spaceAfter=3),
    'body': ParagraphStyle('b', fontName='Malgun', fontSize=9.5, leading=15, textColor=INK),
    'bul': ParagraphStyle('bu', fontName='Malgun', fontSize=9.5, leading=15, textColor=INK, leftIndent=10, bulletIndent=0),
    'cap': ParagraphStyle('c', fontName='Malgun', fontSize=8, leading=11.5, textColor=MUTED, alignment=TA_CENTER, spaceBefore=2),
    'cell': ParagraphStyle('ce', fontName='Malgun', fontSize=8.2, leading=11.5, textColor=INK),
    'cellb': ParagraphStyle('cb', fontName='MalgunBd', fontSize=8.2, leading=11.5, textColor=INK),
    'big': ParagraphStyle('bg', fontName='MalgunBd', fontSize=17, leading=22, textColor=ACCENT, alignment=TA_CENTER),
    'bigcap': ParagraphStyle('bc', fontName='Malgun', fontSize=8, leading=11, textColor=MUTED, alignment=TA_CENTER),
}
W = A4[0] - 36 * mm


def P(text, style='body'):
    return Paragraph(text, S[style])


def bullets(items):
    return [Paragraph(t, S['bul'], bulletText='•') for t in items]


def fig(path, caption, width=W, max_h=None):
    im = Image.open(path)
    h = width * im.height / im.width
    if max_h and h > max_h:
        width, h = max_h * im.width / im.height, max_h
    return KeepTogether([RLImage(path, width=width, height=h), P(caption, 'cap'), Spacer(1, 6)])


def table(rows, widths, header=True, zebra=True):
    data = [[c if isinstance(c, Paragraph) else P(str(c), 'cellb' if (header and i == 0) else 'cell') for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [('GRID', (0, 0), (-1, -1), 0.4, LINE), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]
    if header:
        st.append(('BACKGROUND', (0, 0), (-1, 0), BAND))
    t.setStyle(TableStyle(st))
    return t


def tiles(items):
    cells = [[P(v, 'big') for v, _ in items], [P(c, 'bigcap') for _, c in items]]
    t = Table(cells, colWidths=[W / len(items)] * len(items))
    t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, LINE), ('LINEAFTER', (0, 0), (-2, -1), 0.4, LINE),
                           ('BACKGROUND', (0, 0), (-1, -1), colors.white), ('TOPPADDING', (0, 0), (-1, -1), 6),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    return t


def crop_dashboard():
    """대시보드 전체 캡처를 구역별로 잘라 저장 (캡처는 1920px 폭 기준)"""
    src = os.path.join(EV, 'dashboard_full.png')
    if not os.path.exists(src):
        return {}
    im = Image.open(src)
    parts = {'dash_top': (0, 1665), 'dash_targets': (1690, 2815), 'dash_spots': (2840, 3845), 'dash_monitor': (3860, 4640)}
    out = {}
    for name, (y0, y1) in parts.items():
        p = os.path.join(EV, f'{name}.png')
        im.crop((0, y0, im.width, min(y1, im.height))).save(p)
        out[name] = p
    return out


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Malgun', 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, '2026 제주 관광 데이터 활용사례 공모전 · 동국대학교 BAF 마케팅팀 · 서식 5 응모작 관련 참고자료')
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f'{doc.page}')
    canvas.restoreState()


def build():
    dash = crop_dashboard()
    final = pd.read_csv(os.path.join(V5, 'v5_관광동_최종.csv'), encoding='utf-8-sig', index_col=0)
    spots = pd.read_csv(os.path.join(V5, 'dashboard', 'spots.csv'))
    kpi = pd.read_csv(os.path.join(V5, 'dashboard', 'kpi.csv'))
    acts = pd.read_csv(os.path.join(V5, 'dashboard', 'actions.csv')).set_index('타깃')
    mde = pd.read_csv(os.path.join(V5, 'v5_효과측정_MDE.csv'), encoding='utf-8-sig')
    model = pd.read_csv(os.path.join(V5, 'dashboard', 'model.csv')).set_index('지표')['값']
    bg = pd.read_csv(os.path.join(V5, 'dashboard', 'background.csv')).set_index('연도')
    arr_chg = bg.at[2025, '관광지_관광객도착'] / bg.at[2023, '관광지_관광객도착'] - 1
    upa_chg = bg.at[2025, '관광지도착당_소비'] / bg.at[2023, '관광지도착당_소비'] - 1
    lo, hi = acts['기대소비_하한'].sum(), acts['기대소비_상한'].sum()
    ex = spots[spots['비고'] == '확대 후보']

    st = []
    # ── 표지
    st += [Spacer(1, 40 * mm), P('멈추지 않는 관광객을 지역 소비로', 'title'),
           P('내비게이션·통신·카드 데이터로 찾은 제주 \'통과형 관광지\'와 핀포인트 처방', 'sub'), Spacer(1, 6 * mm),
           P('2026 제주 관광 데이터 활용사례 공모전 · 서식 5 응모작 관련 참고자료 (분석 보고서)', 'body'),
           P('동국대학교 BAF 마케팅팀 (이동은 · 조휴선 · 권민서)', 'body'), Spacer(1, 10 * mm),
           tiles([(f'{arr_chg:+.1%}', '관광지 관광객 도착<br/>2023→2025'), (f'{upa_chg:+.1%}', '관광지 도착 1건당 카드 소비<br/>2023→2025'),
                  ('2곳', '최종 타깃<br/>한경면 · 송산동'), (f'연 {lo:.0f}~{hi:.0f}억', '타깃 2곳 기대 추가 소비<br/>(카드 결제 기준)')]),
           Spacer(1, 10 * mm),
           table([['자료', '위치'],
                  ['공개 대시보드 (로그인 불필요)', DASH_URL],
                  ['분석 노트북 · 코드 · 데이터 처리 기록', GIT_URL],
                  ['분석 노트북 파일', '제주_통과형_v5_통합분석.ipynb (66개 셀, 그림 10종, 결과표 13종)']],
                 [W * 0.35, W * 0.65]),
           Spacer(1, 6 * mm),
           P('분석 기간 2023.01~2025.12(36개월, 43개 읍면동). 2026.01~06 데이터는 분석에 쓰지 않고 사후 검증에만 사용. '
             '금액은 카드 결제 기준이라 실제 지역 매출보다 작을 수 있음.', 'cap'),
           PageBreak()]

    # ── 1. 요약
    st += [P('1. 한눈에 보기', 'h1'),
           P('제주 관광은 관광지에 도착하는 관광객이 줄었지만 도착 1건당 소비는 늘어난 국면입니다. 관광객을 더 부르기보다 '
             '<b>이미 온 관광객이 근처 상권에서 소비하도록 잇는 것</b>이 필요합니다. 제주관광빅데이터플랫폼 데이터 4종을 결합해 '
             '관광객은 많이 오지만 지역 소비로 이어지지 않는 <b>통과형 지역·관광지</b>를 찾고, 원인을 진단해 실행 가능한 처방과 측정 계획을 만들었습니다.'),
           Spacer(1, 4)]
    st += bullets([
        '<b>강건한 통과형 3곳</b>: 한경면·송산동·효돈동 (9개 정의 합의 + 기준 8가지 민감도 + 3개 연도 모두 상위)',
        '<b>사후 검증</b>: 분석에 쓰지 않은 2026년 상반기에도 한경면 2위·송산동 6위 유지(28곳 중) → 최종 타깃. 효돈동은 11위로 모니터링',
        '<b>원인</b>: 소비가 새는 이유는 \'덜 써서\'가 아니라 \'근처 가게로 이어지지 않아서\' (한경면 격차의 79%)',
        f'<b>처방 근거</b>: 로컬 소비처 방문이 10% 늘면 관광객 카드 소비 약 +3.5% (28개 동 × 36개월 패널, 탄력성 {model["로컬 방문 탄력성"]:.2f}, p&lt;0.001)',
        '<b>핀포인트</b>: 신창풍차해안도로(로컬전환비 0.11, 제주 마을 하위 9%), 정방폭포 일대(0.01, 하위 4%)',
        f'<b>확대 적용</b>: 같은 기준으로 제주 전역 확대 후보 {len(ex)}곳, 연 {ex["연 추가 소비_보수(억원)"].sum():.0f}억~{ex["연 추가 소비_상한(억원)"].sum():.0f}억 원',
        '<b>활용</b>: 웹 대시보드 공개, 서귀포시·제주시 관광진흥과와 서귀포 매일올레시장 상인회에 결과 전달',
    ])
    st += [Spacer(1, 8), P('2. 활용한 데이터', 'h1'),
           table([['데이터', '원천', '단위·기간', '쓴 곳'],
                  ['제주 지역별 차량 도착 수', '티맵', '읍면동×월, 2023.01~2026.06', '트래픽 지표, 배경 검증, 사후 검증, 효과 측정 비교군'],
                  ['제주 지역별 방문객(읍면동)', 'SKT 이동통신 (30분 이상 체류)', '읍면동×월', '트래픽 지표, 체류율, 사후 검증'],
                  ['제주 지역별 소비', 'BC카드', '읍면동×월×관광객구분×업종 5종', '관광객 소비(숙박 제외), 업종별 누수, 패널 검증, 기대효과'],
                  ['제주 지역별 인기 장소', '티맵 O-D', '목적지×월, 84만여 행, 카테고리 542종', '관광지·로컬 소비처 분류, 로컬전환비, 핀포인트 마을, 관광지 단위 분석'],
                  ['전국주차장정보표준데이터 (보조)', '공공데이터포털', '주차장 위경도', '마을 위치 추정 → 2km 인접 상권 탐색'],
                  ['행정동 경계 (보조)', '통계청 SGIS, vuski/admdongkor', '제주 43개 동', '지도, 대시보드']],
                 [W * 0.22, W * 0.19, W * 0.24, W * 0.35]),
           Spacer(1, 6), P('데이터를 다루며 확인하고 처리한 점', 'h2')]
    st += bullets(['소비 데이터의 49%가 도민 소비 → 관광객(내국인·외국인) 소비만 사용',
                   '숙박업 카드 소비가 10개 동에서 1% 미만(온라인 선결제 추정) → 동별 비교에서 제외, 포함 버전으로 결과 동일 확인',
                   '인기 장소 카테고리 542종을 관광지 / 로컬 소비처 / 숙박 / 비관광으로 명시 분류 (분류표 공개)',
                   '도민 생활 이동이 대부분인 13개 동과 도서 2곳 제외 → 관광 동 28곳 분석',
                   '같은 관광지가 주소에 따라 두 마을로 잡히는 경우(천지연폭포) 마을 단위로 따로 계산해 근거로 활용'])
    st.append(PageBreak())

    # ── 3. 배경
    st += [P('3. 배경 검증: 덜 오지만 더 쓰는 제주', 'h1'),
           fig(os.path.join(V5, '00_배경_연도추이.png'), f'그림 1. 2023=100 기준 연도별 추이. 관광지 관광객 도착 {arr_chg:+.1%}, 도착 1건당 카드 소비 {upa_chg:+.1%}', width=W * 0.8),
           P('4. 통과형 판정: 규모 착시를 걷어 낸 9개 정의의 합의', 'h1'),
           P('트래픽 Z점수에서 소비 Z점수를 빼는 단순 지표는 규모가 큰 동일수록 점수가 높아지는 편향이 있었습니다(규모와 상관 0.61). '
             '트래픽 3종(차량 도착·관광지 관광객 도착·SKT 방문) × 계산법 3종(회귀잔차·로그 Z차이·순위차)의 9개 정의를 표준화해 평균한 '
             '합의점수로 바꿔 편향을 없앴습니다(−0.30). 이어 기준 8가지 민감도, 연도별 재계산, 월 부트스트랩 1,000회로 안정성을 확인했습니다.'),
           fig(os.path.join(V5, '01_통과형_합의점수.png'), '그림 2. 관광 동 28곳의 통과형 합의점수(왼쪽, 빨강=강건한 통과형)와 원안 지표의 규모 편향 비교(오른쪽)')]
    rows = [['동', '유형', '합의점수', '민감도 선정 (8개 중)', '연도 순위 23/24/25', '2026 상반기 검증 순위', '결정']]
    h1 = {'한경면': 2, '송산동': 6, '효돈동': 11}
    for n, dec in [('한경면', '최종 타깃'), ('송산동', '최종 타깃'), ('효돈동', '모니터링')]:
        r = final.loc[n]
        rows.append([n, r['유형'], f"{r['합의점수']:.2f}", int(r['민감도_선정횟수']),
                     f"{int(r['연도순위_2023'])} / {int(r['연도순위_2024'])} / {int(r['연도순위_2025'])}", f'{h1[n]}위', dec])
    st += [table(rows, [W * 0.1, W * 0.17, W * 0.1, W * 0.14, W * 0.17, W * 0.17, W * 0.15]), PageBreak()]

    # ── 5. 유형·벤치마킹
    st += [P('5. 같은 조건끼리 비교: 관광 환경 유형', 'h1'),
           P(f'소비·트래픽을 빼고 관광 환경(공급 규모, 자연·체험 목적지 비중)만으로 관광 동을 3개 유형으로 나눴습니다'
             f'(실루엣 {model["군집 실루엣"]:.2f}, 부트스트랩 안정성 {model["군집 부트스트랩 ARI"]:.2f}). 유형마다 통과형 점수 수준이 달라(ANOVA p=0.008) '
             '같은 유형 안에서 타깃과 벤치마킹 지역을 골랐습니다. 벤치마킹은 기대 이상 소비 + 관광 수요 규모가 비슷(1/3~3배) + 환경이 가장 가까운 동입니다.'),
           fig(os.path.join(V5, '02_관광환경_유형.png'), '그림 3. 관광 동 28곳의 관광 환경 유형 (빨간 테두리 = 강건한 통과형)', width=W * 0.85),
           P('6. 원인 진단: "안 멈추나" vs "멈춰도 덜 쓰나"', 'h1'),
           P('관광지 도착 1건당 소비 = 로컬전환비(관광지 → 근처 식당·카페·로드샵 도착) × 로컬 방문 1건당 소비로 정확히 분해됩니다. '
             '한경면은 벤치마킹 조천읍 대비 격차의 79%가 로컬전환비(안 멈춤)에서 나왔고, 관광 동 사이 도착당 소비 차이도 사실상 전부 로컬전환비 차이였습니다.'),
           fig(os.path.join(V5, '03_소비퍼널_분해.png'), '그림 4. 소비 퍼널(왼쪽)과 벤치마킹 대비 격차의 원인 분해(오른쪽)'),
           P(f'<b>레버 검증</b>: 28개 동 × 36개월 패널에서 동·월 고정효과로 고유 특성과 계절을 통제하면, 같은 관광지 방문 규모에서 로컬 소비처 도착이 10% 늘 때 '
             f'관광객 카드 소비가 약 +3.5% 늘었습니다(탄력성 {model["로컬 방문 탄력성"]:.2f}, 동 단위 군집 강건 표준오차, p&lt;0.001). '
             '"관광지에서 근처 상권으로 동선을 이으면 소비가 는다"는 처방의 근거입니다.'),
           PageBreak()]

    # ── 7. 핀포인트·지도
    st += [P('7. 핀포인트: 동 안에서 정확히 어디인가', 'h1'),
           fig(os.path.join(V5, '05_핀포인트_마을.png'), '그림 5. 마을별 관광지 도착 vs 로컬 소비처 도착 (괄호 = 로컬전환비, 제주 관광 마을 중앙값 1.03)'),
           fig(os.path.join(V5, '06_지도_통과형.png'), '그림 6. 제주 읍면동 지도: 통과형 합의점수, 관광 환경 유형, 로컬전환비, 타깃·벤치마킹 (빗금 = 판정 제외)', max_h=118 * mm),
           fig(os.path.join(V5, '07_지도_서귀포시내.png'), '그림 7. 서귀포 시내 확대: 송산동(정방폭포)과 인접한 서귀동 도심 상권', max_h=62 * mm),
           PageBreak()]

    # ── 8. 스팟
    st += [P('8. 관광지(스팟) 단위 진단과 확대 적용', 'h1'),
           P(f'마을 관광 수요의 절반 이상을 혼자 끌어오는 관광지 {int(model["분석 스팟 수"])}곳을 종류별로 비교했습니다. 폭포·계곡형은 로컬전환비 중앙값이 0.02로 '
             '다른 종류(0.6~1.7)보다 압도적으로 낮았고, 같은 천지연폭포라도 상권과 붙은 서귀동 쪽 진입부는 4.82였습니다. '
             '관광지 도착 1만 건당 로컬 소비처 수로 "공급 부족"과 "연결 부족"을 나누고, 주차장 위경도로 잡은 마을 위치로 2km 이내 인접 상권을 찾았습니다.'),
           fig(os.path.join(V5, '08_스팟_공급연결진단.png'), '그림 8. 관광지 단위 진단 (크기 = 관광객 도착, 점선 = 중앙값)', width=W * 0.82)]
    rows = [['관광지', '종류', '동', '관광객 도착', '로컬전환비', '진단', '연 추가 소비(억원) 보수~상한']]
    for _, r in ex.sort_values('관광객도착', ascending=False).iterrows():
        rows.append([r['목적지명'], r['스팟종류'], r['읍면동명'], f"{int(r['관광객도착']):,}", f"{r['로컬전환비']:.2f}", r['진단'],
                     f"{r['연 추가 소비_보수(억원)']:.0f} ~ {r['연 추가 소비_상한(억원)']:.0f}"])
    rows.append([P('<b>합계</b>', 'cell'), '', '', '', '', '',
                 f"{ex['연 추가 소비_보수(억원)'].sum():.0f} ~ {ex['연 추가 소비_상한(억원)'].sum():.0f}"])
    st += [P('확대 적용 후보 (로컬전환비 하위 25%, 관광객 도착 2만 건 이상, 실내·테마 제외)', 'h2'),
           table(rows, [W * 0.19, W * 0.13, W * 0.1, W * 0.13, W * 0.12, W * 0.12, W * 0.21]),
           P('보수 추정은 7-5장 패널 탄력성(0.36) 적용, 상한은 늘어난 방문이 그 동의 방문당 소비만큼 그대로 쓴다고 가정', 'cap'),
           PageBreak()]

    # ── 9. 처방·KPI
    st += [P('9. 최종 타깃 처방과 KPI', 'h1')]
    for tgt in ['한경면', '송산동']:
        a = acts.loc[tgt]
        st += [P(f'{tgt} — {a["유형"]} · 벤치마킹 {a["벤치마킹"]}', 'h2'),
               table([['항목', '내용'],
                      ['핵심 관광지·진단', a['핵심 스팟·진단']],
                      ['같은 종류 벤치마킹', a['스팟 벤치마킹(같은 종류)']],
                      ['새는 업종 · 집중 시기', f"{a['새는 업종']} · {a['취약 시기']}"],
                      ['제안 액션', '<br/>'.join(f'{i + 1}) {t}' for i, t in enumerate(str(a['제안 액션']).split(' / ')))],
                      ['기대 추가 소비', f"연 {a['기대소비_하한']:.0f}억 ~ {a['기대소비_상한']:.0f}억 원 (기대 소비 격차 25~100% 해소, 카드 결제 기준)"]],
                     [W * 0.2, W * 0.8])]
        krow = [['KPI', '2025 현재', '목표', '목표 기준']]
        for _, k in kpi[kpi['타깃'] == tgt].iterrows():
            fmt = (lambda v: f'{v:,.0f}') if '천원' in k['지표'] else (lambda v: f'{v:.2f}')
            krow.append([k['지표'], fmt(k['현재']), fmt(k['목표']), k['기준']])
        st += [Spacer(1, 3), table(krow, [W * 0.36, W * 0.14, W * 0.14, W * 0.36]), Spacer(1, 6)]
    st += [fig(os.path.join(V5, '04_월별_격차.png'), '그림 9. 월별 도착당 소비 (타깃 ÷ 벤치마킹, 빨강 = 격차가 큰 달 → 집중 운영 시기)'),
           PageBreak()]

    # ── 10. 효과 측정
    st += [P('10. 효과 측정 설계', 'h1'),
           P('이중차분(DiD): 시범사업 전 12개월을 기준선으로, 타깃의 로컬전환비 변화에서 같은 유형 비교 지역의 변화를 뺍니다. '
             '2023~2025 데이터에 가짜 시범사업을 걸어 본 플라시보 분포로 "우연과 구분되는 최소 효과(MDE, 유의수준 5%·검정력 80%)"를 미리 계산했습니다.')]
    rows = [['측정 지표', '사후 기간', 'MDE', 'KPI 목표 변화', '검출']]
    for _, r in mde.iterrows():
        rows.append([r['측정 단위'], f"{int(r['사후 기간(개월)'])}개월", f"+{r['MDE']:.0%}", f"+{r['KPI 목표 변화']:.0%}",
                     '가능' if str(r['검출 가능']) == 'True' else '어려움'])
    st += [table(rows, [W * 0.3, W * 0.15, W * 0.15, W * 0.22, W * 0.18]), Spacer(1, 4),
           P('→ 핀포인트 마을 지표로는 사업 후 6개월, 한경면 전체로는 12개월이면 효과를 확인할 수 있습니다. '
             '송산동은 동 전체로는 효과가 묻혀 정방폭포 일대 마을 지표를 주 KPI로 씁니다.'),
           fig(os.path.join(V5, '09_효과측정_플라시보.png'), '그림 10. 아무 일도 없을 때(플라시보) DiD 분포와 MDE·KPI 목표 (동 단위, 사후 12개월)'),
           PageBreak()]

    # ── 11. 활용
    st += [P('11. 활용: 공개 대시보드와 기관 전달', 'h1'),
           P(f'분석 결과를 지도·타깃 처방·관광지 진단·월별 모니터링이 담긴 웹 대시보드로 만들어 로그인 없이 공개했습니다: <b>{DASH_URL}</b>. '
             '대시보드 데이터는 분석 노트북이 만들며, 플랫폼 데이터가 갱신되면 노트북을 다시 돌려 매월 업데이트할 수 있습니다.')]
    if dash:
        st += [fig(dash['dash_top'], '그림 11. 공개 대시보드: 핵심 숫자와 통과형 지도 (동을 누르면 상세 값 표시)', max_h=150 * mm), PageBreak(),
               fig(dash['dash_targets'], '그림 12. 공개 대시보드: 최종 타깃 처방과 KPI', max_h=110 * mm),
               fig(dash['dash_spots'], '그림 13. 공개 대시보드: 관광지 단위 진단(산점도·필터 표)', max_h=100 * mm),
               PageBreak()]
    st += [P('분석 결과 전달 (10/29)', 'h2'),
           table([['기관', '전달 내용', '회신'],
                  ['서귀포시 관광진흥과', '송산동(정방폭포 일대) 결과, 서귀동 상권 연결 처방, 폭포형 관광지 확대 적용', '[회신 요지]'],
                  ['제주시 관광진흥과', '한경면(신창풍차해안도로) 결과, 로컬 소비 거점 처방, 제주시 확대 후보', '[회신 요지]'],
                  ['서귀포 매일올레시장 상인회', '정방폭포 → 올레시장·이중섭거리 동선 연결 제안', '[회신 요지]']],
                 [W * 0.24, W * 0.56, W * 0.2]),
           P('보낸 메일과 회신 캡처는 별도 이미지로 첨부', 'cap'), Spacer(1, 8),
           P('12. 한계와 보완', 'h1')]
    st += bullets(['체류시간 데이터가 없어 "통과"는 트래픽 대비 소비가 낮다는 간접 지표다 → 9개 정의 합의와 사후 검증으로 보완',
                   '내비게이션 도착은 걸어서 들른 방문을 잡지 못한다 → 절대량이 아닌 동·마을 간 비율 지표로만 쓰고, 카드 소비와 함께 움직이는지 패널로 확인',
                   '카드 데이터는 표본 기준이다 → 모든 금액을 "카드 결제 기준"으로 표기하고 상대 비교로 판정',
                   '관광 카테고리 분류와 인접 상권 위치(주차장 좌표)는 팀이 정한 근사치다 → 분류표와 코드를 공개'])
    st += [Spacer(1, 8), P('출처: 제주관광빅데이터플랫폼(data.ijto.or.kr), 공공데이터포털 전국주차장정보표준데이터, '
                           '통계청 SGIS 행정동 경계(공공누리 제1유형)·vuski/admdongkor 가공본(CC BY 4.0)', 'cap')]

    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title='서식5 증빙자료 - 제주 통과형 관광지 분석 보고서', author='동국대학교 BAF 마케팅팀')
    doc.build(st, onFirstPage=on_page, onLaterPages=on_page)
    print(OUT)


if __name__ == '__main__':
    build()
