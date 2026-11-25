# Prompt Efficiently for Gemini CLI

Explicit rough input-token estimates and conservative prompt tightening through the PE skill. Not automatic coding-agent metering. The helper uses the same PE account, free quota and Pro entitlement as the website. Prompt text stays local.

## Install
Run `gemini extensions install https://github.com/promptefficiently/pe-gemini-cli` in your own terminal, then restart Gemini CLI. Or unzip the download from promptefficiently.com and run `gemini extensions install /absolute/path/to/this-folder`.

## Sign in and use
Create a Python 3.10+ virtual environment, install requirements.txt with pip, then run `python pe.py login` in your own terminal. Configure the absolute virtual-environment Python path in your Gemini session, then explicitly ask the PE skill to estimate or tighten supplied prompt text. A functioning secure OS keyring is required. There is no plaintext fallback. Never give the AI your email code or session token.

The helper can also be used directly with `estimate` or `tighten`, passing prompt data on stdin, not shell arguments. Use `status`, `upgrade` and `logout` for account management. Review a suggestion before using it. PE does not change files or send a revised prompt automatically.

## Limits
Word-based input approximation, not a model tokenizer, full agent-run cost, provider credit price or provider remaining balance. Context, output and tool calls excluded. A new successful check consumes one free use unless the server confirms Pro. Failures never grant offline access. Python/keyring dependencies are free software; ordinary host account usage may have its own costs.


Licence: MIT (see LICENSE). Sign-in, rewrites and billing run on Prompt Efficiently servers and are not part of this repository. Not affiliated with the AI products it supports.
