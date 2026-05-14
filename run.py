#!/usr/bin/env python3
import os
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

for (i, filename) in enumerate(filenames):
    with open(filename + ".swift", "w") as f:
        s = ""
        s += """
struct ViewModel {
    let value: String
}
func doSomething(viewModel: ViewModel) -> String {
    return viewModel.value
}
"""
        for j in range(number_of_iterations):
            s += (code[i] + '\n').format(j)
        f.write(s)
    print("Benchmarking:", code[i])
    os.system("hyperfine --warmup 1 'xcrun swiftc -typecheck {}'".format(filename + ".swift"))
