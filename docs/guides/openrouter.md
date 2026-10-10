# OpenRouter support

TinyTroupe can use OpenRouter through its OpenAI-compatible API for both chat
completions and embeddings.

Add the following to the repository-root `.env` file:

```dotenv
TINY_TROUPE_API_TYPE=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key

# Keep one model active; comment out the other line.
OPENROUTER_MODEL=openai/gpt-5-mini
# OPENROUTER_MODEL=openai/gpt-4o-mini

OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-3-small
TINY_TROUPE_MAX_COMPLETION_TOKENS=16384
```

Restart the Python process or notebook kernel after changing `.env`, because
TinyTroupe reads its configuration during import. The model names must be
OpenRouter model slugs, including their provider prefix.

The optional `OPENROUTER_SITE_URL` and `OPENROUTER_APP_NAME` variables send
OpenRouter's attribution headers.
