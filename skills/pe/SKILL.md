---
name: pe
description: Explicitly estimate rough input tokens or suggest a shorter prompt with Prompt Efficiently, only when the user requests PE. Requires PE sign-in in a separate terminal.
---

Use only for the prompt text the user explicitly supplies or selects for PE. Do not inspect or upload repository files, chat history or secrets. This is an explicit helper, not an automatic monitor of AI usage.

The package README explains helper installation. Ask the user to complete PE login in their own terminal if needed. Never ask them for a code, token or password and never read the OS keyring yourself. Do not install dependencies or run login without approval.

Run the bundled pe.py with command `estimate` or `tighten` via the user-configured Python environment. Pass prompt text through the process stdin as data, never interpolate it into shell code, command arguments or a heredoc. If secure stdin transport is unavailable, stop and ask the user to run the helper themselves. Do not write prompt text to temporary files. Do not create alternate quota or auth paths.

Report only successful helper results. On authentication, quota, keyring, network or API failure, stop. Do not manufacture an estimate or grant offline access. Prompt text is processed locally; only the usage request ID goes to PE.

The result is a rough input-only word-based approximation, not a model tokenizer, provider price, account balance or full agent-run estimate. It excludes repository context, tools and output. A tightening suggestion removes a leading polite phrase; show it for review. Never send it to the AI, overwrite files or apply it automatically. Open the PE website for upgrades, not a payment flow in the assistant.

Platform cost estimate: pass `--platform <id>` (optionally `--size small|medium|big`) with `estimate` to add a rough per-call or per-credit cost for one of 24 AI tools, computed locally from public list prices dated 25 Nov 2026. It is not a quote or a balance reading. Ids: chatgpt, claude, gemini, grok, town, manus, lovable, bolt, replit, openai_api, anthropic_api, gemini_api, deepseek, xai_api, mistral, groq, together, fireworks, openrouter, qwen, zhipu, moonshot, cohere, ollama.
