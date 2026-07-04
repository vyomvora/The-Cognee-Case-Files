"""
Provider-agnostic LLM wrapper. The rest of the app only ever calls ask_llm().

Configure via three env vars (see .env.example): LLM_PROVIDER, LLM_MODEL,
LLM_API_KEY (+ optional LLM_BASE_URL). Swap providers by changing env vars --
no code changes needed elsewhere.

The LLM is used for exactly two jobs (per README section 4): suspect
roleplay narration and atmospheric clue-discovery prose. It never decides
guilt -- every verdict in this game is graph logic in graph_store.py.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "").strip().lower()
LLM_MODEL = os.environ.get("LLM_MODEL", "").strip()
LLM_API_KEY = os.environ.get("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "").strip() or None


def ask_llm(system: str, messages: list[dict[str, str]]) -> str:
    """
    Ask the configured LLM for a completion.

    Parameters
    ----------
    system: the system prompt.
    messages: a list of {"role": "user"|"assistant", "content": str}.

    Returns
    -------
    The model's text reply. If no LLM_API_KEY is configured, returns a
    canned in-character fallback so the game stays playable before a key is
    added -- see _fallback_reply().
    """
    if not LLM_API_KEY:
        return _fallback_reply(messages)

    try:
        import litellm

        model = LLM_MODEL
        if LLM_PROVIDER and "/" not in model:
            model = f"{LLM_PROVIDER}/{LLM_MODEL}"

        response = litellm.completion(
            model=model,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            messages=[{"role": "system", "content": system}, *messages],
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # LLM outages must never break the game loop
        print(f"[llm_client] LLM call failed (model={LLM_PROVIDER}/{LLM_MODEL}): {exc}", file=sys.stderr)
        return _fallback_reply(messages, error=str(exc))


def _fallback_reply(messages: list[dict[str, str]], error: str | None = None) -> str:
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    prefix = "[LLM_API_KEY not set -- add one to .env for full narration] " if not error else "[LLM error, showing plain facts] "
    return f"{prefix}{last_user}"
