# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/llmloop/loop.go`
- 总行数: 794 | 节选: 头部 30 行 + 13 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package llmloop

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"github.com/alibaba/open-code-review/internal/config/template"
	"github.com/alibaba/open-code-review/internal/diff"
	"github.com/alibaba/open-code-review/internal/llm"
	"github.com/alibaba/open-code-review/internal/model"
	"github.com/alibaba/open-code-review/internal/session"
	"github.com/alibaba/open-code-review/internal/stdout"
	"github.com/alibaba/open-code-review/internal/telemetry"
	"github.com/alibaba/open-code-review/internal/tool"
	"github.com/google/uuid"
)

// Deps bundles all per-call dependencies the Runner needs. Both
// internal/agent (diff review) and internal/scan (full-file scan) build a
// Deps from their own state and hand it to NewRunner.
type Deps struct {
	LLMClient         llm.LLMClient
	Model             string
```

## 关键符号（行号 → 定义）

```go
    28  type Deps struct {
    84  type Runner struct {
   102  func NewRunner(deps Deps) *Runner {
   214  type MainLoopStop int
   295  	const maxConsecutiveEmptyRounds = 3
   366  		var results []tool.ToolCallResult
   486  func graceRoundToolDefs(defs []llm.ToolDef) []llm.ToolDef {
   603  				var d *model.Diff
   731  		var err error
   752  		var err error
   774  func parseToolArgs(raw string) (map[string]any, error) {
   775  	var args map[string]any
   787  func lookupTool(reg *tool.Registry, t tool.Tool) tool.Provider {
```
