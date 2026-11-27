"""Prompt Efficiently local platform estimator. Same maths as the browser extension and the Dify plugin.
Rough guides only, not quotes or balance readings. Rates dated 25 Nov 2026 with sources in each platform entry."""
import math
import re

"""Prompt Efficiently platform data, ported verbatim from the live PE extension estimator (promptefficiently.com, extension 0.3.1)."""
PLATFORMS = [{'freeLabel': 'Free: limited messages per window',
  'id': 'chatgpt',
  'kind': 'caps',
  'logo': 'assets/logos/chatgpt.png',
  'name': 'ChatGPT',
  'paidLabel': 'Go / Plus / Pro tiers',
  'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True},
            {'id': 'go', 'label': 'Go $8/mo', 'unpublished': True},
            {'id': 'plus', 'label': 'Plus $20/mo', 'unpublished': True},
            {'id': 'pro', 'label': 'Pro 200 $200/mo', 'unpublished': True},
            {'id': 'pro100', 'label': 'Pro 100 $100/mo', 'unpublished': True},
            {'id': 'pro500', 'label': 'Pro 500 $500/mo', 'unpublished': True}],
  'unit': 'messages',
  'unverified': 'Caps are not published by OpenAI. Free gives unlimited GPT-6 text chats with guardrails and '
                'Go/Plus/Pro tiers exist (openai.com, 22 Nov), but per-message figures come from a third-party '
                'tracker. Treat as rough.'},
 {'freeLabel': 'Free: limited every 5 hours and weekly',
  'id': 'claude',
  'kind': 'caps',
  'logo': 'assets/logos/claude.png',
  'name': 'Claude',
  'paidLabel': 'Pro $20/mo · Max $100/mo · Ultra $200/mo',
  'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True},
            {'id': 'pro', 'label': 'Pro $20/mo', 'unpublished': True},
            {'id': 'max', 'label': 'Max $100/mo', 'unpublished': True},
            {'id': 'ultra', 'label': 'Ultra $200/mo', 'unpublished': True}],
  'unit': 'messages',
  'unverified': 'Window structure confirmed on claude.com (22 Nov), but exact caps are not published. Treat as rough.'},
 {'freeLabel': 'Free tier with limits',
  'id': 'gemini',
  'kind': 'caps',
  'logo': 'assets/logos/gemini.png',
  'name': 'Gemini',
  'paidLabel': 'Google AI plans multiply limits 2x-4x',
  'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True},
            {'id': 'aipro', 'label': 'Google AI Pro', 'unpublished': True},
            {'id': 'aiultra', 'label': 'Google AI Ultra', 'unpublished': True}],
  'unit': 'messages',
  'unverified': 'Paid plans raise limits 2x-4x (Google One, 22 Nov); exact free limits are not published. Treat as '
                'rough.'},
 {'confidence': 'Official (xAI FAQ, Nov 2026): paid plans share one weekly usage pool; the free tier has no published '
                'message count and resets on its own schedule. Reported, not official: pool sizes scale about '
                '1x/4x/15x/50x by tier.',
  'freeLabel': 'Free: limited chats, resets on its own schedule',
  'id': 'grok',
  'kind': 'caps',
  'logo': 'assets/logos/grok.png',
  'name': 'Grok',
  'paidLabel': 'X Subscription $8-200/mo, shared weekly pool',
  'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True},
            {'id': 'plus', 'label': 'Plus $8/mo', 'unpublished': True},
            {'id': 'premium', 'label': 'Premium $30/mo', 'unpublished': True},
            {'id': 'super', 'label': 'Super $100/mo', 'unpublished': True},
            {'id': 'ultra', 'label': 'Ultra $200/mo', 'unpublished': True}],
  'unit': 'messages'},
 {'badge': 'Msgs + credits',
  'confidence': 'Free plan verified on town.com (22 Nov): 30 chat messages a month. Paid plans include monthly credits '
                '(1,250+). Per-task rates are not published, so treat as rough.',
  'creditPerTask': {'big': [30, 70], 'medium': [12, 30], 'small': [5, 12]},
  'freeAllowance': 30,
  'freeLabel': 'Free: 30 messages a month',
  'freePeriod': 'month',
  'freeUnit': 'messages',
  'id': 'town',
  'kind': 'credits',
  'logo': 'assets/logos/town.png',
  'name': 'Town AI',
  'paidLabel': 'Starter $15/mo · Pro $49/mo billed annually',
  'perTask': {'big': [4, 8], 'medium': [2, 4], 'small': [1, 2]},
  'plans': [{'allowance': 30, 'id': 'free', 'label': 'Free', 'period': 'month', 'unit': 'messages'},
            {'allowance': 1250, 'id': 'starter', 'label': 'Starter $15/mo', 'period': 'month', 'unit': 'credits'},
            {'allowance': 5000,
             'id': 'pro',
             'label': 'Pro $49/mo billed annually',
             'period': 'month',
             'unit': 'credits'},
            {'allowance': 12000,
             'id': 'power',
             'label': 'Power $99/mo billed annually',
             'period': 'month',
             'unit': 'credits'},
            {'allowance': 40000,
             'id': 'powerplus',
             'label': 'Power Plus $199/mo billed annually',
             'period': 'month',
             'unit': 'credits'}],
  'unit': 'messages'},
 {'confidence': 'Free daily-refresh credits are limited to 1,500 credits of consumption per month and can only be used '
                'with Manus 2.0 lite. Actual credits depend on model tokens, virtual-machine work and external tools. '
                'Our task ranges are rough estimates, not Manus prices or a reading of your remaining balance.',
  'freeAllowance': 300,
  'freeLabel': 'Free: 300 credits a day',
  'freePeriod': 'day',
  'freeUnit': 'credits',
  'id': 'manus',
  'kind': 'credits',
  'logo': 'assets/logos/manus.png',
  'name': 'Manus',
  'paidAllowance': 4000,
  'paidLabel': 'Pro from $20/mo',
  'paidPeriod': 'month',
  'paidUnit': 'credits',
  'perTask': {'big': [80, 200], 'medium': [30, 80], 'small': [10, 30]},
  'perType': {'app': [80, 200], 'edit': [10, 30], 'feature': [30, 80], 'general': [10, 80], 'question': [10, 30]},
  'plans': [{'allowance': 300, 'id': 'free', 'label': 'Free', 'period': 'day', 'unit': 'credits'},
            {'allowance': 4000,
             'id': 'pro',
             'label': 'Pro $20/mo',
             'period': 'month',
             'unit': 'credits',
             'unpublished': True},
            {'allowance': 8000,
             'id': 'pro40',
             'label': 'Pro $40/mo',
             'period': 'month',
             'unit': 'credits',
             'unpublished': True}],
  'unit': 'credits'},
 {'confidence': 'Based on Lovable’s published per-prompt costs: a small tweak is about 0.5 credits, a feature 0.9–1.7, '
                'a landing page 1.7 (lovable.dev, 22 Nov).',
  'freeAllowance': 5,
  'freeLabel': 'Free: 5 credits a day (max 30 a month)',
  'freePeriod': 'day',
  'freeUnit': 'credits',
  'id': 'lovable',
  'kind': 'credits',
  'logo': 'assets/logos/lovable.png',
  'name': 'Lovable',
  'paidAllowance': 100,
  'paidLabel': 'Pro $25/mo, 100 credits',
  'paidPeriod': 'month',
  'paidUnit': 'credits',
  'perTask': {'big': [2.5, 5], 'medium': [1, 2.5], 'small': [0.5, 1]},
  'perType': {'app': [1.7, 4], 'edit': [0.5, 0.9], 'feature': [0.9, 1.7], 'general': [0.5, 1.7], 'question': [0.5, 1]},
  'plans': [{'allowText': '5 credits a day, max 30 a month',
             'allowance': 5,
             'id': 'free',
             'label': 'Free',
             'period': 'day',
             'unit': 'credits'},
            {'allowance': 100, 'id': 'pro', 'label': 'Pro $25/mo', 'period': 'month', 'unit': 'credits'}],
  'unit': 'credits'},
 {'confidence': 'Bolt publishes its allowances (300K tokens a day free) but not per-task costs, so treat as rough.',
  'freeAllowance': 300000,
  'freeLabel': 'Free: ~300K tokens a day, 1M a month',
  'freePeriod': 'day',
  'freeUnit': 'tokens',
  'id': 'bolt',
  'kind': 'credits',
  'logo': 'assets/logos/bolt.png',
  'name': 'Bolt',
  'paidAllowance': 10000000,
  'paidLabel': 'Pro $25/mo from 10M tokens',
  'paidPeriod': 'month',
  'paidUnit': 'tokens',
  'perTask': {'big': [400000, 1000000], 'medium': [150000, 400000], 'small': [50000, 150000]},
  'perType': {'app': [400000, 1000000],
              'edit': [50000, 150000],
              'feature': [150000, 400000],
              'general': [50000, 300000],
              'question': [20000, 60000]},
  'plans': [{'allowText': '300K tokens a day, 1M a month',
             'allowance': 300000,
             'id': 'free',
             'label': 'Free',
             'period': 'day',
             'unit': 'tokens'},
            {'allowance': 10000000, 'id': 'pro', 'label': 'Pro $25/mo', 'period': 'month', 'unit': 'tokens'}],
  'unit': 'tokens'},
 {'badge': 'Credits ($)',
  'confidence': 'Replit charges in credits worth $1 each, priced by the effort the Agent spends (replit.com, 22 Nov). '
                'No per-task rates are published, so treat as rough.',
  'freeLabel': 'Trial usage credit',
  'id': 'replit',
  'kind': 'credits',
  'logo': 'assets/logos/replit.png',
  'name': 'Replit',
  'paidAllowance': 20,
  'paidLabel': 'Core $20/mo, $20 usage credit',
  'paidPeriod': 'month',
  'paidUnit': 'dollars',
  'perTask': {'big': [2, 8], 'medium': [0.5, 2], 'small': [0.1, 0.5]},
  'perType': {'app': [2, 8], 'edit': [0.1, 0.5], 'feature': [0.5, 2], 'general': [0.1, 2], 'question': [0.05, 0.25]},
  'plans': [{'id': 'free', 'label': 'Free'},
            {'allowance': 20, 'id': 'core', 'label': 'Core $20/mo', 'period': 'month', 'unit': 'dollars'},
            {'allowance': 100, 'id': 'pro', 'label': 'Pro $100/mo', 'period': 'month', 'unit': 'dollars'}],
  'unit': 'dollars'}]

