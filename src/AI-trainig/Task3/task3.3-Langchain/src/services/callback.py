import logging
from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class OpenRouterTokenLogger(BaseCallbackHandler):
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        print("\n[CALLBACK] LLM call initiated via OpenRouter...")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        print("[CALLBACK] LLM execution finished. Processing metrics...")
        token_usage = {}
        if response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    if hasattr(gen, "message") and hasattr(gen.message, "usage_metadata"):
                        if gen.message.usage_metadata:
                            token_usage = gen.message.usage_metadata
                            break
        if token_usage:
            print(f" Input Tokens:  {token_usage.get('input_tokens', 0)}")
            print(f" Output Tokens: {token_usage.get('output_tokens', 0)}")
            print(f" Total Tokens:  {token_usage.get('total_tokens', 0)}")