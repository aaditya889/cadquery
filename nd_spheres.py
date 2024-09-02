import sympy as sym
import cadquery as cq


class Vector:
  vx = None
  vy = None
  vz = None
  
  def __init__(self, vx, vy, vz=0):
    self.vx = vx
    self.vy = vy
    self.vz = vz
 

  def __add__(self, o):
    return Vector((self.vx + o.vx), (self.vy + o.vy), (self.vz + o.vz))
  

  def __sub__(self, o):
    return Vector((self.vx - o.vx), (self.vy - o.vy), (self.vz - o.vz))
  

  def __pos__(self):
    return ((self.vx**2 + self.vy**2 + self.vz**2)**0.5)
  

  def __truediv__(self, o):
    L = +o
    return Vector(self.vx/L, self.vy/L, self.vz/L)
  

  def __mul__(self, o):
    return Vector(self.vx*o, self.vy*o, self.vz*o)
  
  
  def dot(self, o):
    return (self.vx*o.vx + self.vy*o.vy + self.vz*o.vz)
  

  def cross(self, o):
    return Vector((self.vy*o.vz - self.vz*o.vy), (self.vz*o.vx - self.vx*o.vz), (self.vx*o.vy - self.vy*o.vx))
  
  
  def __str__(self) -> str:
    xhat = 'x\u0302'
    yhat =  'y\u0302'
    zhat = 'z\u0302'
    return f'({self.vx}) {xhat} + ({self.vy}) {yhat} + ({self.vz}) {zhat}'


def find_intersection_points_of_two_3d_circles(c1, c2, plane_vector, tolerance=0.1):
  (x1, y1, z1, r1) = c1
  (x2, y2, z2, r2) = c2
  
  c1_vector = Vector(x1, y1, z1)
  c2_vector = Vector(x2, y2, z2)
  
  print(f'c1_vector: {c1_vector}, c2_vector: {c2_vector}')
  
  c2x = +(c2_vector - c1_vector)
  
  xiF1 = (r1**2 - r2**2 + c2x**2)/(2*c2x)
  if (r1**2 - xiF1**2) < 0:
    if (r1**2 - xiF1**2) < tolerance:
      print("Warning: The circles are not intersecting, but are very close to each other!")
      xiF1 = r1
    else:
      print("Error: The circles are not intersecting!")
      return (None, None)

  yi1F1 = (r1**2 - xiF1**2)**0.5
  Dx = xiF1
  Dy = yi1F1
  del_c = c2_vector - c1_vector
  Dc = +del_c
  r_cap_c = del_c / Dc
  piF0 = c1_vector + (r_cap_c * Dx)
  n_vector = plane_vector.cross(r_cap_c)
  n_cap = n_vector / +n_vector
  P1F0 = piF0 + (n_cap * Dy)
  P2F0 = piF0 - (n_cap * Dy)
  
  return (P1F0.vx, P1F0.vy, P1F0.vz), (P2F0.vx, P2F0.vy, P2F0.vz)


def find_intersection_points_of_3_spheres(s1, s2, s3, tolerance=0.1):
  (x1, y1, z1, r1) = s1
  (x2, y2, z2, r2) = s2
  (x3, y3, z3, r3) = s3
  
  s1_vector = Vector(x1, y1, z1)
  s2_vector = Vector(x2, y2, z2)
  s3_vector = Vector(x3, y3, z3)
  s2x = +(s2_vector - s1_vector)
  
  xiF1 = (r1**2 - r2**2 + s2x**2)/(2*s2x)
  if (r1**2 - xiF1**2) < 0:
    return (None, None)

  yi1F1 = (r1**2 - xiF1**2)**0.5
  Dx = xiF1
  Dy = yi1F1
  del_c = s2_vector - s1_vector
  Dc = +del_c
  r_cap_c = del_c / Dc
  piF0 = s1_vector + (r_cap_c * Dx)
  print(f'p1F0: {piF0}')
  # Center of new circle (Ci) = piF0, Radius = Dy, Normal vector to the plane of the circle = r_cap_c
  # Minor circle of the third sphere intersecting with the plane of the intersection circle:
  normal_distance_of_s3_from_plane_of_ci = (r_cap_c.dot(s3_vector - piF0))
  print('normal_distance_of_s3_from_plane_of_ci:', normal_distance_of_s3_from_plane_of_ci)
  
  if r3 - abs(normal_distance_of_s3_from_plane_of_ci) < 0:
    if r3 - abs(normal_distance_of_s3_from_plane_of_ci) < tolerance:
      print("Warning: The spheres are not intersecting, but are very close to each other!")
      r3 = abs(normal_distance_of_s3_from_plane_of_ci)
    else:
      print("Error: The spheres are not intersecting!")
      return (None, None)
  
  radius_of_second_circle = (r3**2 - normal_distance_of_s3_from_plane_of_ci**2)**0.5
  center_of_second_circle = s3_vector - (r_cap_c * normal_distance_of_s3_from_plane_of_ci)    # It's minus since we need the minor circle on S3 "towards" the plane of Ci, and r_cap_c is pointing "away" from the plane of Ci
  
  print(f's3_vector: {s3_vector}, r_cap_c: {r_cap_c}, normal_distance_of_s3_from_plane_of_ci: {normal_distance_of_s3_from_plane_of_ci}, radius_of_second_circle: {radius_of_second_circle}, center_of_second_circle: {center_of_second_circle}')
  (x1, y1, z1, r1) = (piF0.vx, piF0.vy, piF0.vz, Dy)
  (x2, y2, z2, r2) = (center_of_second_circle.vx, center_of_second_circle.vy, center_of_second_circle.vz, radius_of_second_circle)
  # print((x1, y1, z1, r1))
  # print((x2, y2, z2, r2))

  return find_intersection_points_of_two_3d_circles((x1, y1, z1, r1), (x2, y2, z2, r2), r_cap_c, tolerance=tolerance)


def check_if_point_lies_on_a_circle(c, p, tolerance=0.01):
  (x, y, r) = c
  (px, py) = p
  return abs((px - x)**2 + (py - y)**2 - r**2) < tolerance


def check_if_point_lies_on_a_sphere(s, p, tolerance=0.1):
  (x, y, z, r) = s
  (px, py, pz) = p
  return abs((px - x)**2 + (py - y)**2 + (pz - z)**2 - r**2) < tolerance

