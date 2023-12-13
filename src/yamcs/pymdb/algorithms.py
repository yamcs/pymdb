from dataclasses import dataclass


@dataclass
class JavaAlgorithm:
    java: str


hex = JavaAlgorithm("org.yamcs.algo.Hex")

remaining_binary = JavaAlgorithm("org.yamcs.algo.RemainingBinaryDecoder")
