import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from pathlib import Path
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Apply low-pass filter to vehicle telemetry.")
    parser.add_argument('--input_file', type=str, default="data/processed/simulation_telemetry.csv",
                        help="Path to raw simulation telemetry CSV.")
    parser.add_argument('--output_file', type=str, default="data/processed/filtered_telemetry.csv",
                        help="Path to save filtered telemetry CSV.")
    parser.add_argument('--cutoff_hz', type=float, default=15.0,
                        help="Low-pass filter cutoff frequency (Hz).")
    return parser.parse_args()

def butter_lowpass(cutoff_hz, fs, order=4):
    """
    Designs a digital Butterworth low-pass filter.
    """
    nyquist_freq = 0.5 * fs
    normal_cutoff = cutoff_hz / nyquist_freq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def apply_lowpass_filter(data, cutoff_hz=15.0, fs=50.0, order=4):
    b, a = butter_lowpass(cutoff_hz, fs, order=order)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

if __name__ == "__main__":
    args = parse_arguments()
    
    file_path = Path(args.input_file)
    if not file_path.exists():
        raise FileNotFoundError(f"Error: Input file '{file_path}' not found. Run dynamics.py first.")
        
    df = pd.read_csv(file_path)

    time_steps = np.diff(df['time_s'].values)
    mean_dt = np.mean(time_steps)
    fs = 1.0 / mean_dt if mean_dt > 0 else 50.0
    print(f"5. Processing signal: Estimated sampling frequency = {fs:.2f} Hz, Cutoff = {args.cutoff_hz} Hz")

    if 'sprung_acceleration_ms2' in df.columns:
        raw_accel = df['sprung_acceleration_ms2'].values
        df['filtered_acceleration_ms2'] = apply_lowpass_filter(raw_accel, cutoff_hz=args.cutoff_hz, fs=fs)

    out_file = Path(args.output_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)
    print(f"6. Filtered telemetry successfully saved to {out_file}")
