"""Build the MOVAVYMOVA podcast carousel as one HTML file (one .slide per card)."""
import pathlib, re

ROOT = pathlib.Path(__file__).parent

CYR = "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"
LAT = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,"
       "U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")


def font_faces():
    css = []
    for w in (500, 600, 700, 800, 900):
        for sub, rng in (("latin", LAT), ("cyrillic", CYR)):
            css.append(f"@font-face{{font-family:M;font-weight:{w};"
                       f"src:url(fonts/montserrat-{sub}-{w}-normal.woff2) format('woff2');unicode-range:{rng}}}")
    return "\n".join(css)


def icon(name, color="#fff", size=46, sw=1.8):
    svg = (ROOT / "icons" / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r'width="\d+"', f'width="{size}"', svg, count=1)
    svg = re.sub(r'height="\d+"', f'height="{size}"', svg, count=1)
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    svg = re.sub(r'stroke-width="[\d.]+"', f'stroke-width="{sw}"', svg)
    return svg


HANDLE = '<div class="handle">@movavymova</div>'


def swoosh(kicker, title, sub=""):
    return f"""
    <div class="swoosh"></div>
    <div class="head">
      <div class="kicker">{kicker}</div>
      <h1>{title}</h1>
      {f'<p class="sub">{sub}</p>' if sub else ''}
    </div>"""


def card(ic, name, by, tag, text, chips):
    chips_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    return f"""
    <div class="card">
      <div class="dot">{icon(ic)}</div>
      <div class="body">
        <div class="row"><span class="name">{name}</span><span class="tag">{tag}</span></div>
        <div class="by">{by}</div>
        <p>{text}</p>
        <div class="chips">{chips_html}</div>
      </div>
    </div>"""


def level_slide(n, level, fits, cards):
    return f"""
  <section class="slide level" id="s{n}">
    {swoosh("РІВЕНЬ", level, fits)}
    <div class="num">{n:02d}</div>
    <div class="cards">{''.join(card(*c) for c in cards)}</div>
    {HANDLE}
  </section>"""


ARROW = icon("arrow-right", "#141414", 40, 2.4)

slides = []

# 1. Cover — the brand's black staircase, re-used as a level ladder
slides.append(f"""
  <section class="slide cover" id="s1">
    <div class="swoosh big"></div>
    <div class="head">
      <div class="kicker">АНГЛІЙСЬКА НА СЛУХ —</div>
      <h1>9 ПІДКАСТІВ,<br>ЯКІ НЕ ХОЧЕТЬСЯ<br>ВИМИКАТИ</h1>
      <div class="tags"><span class="tag lg">від A1 до C1</span><span class="tag lg">без нудних уроків</span></div>
    </div>
    <div class="stairs">
      <div class="step s1"><span>A1–A2</span></div>
      <div class="step s2"><span>B1–B2</span></div>
      <div class="step s3"><span>C1</span></div>
      <div class="bubble">{icon("headphones", "#141414", 92, 1.9)}</div>
    </div>
    <div class="path"></div>
    <div class="swipe">Гортай {ARROW}</div>
    {HANDLE}
  </section>""")

# 2. Method
steps = [
    ("ear", "Слухай без тексту", "лови суть", "Не зупиняйся на кожному слові. Питання одне: про що це?"),
    ("file-text", "Слухай з транскриптом", "деталі", "Випиши 5 фраз, які хочеш забрати собі, а не 30 окремих слів."),
    ("repeat", "Ще раз без тексту", "прогрес", "Порівняй: скільки ти розумієш тепер? Саме цей момент мотивує."),
]
step_html = "".join(f"""
      <div class="step-row">
        <div class="dot">{icon(i)}</div>
        <div><div class="st">{t}</div><span class="tag">{tg}</span><p>{d}</p></div>
      </div>""" for i, t, tg, d in steps)
slides.append(f"""
  <section class="slide method" id="s2">
    {swoosh("ПЕРШ НІЖ НАТИСНУТИ PLAY —", "МЕТОД<br>ТРЬОХ ПРОСЛУХОВУВАНЬ", "Один випуск, три підходи. Так підкаст стає уроком, а не фоном.")}
    <div class="steps">{step_html}</div>
    <div class="note"><div class="note-ic">{icon("gauge", "#141414", 44, 2)}</div>
      <p><b>Швидкість 0.8×</b> — це не соромно.<br>Це тренування, а не іспит.</p></div>
    {HANDLE}
  </section>""")

