#!/usr/bin/env python3
import argparse
import subprocess

VIEW_MODEL_PRELUDE = """
struct ViewModel {
    let value: String
}
func doSomething(viewModel: ViewModel) -> String {
    return viewModel.value
}
"""

VIEW_MODEL_OVERLOAD_PRELUDE = """
struct ViewModel {
    let value: Int
    let name: String
}
struct PreviewViewModel {
    let value: Int
    let name: String
}
struct LegacyViewModel {
    let value: Int
    let name: String
}
func score(_ model: ViewModel) -> Int {
    return model.value
}
func score(_ model: PreviewViewModel) -> Int16 {
    return Int16(model.value)
}
func score(_ model: LegacyViewModel) -> Double {
    return Double(model.value)
}
"""

AMBIGUOUS_INIT_PRELUDE = """
struct IntPayload {
    let value: Int
    let name: String
}
struct Int8Payload {
    let value: Int
    let name: String
}
struct Int16Payload {
    let value: Int
    let name: String
}
struct Int32Payload {
    let value: Int
    let name: String
}
struct Int64Payload {
    let value: Int
    let name: String
}
struct DoublePayload {
    let value: Int
    let name: String
}
func choose(_ payload: IntPayload) -> Int {
    return payload.value
}
func choose(_ payload: Int8Payload) -> Int8 {
    return Int8(payload.value)
}
func choose(_ payload: Int16Payload) -> Int16 {
    return Int16(payload.value)
}
func choose(_ payload: Int32Payload) -> Int32 {
    return Int32(payload.value)
}
func choose(_ payload: Int64Payload) -> Int64 {
    return Int64(payload.value)
}
func choose(_ payload: DoublePayload) -> Double {
    return Double(payload.value)
}
"""

OVERLOADED_INIT_PRELUDE = """
struct Quantity {
    let value: Int

    init(_ value: Int) {
        self.value = value
    }

    init(_ value: Int8) {
        self.value = Int(value)
    }

    init(_ value: Int16) {
        self.value = Int(value)
    }

    init(_ value: Int32) {
        self.value = Int(value)
    }

    init(_ value: Double) {
        self.value = Int(value)
    }
}
func measure(_ quantity: Quantity) -> Int {
    return quantity.value
}
"""

OVERLOADED_LITERAL_PRELUDE = """
func total(_ values: [Int]) -> Int {
    return values.reduce(0, +)
}
func total(_ values: [Int8]) -> Int8 {
    return values.reduce(0, +)
}
func total(_ values: [Int16]) -> Int16 {
    return values.reduce(0, +)
}
func total(_ values: [Int32]) -> Int32 {
    return values.reduce(0, +)
}
func total(_ values: [Double]) -> Double {
    return values.reduce(0, +)
}
"""

