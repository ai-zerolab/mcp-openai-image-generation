# mcp-openai-image-generation

[![Release](https://img.shields.io/github/v/release/ai-zerolab/mcp-openai-image-generation)](https://img.shields.io/github/v/release/ai-zerolab/mcp-openai-image-generation)
[![Commit activity](https://img.shields.io/github/commit-activity/m/ai-zerolab/mcp-openai-image-generation)](https://img.shields.io/github/commit-activity/m/ai-zerolab/mcp-openai-image-generation)
[![License](https://img.shields.io/github/license/ai-zerolab/mcp-openai-image-generation)](https://img.shields.io/github/license/ai-zerolab/mcp-openai-image-generation)

OpenAI image generation MCP server

- **Github repository**: <https://github.com/ai-zerolab/mcp-openai-image-generation/>

## Configuration

```json
{
  "mcpServers": {
    "openai-image-generation": {
      "command": "uvx",
      "args": ["mcp-openai-image-generation@latest", "stdio"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "OPENAI_BASE_URL": "${OPENAI_BASE_URL}"
      }
    }
  }
}
```
