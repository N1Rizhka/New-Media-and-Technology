# Brief: write the Week <N> question bank for 16 NMTA mock exams

## Context

A university student is preparing for the final exam of "New Media Technology and Analytics" (NMTA, Tongji SEM, Fall 2026, lecturer Wei HU). The exam is on Thursday 26 November 2026, 90 minutes, on paper, 100 marks:

- Part A: 15 multiple-choice questions, 2 marks each (30 marks). Four options (a)-(d), exactly one correct.
- Part B: 5 short-answer questions, 6 marks each (30 marks). The student writes 3-5 sentences, plus any requested arithmetic.
- Part C: 2 cases, 20 marks each (40 marks). A scenario with data exhibits, then 3 sub-questions (usually 8 + 6 + 6 marks).
- Every formula needed is printed on the paper beside the question. A non-programmable calculator is allowed. No question asks to write program code; questions ask to read analytical output and connect it to a business decision.

The student asked for 16 mock exams whose questions are 100% different from each other, with answer keys, and said: "don't go much into details with the coding part, concentrate on the close to basic calculations and meaning behind concepts." The student has some machine learning background.

We are building the mocks from 8 per-week question banks, written in parallel by 8 writers. You write the bank for **Week <N>** only. An assembler script will distribute your items across the 16 mocks: about 2 MCQs per mock, one short answer in most mocks, one case in every other mock.

## Your files (read before writing)

- The exact examined lecture content for your week (text of the examined pages only): `/tmp/txt/scope_w<N>.txt`. This is the authority on scope.
- The study book chapter for your week (a complete textbook of the examined material, with "Framework to remember" boxes and worked examples): `/tmp/book/w<N>.html`. Its `<h3>` headings are the topic list you must cover.
- The full lecture text (background only; non-examined pages are NOT in scope): `/tmp/txt/Week-0<N>-Lecture-0<N>.txt`.
- The official mock exam and its answer key, to copy the STYLE, difficulty and marking-guide format (not the content): `/tmp/txt/MOCK_exam_paper.txt`, `/tmp/txt/MOCK_exam_answer_key.txt`.
- Official scope statement: `/tmp/txt/Exam-scope-briefing-V2.txt`.

## Scope rules (strict)

- Only content of the examined pages of Week <N> (see the scope file). Excluded everywhere: Week 9 and later, ALL ethical and legal topics (privacy, bias, law, governance, policy, compliance), course administration, software-operation instructions, code writing.
- New fictional scenarios only. Do NOT use the scenarios of the assignments or the group project (Lumen Beauty, Capital Bikeshare, TeaPop assignment tasks, Lumen BakeBox) and do not copy the official mock or the study book's practice questions. Invent new fictional companies/creators/apps (vary them: every case and every short answer gets its own company name; MCQs can be anonymous or named). Concepts, formulas and taught named examples (e.g. a taught case company) may be referred to as course knowledge in a stem when that is what is being tested, but the question itself must be new.
- Emphasis: basic calculations (by hand/calculator, clean numbers) and the meaning behind concepts and frameworks, and interpreting outputs for a business decision. Code: at most reading a tiny output table; never ask about syntax or library calls.
- Use the course's own terminology, definitions and frameworks exactly as the study book/lecture teaches them (e.g. the course's definition of lift, its names for the three targeting strategies, the four Kotler tests, its reading of p-values, etc.). If the course teaches a named list (e.g. "five forces", "four measurement scales", "three sentiment methods"), test it in the course's form.

## Coverage and uniqueness (the core requirement)

- Every `<h3>` topic of your chapter that is examined must be tested at least once across your bank, and the "Core framework" boxes of your chapter should each be tested at least once. Calculation topics (any formula your week teaches) should be tested several times with different numbers and different twists.
- No two items in your bank may test the same point in the same way. Different numbers on the same calculation is NOT enough to count as different: vary what is asked (compute vs interpret vs pick the wrong statement vs diagnose a mistake vs choose between options), the scenario, and the twist. Each item gets a `tests` field (one line: the precise learning point), and those must be pairwise distinct.
- MCQ answer letters: balance them (about 8 each of a, b, c, d across 32 items), and make distractors plausible, similar in length and style to the correct option (do not make the correct option the longest one).

