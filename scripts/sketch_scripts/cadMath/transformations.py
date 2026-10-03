import cadquery as cq
import numpy as np


def transform_vector(x_rad, y_rad, z_rad, vector, type="extrinsic"):
  # cq.Matrix
  x = np.array([[1, 0, 0], [0, np.cos(x_rad), -np.sin(x_rad)], [0, np.sin(x_rad), -np.cos(x_rad)]])
  y = np.array([[np.cos(y_rad), 0, np.sin(y_rad)], [0, 1, 0], [-np.sin(y_rad), 0, np.cos(y_rad)]])
  z = np.array([[np.cos(z_rad), -np.sin(z_rad), 0], [np.sin(z_rad), np.cos(z_rad), 0], [0, 0, 1]])

  if (type == "extrinsic"):
    rotated = z @ y @ x @ vector
  else:
    rotated = x @ y @ z @ vector
    
  rotated[np.abs(rotated) < np.exp(-10)] = 0
  return cq.Vector(tuple(rotated))


def get_new_workplane(location_obj: cq.Plane | cq.Location):
  if (isinstance(location_obj, cq.Plane)):
    # print(f"location_obj is a Plane object: {location_obj.location.toTuple()}")
    plane = location_obj.location
  else:
    # print(f"location_obj is a Location object: {location_obj.toTuple()}")
    plane = location_obj

  # plane = location_obj.location if isinstance(location_obj, cq.Plane) else location_obj
  # print(f"Fetching workplane for location: {plane.toTuple()}")
  plane_rx = np.deg2rad(plane.toTuple()[1][0]) 
  plane_ry = np.deg2rad(plane.toTuple()[1][1]) 
  plane_rz = np.deg2rad(plane.toTuple()[1][2]) 

  plane_tx = plane.toTuple()[0][0]
  plane_ty = plane.toTuple()[0][1]
  plane_tz = plane.toTuple()[0][2]

  new_origin = cq.Vector(plane_tx, plane_ty, plane_tz)
  new_normal = transform_vector(plane_rx, plane_ry, plane_rz, np.array([0, 0, 1]), type="extrinsic").normalized()
  print(f"Normal: {new_normal.toTuple()},, New normal: {(new_normal*-1).toTuple()}")
  return cq.Workplane(cq.Plane(origin=new_origin, normal=(new_normal*-1)))