# API model providers, billed per token. Rates are USD per 1M tokens (input, output), each tied to a
# named flagship model with its public source, checked 25 Nov 2026. Rough guide only.
API_PLATFORMS = [
 {'confidence': 'GPT-6 Sol rates (developers.openai.com pricing, 25 Nov). GPT-6 Luna is cheaper at $0.10/$0.50.',
  'id': 'openai_api',
  'inRate': 2.0,
  'kind': 'tokens',
  'modelNote': 'priced as GPT-6 Sol',
  'name': 'OpenAI API',
  'outRate': 10.0,
  'unit': 'dollars'},
 {'confidence': 'Claude Sonnet 5.5 rates (platform.claude.com pricing, 25 Nov). Haiku 5.5 is cheaper at $0.10/$0.50.',
  'id': 'anthropic_api',
  'inRate': 2.0,
  'kind': 'tokens',
  'modelNote': 'priced as Claude Sonnet 5.5',
  'name': 'Anthropic API',
  'outRate': 10.0,
  'unit': 'dollars'},
 {'confidence': 'Gemini 3.1 Flash rates (ai.google.dev/gemini-api pricing, 25 Nov). Pro is $2/$10 until 30 Nov.',
  'id': 'gemini_api',
  'inRate': 1.5,
  'kind': 'tokens',
  'modelNote': 'priced as Gemini 3.1 Flash',
  'name': 'Gemini API',
  'outRate': 7.5,
  'unit': 'dollars'},
 {'confidence': 'deepseek-flash peak rates, cache miss (api-docs.deepseek.com, 25 Nov). Off-peak is half.',
  'id': 'deepseek',
  'inRate': 0.3,
  'kind': 'tokens',
  'modelNote': 'priced as deepseek-flash, peak',
  'name': 'DeepSeek API',
  'outRate': 1.2,
  'unit': 'dollars'},
 {'confidence': 'grok-4.7 short-context rates (docs.x.ai pricing, 25 Nov). Long context over 200k is double.',
  'id': 'xai_api',
  'inRate': 2.0,
  'kind': 'tokens',
  'modelNote': 'priced as grok-4.7',
  'name': 'xAI API',
  'outRate': 6.0,
  'unit': 'dollars'},
 {'confidence': 'Mistral Large 4 rates (docs.mistral.ai pricing, 25 Nov). Small 4 is $0.15/$0.60.',
  'id': 'mistral',
  'inRate': 0.7,
  'kind': 'tokens',
  'modelNote': 'priced as Mistral Large 4',
  'name': 'Mistral API',
  'outRate': 2.1,
  'unit': 'dollars'},
 {'confidence': 'gpt-oss-120b rates (console.groq.com/docs/models, 25 Nov). gpt-oss-20b is $0.075/$0.30.',
  'id': 'groq',
  'inRate': 0.15,
  'kind': 'tokens',
  'modelNote': 'priced as gpt-oss-120b',
  'name': 'Groq',
  'outRate': 0.6,
  'unit': 'dollars'},
 {'confidence': 'Qwen3.8 Flash rates (together.ai/pricing, 25 Nov). Other hosts and models vary.',
  'id': 'together',
  'inRate': 0.15,
  'kind': 'tokens',
  'modelNote': 'priced as Qwen3.8 Flash',
  'name': 'Together AI',
  'outRate': 0.47,
  'unit': 'dollars'},
 {'confidence': 'GLM 5.3 Flash rates (fireworks.ai/pricing, 25 Nov). Other hosts and models vary.',
  'id': 'fireworks',
  'inRate': 0.15,
  'kind': 'tokens',
  'modelNote': 'priced as GLM 5.3 Flash',
  'name': 'Fireworks AI',
  'outRate': 0.5,
  'unit': 'dollars'},
 {'confidence': 'Llama 3.3 70B from $0.10/$0.32 (openrouter.ai model page, 25 Nov). Price varies by model and host.',
  'id': 'openrouter',
  'inRate': 0.1,
  'kind': 'tokens',
  'modelNote': 'priced as Llama 3.3 70B, cheapest host',
  'name': 'OpenRouter',
  'outRate': 0.32,
  'unit': 'dollars'},
 {'confidence': 'qwen-max international rates (alibabacloud.com Model Studio pricing, 25 Nov). China region is cheaper.',
  'id': 'qwen',
  'inRate': 1.6,
  'kind': 'tokens',
  'modelNote': 'priced as qwen-max, international',
  'name': 'Qwen API',
  'outRate': 6.4,
  'unit': 'dollars'},
 {'confidence': 'GLM-5.3 rates (docs.z.ai pricing, 25 Nov). GLM-5.3-Flash is $0.15/$0.50.',
  'id': 'zhipu',
  'inRate': 1.4,
  'kind': 'tokens',
  'modelNote': 'priced as GLM-5.3',
  'name': 'Zhipu GLM API',
  'outRate': 4.4,
  'unit': 'dollars'},
 {'confidence': 'kimi-k3.1-pro rates (platform.moonshot.ai pricing, 25 Nov). Batch API is 60% of standard.',
  'id': 'moonshot',
  'inRate': 2.0,
  'kind': 'tokens',
  'modelNote': 'priced as kimi-k3.1-pro',
  'name': 'Moonshot Kimi API',
  'outRate': 10.0,
  'unit': 'dollars'},
 {'confidence': 'Command A rates (cohere.com pricing via openrouter.ai/cohere/command-a, 25 Nov).',
  'id': 'cohere',
  'inRate': 2.5,
  'kind': 'tokens',
  'modelNote': 'priced as Command A',
  'name': 'Cohere API',
  'outRate': 10.0,
  'unit': 'dollars'},
 {'confidence': 'Ollama runs models on your own machine: no token bill, only your hardware.',
  'id': 'ollama',
  'inRate': 0.0,
  'kind': 'tokens',
  'modelNote': 'local model, no per-token charge',
  'name': 'Ollama (local)',
  'outRate': 0.0,
  'unit': 'dollars'}]
