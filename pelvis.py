from cq_server.ui import ui, show_object
from pythonnexus.libs.sheets import fetch_data_from_excel
from pythonnexus.libs.cadquery.graphs import plot_spheres
from nd_spheres import find_intersection_points_of_3_spheres, check_if_point_lies_on_a_sphere
import cadquery as cq


def test_pelvis_data(data_points):
  sheet_path = 'https://docs.google.com/spreadsheets/d/1TQkhx1Id3JF_4AzuyjKbKF11K2_vlm_FVzpw6TJ6YQU/edit?gid=1931147181#gid=1931147181'
  sheet_name = 'Sheet2'
  # sheet_data = fetch_data_from_excel('rectum ptv.xlsx', 'Upper', ['distance from left greater trochanter', 'distance from right greater trochanter', 'distance from left si joint', 'distance from right si joint'])
  sheet_data = fetch_data_from_excel(sheet_path, sheet_name, ['distance from left greater trochanter', 'distance from right greater trochanter', 'distance from left si joint', 'distance from right si joint', 'distance from sacral promontary', 'distance from bladder', 'distance from pubic symphysis'])
  p_rsi = (0, 0, 0)
  p_lsi = (10.86, 0, 0)
  p_sp = (5.43, 0, 0)
  
  p_rgt = (-6.34, 7.7978779164590675, 9.14)
  # p_lgt = (17.81, 7.7978779164590675, 0)
  
  print(f'Number of Data points: {len(sheet_data["distance from left greater trochanter"])}')
  tolerance = 0.1
  # print(sheet_data)
  for distances in zip( sheet_data['distance from right si joint'], sheet_data['distance from left si joint'], sheet_data['distance from sacral promontary'], sheet_data['distance from right greater trochanter'], sheet_data['distance from left greater trochanter']):
    print(f'====================================\nDistances: {distances}\n====================================')

    s1 = (p_rsi[0], p_rsi[1], p_rsi[2], float(distances[0]))
    s2 = (p_lsi[0], p_lsi[1], p_lsi[2], float(distances[1]))
    s3 = (p_sp[0], p_sp[1], p_sp[2], float(distances[2]))
    print(f'Spheres: {s1}, {s2}, {s3}')
    cq_s1 = cq.Workplane().pushPoints([(s1[0], s1[1], s1[2])]).sphere(s1[3])
    cq_s2 = cq.Workplane().pushPoints([(s2[0], s2[1], s2[2])]).sphere(s2[3])
    cq_s3 = cq.Workplane().pushPoints([(s3[0], s3[1], s3[2])]).sphere(s3[3])
    show_object(cq_s1, name='s1', options={'color': 'red'})
    show_object(cq_s2, name='s2', options={'color': 'green'})
    show_object(cq_s3, name='s3', options={'color': 'blue'})
    
    # exit(0)
    
    (p1, p2) = find_intersection_points_of_3_spheres(s1, s2, s3, tolerance=tolerance)
    
    if p1 and p2:
      if check_if_point_lies_on_a_sphere((p_rgt[0], p_rgt[1], p_rgt[2], float(distances[3])), p1, tolerance=tolerance):
        print(f'P1: {p1} is on the sphere!')
        # data_points.append(p1)
      else:
        print(f'P1: {p1} is not on the sphere, ignoring')
        
      if check_if_point_lies_on_a_sphere((p_rgt[0], p_rgt[1], p_rgt[2], float(distances[3])), p2, tolerance=tolerance):
        print(f'P2: {p2} is on the sphere!')
        data_points.append(p2)
      else:
        print(f'P2: {p2} is not on the sphere, ignoring')
    else:
      print('No intersection points found!')


data_points = []
test_pelvis_data(data_points=data_points)
print(f'Data points: {data_points}')
print(f'Number of Data points we got: {len(data_points)}')
# result = (
#   cq.Workplane()
#   .pushPoints(data_points)
#   .sphere(.1)
# )

# show_object(result)


# result = (
#     cq.Workplane()
#     .pushPoints([(0, 0, 0), (10, 0, 0)])
#     .sphere(20)
#     .pushPoints([(10, 17.32, 0)])
#     .sphere(20)
#     .pushPoints([(p1[0], p1[1], p1[2]), (p2[0], p2[1], p2[2])])
#     .sphere(.5)
#     # .circle(10)
#     # .workplane("XZ")
#     # .faces(">Z")
#     # .workplane("XY")
#     # .rect(5, 5)
#     # .vertices()
#     # .circle(.01, forConstruction=True)
#     # .pushPoints([(0, 0), (10, 0), (10, 10), (0, 10)])
# )

# show_object(result)
