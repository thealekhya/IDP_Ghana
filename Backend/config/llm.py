import os


def get_llm():
    """
    Return a LangChain chat model based on environment:
      - LLM_PROVIDER=openai (default) uses OPENAI_API_KEY
      - LLM_PROVIDER=gemini uses GEMINI_API_KEY

    This keeps the rest of the codebase provider-agnostic.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    model = os.getenv("LLM_MODEL", "").strip()

    if provider == "gemini":
        # Lazy import so projects without Gemini deps still import.
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("GEMINI_API_KEY is not set but LLM_PROVIDER=gemini.")

        return ChatGoogleGenerativeAI(
            # Use a model name that exists for google-genai v1beta
            # (common choices: gemini-2.0-flash, gemini-flash-latest)
            model=model or "gemini-2.0-flash",
            temperature=0.4,
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )

    # Default: OpenAI
    from langchain_openai import ChatOpenAI

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set but LLM_PROVIDER=openai.")

    return ChatOpenAI(
        model=model or "gpt-4o",
        temperature=0.4,
    )

