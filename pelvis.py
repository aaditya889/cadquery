from pythonnexus.libs.sheets import fetch_data_from_excel
from nd_spheres import find_intersection_points_of_3_spheres


# def find_intersection_points_of_circles(c1, c2):
#   (x1, y1, r1) = c1
#   (x2, y2, r2) = c2
#   # https://stackoverflow.com/questions/3349125/circle-circle-intersection-points
#   d = ((x1 - x2)**2 + (y1 - y2)**2)**.5
#   if d > r1 + r2:
#       return None
#   if d < abs(r1 - r2):
#       return None
#   if d == 0 and r1 == r2:
#       return None
#   a = (r1**2 - r2**2 + d**2) / (2 * d)
#   h = (r1**2 - a**2)**.5
#   x = x1 + a * (x2 - x1) / d
#   y = y1 + a * (y2 - y1) / d
#   x3 = x + h * (y2 - y1) / d
#   y3 = y - h * (x2 - x1) / d
#   x4 = x - h * (y2 - y1) / d
#   y4 = y + h * (x2 - x1) / d
#   return (x3, y3), (x4, y4)


# def find_intersection_points_of_circles_manual(c1, c2):
#   (x1, y1, r1) = c1
#   (x2, y2, r2) = c2
  
#   c1_vector = Vector(x1, y1)
#   c2_vector = Vector(x2, y2)
#   c1x = c1y = c2y = 0
#   c2x = +(c2_vector - c1_vector)
  
#   xiF1 = (r1**2 - r2**2 + c2x**2)/(2*c2x)
#   # print('xiF1^2: ', xiF1**2)
#   # print('r1^2: ', r1**2)
#   if (r1**2 - xiF1**2) < 0:
#     return None

#   yi1F1 = (r1**2 - xiF1**2)**0.5
#   yi2F1 = -((r1**2 - xiF1**2)**0.5)
#   Dx = xiF1
#   Dy = yi1F1
#   del_c = c2_vector - c1_vector
#   Dc = +del_c
#   r_cap_c = del_c / Dc
#   # print('r_cap_c: ', r_cap_c)
#   piF0 = c1_vector + (r_cap_c * Dx)
#   # print('piF0: ', piF0)
#   # print('Dx: ', Dx, 'Dy: ', Dy)
#   n_cap = Vector(-r_cap_c.vy, r_cap_c.vx)
#   # print('n_cap: ', n_cap)
#   # print(n_cap*Dy)
#   P1F0 = piF0 + (n_cap * Dy)
#   P2F0 = piF0 - (n_cap * Dy)
  
#   return (P1F0.vx, P1F0.vy), (P2F0.vx, P2F0.vy)

  
def check_if_point_lies_on_a_circle(c, p, tolerance=0.0001):
  (x, y, r) = c
  (px, py) = p
  return abs((px - x)**2 + (py - y)**2 - r**2) < tolerance


def testing():
  pass
  # c1 = (0, 0, 10)
  # c2 = (20, 0, 10)
  # (p1, p2) = find_intersection_points_of_circles(c1, c2)
  # print(f'Stack -> P1: {p1}, P2: {p2}')
  # (p3, p4) = find_intersection_points_of_circles_manual(c1, c2)
  # print(f'Original -> P1: {p3}, P2: {p4}')


def test_pelvis_data():
  sheet_data = fetch_data_from_excel('rectum ptv.xlsx', 'Upper', ['distance from left greater trochanter', 'distance from right greater trochanter', 'distance from left si joint', 'distance from right si joint'])
  distance_from_left_greater_trochanter_coordinates = (0, 0)
  distance_from_right_greater_trochanter_coordinates = (0, 1)
  distance_from_left_si_joint_coordinates = (0, 0)
  distance_from_right_si_joint_coordinates = (103.5, 0)
  data_points = []

  for distances in zip(sheet_data['distance from left greater trochanter'], sheet_data['distance from right greater trochanter'], sheet_data['distance from left si joint'], sheet_data['distance from right si joint']):
    c1 = (distance_from_left_greater_trochanter_coordinates[0], distance_from_left_greater_trochanter_coordinates[1], distances[0])
    c2 = (distance_from_right_greater_trochanter_coordinates[0], distance_from_right_greater_trochanter_coordinates[1], distances[1])
    c3 = (distance_from_left_si_joint_coordinates[0], distance_from_left_si_joint_coordinates[1], distances[2])
    c4 = (distance_from_right_si_joint_coordinates[0], distance_from_right_si_joint_coordinates[1], distances[3])
    # intersection1 = find_intersection_points_of_circles(c1, c2)
    # intersection2 = find_intersection_points_of_circles(c3, c4)
    
    # if intersection1 is not None:
    #   p1, p2 = intersection1
    # if intersection2 is not None:
    #   p3, p4 = intersection2
    
    # if intersection1:
    #   print('p1: ', p1, 'p2: ',  p2)
    # if intersection2:
    #   print('p3: ', p3, 'p4: ', p4)
    

if __name__ == '__main__':
  testing()
  # A = Vector(2, -3)
  # B = Vector(2, 1)
  
  # print((A * (+A)))
  
  
  
  
# ------------------------------------------------------------------------------------------------------------------------
# Visualising the data points using cadquery
# ------------------------------------------------------------------------------------------------------------------------
  
  
# import cadquery as cq
# # from cadquery import show_object
# from cq_server.ui import ui, show_object

# height = 60.0
# width = 80.0
# thickness = 10.0
# diameter = 22.0
# padding = 12.0

# # # make the base
# result = (
#     cq.Workplane("XY")
#     .circle(10)
#     .workplane("XZ")
#     .faces(">Z")
#     .workplane("XY")
#     .rect(5, 5)
#     .vertices()
#     .circle(.01, forConstruction=True)
#     .pushPoints([(0, 0), (10, 0), (10, 10), (0, 10)])
    
# )

# result = cq.importers.importStep('./Pelvis AP203.STEP')

# Render the solid
# show_object(result)

# print(fetch_data_from_excel('rectum ptv.xlsx', 'Sheet1', ['distance from left greater trochanter']))


# Export
# cq.exporters.export(result, "result.stl")
# cq.exporters.export(result.section(), "result.dxf")
# cq.exporters.export(result, "result.step")