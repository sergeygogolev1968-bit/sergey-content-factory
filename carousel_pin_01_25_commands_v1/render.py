from pathlib import Path
import hashlib
import json
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FINAL = ROOT / 'final'
FINAL.mkdir(exist_ok=True)
SOURCE = Path('C:/Users/Sergey/.codex/attachments/53b0bb31-243f-4af4-b182-d8f90aa86ab2/Вставленный текст.txt')
if not (ROOT / 'provided-copy.md').exists():
    source = SOURCE.read_text(encoding='utf-8-sig')
    excerpt = source.split('## Закреп №1 — максимальная польза', 1)[1].split('## Закреп №2', 1)[0].strip()
    (ROOT / 'provided-copy.md').write_text(excerpt + '\n', encoding='utf-8')
copy = (ROOT / 'provided-copy.md').read_text(encoding='utf-8')
commands = [(int(n), t.strip()) for n, t in re.findall(r'(?m)^(\d+)\. (.+)$', copy)]
assert [n for n, _ in commands] == list(range(1, 26))

S = 2
W, H = 1080, 1350
WHITE, ORANGE, MUTED = '#f7f5ef', '#ff8000', '#bec6c9'
FONT_DIR = Path('C:/Windows/Fonts')
FONTS = {'head': 'impact.ttf', 'body': 'segoeui.ttf', 'bold': 'segoeuib.ttf'}
font_cache = {}
bounds = []

def font(kind, size):
    key = kind, size
    if key not in font_cache:
        font_cache[key] = ImageFont.truetype(str(FONT_DIR / FONTS[kind]), round(size * S))
    return font_cache[key]

def length(text, kind, size):
    return font(kind, size).getlength(text) / S

def wrap(text, width, kind, size):
    lines = []
    for paragraph in text.split('\n'):
        line = ''
        for word in paragraph.split():
            candidate = f'{line} {word}'.strip()
            if length(candidate, kind, size) > width and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines

def text(d, value, x, y, size=40, kind='body', color=WHITE, width=936, leading=1.3):
    lines = wrap(value, width, kind, size)
    for line in lines:
        box = d.textbbox((x*S, y*S), line, font=font(kind, size), anchor='lt')
        box = [v / S for v in box]
        assert box[0] >= 68 and box[2] <= 1010, (value, box)
        assert box[1] >= 60 and box[3] <= 1295, (value, box)
        bounds.append({'text': line, 'box': box, 'font_size': size})
        d.text((x*S, y*S), line, font=font(kind, size), fill=color, anchor='lt')
        y += size * leading
    return y

def line(d, xy, fill='#414647', width=1):
    d.line(tuple(v*S for v in xy), fill=fill, width=max(1, round(width*S)))

def base(label):
    im = Image.new('RGB', (W*S, H*S))
    d = ImageDraw.Draw(im)
    for y in range(H*S):
        t = y / (H*S)
        color = (round(18-4*t), round(28-7*t), round(33-9*t))
        d.line((0, y, W*S, y), fill=color)
    d.polygon([(672*S,60*S),(1008*S,132*S),(1008*S,1340*S),(672*S,1274*S)], fill='#1b2021')
    d.polygon([(290*S,1350*S),(1008*S,648*S),(1008*S,1340*S)], fill='#23221e')
    line(d, (672,60,1008,132), '#383b3b')
    line(d, (1008,132,1008,1340), '#383b3b')
    line(d, (72,66,88,66), ORANGE, 2)
    line(d, (72,66,72,89), ORANGE, 2)
    line(d, (88,66,88,89), ORANGE, 2)
    text(d, label, 110, 66, 24, 'bold', MUTED, width=800)
    line(d, (72,1232,1008,1232))
    text(d, 'Сергей Корнеев', 72, 1268, 25, color=MUTED)
    line(d, (980,1280,1004,1280), ORANGE, 3)
    line(d, (995,1271,1004,1280), ORANGE, 3)
    line(d, (995,1289,1004,1280), ORANGE, 3)
    return im, d

pages = []
all_bounds = []
def save(im, number, title, used_commands=None):
    path = FINAL / f'slide_{number:02d}.jpg'
    im.resize((W,H), Image.Resampling.LANCZOS).save(path, 'JPEG', quality=95, subsampling=0, optimize=True)
    pages.append({'file': path.name, 'title': title, 'command_numbers': used_commands or []})
    all_bounds.append({'file': path.name, 'text': bounds.copy()})
    bounds.clear()

im, d = base('ПРАКТИКА С AI')
text(d, '25', 68, 157, 276, 'head', ORANGE)
text(d, 'КОМАНД', 72, 463, 108, 'head')
text(d, 'ChatGPT,', 72, 597, 110, 'head')
text(d, 'которые реально\nэкономят часы', 72, 777, 62, 'bold', leading=1.25)
line(d, (72,1015,182,1015), ORANGE, 5)
text(d, 'Сохрани — пригодится\nне один раз', 72, 1052, 39, color=MUTED)
save(im, 1, '25 команд ChatGPT, которые реально экономят часы')

im, d = base('БОЛЬШЕ, ЧЕМ ПОИСК')
text(d, 'Большинство использует\nChatGPT как обычный поиск.', 72, 185, 51, 'bold', leading=1.28)
text(d, 'А можно заставить его:', 72, 405, 43, color=ORANGE)
items = ['думать по шагам', 'сравнивать варианты', 'проверять ошибки', 'сокращать рутину', 'собирать готовый результат']
for k, item in enumerate(items):
    yy = 508 + k*91
    line(d, (74,yy+22,94,yy+22), ORANGE, 3)
    text(d, item, 120, yy, 41, width=884)
