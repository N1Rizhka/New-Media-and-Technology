#!/usr/bin/env python3
"""Assemble per-week question banks into N mock exams + answer keys (HTML + PDF)."""
import json, os, re, subprocess, sys, html, random
from collections import Counter, defaultdict

SRC = os.environ.get('MOCK_SRC', '/tmp/mock')
OUT = sys.argv[1] if len(sys.argv) > 1 else '/workspace/exam_prep'
N_EXAMS = 16
WEEKS = range(1, 9)
WEEK_NAMES = {1: 'Introduction and Fundamentals I', 2: 'Fundamentals II', 3: 'Association and Rules',
              4: 'Classification', 5: 'Regression', 6: 'Clustering',
              7: 'Text Analysis and NLP', 8: 'Social Network Analysis'}
CASE_PAIRS = [(1, 5), (2, 6), (3, 7), (4, 8), (1, 6), (2, 7), (3, 8), (4, 5),
              (1, 7), (2, 8), (3, 5), (4, 6), (1, 8), (2, 5), (3, 6), (4, 7)]
DROP = set()
for _w in WEEKS:
    if os.path.exists(f'{SRC}/drop_w{_w}.json'):
        DROP |= set(json.load(open(f'{SRC}/drop_w{_w}.json')))


def load():
    banks = {}
    for w in WEEKS:
        b = json.load(open(f'{SRC}/bank_w{w}.json'))
        for k in ('mcq', 'short', 'cases'):
            b[k] = [it for it in b[k] if it['id'] not in DROP]
            for it in b[k]:
                it['week'] = w
        banks[w] = b
    return banks


def topic_order(bank, items, key='topic'):
    """Stable order by the first appearance of each topic, so dealing round-robin spreads topics."""
    order = {}
    for it in items:
        t = it.get(key) if key == 'topic' else (it.get('topics') or [''])[0]
        order.setdefault(t, len(order))
    return order


def deal(items, n_slots_per_exam_fn):
    """Interleave items by topic so consecutive picks differ in topic."""
    groups = defaultdict(list)
    for it in items:
        groups[it['topic']].append(it)
    seq = []
    queues = list(groups.values())
    while any(queues):
        for q in queues:
            if q:
                seq.append(q.pop(0))
    return seq


def plan(banks):
    exams = [{'n': e + 1, 'mcq': [], 'short': [], 'cases': []} for e in range(N_EXAMS)]
    # Part A: 2 per week, except one week per exam gets 1 (rotating) -> 15
    for w in WEEKS:
        seq = deal(banks[w]['mcq'], None)
        need = [1 if (e % 8) + 1 == w else 2 for e in range(N_EXAMS)]
        if len(seq) < sum(need):
            sys.exit(f'week {w}: only {len(seq)} MCQs, need {sum(need)}')
        i = 0
        # first pass one item each, second pass the second item, to spread topics
        for rnd in range(2):
            for e in range(N_EXAMS):
                if need[e] > rnd:
                    exams[e]['mcq'].append(seq[i]); i += 1
    # Part B: 80 slots cycling weeks 1..8, chunks of 5 -> distinct weeks per exam
    slots = [((s % 8) + 1) for s in range(N_EXAMS * 5)]
    seqs = {w: deal(banks[w]['short'], None) for w in WEEKS}
    used = Counter()
    for e in range(N_EXAMS):
        for w in slots[e * 5:(e + 1) * 5]:
            if used[w] >= len(seqs[w]):
                sys.exit(f'week {w}: not enough short answers')
            exams[e]['short'].append(seqs[w][used[w]]); used[w] += 1
    # Part C
    cidx = Counter()
    for e, pair in enumerate(CASE_PAIRS):
        for w in pair:
            cs = banks[w]['cases']
            if cidx[w] >= len(cs):
                sys.exit(f'week {w}: not enough cases')
            exams[e]['cases'].append(cs[cidx[w]]); cidx[w] += 1
    for ex in exams:
        ex['mcq'].sort(key=lambda it: it['week'])
        ex['short'].sort(key=lambda it: it['week'])
        ex['cases'].sort(key=lambda it: it['week'])
    return exams


