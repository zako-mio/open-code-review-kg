# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/session/manifest.go`
- 总行数: 968 | 节选: 头部 30 行 + 29 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package session

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"path"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"
	"unicode/utf8"
)

// ManifestSchemaVersion identifies the versioned, machine-readable coverage
// contract emitted for a review (or scan) run. Consumers should gate on this
// value; unknown future versions must be ignored rather than misread.
const ManifestSchemaVersion = "ocr.run-manifest/v1"

// OperationReview is the manifest operation for a diff review run. It is the
// only operation wired in v1 (scan stays legacy with no manifest).
const OperationReview = "review"

// Input modes describe how the run's input was selected. They are stored in
// ManifestInput.Mode (mandatory) and decide how the remaining input fields are
```

## 关键符号（行号 → 定义）

```go
    23  const ManifestSchemaVersion = "ocr.run-manifest/v1"
    27  const OperationReview = "review"
    40  func validInputMode(m string) bool {
    53  type FailureClass string
    89  type RunFailureClass string
   119  func itemFailureForRunClass(c RunFailureClass) FailureClass {
   139  type RunFailure struct {
   154  type pendingFailureCause struct {
   163  type TerminalState string
   181  type CoverageItem struct {
   199  func ItemID(operation, mode, oldPath, newPath string) string {
   216  func normalizePath(p string) string {
   231  type Coverage struct {
   240  type ManifestRepository struct {
   249  type ManifestInput struct {
   261  type ManifestExecution struct {
   274  type RunManifest struct {
   290  type itemState string
   300  type builderItem struct {
   330  type ManifestBuilder struct {
   351  func NewManifestBuilder(runID, operation string) *ManifestBuilder {
   617  const maxReasonLen = 500
   636  func stripUnsafeChars(s string) string {
   662  func sanitizeReason(s string) string {
   779  	type sweptItem struct {
   826  func emptyManifest() RunManifest {
   894  func cloneItems(src []CoverageItem) []CoverageItem {
   941  func computeTerminal(cov Coverage, rf *RunFailure) TerminalState {
   960  func sortItems(items []CoverageItem) {
```
