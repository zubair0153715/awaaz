# Awaaz — آواز

**Free read-aloud reader. No account, no card, no word limit, no meter.**

Paste any text, upload a `.txt` or a PDF, and hear it read aloud with
word-by-word highlighting — in Urdu, Roman-Urdu or English. The voice
comes from your own device/browser (Web Speech API), so reading costs
nothing and can never be quota-exhausted.

## Why it exists

Speechify, the reference text-to-speech reader, charges **$139/year
($29/month)** for the voices and speed that make it worth using. The
free plan gives 10 robotic-sounding voices and caps speed at ~1.5x;
Premium HD voices sit behind a monthly word limit and silently drop
back to a robotic voice mid-book; the 3-day trial needs a card and
auto-charges $139; refunds close 7 days after sign-up; and there is no
Urdu-first experience for a Pakistani reader. Awaaz is the free,
open, original alternative — built clean-room from public pricing
pages and review complaints only. See the full gap analysis in the
operator's workspace (`market-gaps/daily/2026-11-02-awaaz.md`).

Live: https://clinic-demo.fastapicloud.dev/awaaz

## What it does

- **Read aloud, free and unlimited** — paste text, upload `.txt`, or
  upload a PDF (text extracted in the browser via pdf.js). Speed
  0.5–3x free, pitch control, any voice installed on your device.
- **Word-by-word highlighting** — the spoken word lights up as it is
  read (Chromium boundary events), with a sentence-level fallback;
  click any sentence to start from there; previous/next sentence jump.
- **Urdu-first** — Urdu script, Roman-Urdu and English auto-detected
  per document; the voice picker auto-offers the matching device voice.
- **Smart reading stats, deterministic** — word/sentence counts,
  estimated minutes at the chosen speed, Flesch Reading Ease for
  English, auto-detected headings.
- **Listen-later library** — save documents in your browser
  (localStorage) and resume where you stopped. Nothing is stored on
  the server.
- **Sleep timer** — stop after 5/10/15/30 minutes.
- **Optional AI summary** — one Gemini call summarises the loaded
  text, only when the server key is available. When the key is
  quota-exhausted the button says so honestly and the reader keeps
  working at 100%.

## Honest limits

- Voice quality depends on the voices installed on the user's own
  device/browser; Urdu voices may not exist on every phone.
- Word highlighting works best in Chrome.
- No audio file download in v1 (browser speech cannot export audio).
- Scanned-image PDFs need OCR — not in v1; use a PDF with a text layer.
- AI summary needs server Gemini quota; the reader never does.

## Verify

```bash
python tests/verify.py   # 34 checks, hand-computed fixtures, no AI needed
```

Sentence splitting is verified against hand-counted char offsets
(abbreviations like `Dr.`, `Rs.`, `U.S.`, `e.g.` and decimals like
`3.5` never split); Flesch is verified against a hand-computed score
(`"The cat sat on the mat."` → 116.1); reading time against 360 words
at 180 wpm → 2.0 minutes.
