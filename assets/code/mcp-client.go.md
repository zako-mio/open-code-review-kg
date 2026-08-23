# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/mcp/client.go`
- 总行数: 195 | 节选: 头部 30 行 + 9 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package mcp

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// Client wraps a single MCP server connection.
type Client struct {
	name    string
	session *mcp.ClientSession
	tools   []*mcp.Tool
}

// NewClient starts an MCP server subprocess (stdio transport), initializes the
// connection, and caches the list of available tools. The context governs the
// initialization timeout (Connect + ListTools), NOT the subprocess
// lifetime — the subprocess stays alive until Close is called.
// When dir is non-empty, the subprocess runs with that working directory.
func NewClient(ctx context.Context, name, command string, args, env []string, dir, version string) (*Client, error) {
```

## 关键符号（行号 → 定义）

```go
    19  type Client struct {
    30  func NewClient(ctx context.Context, name, command string, args, env []string, dir, version string) (*Client, error) {
    48  	var success bool
    71  func NewRemoteClient(ctx context.Context, name, url string, headers map[string]string, version string) (*Client, error) {
    72  	var expanded map[string]string
   104  	var success bool
   126  type headerTransport struct {
   180  func contentToText(contents []mcp.Content) string {
   181  	var parts []string
```
