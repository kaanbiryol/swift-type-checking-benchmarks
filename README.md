# Type Inference Performance

Small Swift type-checking benchmarks for comparing how different initializer and type annotation styles affect compile-time type inference performance.

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
python3 run.py <example_number> <number_of_iterations>
```

For example:

```sh
python3 run.py 1 100
```

The script writes all generated Swift files for the selected example into the repository root, then benchmarks them together with one `hyperfine` run. Each generated file is checked with:

```sh
xcrun swiftc -typecheck <file>.swift
```

The `hyperfine` output uses command names such as `inferred function result (a.swift)` and `explicit String result (b.swift)` so the summary identifies which variant was faster.

## Examples

| Example | What it compares |
| --- | --- |
| `0` | Different ways to initialize `String` values. |
| `1` | Passing a `ViewModel` with an explicit type name versus shorthand `.init(...)`. |
| `2` | Different ways to initialize and annotate `ViewModel` values. |
| `3` | Simple function result where an explicit annotation adds overhead. |
| `4` | Solver-heavy `map`/`reduce` expression where an explicit result type helps. |
| `5` | `flatMap`/`reduce` expression where explicit closure and result types help. |

## Generated Files

Running the benchmark creates temporary files named `a.swift`, `b.swift`, `c.swift`, and `d.swift`, depending on the selected example. These files are ignored by Git.

To remove them manually:

```sh
rm -f a.swift b.swift c.swift d.swift
```
