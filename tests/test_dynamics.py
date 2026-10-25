import numpy as np
import pytest
from pathlib import Path
from src.dynamics import quarter_car_ode, load_or_generate_road_profile

def test_road_profile_generation():
    """Verify validity"""
    distance, elevation = load_or_generate_road_profile("data/raw/sample_road_profile.csv")
    
    # Assertions
    assert len(distance) > 0, "Distance array should not be empty."
    assert len(elevation) == len(distance), "Elevation array length must match distance array."
    assert isinstance(distance, np.ndarray), "Distance should be a numpy ndarray."
    assert isinstance(elevation, np.ndarray), "Elevation should be a numpy ndarray."

def test_quarter_car_ode_equilibrium():
    """Verify zeros."""
    # Create a dummy road interpolator that returns flat ground 
    class FlatRoadInterpolator:
        def __call__(self, x):
            return 0.0

    params = {
        'm_s': 250.0,
        'm_u': 35.0,
        'k_s': 15000.0,
        'c_s': 1000.0,
        'k_t': 200000.0,
        'v_car': 20.0
    }
    
    # At rest
    y_at_rest = [0.0, 0.0, 0.0, 0.0]
    
    derivatives = quarter_car_ode(t=0.0, y=y_at_rest, road_interpolator=FlatRoadInterpolator(), p=params)
    
    # At rest on flat ground, velocities and accelerations must all be exactly zero
    assert len(derivatives) == 4, "ODE must return exactly 4 state derivatives."
    assert all(np.isclose(d, 0.0) for d in derivatives), "System at rest on flat ground should have zero acceleration/velocity derivatives."
