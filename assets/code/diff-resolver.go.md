# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/diff/resolver.go`
- 总行数: 307 | 节选: 头部 30 行 + 13 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package diff

import (
	"strings"

	"github.com/alibaba/open-code-review/internal/model"
)

// ResolveLineNumbers populates StartLine/EndLine on each comment by matching
// the ExistingCode against the corresponding file's diff hunks (primary), or
// falling back to scanning the full new-file content line-by-line.
func ResolveLineNumbers(comments []model.LlmComment, diffs []model.Diff) []model.LlmComment {
	if len(comments) == 0 || len(diffs) == 0 {
		return comments
	}

	// Build lookup: newPath -> *Diff
	diffByPath := make(map[string]*model.Diff, len(diffs))
	for i := range diffs {
		d := &diffs[i]
		if d.NewPath != "/dev/null" && d.NewPath != "" {
			diffByPath[d.NewPath] = d
		}
		if d.OldPath != "/dev/null" && d.OldPath != "" {
			diffByPath[d.OldPath] = d
		}
	}
```

## 关键符号（行号 → 定义）

```go
    15  func ResolveLineNumbers(comments []model.LlmComment, diffs []model.Diff) []model.LlmComment {
    62  func ResolveComment(cm *model.LlmComment, d *model.Diff) bool {
   100  func RelocateAcrossFiles(cm *model.LlmComment, diffs []model.Diff) (string, bool) {
   105  	type hit struct {
   109  	var hits []hit
   142  type indexedLine struct {
   151  func resolveFromHunk(d *model.Diff, cm *model.LlmComment) bool {
   186  func extractSideLines(hunk *Hunk, newSide bool) []indexedLine {
   187  	var result []indexedLine
   217  func matchConsecutive(sideLines []indexedLine, targetLines []string) (startLine, endLine int, found bool) {
   238  func resolveFromFileContent(d *model.Diff, cm *model.LlmComment) bool {
   286  func splitAndNormalize(code string) []string {
   301  func normalizeLine(s string) string {
```
