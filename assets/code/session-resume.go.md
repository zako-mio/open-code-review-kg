# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/session/resume.go`
- 总行数: 361 | 节选: 头部 30 行 + 13 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package session

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/alibaba/open-code-review/internal/model"
)

// ResumeState is the replayed, read-only checkpoint index for one prior session.
type ResumeState struct {
	SessionID        string
	RepoDir          string
	GitBranch        string
	Model            string
	ReviewMode       string
	DiffFrom         string
	DiffTo           string
	DiffCommit       string
	ScanPaths        []string
	HasScanPathScope bool
```

## 关键符号（行号 → 定义）

```go
    20  type ResumeState struct {
    51  type ResumeItem struct {
    59  type resumeRecord struct {
    81  func SessionFilePath(repoDir, sessionID string) (string, error) {
    97  func LoadResumeState(repoDir, sessionID string) (*ResumeState, error) {
   107  func LoadReviewResumeState(repoDir, sessionID string) (*ResumeState, error) {
   111  func loadResumeState(repoDir, sessionID string, skipUnparseable bool) (*ResumeState, error) {
   151  	var rec resumeRecord
   256  func manifestReusableFingerprints(m *RunManifest) map[string]bool {
   311  func normalizeScanPaths(paths []string) []string {
   334  func equalStringSlices(a, b []string) bool {
   346  func formatScanScope(paths []string) string {
   353  func copyLlmComments(in []model.LlmComment) []model.LlmComment {
```
