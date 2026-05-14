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

The script writes generated Swift files into the repository root and benchmarks each one with:

```sh
xcrun swiftc -typecheck <file>.swift
```

## Examples

| Example | What it compares |
| --- | --- |
| `0` | Different ways to initialize `String` values. |
| `1` | Passing a `ViewModel` with an explicit type name versus shorthand `.init(...)`. |
| `2` | Different ways to initialize and annotate `ViewModel` values. |

## Generated Files

Running the benchmark creates temporary files named `a.swift`, `b.swift`, `c.swift`, and `d.swift`, depending on the selected example. These files are ignored by Git.

To remove them manually:

```sh
rm -f a.swift b.swift c.swift d.swift
```
