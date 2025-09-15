import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "language" not in st.session_state:
    st.session_state.language = ""
if "level" not in st.session_state:
    st.session_state.level = ""
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "score" not in st.session_state:
    st.session_state.score = 0

# Gemini question generation
def generate_questions(language, level):
    prompt = f"""
    Generate 15 multiple choice questions to evaluate a user's skill in {language} at {level} level.
    Each question should have:
    - A question statement
    - Four options labeled A, B, C, D
    - Indicate the correct option at the end like: Correct Answer: B
    Format:
    Q1. What is...?
    A. Option 1
    B. Option 2
    C. Option 3
    D. Option 4
    Correct Answer: B
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return parse_questions(response.text)

# Parse Gemini response
def parse_questions(text):
    questions = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 6:
            question_text = lines[0]
            options = [line[3:].strip() for line in lines[1:5]]
            correct_line = lines[5]
            correct_option = correct_line.split(":")[-1].strip()
            questions.append({
                "question": question_text,
                "options": options,
                "correct": correct_option
            })
    return questions

# UI
st.set_page_config(page_title="Learnoviax Onboarding", page_icon="🚀", layout="centered")
st.title("🚀 Learnoviax Onboarding")
st.markdown("### Let's personalize your programming journey!")

# Step 1: Choose language
if st.session_state.step == 1:
    st.subheader("Step 1: Choose a Programming Language")
    st.session_state.language = st.selectbox("Select a language", ["Python", "JavaScript", "Java", "C++", "Go", "Ruby", "Swift"])
    if st.button("Next"):
        st.session_state.step = 2
        st.rerun()

# Step 2: Choose level
elif st.session_state.step == 2:
    st.subheader("Step 2: Choose Your Skill Level")
    st.session_state.level = st.selectbox("Select your level", ["Beginner", "Intermediate", "Advanced"])
    if st.button("Generate Evaluation Questions"):
        with st.spinner("Generating questions..."):
            st.session_state.questions = generate_questions(st.session_state.language, st.session_state.level)
        st.session_state.step = 3
        st.rerun()

# Step 3: Ask questions
elif st.session_state.step == 3:
    q_index = st.session_state.current_question
    total = len(st.session_state.questions)

    if q_index < total:
        q = st.session_state.questions[q_index]
        st.subheader(f"🧠 Question {q_index + 1} of {total}")
        st.markdown(f"**{q['question']}**")
        selected = st.radio("Choose your answer:", q["options"], key=f"q{q_index}")

        if st.button("Next Question"):
            st.session_state.answers.append(selected)
            # Evaluate answer
            correct_option = q["correct"]
            correct_text = q["options"][ord(correct_option) - ord("A")]
            if selected == correct_text:
                st.session_state.score += 1
            st.session_state.current_question += 1
            st.rerun()
    else:
        st.session_state.step = 4
        st.rerun()

# Step 4: Show results
elif st.session_state.step == 4:
    st.success("🎉 Evaluation complete!")
    st.markdown(f"### ✅ You scored **{st.session_state.score} / 15**")

    if st.session_state.score >= 12:
        st.balloons()

    st.markdown("### Your Answers:")
    for i, ans in enumerate(st.session_state.answers):
        correct = st.session_state.questions[i]["correct"]
        correct_text = st.session_state.questions[i]["options"][ord(correct) - ord("A")]
        result = "✅ Correct" if ans == correct_text else "❌ Incorrect"
        st.write(f"**Q{i+1}:** {ans} — {result}")





# ------------------------------------------------------
# # app.py
# import os
# import re
# import json
# import ast
# import streamlit as st
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     raise RuntimeError("Please add GEMINI_API_KEY to your .env file.")

# genai.configure(api_key=API_KEY)

# st.set_page_config(
#     page_title="Learnoviax — Onboarding",
#     page_icon="📘",
#     layout="centered",
# )

# # --- small CSS for nicer look ---
# st.markdown(
#     """
#     <style>
#     .stApp { background: linear-gradient(135deg, #f8fbff 0%, #eef7ff 100%); }
#     .card {
#         background: white;
#         border-radius: 12px;
#         padding: 18px;
#         box-shadow: 0 6px 18px rgba(0,0,0,0.06);
#     }
#     .big-title { font-size:24px; font-weight:700; }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# st.markdown('<div class="card">', unsafe_allow_html=True)
# st.markdown('<div class="big-title">📘 Learnoviax — Onboarding & Skill Evaluation</div>', unsafe_allow_html=True)
# st.markdown("Choose language & level — then answer the generated multiple-choice questions one-by-one.")
# st.markdown("</div>", unsafe_allow_html=True)

