#!/usr/bin/env python3
import os
import sys

if len(sys.argv) < 3:
    print("Usage: python run.py <example_number> <number_of_iteration>")
    sys.exit(1)  # Exit the script with a non-zero status code

filenames = []
example_number = sys.argv[1]
number_of_iteration = sys.argv[2]

if example_number == "0":
    filenames = ["a", "b", "c", "d"]
    code = [
        'let a{} = "hello, world!"',
        'let b{} = String("hello, world!")',
        'let c{}: String = .init("hello, world!")',
        'let d{}: String = "hello, world!"'
    ]
elif example_number == "1":
    filenames = ["a", "b"]
    code = [
        'let a{} = doSomething(viewModel: ViewModel(value: "test"))',
        'let b{} = doSomething(viewModel: .init(value: "test"))'
    ]
elif example_number == "2":
    filenames = ["a", "b", "c", "d"]
    code = [
        'let a{} = ViewModel(value: "test")',
        'let b{}: ViewModel = ViewModel(value: "test")'
        'let c{}: ViewModel = .init(value: "test")'
        'let d{}: ViewModel = ViewModel.init(value: "test")'
    ]

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
        for j in range(int(number_of_iteration)):
            s += (code[i] + '\n').format(j)
        f.write(s)
    print("Benchmarking:", code[i])
    os.system("hyperfine --warmup 1 'xcrun swiftc -typecheck {}'".format(filename + ".swift"))
