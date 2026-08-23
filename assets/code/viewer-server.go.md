# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/viewer/server.go`
- 总行数: 374 | 节选: 头部 30 行 + 24 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package viewer

import (
	"embed"
	"fmt"
	"html/template"
	"io/fs"
	"net/http"
	"strconv"
	"strings"
	"time"
)

//go:embed templates/*.html static/style.css static/session.js static/repos.js
var assets embed.FS

func StartServer(addr string) error {
	root, err := SessionsRoot()
	if err != nil {
		return fmt.Errorf("resolve sessions root: %w", err)
	}

	mux := http.NewServeMux()

	// Static assets (must be registered before "/" catch-all)
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.FS(staticFS()))))

```

## 关键符号（行号 → 定义）

```go
    18  var assets embed.FS
    20  func StartServer(addr string) error {
    72  var cstZone = func() *time.Location {
    80  func formatTime(t time.Time) string {
    85  type CommentFileGroup struct {
    91  type SeverityCount struct {
    99  type CategoryCount struct {
   110  var knownCommentCategories = map[string]struct{}{
   121  func normalizedCommentCategory(category string) string {
   129  func normalizedCommentSeverity(severity string) string {
   133  func categoryCounts(comments []*ReviewComment) CategoryCount {
   134  	var counts CategoryCount
   158  func severityCounts(comments []*ReviewComment) SeverityCount {
   159  	var counts SeverityCount
   175  func parseTemplate(name string) (*template.Template, error) {
   208  			var result []struct {
   232  			var groups []CommentFileGroup
   292  func truncateText(n int, s string) string {
   299  func renderTemplate(w http.ResponseWriter, name string, data any) {
   312  func staticFS() fs.FS {
   320  func formatNumber(n int) string {
   321  	var display string
   343  func trimFloatSuffix(s string) string {
   365  func formatDuration(seconds float64) string {
```