# # Helper functions ----------------------------------------------------------
# def ask_gemini_for_questions(language: str, level: str, num_questions: int = 15) -> str:
#     """
#     Call Gemini and return the raw text response (no parsing here).
#     """
#     prompt = f"""
# You are an assistant that MUST output only valid JSON (no commentary, no extra text).
# Generate {num_questions} multiple-choice questions to evaluate a learner of {language} at {level} level.
# Return a JSON array of objects exactly like:
# [
#   {{
#     "question": "Question text here?",
#     "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
#     "answer": "B"
#   }},
#   ...
# ]
# Make sure:
# - Each object has keys: question, options (array of 4 strings), answer (single letter A/B/C/D).
# - Options should start with 'A)', 'B)', 'C)', 'D)' (that helps parsing).
# Do NOT put any extra commentary or analysis outside the JSON.
# """
#     # Use try/except to be resilient to different genai client shapes
#     try:
#         # Preferred new-style usage
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         resp = model.generate_content(prompt)
#         # Many wrappers expose text; fallback to str(resp)
#         raw = getattr(resp, "text", None) or getattr(resp, "content", None) or str(resp)
#     except Exception:
#         # fallback to older genai.generate() shape
#         resp = genai.generate(model="gemini-1.5", input=prompt)
#         # try to extract the candidate content
#         raw = None
#         if hasattr(resp, "candidates") and resp.candidates:
#             cand = resp.candidates[0]
#             raw = getattr(cand, "content", None) or getattr(cand, "output", None) or str(cand)
#         if raw is None:
#             raw = str(resp)
#     return raw


# def extract_json_array_from_text(text: str):
#     """
#     Try multiple strategies to extract a JSON array (list) from arbitrary text.
#     Returns Python object (list) or None.
#     """
#     # 1) direct json.loads if text is pure JSON
#     try:
#         return json.loads(text)
#     except Exception:
#         pass

#     # 2) find the first bracketed JSON array [...] and try json.loads / ast.literal_eval
#     m = re.search(r'(\[.*\])', text, flags=re.DOTALL)
#     if m:
#         candidate = m.group(1)
#         # try strict JSON
#         try:
#             return json.loads(candidate)
#         except Exception:
#             # try ast.literal_eval (handles single quotes)
#             try:
#                 return ast.literal_eval(candidate)
#             except Exception:
#                 # try minor fixes: convert lone single quotes to double quotes (best-effort)
#                 candidate2 = candidate.replace("'", '"')
#                 candidate2 = re.sub(r',\s*([}\]])', r'\1', candidate2)  # remove trailing commas
#                 try:
#                     return json.loads(candidate2)
#                 except Exception:
#                     pass

#     # 3) fallback: parse a question-like plaintext (very permissive)
#     items = []
#     cur = None
#     lines = text.splitlines()
#     for line in lines:
#         s = line.strip()
#         if not s:
#             continue
#         # question start detection
#         if re.match(r'^\d+\.', s) or s.lower().startswith('question') or re.match(r'^q\d*[:.\s]', s, re.I):
#             if cur:
#                 items.append(cur)
#             qtext = re.sub(r'^\d+\.\s*', '', s)  # remove leading "1."
#             qtext = re.sub(r'^[Qq]uest?ion[:\s]*', '', qtext)
#             cur = {"question": qtext, "options": [], "answer": None}
#             continue
#         # options like "A) text" or "A. text" or "A: text"
#         if re.match(r'^[A-D][\)\.\:]\s+', s, re.I):
#             if cur is None:
#                 cur = {"question": "", "options": [], "answer": None}
#             cur["options"].append(s)
#             continue
#         # lines starting with "Answer" or "Correct"
#         if s.lower().startswith("answer") or s.lower().startswith("correct"):
#             m2 = re.search(r'([A-D])', s, re.I)
#             if m2 and cur:
#                 cur["answer"] = m2.group(1).upper()
#             continue
#         # otherwise append to current question body if no options yet
#         if cur and not cur["options"]:
#             cur["question"] = (cur.get("question","") + " " + s).strip()
#         elif cur and cur["options"] and not re.match(r'^[A-D]', s, re.I):
#             # could be continuation of option text
#             if cur["options"]:
#                 cur["options"][-1] += " " + s
#     if cur:
#         items.append(cur)
#     return items or None


