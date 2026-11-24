# Brief: independently check the Week <N> mock-exam question bank

A student sits the NMTA final exam (Tongji SEM, Fall 2026) on Thursday. Another writer produced `/tmp/mock/bank_w<N>.json`: 32 multiple-choice questions (`mcq`), 11 six-mark short answers (`short`) and 4 twenty-mark cases (`cases`), each with answers and a marking guide. These will be assembled into 16 mock exams. The writer's instructions are in `/tmp/mock/BRIEF.md`; read them first. The student will trust these answer keys completely, so a wrong key is the worst possible outcome.

Reference material: the examined lecture content `/tmp/txt/scope_w<N>.txt` (authority on scope and on the course's definitions), the study book chapter `/tmp/book/w<N>.html`, the official mock and key `/tmp/txt/MOCK_exam_paper.txt`, `/tmp/txt/MOCK_exam_answer_key.txt`.

## What to check, item by item (all 47 items)

1. **Arithmetic**: recompute every number in stems, options, explanations, reference answers and marking guides with `python3`. Check that the "wrong" MCQ options really are wrong.
2. **Single correct answer**: for every MCQ, try to argue for each other option under the course's teaching. If a strong student could defend another option, or the keyed answer is wrong, fix it.
3. **Course consistency**: definitions, formulas, framework names and interpretations must match how the course teaches them (scope file and study book). Flag anything taught differently.
4. **Scope**: nothing from Week 9+, nothing ethical/legal (privacy, bias, law, policy, governance), no code writing, no slide/page references.
5. **Answerability**: the stem/exhibits contain all the information the answer needs; printed formulas are correct and sufficient; case sub-questions match their exhibits; marking points sum exactly to the marks.
6. **Uniqueness**: no two items in the bank are essentially the same question (same point asked the same way). If two are, rewrite one to test a different point of the same week, or mark one for dropping.
7. **Giveaways**: the correct MCQ option should not be obviously the longest/most qualified; keep the a/b/c/d balance roughly even.

## How to fix

Edit `/tmp/mock/bank_w<N>.json` in place (keep valid JSON, keep all ids and the schema). Prefer fixing over dropping. If an item cannot be fixed well, add its id to the list in `/tmp/mock/drop_w<N>.json` (a JSON array of ids; create it if absent). Drop at most 2 MCQs, 1 short answer and 0 cases (cases must be fixed). After editing, validate with `python3 -c "import json;json.load(open('/tmp/mock/bank_w<N>.json'))"`.

## Reply with

A list of every change (id, what was wrong, what you changed), any dropped ids, and a final confirmation that all 47 items were checked and the JSON loads.
