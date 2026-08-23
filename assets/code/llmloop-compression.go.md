# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/llmloop/compression.go`
- 总行数: 380 | 节选: 头部 30 行 + 16 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package llmloop

import (
	"context"
	"fmt"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/alibaba/open-code-review/internal/llm"
	"github.com/alibaba/open-code-review/internal/session"
	"github.com/alibaba/open-code-review/internal/stdout"
)

// Compression thresholds, as fractions of MaxTokens.
const (
	tokenSoftThreshold    = 0.60 // async background compression
	tokenWarningThreshold = 0.80 // immediate sync compression
)

// PromptTokenLimit returns tokenWarningThreshold (80%) of maxTokens. It is
// shared by the agent and scan pre-flight gates, their large-input filters, and
// computeActiveZoneSize so the threshold has a single definition. Non-positive
// input is not special-cased — each caller decides what that means.
func PromptTokenLimit(maxTokens int) int {
	return int(float64(maxTokens) * tokenWarningThreshold)
```

## 关键符号（行号 → 定义）

```go
    29  func PromptTokenLimit(maxTokens int) int {
    35  type round struct {
    41  type partitionResult struct {
    49  type compressionJob struct {
    61  type compressionState struct {
    69  func CountMessagesTokens(msgs []llm.Message) int {
    70  	var total int
    79  func groupIntoRounds(messages []llm.Message, start int) []round {
    80  	var rounds []round
   101  func computeActiveZoneSize(rounds []round, messages []llm.Message, maxTokens int, reservedTokens int) int {
   126  func partitionMessages(messages []llm.Message, maxTokens int, prevSummaryTokenEstimate int) partitionResult {
   162  func StripMarkdownFences(s string) string { return stripMarkdownFences(s) }
   166  func stripMarkdownFences(s string) string {
   186  func buildMessageXML(msgs []llm.Message) string {
   187  	var sb strings.Builder
   202  func copyMessages(msgs []llm.Message) []llm.Message {
```
