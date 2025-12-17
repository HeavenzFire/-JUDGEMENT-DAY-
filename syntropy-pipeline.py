#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import argparse
import os

# Deterministic seed
np.random.seed(42)

def parse_args():
    parser = argparse.ArgumentParser(description="Syntropy Pipeline")
    parser.add_argument("--output", type=str, default="pipeline_output.png",
                        help="Path to save output plot")
    parser.add_argument("--length", type=int, default=1024,
                        help="Length of synthetic signal")
    return parser.parse_args()

def main():
    args = parse_args()

    # Generate synthetic signal
    signal = np.random.randn(args.length)

    # FFT Analysis
    spectrum = fft(signal)

    # Save spectrum plot
    os.makedirs("outputs", exist_ok=True)
    output_path = os.path.join("outputs", args.output)
    plt.plot(np.abs(spectrum))
    plt.title("Syntropy Pipeline FFT Output")
    plt.xlabel("Frequency Bin")
    plt.ylabel("Amplitude")
    plt.savefig(output_path)
    plt.close()
    print(f"Pipeline executed successfully. Output saved to {output_path}")

if __name__ == "__main__":
    main()