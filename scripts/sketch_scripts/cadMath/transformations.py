import cadquery as cq
import numpy as np


def transform_vector(x_rad, y_rad, z_rad, vector, type="extrinsic"):
  # cq.Matrix
  x = np.array([[1, 0, 0], [0, np.cos(x_rad), -np.sin(x_rad)], [0, np.sin(x_rad), -np.cos(x_rad)]])
  y = np.array([[np.cos(y_rad), 0, np.sin(y_rad)], [0, 1, 0], [-np.sin(y_rad), 0, np.cos(y_rad)]])
  z = np.array([[np.cos(z_rad), -np.sin(z_rad), 0], [np.sin(z_rad), np.cos(z_rad), 0], [0, 0, 1]])

  intrinsic_rotation = x @ y @ z
  extrinsic_rotation = z @ y @ x

  if (type == "extrinsic"):
    rotated = z @ y @ x @ vector
  else:
    rotated = x @ y @ z @ vector
    
  rotated[np.abs(rotated) < np.exp(-10)] = 0
  return cq.Vector(tuple(rotated))


def get_new_workplane(plane: cq.Plane):
  plane_rx = np.deg2rad(plane.location.toTuple()[1][0])
  plane_ry = np.deg2rad(plane.location.toTuple()[1][1])
  plane_rz = np.deg2rad(plane.location.toTuple()[1][2])

  plane_tx = plane.location.toTuple()[0][0]
  plane_ty = plane.location.toTuple()[0][1]
  plane_tz = plane.location.toTuple()[0][2]

  new_origin = cq.Vector(plane_tx, plane_ty, plane_tz)
  new_normal = transform_vector(plane_rx, plane_ry, plane_rz, np.array([0, 0, 1]), type="extrinsic").normalized()

  return cq.Workplane(cq.Plane(origin=new_origin, normal=new_normal))
