# 源码节选（自动生成，非完整文件）

- 源文件: `open-code-review/internal/telemetry/provider.go`
- 总行数: 85 | 节选: 头部 30 行 + 4 个关键符号
- 完整源码见 `open-code-review/`（同留档目录）

## 文件头

```go
// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

package telemetry

import (
	"context"
	"fmt"
	"os"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/propagation"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

// Global OTel providers. Set by Init, used via otel.GetTracerProvider() / otel.GetMeterProvider().
var (
	tracerProvider *sdktrace.TracerProvider
	meterProvider  *sdkmetric.MeterProvider
	shutdownFuncs  []func(context.Context) error
	initialized    bool
)

// serviceName holds the name set during Init.
var serviceName = "open-code-review"

// Init initializes global TracerProvider and MeterProvider based on
// environment variables and optional config file. Returns true when enabled.
```

## 关键符号（行号 → 定义）

```go
    27  var serviceName = "open-code-review"
    32  func Init(ctx context.Context) bool {
    73  func IsEnabled() bool {
    78  func ContentLogging() bool {
```