PLATFORMS = PLATFORMS + API_PLATFORMS
PLATFORMS = PLATFORMS + [{'id': 'kimi', 'name': 'Kimi', 'unit': 'messages', 'freeLabel': 'Free: limited use', 'paidLabel': 'Plus, Pro, Max and Ultra plans', 'kind': 'caps', 'unverified': 'Kimi lists Plus, Pro, Max and Ultra plans (kimi.com membership). Message counts are not published. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True}, {'id': 'plus', 'label': 'Plus', 'unpublished': True}, {'id': 'pro', 'label': 'Pro', 'unpublished': True}, {'id': 'max', 'label': 'Max', 'unpublished': True}, {'id': 'ultra', 'label': 'Ultra', 'unpublished': True}]}, {'id': 'qwen_chat', 'name': 'Qwen Chat', 'unit': 'messages', 'freeLabel': 'Free: daily caps, sizes not published', 'paidLabel': 'Paid plans exist', 'kind': 'caps', 'unverified': 'Qwen Chat is free with daily caps by chat, model and feature. Sizes are not published. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True}]}, {'id': 'v0', 'name': 'v0', 'unit': 'messages', 'freeLabel': 'Free: 7 messages a day', 'paidLabel': 'Plus $30/user/mo with $30 credits', 'kind': 'caps', 'unverified': 'v0 Free has a 7 message a day limit and Plus includes $30 of monthly credits (v0.app/pricing). Credit cost per prompt varies. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free (7 messages a day)', 'unpublished': True}, {'id': 'plus', 'label': 'Plus $30/user/mo', 'unpublished': True}]}, {'id': 'elevenlabs', 'name': 'ElevenLabs', 'unit': 'credits', 'freeLabel': 'Free: 10,000 credits a month', 'paidLabel': 'Starter, Creator and higher plans', 'kind': 'caps', 'unverified': 'On standard voice models 1 credit is about 1 character of text (ElevenLabs). Cost varies by model and feature, so treat as rough.', 'plans': [{'id': 'free', 'label': 'Free (10,000 credits/mo)', 'unpublished': True}, {'id': 'starter', 'label': 'Starter', 'unpublished': True}, {'id': 'creator', 'label': 'Creator $22/mo', 'unpublished': True}]}, {'id': 'suno', 'name': 'Suno', 'unit': 'credits', 'freeLabel': 'Free: 50 credits renew each day', 'paidLabel': 'Pro 2,500 and Premier 10,000 credits a month', 'kind': 'caps', 'unverified': 'Suno gives 50 credits a day free, 2,500 a month on Pro and 10,000 on Premier (help.suno.com). Credits per song depend on the model. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free (50 credits/day)', 'unpublished': True}, {'id': 'pro', 'label': 'Pro (2,500/mo)', 'unpublished': True}, {'id': 'premier', 'label': 'Premier (10,000/mo)', 'unpublished': True}]}, {'id': 'runway', 'name': 'Runway', 'unit': 'credits', 'freeLabel': 'Free: 125 credits one time', 'paidLabel': 'Standard $12-15/mo, 625 credits', 'kind': 'caps', 'unverified': 'Runway Free gives 125 credits once and Standard 625 credits a month (runway.com/pricing). Cost varies by model and length. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free (125 credits once)', 'unpublished': True}, {'id': 'std', 'label': 'Standard (625/mo)', 'unpublished': True}]}, {'id': 'pika', 'name': 'Pika', 'unit': 'credits', 'freeLabel': 'Free: buy credit packs, no monthly allowance', 'paidLabel': 'Starter $10/mo, 600 credits', 'kind': 'caps', 'unverified': 'Pika lists about 122 credits for a 5 second 720p video and 7 for an image on some models (pika.art/pricing). Cost varies. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free (credit packs)', 'unpublished': True}, {'id': 'starter', 'label': 'Starter $10/mo (600)', 'unpublished': True}]}]
PLATFORMS = PLATFORMS + [{'id': 'le_chat', 'name': 'Le Chat', 'unit': 'messages', 'freeLabel': 'Free: limited messages and web searches', 'paidLabel': "Pro $14.99/mo, up to about 6x Free's messages", 'kind': 'caps', 'unverified': 'Mistral lists Free with limited messages and web searches, and Pro at $14.99 a month with more usage (mistral.ai/pricing). Message counts are not published. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True}, {'id': 'pro', 'label': 'Pro $14.99/mo', 'unpublished': True}]}, {'id': 'perplexity', 'name': 'Perplexity', 'unit': 'messages', 'freeLabel': 'Free: limited daily use', 'paidLabel': 'Pro $17/mo billed yearly', 'kind': 'caps', 'unverified': 'Perplexity lists Free for limited daily use and Pro at $17 a month billed yearly (perplexity.ai/hub/pricing). Exact search counts are not published. Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True}, {'id': 'pro', 'label': 'Pro $17/mo (yearly)', 'unpublished': True}]}, {'id': 'zai_chat', 'name': 'Z.ai chat', 'unit': 'messages', 'freeLabel': 'Free: works without an account', 'paidLabel': 'API and coding plans are separate', 'kind': 'caps', 'unverified': 'The Z.ai chat app is free and the page lists no message cap (chat.z.ai). Treat any estimate as rough.', 'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True}]}, {'id': 'character_ai', 'name': 'Character.ai', 'unit': 'messages', 'freeLabel': 'Free: messaging is free and unlimited', 'paidLabel': 'c.ai lite and c.ai+ add premium features', 'kind': 'caps', 'unverified': 'Character.ai says messaging is free and unlimited, with c.ai lite and c.ai+ adding premium chat styles and memory (character.ai/subscribe). Treat as rough.', 'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True}, {'id': 'lite', 'label': 'c.ai lite', 'unpublished': True}, {'id': 'plus', 'label': 'c.ai+', 'unpublished': True}]}, {'id': 'higgsfield', 'name': 'Higgsfield', 'unit': 'credits', 'freeLabel': 'Free: limited models, no monthly credits', 'paidLabel': 'Paid plans add monthly credits', 'kind': 'caps', 'unverified': "Higgsfield's free plan has no monthly credits and opens a limited set of models. Paid plans add monthly credits, and cost per generation varies by model, length and resolution (higgsfield.ai help centre). Published plan sizes disagree between sources, so no numbers are shown. Treat as rough.", 'plans': [{'id': 'free', 'label': 'Free', 'unpublished': True}, {'id': 'paid', 'label': 'Paid plan', 'unpublished': True}]}]


