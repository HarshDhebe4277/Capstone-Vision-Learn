"""Lightweight client helpers for calling Mistral APIs.

This module uses the Mistral REST API (set `MISTRAL_BASE_URL` and `MISTRAL_API_KEY`).
Refer to https://docs.mistral.ai/ for the latest endpoints and payloads.
"""
import os
import requests
from typing import Dict, Any

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_BASE_URL = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai")


class MistralClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or MISTRAL_API_KEY
        self.base_url = base_url or MISTRAL_BASE_URL
        if not self.api_key:
            raise RuntimeError("MISTRAL_API_KEY not set in environment")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def create_completion(self, model: str, prompt: str, max_tokens: int = 1024) -> Dict[str, Any]:
        """Simple text completion wrapper — adjust route/payload to match Mistral API."""
        url = f"{self.base_url}/v1/models/{model}/completions"
        payload = {
            "input": prompt,
            "max_output_tokens": max_tokens,
        }
        r = requests.post(url, headers=self._headers(), json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def multimodal_infer(self, model: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for multimodal/vision endpoints — check docs for exact contract."""
        url = f"{self.base_url}/v1/models/{model}/infer"
        r = requests.post(url, headers=self._headers(), json=inputs, timeout=120)
        r.raise_for_status()
        return r.json()


class LangChainMistralClient:
    """Optional LangChain-backed client.

    This attempts to use the LangChain Python integration for Mistral if available.
    If LangChain or the Mistral integration is not installed, initialisation raises ImportError
    with guidance on how to install the necessary package.
    """
    def __init__(self, model: str = "mistral-large-3", api_key: str = None):
        self.model = model
        self.api_key = api_key or MISTRAL_API_KEY
        if not self.api_key:
            raise RuntimeError("MISTRAL_API_KEY not set in environment")

        # dynamic import to avoid hard dependency
        try:
            # attempt import path used by langchain integrations
            from langchain.llms import MistralAI  # type: ignore
        except Exception:
            try:
                # some setups expose a package named langchain_mistralai
                from langchain_mistralai import MistralAI  # type: ignore
            except Exception as e:
                raise ImportError(
                    "LangChain Mistral integration not found. Install with `pip install langchain langchain-mistralai` or use the REST MistralClient.`"
                ) from e

        # instantiate the LangChain LLM wrapper
        # provide the API key through env var or params depending on the implementation
        try:
            # MistralAI class commonly accepts model, temperature and apiKey-like args
            self.llm = MistralAI(model=self.model, api_key=self.api_key)
        except TypeError:
            # fallback to passing api key via env (some wrappers read from env)
            os.environ.setdefault("MISTRAL_API_KEY", self.api_key)
            self.llm = MistralAI(model=self.model)

    def create_completion(self, prompt: str, max_tokens: int = 1024) -> Dict[str, Any]:
        # LangChain LLMs typically implement a __call__ returning a string
        result = self.llm.invoke(prompt) if hasattr(self.llm, "invoke") else self.llm(prompt)
        # normalize to a dict similar to REST client
        return {"output": result}


def get_mistral_client(prefer_langchain: bool = True, model: str = "mistral-large-3"):
    """Return a client with unified signature: create_completion(model, prompt, max_tokens)

    The returned client exposes `create_completion(model, prompt, max_tokens)` and
    `multimodal_infer(model, inputs)` where available. If LangChain integration is
    available and `prefer_langchain` is True, a LangChain-backed client is returned.
    Otherwise falls back to the REST `MistralClient`.
    """

    class UnifiedREST:
        def __init__(self, rest_client: MistralClient):
            self._c = rest_client

        def create_completion(self, model: str, prompt: str, max_tokens: int = 1024):
            return self._c.create_completion(model=model, prompt=prompt, max_tokens=max_tokens)

        def multimodal_infer(self, model: str, inputs: Dict[str, Any]):
            return self._c.multimodal_infer(model=model, inputs=inputs)

    class UnifiedLangChain:
        def __init__(self, lc_client: LangChainMistralClient, model: str):
            self._lc = lc_client
            self._model = model

        def create_completion(self, model: str, prompt: str, max_tokens: int = 1024):
            # ignore model argument; LangChain client already constructed with desired model
            return self._lc.create_completion(prompt=prompt, max_tokens=max_tokens)

        def multimodal_infer(self, model: str, inputs: Dict[str, Any]):
            # LangChain multimodal hooks differ — attempt to call multimodal_infer if present
            if hasattr(self._lc, "multimodal_infer"):
                return self._lc.multimodal_infer(model, inputs)
            raise NotImplementedError("multimodal_infer not available on LangChain client")

    # Try LangChain first
    if prefer_langchain:
        try:
            lc = LangChainMistralClient(model=model)
            return UnifiedLangChain(lc, model)
        except Exception:
            # fallback to REST
            pass

    # fallback
    rest = MistralClient()
    return UnifiedREST(rest)

