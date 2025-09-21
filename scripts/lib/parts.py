import cadquery as cq

class AssembledPart():
  original_assembled: cq.Assembly

  def __init__(self, assembled_part):
    self.original_assembled = assembled_part

  def clone(self):
    return self.original_assembled._copy()
  
  def clone_and_rotate(self, rotation_vector: cq.Location=cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90), axis="Z", angle=90):

    print(rotation_vector.toTuple())
    if (rotation_vector.toTuple() == cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90).toTuple()):
      print(f"Rotating through X/Y axis with {angle} degrees")
      match axis:
        case "Z":
          pass
        case "X":
          rotation_vector = cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), angle)
          print(f"Rotating through {rotation_vector.toTuple()} axis with {angle} degrees")
        case "Y":
          rotation_vector = cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), angle)
          print(f"Rotating through {rotation_vector.toTuple()} axis with {angle} degrees")

    cloned_assembly = self.clone()
    next(iter(cloned_assembly.objects.values())).loc *= rotation_vector
    
    return cloned_assembly

  def rotate(self, rotation_vector=cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90)):
    next(iter(self.original_assembled.objects.values())).loc *= rotation_vector
    
    return self.original_assembled
