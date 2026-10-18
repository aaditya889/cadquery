from __future__ import annotations
import cadquery as cq

def create_rectangular_slot(workplane: cq.Workplane, slotProperties: dict, faces: list[str], slotName: str) -> tuple[cq.Workplane, dict]:
  slot_planes = {slotName: dict()}

  for face in faces:
    slot_planes[slotName][face] = dict()
    entry_wp = workplane.faces(face).workplane()
    slot_planes[slotName][face]["entry"] = entry_wp.plane
    slot_planes[slotName][face]["floor"] = entry_wp.workplane(offset=-slotProperties["depth"]).plane
    slot_planes[slotName][face]["left"] = entry_wp.workplane().transformed(rotate=(0, 90, 0), offset=(slotProperties["length"]/2, 0, -slotProperties["depth"]/2)).plane
    slot_planes[slotName][face]["right"] = entry_wp.workplane().transformed(rotate=(0, -90, 0), offset=(-slotProperties["length"]/2, 0, -slotProperties["depth"]/2)).plane
    workplane = workplane.faces(face).workplane(centerOption="CenterOfBoundBox").rect(slotProperties["length"], slotProperties["width"]).cutBlind(-slotProperties["depth"])

  return (workplane, slot_planes)