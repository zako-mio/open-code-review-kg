# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/diff/relocation.go`
- 总行数: 118 | 节选: 头部 30 行 + 4 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package diff

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/alibaba/open-code-review/internal/config/template"
	"github.com/alibaba/open-code-review/internal/llm"
	"github.com/alibaba/open-code-review/internal/model"
	"github.com/alibaba/open-code-review/internal/stdout"
	"github.com/alibaba/open-code-review/internal/telemetry"
)

// BuildReLocationMessages renders the re-location prompt for cm against d.
// Returns nil when the task template is absent or empty, which the caller
// treats as "no re-location attempt": no session record, no request.
//
// This is split out of ReLocateComment so the caller can create the
// ReLocationTask session record — and therefore know its RequestNo — before any
// HTTP call happens. It is pure prompt construction: no client, no session, no
// request identity. Keeping it that way is what stops observability concerns
// from sinking into package diff.
func BuildReLocationMessages(cm *model.LlmComment, d *model.Diff, task *template.LlmConversation) []llm.Message {
	if task == nil || len(task.Messages) == 0 {
		return nil
```

## 关键符号（行号 → 定义）

```go
    28  func BuildReLocationMessages(cm *model.LlmComment, d *model.Diff, task *template.LlmConversation) []llm.Message {
    49  func ReLocateComment(
    76  	var totalTokens int64
    99  func extractCodeBlock(text string) string {
```
