# Changelog

All notable changes to the companion code are documented here. Releases are
tagged to match printed editions of the book.

## [1.0.1] — 2026-11-25
### Fixed
- Seven Python files contained stray Markdown fence lines (```` ```python ````)
  left over from extraction and did not run. All 131 Python files now parse:
  `chapter-04/generator.py`, `chapter-05/eleven_labs_voice_cloner.py`,
  `chapter-06/document_ingestor.py`, `chapter-06/local_code_assistant.py`,
  `chapter-08/building_with_n8n_5.py`, `chapter-09/review_status.py`,
  `chapter-10/cost_optimized_pipeline.py`.
- `chapter-04/generator.py` and `chapter-06/local_code_assistant.py` were cut
  short at a prompt string containing a code fence; they are now complete.
  The fragments `chapter-06/step_3_build_a_custom_integration*.py` are merged
  back into `local_code_assistant.py`.
- Removed duplicated/truncated lines in `chapter-03` n8n workflow JSON files and
  `chapter-07/ask_a_question.sh`.

## [1.0.0] — 2026 First Edition
- Initial release: code samples for Chapters 1–10.
- Model references current as of mid-2026 (Claude Opus 4.8, GPT-5.5, Gemini 3.5,
  Grok 4.3, DeepSeek V4 Pro, Qwen 3.6, Llama 4, GLM-5.1).