CSS = """
@page { size: A4; margin: 16mm 16mm 16mm 16mm; }
* { box-sizing: border-box; }
body { font-family: 'Charter','Georgia','Times New Roman',serif; font-size: 10.6pt; line-height: 1.42; color: #111; margin: 0; }
.wrap { max-width: 178mm; margin: 0 auto; }
h1 { font-size: 19pt; margin: 0 0 2mm; text-align: center; }
h2 { font-size: 13.5pt; margin: 7mm 0 2mm; border-bottom: 1.5px solid #0b6b6b; padding-bottom: 1mm; color: #0b4f4f; }
h3 { font-size: 11.5pt; margin: 5mm 0 1.5mm; color: #0b4f4f; }
.sub { text-align: center; color: #444; margin: 0 0 4mm; }
.runner { font-size: 8.5pt; color: #0b6b6b; border-bottom: 1px solid #9cc; padding-bottom: 1mm; margin-bottom: 4mm; display: flex; justify-content: space-between; }
table.cover { border-collapse: collapse; margin: 3mm auto 4mm; }
table.cover td, table.cover th { border: 1px solid #555; padding: 1.5mm 5mm; text-align: center; }
.idbox { display: grid; grid-template-columns: 1fr 1fr; gap: 2mm 8mm; margin: 4mm 0; }
.idbox div { border-bottom: 1px solid #777; padding-top: 4mm; font-size: 9.5pt; color: #444; }
ol.instr { padding-left: 5mm; font-size: 9.8pt; }
ol.instr li { margin-bottom: 1mm; }
.grid { display: grid; grid-template-columns: repeat(15, 1fr); border: 1px solid #555; margin: 2mm 0 4mm; }
.grid div { border-right: 1px solid #999; text-align: center; font-size: 8.5pt; padding: 1mm 0 7mm; }
.grid div:last-child { border-right: none; }
.q { margin: 0 0 4mm; break-inside: avoid; }
.q .qh { font-weight: bold; }
.q ol.opts { list-style: none; padding-left: 6mm; margin: 1mm 0 0; }
.q ol.opts li { margin: 0.6mm 0; }
.formula { background: #eef6f6; border-left: 3px solid #0b6b6b; padding: 1mm 2.5mm; margin: 1.5mm 0; font-size: 9.8pt; }
table.ex { border-collapse: collapse; margin: 2mm 0; font-size: 9.6pt; }
table.ex th, table.ex td { border: 1px solid #888; padding: 0.8mm 2.5mm; text-align: left; vertical-align: top; }
table.ex th { background: #e6efef; }
.space { border: 1px dashed #bbb; border-radius: 2px; margin: 2mm 0 5mm; }
.case { break-before: page; }
.exhibit { margin: 3mm 0; break-inside: avoid; }
.exhibit .et { font-weight: bold; margin-bottom: 1mm; }
.note { font-size: 9.3pt; color: #333; font-style: italic; }
.pb { break-before: page; }
.key table.ak { border-collapse: collapse; width: 100%; font-size: 9.8pt; }
.key table.ak th, .key table.ak td { border: 1px solid #999; padding: 1mm 2mm; vertical-align: top; text-align: left; }
.key table.ak th { background: #e6efef; }
.key .ref, .key .mark { margin: 1.5mm 0; }
.key .lbl { font-weight: bold; color: #0b4f4f; }
.key .blk { margin-bottom: 5mm; break-inside: avoid-page; }
.wk { font-size: 8.5pt; color: #0b6b6b; font-weight: normal; }
.end { text-align: center; margin-top: 8mm; color: #555; }
@media screen { body { background: #f3f3f3; } .wrap { background: #fff; padding: 12mm 14mm; margin: 6mm auto; box-shadow: 0 1px 6px rgba(0,0,0,.15); } }
"""


