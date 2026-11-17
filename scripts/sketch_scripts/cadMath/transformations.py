import cadquery as cq
import numpy as np


def transform_vector(x_rad, y_rad, z_rad, vector, type="extrinsic"):
  x = np.array([[1, 0, 0], [0, np.cos(x_rad), -np.sin(x_rad)], [0, np.sin(x_rad), np.cos(x_rad)]])
  y = np.array([[np.cos(y_rad), 0, np.sin(y_rad)], [0, 1, 0], [-np.sin(y_rad), 0, np.cos(y_rad)]])
  z = np.array([[np.cos(z_rad), -np.sin(z_rad), 0], [np.sin(z_rad), np.cos(z_rad), 0], [0, 0, 1]])

  if (type == "extrinsic"):
    rotated = z @ y @ x @ vector
  else:
    rotated = x @ y @ z @ vector
    
  rotated[np.abs(rotated) < np.exp(-10)] = 0
  return cq.Vector(tuple(rotated))