## Quantities to produce

- `mcq`: exactly 32 items.
- `short`: exactly 11 items (6 marks each).
- `cases`: exactly 4 items (20 marks each, 3 sub-questions; marks 8+6+6 unless a different split like 7+7+6 fits better; sub-question marks must sum to 20). Each case: a scenario paragraph (or two), 1-3 data exhibits (HTML tables), and sub-questions that mix calculation and interpretation like the official mock. A case may combine two topics of your week. Every case should end with at least one sub-question demanding a business decision/recommendation and a limitation.

## Correctness (non-negotiable)

- Verify EVERY number with Python (`python3`) before writing it into the bank: every answer, every intermediate value, every option that is supposed to be wrong must actually be wrong. Use clean numbers that work on a calculator; state rounding (e.g. "to two decimal places") when needed.
- Every MCQ must have exactly one defensible correct answer under the course's teaching. Re-read each stem asking "could a strong student argue for another option?" and fix it if yes.
- Print the needed formula(s) with the question (`formula` field), as the real exam does, unless the question tests a definition.
- Answer keys: reference answer + marking guide in the official style (points that sum exactly to the marks, "1 mark for ...", what to accept, what not to accept, error carried forward rule where relevant).

## Output format

Write ONE JSON file: `/tmp/mock/bank_w<N>.json` (UTF-8, valid JSON; validate it by loading it with `python3 -c "import json;json.load(open(...))"`). Text fields may contain simple inline HTML: `<b>`, `<i>`, `<sub>`, `<sup>`, `<br>`, `&times;`, `&minus;`, `&le;`, `&ge;`, and tables written as `<table class="ex"><tr><th>..</th></tr><tr><td>..</td></tr></table>`. Lists as `<ul><li>..</li></ul>`. No CSS, no images, no scripts. Use the real minus sign `&minus;` for negatives in text.

```json
{
  "week": <N>,
  "mcq": [
    {
      "id": "w<N>-a01",
      "topic": "<exact h3 heading text from the chapter>",
      "tests": "<precise learning point>",
      "stem": "<question text, HTML allowed, may include a small table>",
      "formula": "<formula line printed with the question, or empty string>",
      "options": ["<a text>", "<b text>", "<c text>", "<d text>"],
      "answer": "a|b|c|d",
      "explanation": "<1-3 sentences: why the answer is right, and the key calculation>"
    }
  ],
  "short": [
    {
      "id": "w<N>-b01",
      "topic": "<h3 heading>",
      "tests": "<learning point>",
      "title": "<short title for the answer key, e.g. 'Lift below 1 and a bundle decision'>",
      "stem": "<question, HTML allowed, may include a table; end with the explicit tasks>",
      "formula": "<formula(s) or empty>",
      "reference": "<reference answer, 3-6 sentences with the arithmetic>",
      "marking": "<marking guide; marks sum to exactly 6>"
    }
  ],
  "cases": [
    {
      "id": "w<N>-c01",
      "topics": ["<h3 heading>", "..."],
      "tests": "<learning points>",
      "name": "<fictional company name>",
      "scenario": "<scenario HTML: one or more <p> paragraphs>",
      "exhibits": [ {"title": "Exhibit 1: ...", "html": "<table class=\"ex\">...</table>", "note": "<formula/definition printed under the exhibit, or empty>"} ],
      "questions": [
        {"marks": 8, "stem": "<sub-question>", "answer": "<model answer with full working>", "marking": "<marking guide summing to the marks>"},
        {"marks": 6, "stem": "...", "answer": "...", "marking": "..."},
        {"marks": 6, "stem": "...", "answer": "...", "marking": "..."}
      ]
    }
  ]
}
```

Do not write question numbers ("A3", "C1.2") inside the text; the assembler numbers everything. Do not reference "the slides", slide numbers or page numbers anywhere: the student never reads the slides.

## When you finish

Reply with: (1) counts per section; (2) a coverage table: each `<h3>` topic of your chapter and the item ids that test it; (3) the MCQ answer-letter distribution; (4) any topic you could not test and why; (5) confirmation that every number was checked in Python and the JSON loads.