def page(title, body):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title><style>{CSS}</style></head><body><div class="wrap">{body}</div></body></html>"""


def fml(s):
    return f'<div class="formula">{s}</div>' if s and s.strip() else ''


def para(s):
    s = s.strip()
    return s if s.startswith('<') else f'<p>{s}</p>'


def render_paper(ex):
    n = ex['n']
    runner = f'<div class="runner"><span>New Media Technology and Analytics · Mock Exam {n:02d}</span><span>Practice paper · 90 minutes · 100 marks</span></div>'
    b = [runner, f'<h1>Mock Examination {n:02d}</h1>',
         '<p class="sub">New Media Technology and Analytics (20001920076) · Fall 2026 · Tongji SEM<br>Practice time: 90 minutes, continuously. Total marks: 100.</p>',
         '<div class="idbox"><div>Name</div><div>Student ID</div></div>',
         '<table class="cover"><tr><th>Section</th><th>Part A</th><th>Part B</th><th>Part C</th><th>Total</th></tr>'
         '<tr><td>Maximum marks</td><td>30</td><td>30</td><td>40</td><td>100</td></tr><tr><td>Score</td><td></td><td></td><td></td><td></td></tr></table>',
         '<h3>Instructions</h3><ol class="instr">'
         '<li>Answer every question in English. Circle one option for each Part A question and write its letter in the answer grid; if the two differ, the letter in the grid is marked.</li>'
         '<li>Part A carries 30 marks, Part B 30 marks and Part C 40 marks. Write three to five sentences for each Part B answer. For Part C, show the requested working and explain your decisions.</li>'
         '<li>You may use one A4 sheet of notes, both sides, and a non-programmable calculator. Required formulas are printed beside the relevant questions. No program-code writing is required.</li>'
         '<li>This paper practises the examined content of Weeks 1 to 8. Week 9 and later content and ethical and legal topics are excluded.</li>'
         '<li>All scenarios and figures are fictional. Suggested timing: Part A 20 minutes, Part B 30 minutes, Part C 40 minutes.</li></ol>',
         '<h2>Part A: Multiple choice</h2><p>15 questions, 2 marks each, 30 marks. Circle one answer per question and write its letter in the answer grid.</p>',
         '<div class="grid">' + ''.join(f'<div>A{i}</div>' for i in range(1, 16)) + '</div>']
    for i, q in enumerate(ex['mcq'], 1):
        opts = ''.join(f'<li>({l}) {o}</li>' for l, o in zip('abcd', q['options']))
        b.append(f'<div class="q"><span class="qh">A{i} (2 marks).</span> {q["stem"]}{fml(q.get("formula",""))}<ol class="opts">{opts}</ol></div>')
    b.append('<h2 class="pb">Part B: Short answer</h2><p>5 questions, 6 marks each, 30 marks. Write three to five sentences per answer. Show any requested arithmetic.</p>')
    for i, q in enumerate(ex['short'], 1):
        b.append(f'<div class="q"><span class="qh">B{i} (6 marks).</span> {q["stem"]}{fml(q.get("formula",""))}<div class="space" style="height:62mm"></div></div>')
    b.append('<h2 class="pb">Part C: Case analysis</h2><p>2 cases, 20 marks each, 40 marks. Answer every question. All businesses and figures are fictional.</p>')
    for ci, c in enumerate(ex['cases'], 1):
        cls = 'case' if ci > 1 else ''
        b.append(f'<div class="{cls}"><h3>Case {ci}: {c["name"]} (20 marks)</h3>{c["scenario"]}')
        for exh in c.get('exhibits', []):
            note = f'<div class="note">{exh["note"]}</div>' if exh.get('note') else ''
            b.append(f'<div class="exhibit"><div class="et">{exh["title"]}</div>{exh["html"]}{note}</div>')
        for qi, sq in enumerate(c['questions'], 1):
            h = 20 + 9 * sq['marks']
            b.append(f'<div class="q"><span class="qh">C{ci}.{qi} ({sq["marks"]} marks).</span> {sq["stem"]}<div class="space" style="height:{h}mm"></div></div>')
        b.append('</div>')
    b.append('<p class="end">End of paper.</p>')
    return page(f'NMTA Mock Exam {n:02d}', '\n'.join(b))


def render_key(ex):
    n = ex['n']
    runner = f'<div class="runner"><span>NMTA · Mock Exam {n:02d} · Answers and marking guide</span><span>For self-checking after your attempt</span></div>'
    b = [runner, '<div class="key">', f'<h1>Mock Examination {n:02d}: Answers and Marking Guide</h1>',
         '<p class="sub">New Media Technology and Analytics (20001920076) · Total marks: 100</p>',
         '<p>Compare the reasoning as well as the final answer. Equivalent, accurate explanations earn the stated marks; the sample wording is not required. Add the marks for distinct points, never award the same point twice, and do not exceed the question total. Calculations may be given as fractions, decimals or percentages.</p>',
         '<h2>Part A: Answers and explanations</h2><p>Each correct choice earns 2 marks; a wrong, blank or multiple answer earns 0.</p>',
         '<table class="ak"><tr><th style="width:9%">Q</th><th style="width:9%">Answer</th><th style="width:16%">Week</th><th>Explanation</th></tr>']
    for i, q in enumerate(ex['mcq'], 1):
        b.append(f'<tr><td>A{i}</td><td>({q["answer"]})</td><td>W{q["week"]}: {html.escape(q["topic"])}</td><td>{q["explanation"]}</td></tr>')
    b.append('</table>')
    b.append('<h2>Part B: Reference answers and marking guidance</h2>')
    for i, q in enumerate(ex['short'], 1):
        b.append(f'<div class="blk"><h3>B{i}: {q["title"]} (6 marks) <span class="wk">Week {q["week"]} · {html.escape(q["topic"])}</span></h3>'
                 f'<div class="ref"><span class="lbl">Reference answer.</span> {q["reference"]}</div>'
                 f'<div class="mark"><span class="lbl">Marking.</span> {q["marking"]}</div></div>')
    b.append('<h2>Part C: Case analysis</h2>')
    for ci, c in enumerate(ex['cases'], 1):
        b.append(f'<h3>Case {ci}: {c["name"]} <span class="wk">Week {c["week"]} · {html.escape(", ".join(c.get("topics", [])))}</span></h3>')
        for qi, sq in enumerate(c['questions'], 1):
            b.append(f'<div class="blk"><p class="qh"><b>C{ci}.{qi} ({sq["marks"]} marks).</b></p>'
                     f'<div class="ref"><span class="lbl">Model answer.</span> {sq["answer"]}</div>'
                     f'<div class="mark"><span class="lbl">Marking.</span> {sq["marking"]}</div></div>')
    b.append('</div>')
    return page(f'NMTA Mock Exam {n:02d} Answer Key', '\n'.join(b))


def pdf(src, dst):
    # Headless Chrome on this VM writes the PDF and then hangs, so wait for the
    # "bytes written" line and kill the process group.
    import signal, time
    if os.path.exists(dst):
        os.remove(dst)
    p = subprocess.Popen(['google-chrome', '--headless', '--no-sandbox', '--disable-gpu', '--no-first-run',
                          '--disable-extensions', '--disable-dev-shm-usage', '--user-data-dir=/tmp/chr-mock',
                          '--no-pdf-header-footer', f'--print-to-pdf={dst}', f'file://{src}'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, start_new_session=True)
    t0 = time.time()
    for line in p.stderr:
        if 'bytes written' in line or time.time() - t0 > 90:
            break
    os.killpg(p.pid, signal.SIGKILL)
    p.wait()
    if not os.path.exists(dst) or os.path.getsize(dst) == 0:
        sys.exit(f'PDF failed: {dst}')


def check(banks, exams):
    errs = []
    ids = Counter()
    for ex in exams:
        assert len(ex['mcq']) == 15 and len(ex['short']) == 5 and len(ex['cases']) == 2, ex['n']
        for k in ('mcq', 'short', 'cases'):
            for it in ex[k]:
                ids[it['id']] += 1
        for c in ex['cases']:
            s = sum(q['marks'] for q in c['questions'])
            if s != 20:
                errs.append(f'{c["id"]} marks sum {s}')
        for q in ex['mcq']:
            if len(q['options']) != 4 or q['answer'] not in 'abcd':
                errs.append(f'{q["id"]} options/answer malformed')
    dup = [i for i, c in ids.items() if c > 1]
    if dup:
        errs.append(f'duplicate use: {dup}')
    return errs


def main():
    banks = load()
    exams = plan(banks)
    errs = check(banks, exams)
    if errs:
        print('\n'.join(errs)); sys.exit(1)
    pdir, kdir = f'{OUT}/mock_exams', f'{OUT}/mock_exam_answer_keys'
    for d in (pdir, kdir, f'{pdir}/html', f'{kdir}/html'):
        os.makedirs(d, exist_ok=True)
    for ex in exams:
        n = ex['n']
        ph, kh = f'{pdir}/html/NMTA_Mock_Exam_{n:02d}.html', f'{kdir}/html/NMTA_Mock_Exam_{n:02d}_Answer_Key.html'
        open(ph, 'w').write(render_paper(ex)); open(kh, 'w').write(render_key(ex))
        if '--nopdf' not in sys.argv:
            pdf(ph, f'{pdir}/NMTA_Mock_Exam_{n:02d}.pdf'); pdf(kh, f'{kdir}/NMTA_Mock_Exam_{n:02d}_Answer_Key.pdf')
        print('built', n, flush=True)
    json.dump([{'n': ex['n'], 'mcq': [q['id'] for q in ex['mcq']], 'short': [q['id'] for q in ex['short']],
                'cases': [q['id'] for q in ex['cases']]} for ex in exams], open(f'{SRC}/plan.json', 'w'), indent=1)
    # coverage
    cov = defaultdict(lambda: defaultdict(list))
    for ex in exams:
        for k in ('mcq', 'short'):
            for it in ex[k]:
                cov[it['week']][it['topic']].append(ex['n'])
        for c in ex['cases']:
            for t in c.get('topics', []):
                cov[c['week']][t].append(ex['n'])
    json.dump({w: {t: sorted(set(v)) for t, v in d.items()} for w, d in cov.items()}, open(f'{SRC}/coverage.json', 'w'), indent=1)
    letters = Counter(q['answer'] for ex in exams for q in ex['mcq'])
    print('answer letters', dict(letters))
    write_index(exams, pdir, kdir)


def write_index(exams, pdir, kdir):
    rows = []
    for ex in exams:
        weeks_a = sorted({q['week'] for q in ex['mcq']})
        weeks_b = sorted({q['week'] for q in ex['short']})
        cases = ', '.join(f"{c['name']} (W{c['week']})" for c in ex['cases'])
        rows.append(f"<tr><td>{ex['n']:02d}</td><td><a href='NMTA_Mock_Exam_{ex['n']:02d}.pdf'>paper</a> · "
                    f"<a href='html/NMTA_Mock_Exam_{ex['n']:02d}.html'>html</a></td>"
                    f"<td><a href='../mock_exam_answer_keys/NMTA_Mock_Exam_{ex['n']:02d}_Answer_Key.pdf'>key</a></td>"
                    f"<td>{cases}</td></tr>")
    body = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>NMTA Mock Exams Index</title>
<style>body{{font-family:Georgia,serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.45}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #999;padding:.4rem .6rem;text-align:left}}
th{{background:#e6efef}} h1{{color:#0b4f4f}}</style></head><body>
<h1>NMTA Mock Examinations</h1>
<p>Sixteen practice papers matching the final exam structure (Part A 30 · Part B 30 · Part C 40). Sit one under exam conditions, then mark with the matching key.</p>
<table><tr><th>#</th><th>Paper</th><th>Answer key</th><th>Cases</th></tr>
{''.join(rows)}</table>
<p><a href="README.md">How to use these papers</a></p>
</body></html>"""
    open(f'{pdir}/index.html', 'w').write(body)


if __name__ == '__main__':
    main()
