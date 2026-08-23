# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/agent/agent.go`
- 总行数: 1900 | 节选: 头部 30 行 + 55 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package agent

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"maps"
	"runtime/debug"
	"slices"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/alibaba/open-code-review/internal/config/rules"
	"github.com/alibaba/open-code-review/internal/config/template"
	"github.com/alibaba/open-code-review/internal/config/toolsconfig"
	"github.com/alibaba/open-code-review/internal/diff"
	"github.com/alibaba/open-code-review/internal/gitcmd"
	"github.com/alibaba/open-code-review/internal/llm"
```

## 关键符号（行号 → 定义）

```go
    44  type AgentWarning = llmloop.AgentWarning
    47  type CommentWorkerPool = llmloop.CommentWorkerPool
    50  func NewCommentWorkerPool(workerCount int) *CommentWorkerPool {
    55  type Args struct {
   171  type RuntimeConfig struct {
   181  type Agent struct {
   202  type ResumeInfo = session.ResumeInfo
   205  func New(args Args) *Agent {
   496  	var provider *diff.Provider
   600  	var wg sync.WaitGroup
   610  	var dispatched int64
   698  			var fileCtx context.Context
   699  			var cancel context.CancelFunc
   775  		var setErr error
   797  	var reused int64
   832  func countDispatchable(diffs []model.Diff) int64 {
   833  	var n int64
   849  func reviewItemFingerprint(mode string, d model.Diff) string {
   942  	type pair struct{ id, fingerprint string }
   974  	var fields []string
  1016  func hashFields(fields ...string) string {
  1018  	var lenBuf [8]byte
  1030  func manifestPaths(d model.Diff) (oldPath, newPath string) {
  1103  var errMainTaskEmpty = errors.New("main_task.messages is empty in template")
  1111  func classifyItemError(err error) (session.FailureClass, string) {
  1136  func classifyMainLoopStop(stop llmloop.MainLoopStop) (session.FailureClass, string) {
  1149  type subtaskStop struct {
  1204  func resumedFromSession(resume *session.ResumeState) string {
  1239  	var planResult string
  1247  		var err error
  1350  var filterTools = []llm.ToolDef{
  1462  	var totalTokens int64
  1493  func buildFilterCommentsJSON(comments []model.LlmComment) string {
  1494  	type filterComment struct {
  1514  func parseFilterToolCalls(calls []llm.ToolCall, total int) map[int]struct{} {
  1515  	var indices map[int]struct{}
  1523  			var args struct {
  1534  				var idx int
  1546  func parseFilterResponse(raw string, total int) map[int]struct{} {
  1548  	var ids []string
  1559  		var idx int
  1569  	var sb strings.Builder
  1609  	var kept []model.Diff
  1652  	var kept []model.Diff
  1731  	var totalTokens int64
  1744  func formatToolDefs(toolDefs []llm.ToolDef) string {
  1749  	var sb strings.Builder
  1793  type orderedToolParameter struct {
  1799  func orderedToolParameters(raw json.RawMessage) ([]orderedToolParameter, bool) {
  1804  	var def struct {
  1828  	var params []orderedToolParameter
  1838  		var meta struct {
  1880  func BuildToolDefs(entries []toolsconfig.ToolConfigEntry, planOnly bool) []llm.ToolDef {
  1881  	var defs []llm.ToolDef
  1887  		var fn llm.FunctionDef
```