SIZES = {"small": "A single task or question", "medium": "A small project or feature", "big": "A big build, many steps"}
CAP_ESTIMATES = {"small": [1, 2], "medium": [2, 5], "big": [5, 12]}
CAP_PER_TYPE = {"question": [1, 2], "edit": [1, 2], "feature": [2, 5], "app": [5, 12], "general": [1, 3]}

TASK_TYPES = [
    ("question", "a question or explanation", re.compile(r"^(what|how|why|when|where|who|explain|summari[sz]e|write|draft|is |are |can |does|do )\b|\?\s*$", re.I)),
    ("edit", "a small edit", re.compile(r"\b(fix|change|update|remove|rename|tweak|adjust|move|make the)\b", re.I)),
    ("app", "a full build", re.compile(r"\b(app|website|marketplace|platform|dashboard|clone|system)\b", re.I)),
    ("feature", "a feature or page", re.compile(r"\b(auth|login|sign ?up|form|page|section|component|table|checkout|search|filter|landing)\b", re.I)),
]

# Rough per-size output-token ranges for API (per-token) platforms. Documented as a rough guide.
API_OUTPUT_TOKENS = {"small": (50, 300), "medium": (300, 1500), "big": (1500, 6000)}

def js_round(x):
    import math
    return math.floor(x + 0.5)



