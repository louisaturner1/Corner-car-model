import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def compute_performance_metrics(df):
    metrics = {}
    
    # Ride comfort: Root mean square of sprung acceleration 
    accel_key = 'filtered_acceleration_ms2' if 'filtered_acceleration_ms2' in df.columns else 'sprung_acceleration_ms2'
    metrics['rms_acceleration_ms2'] = float(np.sqrt(np.mean(df[accel_key]**2)))
    
    # Suspension & Travel Limits: Peak absolute suspension travel
    if 'suspension_displacement_m' in df.columns:
        metrics['max_suspension_disp_m'] = float(np.max(np.abs(df['suspension_displacement_m'])))
    else:
        metrics['max_suspension_disp_m'] = 0
        
    # 3. Handling: Peak sprung acceleration
    metrics['peak_acceleration_ms2'] = float(np.max(np.abs(df[accel_key])))
    
    return metrics

def generate_evaluation_plots(df, output_dir="data/processed"):
    """
    Generates professional 2-panel engineering plots comparing road profile,
    body displacement, and sprung acceleration over time.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    time = df['time_s'].values
    
    # Set up matplotlib figure style
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Plot 1: Elevation & Displacements
    if 'road_elevation_m' in df.columns:
        ax1.plot(time, df['road_elevation_m'] * 100, label='Road Profile ($z_r$ - cm)', color='tab:green', linestyle='--')
    if 'sprung_displacement_m' in df.columns:
        ax1.plot(time, df['sprung_displacement_m'] * 100, label='Sprung mass displacement ($z_s$ - cm)', color='tab:blue', linewidth=2)
    if 'unsprung_displacement_m' in df.columns:
        ax1.plot(time, df['unsprung_displacement_m'] * 100, label='Unsprung mass displacement ($z_u$ - cm)', color='tab:red', alpha=0.7)
        
    ax1.set_ylabel('Displacement / Height (cm)')
    ax1.set_title('2-DOF quarter car simulation: Kinematic response')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right')
    
    # Plot 2: Acceleration 
    accel_col = 'filtered_acceleration_ms2' if 'filtered_acceleration_ms2' in df.columns else 'sprung_acceleration_ms2'
    ax2.plot(time, df[accel_col], label=f'Sprung Acceleration ({accel_col.replace("_", " ")})', color='tab:yellow', linewidth=1.5)
    
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Acceleration ($m/s^2$)')
    ax2.set_title('Chassis vertical acceleration (Ride comfort)')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    
    plot_file = out_path / "simulation_performance_plot.png"
    plt.savefig(plot_file, dpi=300)
    plt.close()
    print(f"7. Evaluation plot successfully saved to {plot_file}")

def evaluate_pipeline(input_path="data/processed/filtered_telemetry.csv"):
    """
    Loads telemetry, calculates evaluation metrics, prints an engineering report, and plots results.
    """
    file_path = Path(input_path)
    if not file_path.exists():
        file_path = Path("data/processed/simulation_telemetry.csv")
        if not file_path.exists():
            raise FileNotFoundError(f"Error: No telemetry data found. Run dynamics.py first.")
            
    print(f"8. Loading telemetry for evaluation from {file_path}")
    df = pd.read_csv(file_path)
    
    metrics = compute_performance_metrics(df)
    print("\n" + "="*50)
    print(" VEHICLE DYNAMICS PERFORMANCE & EVALUATION REPORT")
    print("="*50)
    print(f"9. RMS sprung acceleration (Ride comfort): {metrics['rms_acceleration_ms2']:.4f} m/s^2")
    print(f"10. Peak sprung acceleration:               {metrics['peak_acceleration_ms2']:.4f} m/s^2")
    print(f"11. Max Absolute Suspension Travel:         {metrics['max_suspension_travel_m']*1000:.2f} mm")
    print("="*50 + "\n")
    
    generate_evaluation_plots(df)  
    return metrics

if __name__ == "__main__":
    evaluate_pipeline()
