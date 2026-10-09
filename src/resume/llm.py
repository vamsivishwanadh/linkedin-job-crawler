from __future__ import annotations

import json
import os
import time
from typing import TypeVar

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError
from pydantic import BaseModel, ValidationError

from src.config import load_env_file

T = TypeVar("T", bound=BaseModel)


class LlmConfig:
    def __init__(self, model: str, max_retries: int = 3) -> None:
        self.model = model
        self.max_retries = max_retries

    @staticmethod
    def from_env(model_override: str | None = None) -> "LlmConfig":
        model = (model_override or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini").strip()
        return LlmConfig(model=model)


def get_openai_client() -> OpenAI:
    load_env_file()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to .env (see .env.example)."
        )
    return OpenAI(api_key=key)


def complete_json(
    client: OpenAI,
    config: LlmConfig,
    system: str,
    user: str,
    model_type: type[T],
) -> T:
    last_error: Exception | None = None
    for attempt in range(config.max_retries):
        try:
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content or ""
            data = json.loads(content)
            return model_type.model_validate(data)
        except (json.JSONDecodeError, ValidationError, KeyError, IndexError) as exc:
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
        except RateLimitError as exc:
            last_error = exc
            time.sleep(2.0 * (attempt + 1))
        except APIStatusError as exc:
            last_error = exc
            if exc.status_code == 401:
                raise RuntimeError(
                    "OpenAI rejected OPENAI_API_KEY (401). Use the key in project .env "
                    "(it overrides Windows system env). Remove stale OPENAI_API_KEY from "
                    "Windows Environment Variables if needed, or rotate the key at "
                    "https://platform.openai.com/account/api-keys"
                ) from exc
            if attempt + 1 >= config.max_retries:
                raise
            time.sleep(1.0 * (attempt + 1))
        except APIConnectionError as exc:
            last_error = exc
            if attempt + 1 >= config.max_retries:
                raise
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"LLM returned invalid JSON after retries: {last_error}")