EXAMPLES = {
    "contextual-init": {
        "summary": "shorthand .init with a concrete function-argument context",
        "prelude": VIEW_MODEL_PRELUDE,
        "variants": [
            (
                "explicit ViewModel initializer argument",
                "a",
                'let a{} = doSomething(viewModel: ViewModel(value: "test"))',
            ),
            (
                "shorthand .init argument",
                "b",
                'let b{} = doSomething(viewModel: .init(value: "test"))',
            ),
        ],
    },
    "flatmap-chain": {
        "summary": "closure parameter and result inference through flatMap/reduce",
        "prelude": "",
        "variants": [
            (
                "inferred flatMap closure/result",
                "a",
                'let a{} = [1, 2, 3].flatMap {{ value in [value, value + 1] }}.reduce(0, +)',
            ),
            (
                "explicit flatMap closure/result",
                "b",
                'let b{}: Int = [1, 2, 3].flatMap {{ (value: Int) -> [Int] in [value, value + 1] }}.reduce(0, +)',
            ),
        ],
    },
    "overloaded-payload-init": {
        "summary": "shorthand .init while resolving overloaded payload/result types",
        "prelude": AMBIGUOUS_INIT_PRELUDE,
        "variants": [
            (
                "explicit initializer in numeric overload",
                "a",
                'let a{} = choose(IntPayload(value: 1, name: "test")) + choose(IntPayload(value: 2, name: "test")) + 1',
            ),
            (
                "shorthand .init in numeric overload",
                "b",
                'let b{} = choose(.init(value: 1, name: "test")) + choose(.init(value: 2, name: "test")) + 1',
            ),
        ],
    },
    "overloaded-model-init": {
        "summary": "shorthand .init in overloaded model scoring calls",
        "prelude": VIEW_MODEL_OVERLOAD_PRELUDE,
        "variants": [
            (
                "explicit ViewModel initializer",
                "a",
                'let a{} = score(ViewModel(value: 1, name: "test")) + score(ViewModel(value: 2, name: "test")) + 1',
            ),
            (
                "shorthand .init ViewModel",
                "b",
                'let b{} = score(.init(value: 1, name: "test")) + score(.init(value: 2, name: "test")) + 1',
            ),
        ],
    },
    "overloaded-inits": {
        "summary": "one nominal type with several initializer overloads",
        "prelude": OVERLOADED_INIT_PRELUDE,
        "variants": [
            (
                "shorthand .init with overloaded initializers",
                "a",
                'let a{} = measure(.init(1)) + measure(.init(2)) + measure(.init(3))',
            ),
            (
                "explicit Quantity initializer and Int literals",
                "b",
                'let b{} = measure(Quantity(Int(1))) + measure(Quantity(Int(2))) + measure(Quantity(Int(3)))',
            ),
        ],
    },
    "overloaded-literals": {
        "summary": "overloaded array and numeric literals",
        "prelude": OVERLOADED_LITERAL_PRELUDE,
        "variants": [
            (
                "inferred overloaded array literals",
                "a",
                'let a{} = total([1, 2, 3]) + total([4, 5, 6]) + 1',
            ),
            (
                "explicit Int array literals",
                "b",
                'let b{}: Int = total([Int(1), Int(2), Int(3)]) + total([Int(4), Int(5), Int(6)]) + 1',
            ),
        ],
    },
}


def positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def non_negative_int(value):
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be at least 0")
    return parsed


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Swift type-checking benchmarks and compare them with hyperfine."
    )
    parser.add_argument("example_name", nargs="?", choices=sorted(EXAMPLES.keys()))
    parser.add_argument("number_of_iterations", nargs="?", type=positive_int)
    parser.add_argument(
        "--list",
        action="store_true",
        help="list available benchmark names and exit",
    )
    parser.add_argument(
        "--warmup",
        type=non_negative_int,
        default=1,
        help="number of hyperfine warmup runs before timing each command (default: 1)",
    )
    parser.add_argument(
        "--runs",
        type=positive_int,
        help="exact number of timed hyperfine runs for each command",
    )
    args = parser.parse_args()

    if args.list:
        for name, example in EXAMPLES.items():
            print("{}: {}".format(name, example["summary"]))
        raise SystemExit(0)

    if args.example_name is None:
        parser.error("the following argument is required: example_name")

    if args.number_of_iterations is None:
        parser.error("the following argument is required: number_of_iterations")

    return args


def write_swift_file(filename, prelude, code, number_of_iterations):
    with open(filename + ".swift", "w") as f:
        f.write(prelude)
        if prelude and not prelude.endswith("\n"):
            f.write("\n")

        for j in range(number_of_iterations):
            f.write((code + "\n").format(j))


def main():
    args = parse_args()
    example = EXAMPLES[args.example_name]
    commands = []
    command_names = []

    for (label, filename, code) in example["variants"]:
        benchmark_label = "{} ({}.swift)".format(label, filename)
        write_swift_file(filename, example["prelude"], code, args.number_of_iterations)
        print("Generated:", benchmark_label, "=>", code.format("{}"), flush=True)
        command_names.extend(["--command-name", benchmark_label])
        commands.append("xcrun swiftc -typecheck {}".format(filename + ".swift"))

    hyperfine_args = ["hyperfine", "--warmup", str(args.warmup)]
    if args.runs is not None:
        hyperfine_args.extend(["--runs", str(args.runs)])

    subprocess.run([*hyperfine_args, *command_names, *commands], check=True)


if __name__ == "__main__":
    main()