# 3–5. Levels
slides.append(level_slide(3, "A1–A2", "Підійде, якщо ти вже знаєш базові фрази, але носії говорять «занадто швидко».", [
    ("book-open", "Easy Stories in English", "Ariel Goodbody", "історії",
     "Оповідання з позначкою рівня: Beginner, Pre-Intermediate, Intermediate. Автор — лінгвіст, випускник Кембриджу.",
     ["транскрипти на сайті", "обирай свій рівень"]),
    ("message-circle-more", "The English We Speak", "BBC Learning English", "сленг",
     "Один випуск — одна жива фраза. Є навіть «side quest» та «understood the assignment».",
     ["~3 хв", "щотижня"]),
    ("newspaper", "Plain English", "ведучий Jeff", "новини",
     "Актуальні новини простою мовою. Кожна історія записана у двох швидкостях.",
     ["повільна — безкоштовно", "+ розбір виразу"]),
]))
slides.append(level_slide(4, "B1–B2", "Підійде, якщо ти дивишся серіали з субтитрами й хочеш колись їх вимкнути.", [
    ("ear", "All Ears English", "Lindsay McMahon & Michelle Kaplan", "розмовна",
     "Американська англійська для живого спілкування. Девіз шоу: «Connection NOT Perfection».",
     ["американський акцент", "small talk"]),
    ("atom", "Short Wave", "NPR", "наука",
     "Одне наукове питання — один короткий випуск. Ідеально на дорогу до роботи.",
     ["до ~15 хв", "сучасна лексика"]),
    ("lightbulb", "Stuff You Should Know", "Josh Clark & Chuck Bryant", "про все",
     "Двоє друзів пояснюють, як влаштовано все на світі, від побутових речей до історії.",
     ["з 2008 року", "тисячі тем"]),
]))
slides.append(level_slide(5, "C1", "Підійде, якщо хочеш не «розуміти англійську», а слухати її для задоволення.", [
    ("fish", "No Such Thing As A Fish", "дослідники шоу QI", "факти",
     "Команда, яка шукає факти для британського шоу QI, щотижня приносить свої найдивніші знахідки.",
     ["британський гумор", "щотижня"]),
    ("building-2", "99% Invisible", "Roman Mars", "дизайн",
     "Історії про дизайн, якого ми не помічаємо: прапори, шрифти, міські лавки.",
     ["сторітелінг", "архітектура"]),
    ("book-a", "The Allusionist", "Helen Zaltzman", "слова",
     "Звідки беруться слова і як змінюється мова. Мрія для всіх, хто любить мови.",
     ["транскрипти на сайті", "з 2015 року"]),
]))

# 6. Facts
facts = [
    ("fish", "«Риби» як наукової групи не існує",
     "Лосось за походженням ближчий до верблюда, ніж до міксини. Звідси й назва підкасту <b>No Such Thing As A Fish</b>."),
    ("eye", "99% — це цитата",
     "Назву <b>99% Invisible</b> взято з вислову архітектора й винахідника Бакмінстера Фуллера."),
    ("sparkles", "BBC пояснює геймерський сленг",
     "У <b>The English We Speak</b> є випуск про «side quest» — побічну місію, яка стала словом із життя."),
]
fact_html = "".join(f"""
      <div class="fact">
        <div class="dot y">{icon(i, "#141414")}</div>
        <div><div class="ft">{t}</div><p>{d}</p></div>
      </div>""" for i, t, d in facts)
slides.append(f"""
  <section class="slide facts" id="s6">
    {swoosh("БОНУС —", "«О, Я ЦЬОГО<br>НЕ ЗНАЛА!»", "Три факти, які варто розповісти друзям.")}
    <div class="fact-list">{fact_html}</div>
    {HANDLE}
  </section>""")

