from sovereignspec.adapters.aider import AiderAdapter
from sovereignspec.adapters.base import AgentAdapter
from sovereignspec.adapters.claude_code import ClaudeCodeAdapter
from sovereignspec.adapters.cline import ClineAdapter
from sovereignspec.adapters.codex import CodexAdapter
from sovereignspec.adapters.continue_ import ContinueAdapter
from sovereignspec.adapters.cursor import CursorAdapter
from sovereignspec.adapters.gemini_cli import GeminiCLIAdapter
from sovereignspec.adapters.generic import GenericFilesystemAdapter
from sovereignspec.adapters.opencode import OpenCodeAdapter
from sovereignspec.adapters.roocode import RooCodeAdapter
from sovereignspec.adapters.windsurf import WindsurfAdapter

_ADAPTER_REGISTRY: dict[str, type[AgentAdapter]] = {
    "claude-code": ClaudeCodeAdapter,
    "opencode": OpenCodeAdapter,
    "cursor": CursorAdapter,
    "cline": ClineAdapter,
    "roocode": RooCodeAdapter,
    "codex": CodexAdapter,
    "gemini-cli": GeminiCLIAdapter,
    "aider": AiderAdapter,
    "windsurf": WindsurfAdapter,
    "continue": ContinueAdapter,
    "generic": GenericFilesystemAdapter,
}


def get_adapter(name: str) -> AgentAdapter:
    cls = _ADAPTER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown adapter '{name}'. Available: {', '.join(sorted(_ADAPTER_REGISTRY))}")
    return cls()


def list_adapters() -> list[str]:
    return sorted(_ADAPTER_REGISTRY)
