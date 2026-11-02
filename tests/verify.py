"""Awaaz verification — hand-computed fixtures, no AI needed.

English fixture (hand-counted offsets):
  "Dr. Khan went to Larkana. He bought 3.5 kg of rice! Did he pay Rs. 500? Yes, he did."
  - "Dr. Khan went to Larkana." = 25 chars -> (0, 25); "Dr." must NOT split
  - "He bought 3.5 kg of rice!" -> (26, 51); "3.5" must NOT split
  - "Did he pay Rs. 500?" -> (52, 71); "Rs." must NOT split
  - "Yes, he did." -> (72, 84); total length 84

Flesch fixture: "The cat sat on the mat." -> 6 words, 1 sentence,
6 syllables -> 206.835 - 1.015*6 - 84.6*1 = 116.145 -> 116.1

Reading time: 360 words at 180 wpm -> 2.0 minutes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "clinic-demo"))

from app.awaaz import engine, gemini
from app.awaaz.pages import AWAAZ_HTML

passed = failed = 0


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {extra}")


EN = ("Dr. Khan went to Larkana. He bought 3.5 kg of rice! "
      "Did he pay Rs. 500? Yes, he did.")
UR = "یہ ایک جملہ ہے۔ یہ دوسرا جملہ ہے؟"
ROMAN = "yeh kitab boht achi hai, mein ne kal parhi thi aur aap ko bhi parhni chahiye"

print("== split_sentences ==")
sents = engine.split_sentences(EN)
check("en: 4 sentences", len(sents) == 4, f"got {len(sents)}")
check("en: offsets", [(s["start"], s["end"]) for s in sents] ==
      [(0, 25), (26, 51), (52, 71), (72, 84)],
      str([(s["start"], s["end"]) for s in sents]))
check("en: texts", [s["text"] for s in sents] ==
      ["Dr. Khan went to Larkana.", "He bought 3.5 kg of rice!",
       "Did he pay Rs. 500?", "Yes, he did."])
check("en: slices match text",
      all(EN[s["start"]:s["end"]] == s["text"] for s in sents))
check("abbrev U.S./e.g. no split",
      len(engine.split_sentences(
          "The U.S. Army uses e.g. tanks and guns. It works.")) == 2)
check("ur: 2 sentences", len(engine.split_sentences(UR)) == 2,
      str(engine.split_sentences(UR)))
check("ur: texts", [s["text"] for s in engine.split_sentences(UR)] ==
      ["یہ ایک جملہ ہے۔", "یہ دوسرا جملہ ہے؟"])
check("empty -> []", engine.split_sentences("   ") == [])
check("double newline splits",
      len(engine.split_sentences("First para here.\n\nSecond para here.")) == 2)

print("== language ==")
check("ur detected", engine.detect_language(UR) == "ur")
check("roman detected", engine.detect_language(ROMAN) == "roman")
check("en detected", engine.detect_language(EN) == "en")

print("== counts & stats ==")
check("word_count", engine.word_count("The cat sat on the mat.") == 6)
check("flesch hand-computed",
      engine.flesch_reading_ease("The cat sat on the mat.") == 116.1,
      str(engine.flesch_reading_ease("The cat sat on the mat.")))
check("flesch None for Urdu", engine.flesch_reading_ease(UR) is None)
a360 = engine.analyze("word " * 360)
check("360 words -> 2.0 min", a360["words"] == 360 and
      a360["minutes_180wpm"] == 2.0, str(a360))
check("analyze offsets consistent",
      all(EN[s["start"]:s["end"]] == s["text"]
          for s in engine.analyze(EN)["sentences"]))
check("analyze language", engine.analyze(UR)["language"] == "ur")

print("== headings ==")
h = engine.find_headings("Chapter One\n\nLong paragraph text here that goes on.")
check("heading found", h == [{"text": "Chapter One", "line": 1}], str(h))
check("long line not heading",
      engine.find_headings("This is a very long line with more than eight words in it here.") == [])

print("== caps ==")
check("empty -> error", engine.check_caps("  ") is not None)
check("over limit -> error", engine.check_caps("x" * 200_001) is not None)
check("normal -> ok", engine.check_caps("hello") is None)

print("== page ==")
check("page mentions speechSynthesis", "speechSynthesis" in AWAAZ_HTML)
check("page has pdf.js loader", "pdf.min.js" in AWAAZ_HTML)
check("page has honest limits", "Honest limits" in AWAAZ_HTML)
check("page has no Speechify trademark claim",
      "Speechify" not in AWAAZ_HTML.split("Honest limits")[0])

print("== routes (TestClient, no main app) ==")
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.awaaz.routes import router

tapp = FastAPI()
tapp.include_router(router)
c = TestClient(tapp, raise_server_exceptions=False)
r = c.get("/awaaz")
check("GET /awaaz 200", r.status_code == 200, str(r.status_code))
check("GET /awaaz html", "Awaaz" in r.text)
r = c.post("/awaaz/api/analyze", data={"text": EN})
check("POST analyze 200", r.status_code == 200, str(r.status_code))
check("POST analyze words", r.json().get("words") == 17,
      str(r.json().get("words")))
r = c.post("/awaaz/api/analyze", data={"text": ""})
check("POST analyze empty 400", r.status_code == 400)
r = c.get("/awaaz/api/ai-status")
check("ai-status bool", isinstance(r.json().get("ai_available"), bool))
if not gemini.key_available():
    r = c.post("/awaaz/api/summarize", data={"text": EN, "language": "en"})
    check("summarize no-key 400", r.status_code == 400, str(r.status_code))
else:
    print("  SKIP summarize 400 (local key present)")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