# 7. CTA
slides.append(f"""
  <section class="slide cta" id="s7">
    <div class="swoosh big"></div>
    <div class="head">
      <div class="kicker">А ЩО СЛУХАЄШ ТИ?</div>
      <h1>НАПИШИ<br>У КОМЕНТАРЯХ</h1>
      <p class="sub">Найцікавіші підкасти додамо до наступної підбірки.</p>
    </div>
    <div class="cta-list">
      <div class="cta-row"><div class="dot">{icon("bookmark")}</div><div>Збережи, щоб <span class="tag">не загубити</span></div></div>
      <div class="cta-row"><div class="dot">{icon("send")}</div><div>Надішли тому, хто <span class="tag">вчить англійську</span></div></div>
      <div class="cta-row"><div class="dot">{icon("message-circle")}</div><div>Хочеш не лише розуміти, а й <span class="tag">говорити?</span></div></div>
    </div>
    <div class="final">
      <div class="bubble-y"><i></i><i></i><i></i></div>
      <div class="final-text">Пиши в директ — <b>ми чекаємо<br>саме на тебе</b></div>
    </div>
    {HANDLE}
  </section>""")

html = f"""<!doctype html><html lang="uk"><head><meta charset="utf-8">
<style>
{font_faces()}
:root{{--y:#F3B500;--k:#141414;--bg:#F4F3EF;--g:#5c5c5c}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#999;font-family:M,sans-serif;color:var(--k)}}
.slide{{width:1080px;height:1350px;position:relative;overflow:hidden;background:var(--bg);margin:0 auto 40px;
  background-image:radial-gradient(#d9d7d0 2px,transparent 2.4px);background-size:34px 34px;background-position:17px 17px}}
.swoosh{{position:absolute;left:-260px;top:-520px;width:1180px;height:860px;border-radius:50%;background:var(--y)}}
.swoosh.big{{left:-240px;top:-470px;width:1300px;height:1000px}}
.head{{position:relative;padding:70px 72px 0}}
.kicker{{font-weight:800;font-size:44px;letter-spacing:.5px;color:var(--k);text-transform:uppercase}}
h1{{font-weight:900;font-size:84px;line-height:1.02;letter-spacing:-.5px;text-transform:uppercase;margin-top:8px}}
.sub{{font-weight:600;font-size:30px;line-height:1.35;margin-top:22px;max-width:760px}}
.tag{{display:inline-block;background:var(--y);color:var(--k);font-weight:800;font-size:22px;padding:5px 12px;
  border-radius:4px;vertical-align:middle;line-height:1.2}}
.tag.lg{{font-size:30px;padding:8px 18px;margin-right:14px;background:var(--k);color:#fff}}
.tags{{margin-top:30px}}
.handle{{position:absolute;right:56px;bottom:40px;font-weight:700;font-size:22px;color:#6b6b6b}}
.dot{{flex:none;width:92px;height:92px;border-radius:50%;background:var(--k);display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 22px rgba(0,0,0,.18)}}
.dot.y{{background:var(--y)}}

/* cover */
.cover .kicker{{color:var(--k);font-size:40px}}
.cover h1{{font-size:96px;margin-top:14px}}
.stairs{{position:absolute;left:150px;bottom:150px;width:780px;height:600px}}
.step{{position:absolute;bottom:0;background:linear-gradient(180deg,#2a2a2a,#0f0f0f);border-radius:6px 6px 0 0;
  box-shadow:-18px 0 0 #000 inset, 0 30px 50px rgba(0,0,0,.25);display:flex;justify-content:center;padding-top:28px}}
.step span{{font-weight:900;font-size:46px;color:var(--y)}}
.step.s1{{left:0;width:250px;height:230px}}
.step.s2{{left:265px;width:250px;height:370px}}
.step.s3{{left:530px;width:250px;height:510px}}
.bubble{{position:absolute;left:560px;top:-190px;width:190px;height:170px;background:var(--y);border-radius:44px;display:flex;
  align-items:center;justify-content:center;box-shadow:0 18px 40px rgba(0,0,0,.2)}}
.bubble:after{{content:"";position:absolute;bottom:-26px;left:46px;border:20px solid transparent;border-top:30px solid var(--y);border-left:8px solid var(--y)}}
.path{{position:absolute;left:58px;top:740px;width:320px;height:210px;border-left:4px dashed var(--k);border-top:4px dashed var(--k);
  border-radius:120px 0 0 0;opacity:.35}}
.swipe{{position:absolute;left:72px;bottom:44px;font-weight:800;font-size:30px;display:flex;align-items:center;gap:10px}}

/* method */
.method .kicker,.level .kicker,.facts .kicker{{font-size:34px}}
.method h1{{font-size:70px}}
.steps{{position:absolute;left:72px;right:72px;top:500px;display:flex;flex-direction:column;gap:30px}}
.step-row{{display:flex;gap:34px;align-items:flex-start}}
.st{{font-weight:800;font-size:36px;margin-bottom:8px}}
.step-row p{{font-weight:500;font-size:26px;line-height:1.38;color:#333;margin-top:10px}}
.note{{position:absolute;left:72px;right:72px;bottom:96px;background:var(--k);color:#fff;border-radius:28px;padding:30px 36px;
  display:flex;gap:28px;align-items:center}}
.note p{{font-size:28px;line-height:1.4;font-weight:500}}
.note b{{color:var(--y);font-weight:800}}
.note-ic{{flex:none;width:76px;height:76px;border-radius:50%;background:var(--y);display:flex;align-items:center;justify-content:center}}

/* levels */
.level h1{{font-size:140px;letter-spacing:-2px}}
.level .sub{{font-size:28px;max-width:600px;margin-top:6px}}
.num{{position:absolute;right:64px;top:60px;font-weight:900;font-size:40px;color:var(--k);opacity:.25}}
.cards{{position:absolute;left:56px;right:56px;top:440px;display:flex;flex-direction:column;gap:22px}}
.card{{background:#fff;border-radius:28px;padding:26px 30px;display:flex;gap:28px;box-shadow:0 10px 30px rgba(0,0,0,.07)}}
.card .row{{display:flex;align-items:center;gap:14px;flex-wrap:wrap}}
.card .name{{font-weight:800;font-size:34px;letter-spacing:-.3px}}
.by{{font-weight:600;font-size:21px;color:#8a8a8a;margin-top:4px}}
.card p{{font-weight:500;font-size:25px;line-height:1.38;color:#2b2b2b;margin-top:12px}}
.chips{{margin-top:14px;display:flex;gap:10px;flex-wrap:wrap}}
.chip{{font-weight:700;font-size:20px;border:2px solid var(--k);border-radius:40px;padding:5px 16px}}

/* facts */
.facts h1{{font-size:80px}}
.fact-list{{position:absolute;left:56px;right:56px;top:520px;display:flex;flex-direction:column;gap:30px}}
.fact{{background:var(--k);color:#fff;border-radius:28px;padding:36px 36px;display:flex;gap:30px;align-items:flex-start}}
.ft{{font-weight:800;font-size:34px;color:var(--y);line-height:1.2}}
.fact p{{font-weight:500;font-size:26px;line-height:1.42;margin-top:12px;color:#eee}}
.fact b{{color:#fff;font-weight:800}}

/* cta */
.cta .kicker{{color:var(--k);font-size:40px}}
.cta h1{{font-size:100px}}
.cta-list{{position:absolute;left:72px;right:72px;top:620px;display:flex;flex-direction:column;gap:34px}}
.cta-row{{display:flex;align-items:center;gap:30px;font-weight:700;font-size:34px;line-height:1.4}}
.cta-row .tag{{font-size:32px;padding:4px 14px}}
.final{{position:absolute;left:72px;right:72px;bottom:110px;display:flex;align-items:center;gap:34px}}
.bubble-y{{position:relative;width:170px;height:130px;background:var(--y);border-radius:36px;display:flex;align-items:center;
  justify-content:center;gap:14px;box-shadow:0 16px 36px rgba(0,0,0,.18);transform:rotate(-6deg)}}
.bubble-y:after{{content:"";position:absolute;bottom:-24px;left:34px;border:16px solid transparent;border-top:26px solid var(--y);border-left:6px solid var(--y)}}
.bubble-y i{{width:20px;height:20px;border-radius:50%;background:#fff}}
.final-text{{font-weight:600;font-size:36px;line-height:1.3}}
.final-text b{{font-weight:900;text-transform:uppercase}}
</style></head><body>
{''.join(slides)}
</body></html>"""

(ROOT / "carousel.html").write_text(html)
print("ok", len(slides), "slides")
