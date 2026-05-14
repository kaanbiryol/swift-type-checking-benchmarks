#!/usr/bin/env python3
import subprocess
import sys

EXAMPLES = {
    "0": (
        ["a", "b", "c", "d"],
        [
            'let a{} = "hello, world!"',
            'let b{} = String("hello, world!")',
            'let c{}: String = .init("hello, world!")',
            'let d{}: String = "hello, world!"'
        ],
    ),
    "1": (
        ["a", "b"],
        [
            'let a{} = doSomething(viewModel: ViewModel(value: "test"))',
            'let b{} = doSomething(viewModel: .init(value: "test"))'
        ],
    ),
    "2": (
        ["a", "b", "c", "d"],
        [
            'let a{} = ViewModel(value: "test")',
            'let b{}: ViewModel = ViewModel(value: "test")',
            'let c{}: ViewModel = .init(value: "test")',
            'let d{}: ViewModel = ViewModel.init(value: "test")'
        ],
    ),
    "3": (
        ["a", "b"],
        [
            'let a{} = doSomething(viewModel: ViewModel(value: "test"))',
            'let b{}: String = doSomething(viewModel: ViewModel(value: "test"))'
        ],
    ),
    "4": (
        ["a", "b"],
        [
            'let a{} = [1, 2, 3, 4, 5].map {{ numericOverloaded($0) + 1 }}.reduce(0, +)',
            'let b{}: Int = [1, 2, 3, 4, 5].map {{ numericOverloaded($0) + 1 }}.reduce(0, +)'
        ],
    ),
    "5": (
        ["a", "b"],
        [
            'let a{} = [1, 2, 3].flatMap {{ value in [value, value + 1] }}.reduce(0, +)',
            'let b{}: Int = [1, 2, 3].flatMap {{ (value: Int) -> [Int] in [value, value + 1] }}.reduce(0, +)'
        ],
    ),
}

LABELS = {
    "0": [
        "inferred string literal",
        "String initializer",
        "explicit String .init",
        "explicit String literal",
    ],
    "1": [
        "explicit ViewModel initializer argument",
        "shorthand .init argument",
    ],
    "2": [
        "inferred ViewModel initializer",
        "explicit ViewModel annotation",
        "explicit annotation with .init",
        "explicit ViewModel.init call",
    ],
    "3": [
        "inferred function result",
        "explicit String result",
    ],
    "4": [
        "inferred overloaded map/reduce",
        "explicit Int result",
    ],
    "5": [
        "inferred flatMap closure/result",
        "explicit flatMap closure/result",
    ],
}


def usage():
    examples = ", ".join(EXAMPLES.keys())
    print("Usage: python3 run.py <example_number> <number_of_iterations>")
    print(f"Available examples: {examples}")


if len(sys.argv) != 3:
    usage()
    sys.exit(1) 

example_number = sys.argv[1]
if example_number not in EXAMPLES:
    usage()
    sys.exit(1)

try:
    number_of_iterations = int(sys.argv[2])
except ValueError:
    usage()
    sys.exit(1)

if number_of_iterations < 1:
    print("number_of_iterations must be at least 1")
    sys.exit(1)

filenames, code = EXAMPLES[example_number]
labels = LABELS[example_number]
if len(filenames) != len(code) or len(filenames) != len(labels):
    print("example metadata is inconsistent")
    sys.exit(1)

commands = []
benchmark_labels = []

for (i, filename) in enumerate(filenames):
    label = "{} ({}.swift)".format(labels[i], filename)
    benchmark_labels.append(label)
    with open(filename + ".swift", "w") as f:
        s = ""
        s += """
struct ViewModel {
    let value: String
}
func doSomething(viewModel: ViewModel) -> String {
    return viewModel.value
}
func numericOverloaded(_ value: Int) -> Int {
    return value
}
func numericOverloaded(_ value: Int8) -> Int8 {
    return value
}
func numericOverloaded(_ value: Int16) -> Int16 {
    return value
}
func numericOverloaded(_ value: Int32) -> Int32 {
    return value
}
func numericOverloaded(_ value: Int64) -> Int64 {
    return value
}
func numericOverloaded(_ value: UInt) -> UInt {
    return value
}
func numericOverloaded(_ value: UInt8) -> UInt8 {
    return value
}
func numericOverloaded(_ value: UInt16) -> UInt16 {
    return value
}
func numericOverloaded(_ value: UInt32) -> UInt32 {
    return value
}
func numericOverloaded(_ value: UInt64) -> UInt64 {
    return value
}
func numericOverloaded(_ value: Float) -> Float {
    return value
}
func numericOverloaded(_ value: Double) -> Double {
    return value
}
"""
        for j in range(number_of_iterations):
            s += (code[i] + '\n').format(j)
        f.write(s)
    print("Generated:", label, "=>", code[i].format("{}"), flush=True)
    commands.append("xcrun swiftc -typecheck {}".format(filename + ".swift"))

command_names = []
for label in benchmark_labels:
    command_names.extend(["--command-name", label])

subprocess.run(["hyperfine", "--warmup", "1", *command_names, *commands], check=True)