# def normalize_questions(raw_list):
#     """
#     Normalize parsed question dicts to:
#     { "question": str, "options": ["A) ...","B) ...","C) ...","D) ..."], "answer": "A" }
#     Returns cleaned list (only items with 4 options).
#     """
#     cleaned = []
#     for entry in raw_list:
#         if not isinstance(entry, dict):
#             continue
#         q = entry.get("question") or entry.get("prompt") or str(entry)
#         opts = entry.get("options") or []
#         ans = entry.get("answer") or entry.get("correct") or entry.get("answer_letter") or None

#         # If options is a single string with lines, split
#         if isinstance(opts, str):
#             opts_lines = [o.strip() for o in re.split(r'\n|(?=\n[A-D][\)\.\:])', opts) if o.strip()]
#             opts = opts_lines

#         # Try to split options if they are embedded in a single string without newlines
#         if isinstance(opts, list) and len(opts) == 1:
#             # try splitting by "A) " pattern
#             parts = re.split(r'(?=[A-D][\)\.\:]\s)', opts[0])
#             parts = [p.strip() for p in parts if p.strip()]
#             if len(parts) == 4:
#                 opts = parts

#         # Ensure exactly 4 options
#         if not isinstance(opts, list) or len(opts) != 4:
#             # give up on this entry
#             continue

#         # normalize options to start with "A) " etc.
#         normalized_opts = []
#         for i, opt in enumerate(opts):
#             s = opt.strip()
#             if not re.match(r'^[A-D][\)\.\:]\s*', s, re.I):
#                 # prepend letter
#                 s = f"{chr(65+i)}) {s}"
#             # convert "A. text" or "A)text" to "A) text"
#             s = re.sub(r'^([A-D])[\.\)]\s*', lambda m: m.group(1) + ') ', s, flags=re.I)
#             normalized_opts.append(s)
#         # normalize answer -> single letter
#         letter = None
#         if isinstance(ans, str):
#             a = ans.strip()
#             # if ans is "B" or "b" or "B)" etc.
#             m = re.search(r'([A-D])', a, re.I)
#             if m:
#                 letter = m.group(1).upper()
#             else:
#                 # try to match full text to option
#                 for idx, opt in enumerate(normalized_opts):
#                     if a.lower() in opt.lower():
#                         letter = chr(65 + idx)
#                         break
#         # If no answer provided, try to detect "(correct)" or '*' in options
#         if not letter:
#             for idx, opt in enumerate(normalized_opts):
#                 if '(correct)' in opt.lower() or '[correct]' in opt.lower() or '*' in opt:
#                     letter = chr(65 + idx)
#                     break
#         # If still no letter, set to None (we'll accept None but keep question)
#         cleaned.append({
#             "question": q.strip(),
#             "options": normalized_opts,
#             "answer": letter  # may be None if unknown
#         })
#     return cleaned

# # ----------------------------------------------------------------------------

# # UI inputs
# languages = ["Python", "C++", "Java", "JavaScript", "C#", "Go", "Rust", "Kotlin", "Swift"]
# language = st.selectbox("🔹 Choose a language", languages)
# level = st.radio("🔹 Your self-assessed level", ["Beginner", "Intermediate", "Advanced"], index=0)

# # Buttons and flow state
# if "questions" not in st.session_state:
#     st.session_state.questions = None
# if "raw_response" not in st.session_state:
#     st.session_state.raw_response = None
# if "current_q" not in st.session_state:
#     st.session_state.current_q = 0
# if "score" not in st.session_state:
#     st.session_state.score = 0
# if "answers" not in st.session_state:
#     st.session_state.answers = []

