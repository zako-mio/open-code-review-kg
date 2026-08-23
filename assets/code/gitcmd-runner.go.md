# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/gitcmd/runner.go`
- 总行数: 131 | 节选: 头部 30 行 + 5 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package gitcmd

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"os/exec"
)

const defaultMaxConcurrent = 16

// Runner limits the number of concurrent git subprocesses via an internal
// semaphore. All git command invocations should go through a shared Runner
// instance so that the total system-wide subprocess count stays bounded.
type Runner struct {
	sem chan struct{}
}

// New creates a Runner that allows at most maxConcurrent simultaneous git
// subprocesses. If maxConcurrent <= 0 the default (16) is used.
func New(maxConcurrent int) *Runner {
	if maxConcurrent <= 0 {
		maxConcurrent = defaultMaxConcurrent
	}
	return &Runner{sem: make(chan struct{}, maxConcurrent)}
}
```

## 关键符号（行号 → 定义）

```go
    14  const defaultMaxConcurrent = 16
    19  type Runner struct {
    25  func New(maxConcurrent int) *Runner {
    81  	var stdout, stderr bytes.Buffer
   102  	var stderrBuf bytes.Buffer
```