text(d, 'Вот команды,\nс которых стоит начать.', 72, 1030, 43, 'bold')
save(im, 2, 'Больше, чем поиск')

groups = [('РАЗОБРАТЬСЯ', 'И ПРИНЯТЬ РЕШЕНИЕ'), ('НАВЕСТИ ПОРЯДОК', 'В ТЕКСТЕ'), ('ПРОВЕРИТЬ', 'СВОЮ ИДЕЮ'), ('СОКРАТИТЬ', 'РУТИНУ'), ('УСИЛИТЬ', 'РЕЗУЛЬТАТ')]
for group, (h1, h2) in enumerate(groups):
    im, d = base('25 КОМАНД CHATGPT')
    text(d, h1, 72, 162, 68, 'head')
    text(d, h2, 72, 251, 68, 'head', ORANGE)
    selected = commands[group*5:group*5+5]
    y = 402
    for number, body in selected:
        text(d, f'{number:02d}', 72, y+1, 39, 'head', ORANGE, width=70)
        end = text(d, body, 160, y, 38, width=844, leading=1.27)
        row_height = max(130, end-y+40)
        if number != selected[-1][0]:
            line(d, (160,y+row_height-22,1008,y+row_height-22), '#3a4041')
        y += row_height
    assert y <= 1220, (group, y)
    save(im, group+3, h1+' '+h2, [n for n, _ in selected])

im, d = base('КОНТЕКСТ РЕШАЕТ')
text(d, 'ГЛАВНЫЙ СЕКРЕТ:', 72, 172, 72, 'head')
text(d, 'Хороший результат\nначинается не с', 72, 310, 43)
text(d, '«Сделай мне...»', 72, 454, 65, 'bold', ORANGE)
text(d, 'а с контекста:', 72, 568, 43)
flow = ['цель', 'исходные данные', 'ограничения', 'формат результата', 'критерии качества']
for k, item in enumerate(flow):
    y = 675+k*96
    text(d, item, 116, y, 43, 'bold')
    if k < len(flow)-1:
        line(d, (82,y+17,82,y+99), ORANGE, 2)
        line(d, (77,y+93,82,y+99), ORANGE, 2)
        line(d, (87,y+93,82,y+99), ORANGE, 2)
    d.ellipse((76*S,(y+8)*S,88*S,(y+20)*S),fill=ORANGE)
save(im, 8, 'Главный секрет: контекст')

im, d = base('ПРИМЕНЯЙ НА ПРАКТИКЕ')
text(d, 'СОХРАНИ', 72, 180, 116, 'head', ORANGE)
text(d, 'ЭТУ КАРУСЕЛЬ.', 72, 320, 96, 'head')
text(d, 'Дальше буду выкладывать:', 72, 521, 42)
items = ['готовые промпты', 'AI-инструменты', 'рабочие шаблоны', 'способы экономить часы с AI']
for k, item in enumerate(items):
    y = 620+k*88
    line(d, (74,y+20,94,y+20), ORANGE, 3)
    text(d, item, 120, y, 39, width=884)
text(d, 'Подпишись, чтобы\nне искать всё это самому.', 72, 1030, 43, 'bold')
save(im, 9, 'Сохрани эту карусель')

expected = [f'slide_{i:02d}.jpg' for i in range(1,10)]
assert sorted(p.name for p in FINAL.iterdir()) == expected
technical = []
for name in expected:
    path = FINAL/name
    with Image.open(path) as check:
        assert check.format == 'JPEG' and check.size == (1080,1350)
        check.verify()
    with Image.open(path) as check:
        check.load()
        assert check.mode == 'RGB'
    assert path.stat().st_size <= 8*1024*1024
    technical.append({'file':name, 'format':'JPEG', 'width':1080, 'height':1350, 'bytes':path.stat().st_size, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

sheet = Image.new('RGB', (1128,1476), '#e5e5e2')
sd = ImageDraw.Draw(sheet)
for i, name in enumerate(expected):
    x = 18 + (i%3)*372
    y = 18 + (i//3)*486
    with Image.open(FINAL/name) as slide:
        sheet.paste(slide.resize((348,435), Image.Resampling.LANCZOS), (x,y))
    sd.text((x,y+443), name, fill='#252525', font=ImageFont.truetype(str(FONT_DIR/'segoeui.ttf'),18))
sheet.save(ROOT/'contact-sheet.jpg', quality=95, subsampling=0)
(ROOT/'layout-check.json').write_text(json.dumps(all_bounds, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
report = {
    'version':'carousel_pin_01_25_commands_v1', 'status':'draft',
    'scope':'Закреп №1; только локальная подготовка, без публикации',
    'copy_source':'provided-copy.md — текст пользователя',
    'visual_reference':'assets/carousels_20260928/carousel_09; адаптация фирменного стиля, не точная копия недоступного Canva-макета',
    'technical_qa':'pass', 'content_qa':'pending', 'visual_qa':'pending',
    'command_count':len(commands), 'slide_count':len(pages), 'slides':pages, 'files':technical,
    'publication_authorized':False, 'design_user_approved':False,
    'checks':['JPEG decode and verify', '1080x1350 RGB', 'sequential names', 'no extra final files', 'under 8 MiB each', '25 commands in source order', 'text within canvas safety bounds'],
}
(ROOT/'qa-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'slides':len(pages), 'commands':len(commands), 'technical_qa':'pass', 'final':str(FINAL)}, ensure_ascii=False))