# col1, col2 = st.columns([3,1])
# with col1:
#     if st.button("🚀 Start Evaluation"):
#         with st.spinner("Requesting Gemini and parsing questions..."):
#             st.session_state.raw_response = ask_gemini_for_questions(language, level, num_questions=15)
#             parsed = extract_json_array_from_text(st.session_state.raw_response)
#             if not parsed:
#                 st.error("Could not parse questions from the model output. Open the raw response to debug.")
#                 st.session_state.questions = None
#             else:
#                 normalized = normalize_questions(parsed)
#                 if not normalized:
#                     st.error("Parsed output didn't contain 4-option MCQs. Open raw output to inspect.")
#                     st.session_state.questions = None
#                 else:
#                     st.success(f"Generated {len(normalized)} questions.")
#                     st.session_state.questions = normalized
#                     st.session_state.current_q = 0
#                     st.session_state.score = 0
#                     st.session_state.answers = [None] * len(normalized)

# with col2:
#     st.markdown("### Info")
#     st.caption("Questions are generated by Gemini. Use the raw response expander below if something looks off.")

# # show raw response for debugging
# if st.session_state.raw_response:
#     with st.expander("🔎 Raw model output (inspect for parsing issues)"):
#         st.code(st.session_state.raw_response, language="json")

# # If questions exist, show them one by one
# if st.session_state.questions:
#     total = len(st.session_state.questions)
#     i = st.session_state.current_q
#     qobj = st.session_state.questions[i]

#     st.markdown(f"### Question {i+1} / {total}")
#     st.write(qobj["question"])

#     # show radio with cleaned option labels
#     choice = st.radio("Select an option", qobj["options"], key=f"choice_{i}")

#     # progress bar
#     st.progress((i) / total)

#     coln1, coln2, coln3 = st.columns(3)
#     with coln1:
#         if st.button("⬅️ Prev") and i > 0:
#             st.session_state.current_q -= 1
#     with coln2:
#         if st.button("Next ➡️"):
#             # when moving forward, record chosen answer and update score
#             # find letter of chosen option (starts with "A)" etc)
#             chosen_letter = None
#             m = re.match(r'^([A-D])', choice.strip(), re.I)
#             if m:
#                 chosen_letter = m.group(1).upper()
#             else:
#                 # fallback: find index of choice among options
#                 try:
#                     idx = qobj["options"].index(choice)
#                     chosen_letter = chr(65 + idx)
#                 except Exception:
#                     chosen_letter = None

#             # record
#             st.session_state.answers[i] = chosen_letter

#             correct = qobj.get("answer")
#             if correct and chosen_letter == correct:
#                 st.session_state.score += 1

#             # move forward or finish
#             if st.session_state.current_q < total - 1:
#                 st.session_state.current_q += 1
#             else:
#                 # finished
#                 st.success("✅ Evaluation Complete!")
#                 st.session_state.current_q = total - 1  # stay on last
#     with coln3:
#         if st.button("Finish Now"):
#             st.success("Evaluation finished early.")

#     # If last question and finished, show results
#     if all(a is not None for a in st.session_state.answers):
#         st.markdown("---")
#         st.markdown(f"### Your Score: **{st.session_state.score} / {total}**")
#         st.balloons()
#         # show summary
#         if st.checkbox("Show summary of answers"):
#             for idx, q in enumerate(st.session_state.questions):
#                 ans = st.session_state.answers[idx] or "-"
#                 st.write(f"{idx+1}. {q['question']}")
#                 st.write("   Options:")
#                 for op in q["options"]:
#                     st.write("   - " + op)
#                 st.write(f"   Correct: {q.get('answer') or 'Unknown'}  |  Your answer: {ans}")
#                 st.write("---")

# # Offer regeneration if parse failed
# if st.session_state.questions is None and st.session_state.raw_response:
#     if st.button("Retry Generation (ask Gemini again)"):
#         st.session_state.raw_response = ask_gemini_for_questions(language, level, num_questions=15)
#         parsed = extract_json_array_from_text(st.session_state.raw_response)
#         if parsed:
#             normalized = normalize_questions(parsed)
#             if normalized:
#                 st.session_state.questions = normalized
#                 st.session_state.current_q = 0
#                 st.session_state.score = 0
#                 st.session_state.answers = [None]*len(normalized)
#                 st.success("Successfully parsed questions after retry.")
#             else:
#                 st.error("Retry still returned non-MCQ format. Inspect raw output.")
#         else:
#             st.error("Retry failed to return JSON-like structure. Inspect raw output.")
