import cadquery as cq
# from pythonnexus.libs.sheets import fetch_data_from_excel
# # from cadquery import show_object
from ocp_vscode import show_object, reset_show, set_defaults

# height = 60.0
# width = 80.0
# thickness = 10.0
# diameter = 22.0
# padding = 12.0

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

# def check_if_point_lies_on_a_circle(c, p, tolerance=0.0001):
#   (x, y, r) = c
#   (px, py) = p
#   return abs((px - x)**2 + (py - y)**2 - r**2) < tolerance

# # def find_intersection_points_of_circles_manual(c1, c2):
# #   (x1, y1, r1) = c1
# #   (x2, y2, r2) = c2
  
# #   d = ((x1 - x2)**2 + (y1 - y2)**2)**.5
# #   if d > r1 + r2:
# #     return None
# #   if d < abs(r1 - r2):
# #     return None
# #   if d == 0 and r1 == r2:
# #     return None
    
# #   delta_cx_square = x1**2 - x2**2
# #   delta_cy_square = y1**2 - y2**2
# #   delta_cx = x1 - x2
# #   delta_cy = y1 - y2
# #   delta_r_square = r1**2 - r2**2
# #   k = (delta_cx_square + delta_cy_square - delta_r_square)/2
# #   k2 = k - y1*delta_cy
# #   k3 = (r1**2 - x1**2)*(delta_cy**2) - k2**2
# #   A = delta_cx**2 + delta_cy**2
# #   B = 2 * (k2 * delta_cx + x1 * (delta_cy**2))

# #   x3 = (B + (B**2 + 4*A*k3)**.5) / (2*A)
# #   y311 = -(r1**2 - (x3 - x1)**2)**.5 + y1
# #   y312 = (r1**2 - (x3 - x1)**2)**.5 + y1
# #   y321 = -(r2**2 - (x3 - x2)**2)**.5 + y2
# #   # y322 = (r2**2 - (x3 - x2)**2)**.5 + y2
# #   y3 = y311 if y311 == y321 else y312

# #   x4 = (B - (B**2 + 4*A*k3)**.5) / (2*A)
# #   y411 = -(r1**2 - (x4 - x1)**2)**.5 + y1
# #   y412 = (r1**2 - (x4 - x1)**2)**.5 + y1
# #   y421 = -(r2**2 - (x4 - x2)**2)**.5 + y2
# #   y422 = (r2**2 - (x4 - x2)**2)**.5 + y2
# #   y4 = y411 if y411 == y421 else y412
# #   if (y3 == y4):
# #     y4 = y422 if y422 == y412 else y421

# #   return (x3, y3), (x4, y4)

# # def testing():
# #   c1 = (3.696969, 1, 110)
# #   c2 = (10, 20, 100)
# #   (p1, p2) = find_intersection_points_of_circles(c1, c2)
# #   print(p1)
# #   print(p2)

# sheet_data = fetch_data_from_excel('rectum ptv.xlsx', 'Upper', ['distance from left greater trochanter', 'distance from right greater trochanter', 'distance from left si joint', 'distance from right si joint'])
# distance_from_left_greater_trochanter_coordinates = (0, 0)
# distance_from_right_greater_trochanter_coordinates = (0, 1)
# distance_from_left_si_joint_coordinates = (0, 0)
# distance_from_right_si_joint_coordinates = (103.5, 0)
# data_points = []

# for distances in zip(sheet_data['distance from left greater trochanter'], sheet_data['distance from right greater trochanter'], sheet_data['distance from left si joint'], sheet_data['distance from right si joint']):
#   c1 = (distance_from_left_greater_trochanter_coordinates[0], distance_from_left_greater_trochanter_coordinates[1], distances[0])
#   c2 = (distance_from_right_greater_trochanter_coordinates[0], distance_from_right_greater_trochanter_coordinates[1], distances[1])
#   c3 = (distance_from_left_si_joint_coordinates[0], distance_from_left_si_joint_coordinates[1], distances[2])
#   c4 = (distance_from_right_si_joint_coordinates[0], distance_from_right_si_joint_coordinates[1], distances[3])
#   intersection1 = find_intersection_points_of_circles(c1, c2)
#   intersection2 = find_intersection_points_of_circles(c3, c4)
  
#   if intersection1 is not None:
#     p1, p2 = intersection1
#   if intersection2 is not None:
#     p3, p4 = intersection2
  
#   if intersection1:
#     print('p1: ', p1, 'p2: ',  p2)
#   if intersection2:
#     print('p3: ', p3, 'p4: ', p4)
  
# # make the base
result = (
    cq.Workplane("XY")
    .circle(10)
    .workplane("XZ")
    # .faces(">Z")
    # .workplane("XY")
    .rect(5, 5)
    # .vertices()
    # .circle(.01, forConstruction=True)
    # .pushPoints([(0, 0), (10, 0), (10, 10), (0, 10)])
    
)

# Render the solid
show_object(result)

# print(fetch_data_from_excel('rectum ptv.xlsx', 'Sheet1', ['distance from left greater trochanter']))