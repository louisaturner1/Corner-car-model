import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from pathlib import Path

def butter_lowpass(cutoff_hz, fs, order=4):
  """ Designs a digital butterworth low pass filter.

  Parameters:
    cutoff_hz: float, hz
    fs: float, sampling frequency in hz
    order: int, default
  """
  nyquist_freq = 0.5*fs
  normal_cutoff = cutoff_hz/nyquist_freq
  b,a = butter(order, normal_cutoff, btype='low', analog=False)
  return b,a

def apply_lowpass_filter(data, cutoff_hz=15, fs=50, order=4):
  b,a = butter_lowpass(cutoff_hz, fs, order=order)
  filtered_data = filtfilt(b,a,data)
  return filtered_data

def process_telemetry_file(input_path="data/processed/simulation_telemetry.csv",
                           output_path="data/processed/filtered_telemetry.csv",
                           cutoff_hz=15):
  file_path = Path(input_path)
  if not file_path.exists():
    raise FileNotFoundError(f"Error: Input file '{file_path}' not found. Run dynamics.py first")
  df = pd.read_csv(file_path)

  time_steps = np.diff(df['time_s'].values)
  mean_dt = np.mean(time_steps)
  fs = 1/mean_dt if mean_dt > 0 else 50
  print(f"5. Processing signal: Estimated sampling frequency = {fs:.2f} Hz, Cutoff = {cutoff_hz} Hz")

  if 'sprung_acceleration_ms2' in df.columns:
    raw_accel = df['sprung_acceleration_ms2'].values
    df['filtered_acceleration_ms2'] = apply_lowpass_filter(raw_accel, cutoff_hz=cutoff_hz, fs=fs)

  out_file = Path(output_path)
  out_file.parent.mkdir(parents=True, exist_ok=True)
  df.to_csv(out_file, index=False)
  print(f"6. Filtered telemetry sucessfully saved to {out_file}")
  return df

if __name__ = "__main__":
  process_telemetry_file()
