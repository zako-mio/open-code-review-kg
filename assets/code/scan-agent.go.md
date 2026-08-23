# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/scan/agent.go`
- 总行数: 1173 | 节选: 头部 30 行 + 31 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package scan

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	allowedext "github.com/alibaba/open-code-review/internal/config/allowlist"
	"github.com/alibaba/open-code-review/internal/config/rules"
	"github.com/alibaba/open-code-review/internal/config/template"
	"github.com/alibaba/open-code-review/internal/gitcmd"
	"github.com/alibaba/open-code-review/internal/llm"
	"github.com/alibaba/open-code-review/internal/llmloop"
	"github.com/alibaba/open-code-review/internal/model"
	"github.com/alibaba/open-code-review/internal/session"
	"github.com/alibaba/open-code-review/internal/stdout"
	"github.com/alibaba/open-code-review/internal/telemetry"
	"github.com/alibaba/open-code-review/internal/tool"
)

// changeFilesScanLiteral substitutes for the {{change_files}} placeholder.
```

## 关键符号（行号 → 定义）

```go
    33  const changeFilesScanLiteral = "(not applicable in full-scan mode)"
    43  type Args struct {
    99  type Agent struct {
   119  func NewAgent(args Args) *Agent {
   162  func toLoopTemplate(s template.ScanTemplate) template.Template {
   262  	var reused int64
   263  	var rerun int64
   288  func scanItemFingerprint(it model.ScanItem) string {
   293  func resumedFromSession(resume *session.ResumeState) string {
   429  	var kept []model.ScanItem
   455  	var kept []model.ScanItem
   498  func extFromPath(path string) string {
   533  	var dispatched int64
   578  type batchCheckpoint struct {
   620  func groupCommentsByPath(comments []model.LlmComment) map[string][]model.LlmComment {
   710  			var fileCtx context.Context
   711  			var cancel context.CancelFunc
   814  	const noPlan = "(no pre-scan plan; review the entire file as usual)"
   886  	const pathKey = "__scan_project_summary__"
   917  func buildSummaryCommentsList(comments []model.LlmComment) string {
   918  	const maxLine = 280
   919  	var sb strings.Builder
  1003  func buildDedupCommentsJSON(comments []model.LlmComment) string {
  1004  	type wire struct {
  1027  func applyDedupGroups(rawJSON string, originals []model.LlmComment) ([]model.LlmComment, bool) {
  1032  func applyDedupGroupsWithCheckpoints(
  1041  	var parsed struct {
  1057  	var out []model.LlmComment
  1107  func formatPlanGuidance(raw string) string {
  1114  	var plan struct {
  1128  	var sb strings.Builder
```
