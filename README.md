# Swift Type Checking Benchmarks

Small Swift type-checking benchmarks focused on compile-time type inference, overload resolution, and constraint-solver performance.

The original script comes from this [Swift Forums discussion](https://forums.swift.org/t/regarding-swift-type-inference-compile-time-performance/49748/3).

## Requirements

- macOS with Xcode or the Xcode Command Line Tools installed
- `xcrun swiftc`
- Python 3
- [`hyperfine`](https://github.com/sharkdp/hyperfine)

Install `hyperfine` with Homebrew:

```sh
brew install hyperfine
```

## Usage

```sh
python3 run.py <benchmark_number> <number_of_iterations> [--warmup N] [--runs N]
```

For example:

```sh
python3 run.py 1 100
```

To run each variant with 3 warmup runs and exactly 20 timed runs:

```sh
python3 run.py 4 300 --warmup 3 --runs 20
```

The script writes all generated Swift files for the selected benchmark into the repository root, then benchmarks them together with one `hyperfine` run. Each generated file is checked with:

```sh
xcrun swiftc -typecheck <file>.swift
```

The `hyperfine` output uses command names such as `inferred flatMap closure/result (a.swift)` and `explicit flatMap closure/result (b.swift)` so the summary identifies which variant was faster.

## Observed Results

These results are from one local run. They are useful for comparing the benchmark variants on this machine, but they are not universal Swift performance rules.

Benchmark protocol:

```sh
python3 run.py <example> 300 --warmup 1 --runs 10
```

Environment:

| Field | Value |
| --- | --- |
| Date | 2026-05-14 |
| Machine | Apple M1 Pro |
| CPU count | 8 |
| Memory | 32 GiB |
| OS | macOS 26.3.1 (25D771280a) |
| Swift | Apple Swift 6.3 (`swiftlang-6.3.0.123.5 clang-2100.0.123.102`) |
| Target | `arm64-apple-macosx26.0` |
| hyperfine | 1.19.0 |

Results:

| Example | Inferred / shorthand | Explicit | Result |
| --- | --- | --- | --- |
| `0` | `let a = "hello, world!"` — 130.4 ms | `let c: String = .init(...)` — 226.3 ms | Inferred was 1.73x faster. |
| `1` | `doSomething(viewModel: .init(...))` — 151.5 ms | `doSomething(viewModel: ViewModel(...))` — 167.5 ms | Inferred was 1.11x faster. |
| `2` | inferred `flatMap` closure/result — 3.829 s | explicit closure/result types — 391.0 ms | Explicit was 9.79x faster. |
| `3` | shorthand `.init` in overloaded expression — 5.650 s | explicit `IntPayload(...)` — 346.1 ms | Explicit was 16.33x faster. |
| `4` | `score(.init(...))` — 1.392 s | `score(ViewModel(...))` — 320.5 ms | Explicit was 4.34x faster. |

Interpretation: simple initializer and annotation forms are often close, and small differences can change between runs. The largest effects appear when annotations remove meaningful solver ambiguity: closure parameter/return types, overloaded calls, and contextual shorthand `.init`.
