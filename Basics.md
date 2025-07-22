# Introduction

> **Model Context Protocol (MCP)**: is an open protocol that standardizes how applications provide context to LLMs. 
  
Advantages:
- Flexibility to switch between LLMs and vendors.
- Pre-built integrations that can be directly plugged into.

Capabilities:
- Provide functionalities through **Tools**.
- Expose data through **Resources**.
- Define interactive patterns through **Prompts** (reusable templates for LLM interactions).


# Architecture
MCP follows client-server architecture where the application can connect to multiple MCP servers.

# MCP vs API

| | MCP | API |
|-|-----|-----|
| **Purpose:** | AI-native, designed for LLMs | General purpose, software-to-software |
| **Discovery:** | Dynamic, self-describing capabilities | Requires documentation, no self-discovery |
| **Standardization:** | Uniform protocol for all servers | Varies with different authentication schemes |
| **Adaptability:** | Adapts to changes at runtime | Breaks if API changes, needs update |
| **Integration:** | Easier AI integration with adapters | Requires custom code for each API |