def estimate_tokens(text):
    words = len([w for w in text.strip().split() if w])
    return js_round(words * 1.3)



def detect_task_type(text):
    t = (text or "").strip()
    if not t:
        return None, None
    for key, label, rx in TASK_TYPES:
        if rx.search(t):
            return key, label
    return "general", "a general task"



def _fmt(n):
    if n >= 1000000:
        return "%dM" % (n // 1000000) if n % 1000000 == 0 else "%.1fM" % (n / 1000000.0)
    if n >= 1000:
        return "%dK" % js_round(n / 1000)
    return "%d" % n if float(n).is_integer() else "%.1f" % n


# Rough per-size output-token ranges for API (per-token) platforms. Documented as a rough guide.
API_OUTPUT_TOKENS = {"small": (50, 300), "medium": (300, 1500), "big": (1500, 6000)}



def _money(x):
    if x < 0.001:
        return "$%.4f" % x
    if x < 0.1:
        return "$%.3f" % x
    return "$%.2f" % x



def compute_api_estimate(platform, size, input_tokens):
    """Per-token estimate for API model platforms (Dify LLM nodes etc.)."""
    if not platform["inRate"] and not platform["outRate"]:
        return {
            "rangeText": "$0 per call",
            "subText": platform["modelNote"],
            "pct": None,
            "verdict": "fits",
            "verdictText": "Free, runs on your own machine.",
        }
    out_lo, out_hi = API_OUTPUT_TOKENS[size]
    low = input_tokens * platform["inRate"] / 1e6 + out_lo * platform["outRate"] / 1e6
    high = input_tokens * platform["inRate"] / 1e6 + out_hi * platform["outRate"] / 1e6
    notable = high >= 0.05
    return {
        "rangeText": "%s\u2013%s per call" % (_money(low), _money(high)),
        "subText": platform["modelNote"] + ", plus %s\u2013%s output tokens" % (_fmt(out_lo), _fmt(out_hi)),
        "pct": None,
        "verdict": "tight" if notable else "fits",
        "verdictText": "Notable per-call cost. A shorter prompt cuts the input side." if notable else "Cheap per call.",
    }



def compute_estimate(platform, size, plan, type_key):
    """Faithful port of computeEstimate() from the PE extension estimator.js."""
    plan_label = plan["label"] if plan else "Free"
    if platform["kind"] == "caps":
        lo, hi = CAP_PER_TYPE.get(type_key) or CAP_ESTIMATES[size]
        return {
            "rangeText": "%d\u2013%d messages" % (lo, hi),
            "subText": "on %s. Windows are not published, so no exact percentage is possible." % plan_label,
            "pct": None,
            "verdict": "tight" if size == "big" else "fits",
            "verdictText": "Big builds can hit a message window fast. Split it into steps." if size == "big" else "Should fit in a normal window.",
        }
    use_credits = plan and plan.get("unit") == "credits" and platform.get("creditPerTask")
    if use_credits:
        lo, hi = platform["creditPerTask"][size]
    elif type_key and platform.get("perType") and platform["perType"].get(type_key):
        lo, hi = platform["perType"][type_key]
    else:
        lo, hi = platform["perTask"][size]
    range_unit = (plan and plan.get("unit")) or platform["unit"]
    allowance = plan and plan.get("allowance")
    period = plan and plan.get("period")
    pct_lo = pct_hi = None
    verdict, verdict_text = "fits", "Fits comfortably."
    if allowance:
        pct_lo = lo / allowance * 100
        pct_hi = hi / allowance * 100
        unit_noun = "messages" if range_unit == "messages" else range_unit
        if pct_hi >= 100:
            verdict, verdict_text = "over", "Likely blows your %s for the %s on %s." % (unit_noun, period, plan_label)
        elif pct_hi >= 50:
            verdict, verdict_text = "tight", "Tight: up to about %d%% of your %s\u2019s allowance." % (js_round(pct_hi), period)
        else:
            verdict, verdict_text = "fits", "Fits: about %d\u2013%d%% of your %s\u2019s allowance." % (max(1, js_round(pct_lo)), max(1, js_round(pct_hi)), period)
    money = range_unit == "dollars"
    range_text = ("$%.2f\u2013$%.2f" % (lo, hi)) if money else ("%s\u2013%s %s" % (_fmt(lo), _fmt(hi), "messages" if range_unit == "messages" else range_unit))
    sub_text = ("against %s %s on %s each %s" % (_fmt(allowance) if allowance >= 1000000 else "{:,}".format(allowance), "messages" if range_unit == "messages" else range_unit, plan_label, period)) if allowance else ("on %s" % plan_label)
    return {"rangeText": range_text, "subText": sub_text, "pct": min(100, pct_hi) if pct_hi else None, "verdict": verdict, "verdictText": verdict_text}



def cheapest_free_fit(size, type_key):
    best = None
    for p in PLATFORMS:
        if p["kind"] != "credits" or not p.get("freeAllowance"):
            continue
        r = (p.get("perType", {}).get(type_key) if type_key else None) or p.get("perTask", {}).get(size)
        if not r or r[0] + r[1] <= 0:
            continue
        mid = (r[0] + r[1]) / 2
        headroom = p["freeAllowance"] / mid
        if not best or headroom > best["headroom"]:
            best = {"platform": p["name"], "headroom": headroom, "rangeText": "%s\u2013%s %s" % (_fmt(r[0]), _fmt(r[1]), p["freeUnit"])}
    return best



def platform_by_id(pid):
    for p in PLATFORMS:
        if p["id"] == pid:
            return p
    return None



def plan_by_id(platform, plan_id):
    if not plan_id:
        return None
    for plan in platform.get("plans", []):
        if plan["id"] == plan_id:
            return plan
    return None



def full_estimate(text, platform_id, size, plan_id):
    platform = platform_by_id(platform_id)
    if not platform:
        raise PEError("Unknown platform '%s'." % platform_id)
    plan = plan_by_id(platform, plan_id)
    if plan_id and not plan:
        raise PEError("Unknown plan '%s' for %s." % (plan_id, platform["name"]))
    type_key, type_label = detect_task_type(text)
    if platform["kind"] == "tokens":
        est = compute_api_estimate(platform, size, estimate_tokens(text))
    else:
        est = compute_estimate(platform, size, plan, type_key)
    result = {
        "platform": platform["name"],
        "plan": "Pay per use" if platform["kind"] == "tokens" else (plan or {}).get("label", "Free"),
        "size": size,
        "sizeMeaning": SIZES[size],
        "taskType": type_label,
        "roughInputTokens": estimate_tokens(text),
        "estimate": est["rangeText"],
        "detail": est["subText"],
        "verdict": est["verdict"],
        "verdictText": est["verdictText"],
        "confidence": platform.get("confidence") or platform.get("unverified") or "Rough estimate, not a quote.",
    }
    if platform["kind"] != "tokens":
        fit = cheapest_free_fit(size, type_key)
        if fit:
            fit = {"platform": fit["platform"], "rangeText": fit["rangeText"], "headroom": fit["headroom"]}
            result["cheapestFreeFit"] = fit
    return result

