# Imports and initiallisation 
import argparse
import numpy as np
import pandas as pd
from scipy.intergrate import solve_ivp # Solve initial value problems
from scipy.interpolate import interp1d # 1-D interpolation function
from pathlib import Path # Object-oriented way to handle file and folder paths in python

def parse_arguments():
  """Command line inputs for simulation configurations"""
  parser = arg.parse.ArgumentParser(description="Run two-degree-freedom quarter-car suspension simulation.")
  
  parser.add.argument('--road_file', type=str, default="data/raw/sample_road_profile.csv",
    help="Path to the csv file, containing road distance and elevation.") # Input file configuration

  # Vehicle physical parameters in SI units
  parser.add_argument('--m_s', type=float, default=250.0, help="Sprung mass (kg)")
  parser.add_argument('--m_u', type=float, default=35.0, help="Unsprung mass (kg)")
  parser.add_argument('--k_s', type=float, default=15000.0, help="Suspension spring stiffness (N/m)")
  parser.add_argument('--c_s', type=float, default=1000.0, help="Suspension damping coefficient (N*s/m)")
  parser.add_argument('--k_t', type=float, default=200000.0, help="Tire stiffness (N/m)")
  parser.add_argument('--v_car', type=float, default=20.0, help="Vehicle forward velocity (m/s)")
    
  return parser.parse_args()

def load_or_generate_road_profile(file_path):
  """Loads a road profile from the given path or generates a sysntheitc bump profile if missing."""
  raw_path = Path(file_path)

  if raw_path.exists():
    df = pd.read_csv(raw_path)
    return df['distance_m'].values, df['elevation_m'].values
  else:
    print(f"1. Notice: Road profile at '{raw_path}' not found.
    2. Generating synthetic road profile...")
    distance = np.linspace(0,50,1000)
    elevationn = 0.05*np.exp(-((distance-10)**2)/1) # 5cm simulation bump

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({'distance_m': distance, 'elevation_m': elevation}).to_csv(raw_path, index=False)
    return distance, elevation

def quarter_car_ode(t,y,road_interpolator,p):
  z_s, v_s, z_u, v_u = y

  x = p['v_car']*t
  z_r = road_interpolator(x)

  # Functions
  f_spring = p['k_s']*(z_u-z_s)
  f_damper = p['c_s']*(v_u-v_s)
  f_tire = p['k_t']*(z_r-z_u)

  a_s = (f_spring+f_damper)/p['m_s']
  a_u = (f_tire-f_spring-f_damper)/p['m_u']
  return [v_s, a_s, v_u, a_u]

def run_simulation():
  args = parse_arguments()
  params = {
    'm_s': args.m_s,
    'm_u': args.m_u,
    'k_s': args.k_s,
    'c_s': args.c_s,
    'k_t': args.k_t,
    'v_car': args.v_car,
  }
  print(f"3. Starting quarter-car simulation (Speed: {params['v_car']} m/s, Spring rate: {params['k_s']} N/m)...")

  distance, elevation = load_or_generate_road_profile(args.road_file)
  road_interpolator = interp1d(distance, elevation, bounds_error=False, fill_value=0)

  t_max = distance[-1]/params['v_car']
  t_eval = np.linspace(0,t_max,len(distance))
  y_0 = [0,0,0,0]

  sol = solve_ivp(
    fun=lambda t,y: quarter_car_ode(t,y,road_interpolator,params),
    t_span=(0,t_max),
    y_0=y_0,
    t_eval=t_eval,
    method='RK45'
  )

time = sol.t
z_s, v_s, z_u, v_u = sol.y

accelerations = []
for i in range(len(time)):
  t = time[i]
  f_s = params['k_s']*(z_u[i]-z_s[i])+params['c_s']*(v_u[i]-v_s[i])
  a_s = f_s/params['m_s']
  accelerations.append(a_s)

output_df = pd.DataFrame({
  'time_s': time,
  'road_elevation_m': [road_interpolator(params['v_car']*t) for t in time],
  'sprung_displacement_m': z_s,
  'sprung_accerlation_ms2': accelerations,
  'unsprung_displacement_m': z_u,
  'suspension_displacement_m': z_u-z_s,
})

rms_accel = np.sort(np.mean(np.array(accelerations)**2))
print(f"4. Simulation complete. RMS sprung acceleration: {rms_accel:.4f} m/s^2")

output_dir = Path("data/processed") # Saving processed outputs
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir/"simulation_telemetry.csv"
output_df.to_csv(output_path, index=False)
print(f"5. Telemetry successfully saved to {output_path}")

if __name__ == "__main__":
  run_simulation()

  
