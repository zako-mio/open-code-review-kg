# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/llm/providers.go`
- 总行数: 517 | 节选: 头部 30 行 + 7 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package llm

import (
	"sort"
	"strings"
)

// Provider holds the preset configuration for a known LLM provider.
//
// Protocol uses the canonical names defined in protocol.go:
//   - ProtocolAnthropic ("anthropic")
//   - ProtocolOpenAIChatCompletions ("openai")
//   - ProtocolOpenAIResponses ("openai-responses")
//   - ProtocolAnthropicBedrock ("anthropic-bedrock")
//
// To add a built-in provider that speaks a different protocol, set Protocol
// accordingly and ensure NewLLMClient has a matching case.
type Provider struct {
	Name        string
	DisplayName string
	Protocol    string
	BaseURL     string
	AuthHeader  string // Anthropic-only; empty for OpenAI-compatible
	EnvVar      string // environment variable name for API key fallback
	Models      []string

	// AmbientAuth marks a provider whose credentials come from the
```

## 关键符号（行号 → 定义）

```go
    21  type Provider struct {
    38  var registry = []Provider{
   477  var registryMap map[string]Provider
   479  func init() {
   488  func LookupProvider(name string) (Provider, bool) {
   498  func ListProviders() []Provider {
   509  func copyProvider(p Provider) Provider {
```
