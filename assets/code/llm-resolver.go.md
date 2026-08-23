# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/llm/resolver.go`
- 总行数: 981 | 节选: 头部 30 行 + 51 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package llm

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// ResolvedEndpoint holds the resolved LLM endpoint configuration.
type ResolvedEndpoint struct {
	URL          string
	Token        string
	Model        string
	Provider     string
	Protocol     string            // canonical protocol name (see protocol.go); resolver normalizes aliases
	AuthHeader   string            // Anthropic auth header: "x-api-key" or "authorization"
	Source       string            // human-readable config source label
	ExtraBody    map[string]any    // vendor-specific request body fields
	ExtraHeaders map[string]string // extra HTTP headers for the LLM request
	// Timeout is the per-request HTTP timeout; 0 means use the client default (5 min).
	// Only config file (llm/provider sections) and OCR_LLM_TIMEOUT env var can set this.
```

## 关键符号（行号 → 定义）

```go
    19  type ResolvedEndpoint struct {
    77  type ResolveOptions struct {
    83  func ResolveEndpoint(configPath string) (ResolvedEndpoint, error) {
    89  func ResolveEndpointWithModelOverride(configPath, modelOverride string) (ResolvedEndpoint, error) {
    96  func ResolveEndpointWithOptions(configPath string, opts ResolveOptions) (ResolvedEndpoint, error) {
   155  type envOverrides struct {
   161  func parseEnvOverrides() (envOverrides, error) {
   162  	var env envOverrides
   163  	var err error
   179  func finalizeResolvedEndpoint(source string, ep ResolvedEndpoint, env envOverrides) ResolvedEndpoint {
   203  func parseTimeoutEnv() (time.Duration, bool, error) {
   221  func validateTimeoutSec(sec int) (time.Duration, error) {
   241  func errBedrockNotConfigurable(key string) error {
   247  func tryOCREnv(modelOverride string) (ResolvedEndpoint, bool, error) {
   282  	var authHeader string
   284  		var err error
   298  type llmFileConfig struct {
   313  type providerEntryConfig struct {
   334  type configFile struct {
   343  func tryOCRConfig(path string, opts ResolveOptions) (ResolvedEndpoint, bool, error) {
   352  	var cfg configFile
   371  func tryProviderConfig(cfg configFile, modelOverride string) (ResolvedEndpoint, bool, error) {
   374  	var entry providerEntryConfig
   375  	var ok bool
   426  	var url, protocol, authHeader, model string
   427  	var extraBody map[string]any
   493  	var availableModels []string
   527  		var err error
   596  func tryLegacyLlmConfig(cfg configFile, modelOverride string) (ResolvedEndpoint, bool, error) {
   649  	var authHeader string
   651  		var err error
   698  func tryCCEnv(modelOverride string) (ResolvedEndpoint, bool, error) {
   716  func tryShellRC(modelOverride string) (ResolvedEndpoint, bool, error) {
   727  func shellRCFiles() []string {
   738  	var valid []string
   747  var exportRe = regexp.MustCompile(`^export\s+(ANTHROPIC_\w+)\s*=\s*(?:"([^"]*)"|'([^']*)'|(.+))\s*$`)
   749  var modelSuffixRe = regexp.MustCompile(`\[\d+m\]$`)
   751  func stripModelSuffix(model string) string {
   755  func parseShellRC(path, modelOverride string) (ResolvedEndpoint, bool, error) {
   761  	var baseURL, token, model string
   801  func defaultAuthHeader(protocol string) string {
   810  func ModelListContains(models []string, target string) bool {
   822  func NormalizeAuthHeader(header string) (string, error) {
   840  var reservedHeaders = map[string]bool{
   851  func ParseExtraHeaders(raw string) (map[string]string, error) {
   889  func splitHeaderPairs(raw string) ([]string, error) {
   890  	var pairs []string
   891  	var sb strings.Builder
   915  func ensureMessagesSuffix(rawURL string) string {
   935  func sanitizeRetryCodes(codes []int) (filtered []int, warnings []string, err error) {
   953  func ParseRetryCodes(raw string) ([]int, []string, error) {
```
