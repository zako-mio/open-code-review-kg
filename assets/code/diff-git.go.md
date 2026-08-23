# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/diff/git.go`
- 总行数: 640 | 节选: 头部 30 行 + 23 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package diff

import (
	"bytes"
	"context"
	"fmt"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/bmatcuk/doublestar/v4"

	"github.com/alibaba/open-code-review/internal/gitcmd"
	"github.com/alibaba/open-code-review/internal/model"
)

// DiffContextLines defines the number of context lines around each changed hunk.
const DiffContextLines = 3

// providerDirIgnoreDirs: directory prefixes to always exclude from diff results.
var providerDirIgnoreDirs = []string{
	".idea/",
	".vscode/",
	".svn/",
	".git/",
```

## 关键符号（行号 → 定义）

```go
    23  const DiffContextLines = 3
    26  var providerDirIgnoreDirs = []string{
    42  type Mode int
    51  type Provider struct {
    66  func NewProvider(repoDir, from, to string, runner *gitcmd.Runner) *Provider {
    77  func NewCommitProvider(repoDir, commit string, runner *gitcmd.Runner) *Provider {
    87  func NewWorkspaceProvider(repoDir string, runner *gitcmd.Runner) *Provider {
   101  type InputResolution struct {
   174  	var combined strings.Builder
   216  	var ref string
   237  	var patterns []string
   295  func matchGitignorePattern(relPath, pat string) bool {
   304  func matchGitignoreBody(relPath, body string) bool {
   352  func matchGitignoreDirectory(relPath, pattern string) bool {
   383  	var result []model.Diff
   436  func canonicalRemote(raw string) string {
   479  func joinHostPath(host, path string) string {
   493  func isLocalRemote(s string) bool {
   512  func isASCIILetter(b byte) bool {
   549  func firstLine(out string) string {
   580  	var results []string
   592  		var sb strings.Builder
   618  	var files []string
```
