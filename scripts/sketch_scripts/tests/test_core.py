"""
Checks for the port / mate engine and the feature parts.
Run: python3 tests/test_core.py   (or `pytest tests/` if pytest is installed), from sketch_scripts/.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cadquery as cq
from core import Component, Port, fuse_all
from features import BearingHousing, ScrewBoss, MountingPlate
from operations.slots import create_rectangular_slot

TOL = 1e-6


def close(a: cq.Vector, b, tol=TOL) -> bool:
    return (a - cq.Vector(b)).Length < tol


class Box(Component):
    def __init__(self, name="box", size=(20, 10, 10)):
        super().__init__(name)
        self.size = size

    def _build(self):
        lx, ly, lz = self.size
        self.add_port("top", origin=(0, 0, lz), normal=(0, 0, 1), x_dir=(1, 0, 0))
        self.add_port("bottom", origin=(0, 0, 0), normal=(0, 0, -1), x_dir=(1, 0, 0))
        self.add_port("side", origin=(lx / 2, 0, lz / 2), normal=(1, 0, 0), x_dir=(0, 1, 0))
        return cq.Workplane("XY").box(lx, ly, lz, centered=(True, True, False))


def test_port_keeps_x_dir():
    p = Port("p", (1, 2, 3), normal=(0, 1, 0), x_dir=(0, 0, 1))
    assert close(p.origin, (1, 2, 3)) and close(p.normal_vector, (0, 1, 0)) and close(p.x_dir, (0, 0, 1))


def test_plane_round_trip_keeps_x_dir():
    plane = cq.Plane(origin=(5, -2, 7), xDir=(0, 1, 0), normal=(1, 0, 0))
    q = Port("q", plane)
    assert close(q.origin, plane.origin) and close(q.x_dir, plane.xDir) and close(q.normal_vector, plane.zDir)
    moved = q.moved(cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90))
    assert close(moved.x_dir, (-1, 0, 0)) and close(moved.normal_vector, (0, 1, 0))


def test_mate_coincident_and_repeatable():
    base, lid = Box("base"), Box("lid", size=(10, 10, 4))
    base.translate((100, 0, 0))
    lid.mate("bottom", to=base, to_port="top", invert=True)
    first = lid.location.toTuple()
    lid.mate("bottom", to=base, to_port="top", invert=True)          # repeating must not stack
    assert lid.location.toTuple() == first
    assert close(lid.port("bottom").origin, base.port("top").origin)
    assert close(lid.port("bottom").normal_vector, -base.port("top").normal_vector)
    assert close(lid.port("bottom").x_dir, base.port("top").x_dir)  # in-plane direction kept
    bb = lid.bounding_box()
    assert abs(bb.zmin - 10) < 1e-6 and abs(bb.zmax - 14) < 1e-6 and abs(bb.xmin - 95) < 1e-6


def test_invert_does_not_mutate_parent():
    base, a, b = Box("base"), Box("a", (4, 4, 4)), Box("b", (4, 4, 4))
    before = base.local_port("top").loc.toTuple()
    a.mate("bottom", to=base, to_port="top", invert=True)
    b.mate("bottom", to=base, to_port="top", invert=True)
    assert base.local_port("top").loc.toTuple() == before
    assert a.location.toTuple() == b.location.toTuple()


def test_rebuild_keeps_solid_and_ports_together():
    base, lid = Box("base"), Box("lid", (6, 6, 2))
    lid.mate("bottom", to=base, to_port="side", invert=True)
    port_before, bb_before = lid.port("top").origin, lid.bounding_box()
    lid.build(force_rebuild=True)
    assert close(lid.port("top").origin, port_before)
    assert abs(lid.bounding_box().xmax - bb_before.xmax) < 1e-6


def test_child_placed_in_parent_frame_during_build():
    class Holder(Component):
        def _build(self):
            body = cq.Workplane("XY").box(30, 30, 10, centered=(True, True, False))
            self.add_port("cup_seat", origin=(0, 0, 10), normal=(0, 0, 1))
            cup = BearingHousing(bearing="608")
            cup.mate("mount_face", to=self.local_port("cup_seat"), invert=True)
            return fuse_all(body, cup)
    h = Holder("holder")
    local_bb = h.build().val().BoundingBox()
    h.translate((0, 0, 50))
    h.build(force_rebuild=True)                                      # rebuild after placement must not double-move
    assert abs(h.build().val().BoundingBox().zmax - local_bb.zmax) < 1e-6
    assert abs(h.bounding_box().zmax - (local_bb.zmax + 50)) < 1e-6


def test_feature_parts_valid():
    for part in (BearingHousing(), ScrewBoss(), MountingPlate()):
        assert part.val().isValid(), part
    plate = MountingPlate()
    assert close(plate.port("top_face").origin, (0, 0, plate.thickness))


def test_slot_planes_become_ports():
    class Slotted(Component):
        def _build(self):
            body = cq.Workplane("XY").box(40, 40, 20)
            body, planes = create_rectangular_slot(body, {"length": 10, "width": 4, "depth": 3}, [">X", "<X"], "slots")
            self.add_ports_from_planes(planes)
            return body
    s = Slotted("s")
    s.translate((0, 0, 100))
    assert "slots.>X.floor" in s.ports and "slots.<X.entry" in s.ports
    assert abs(s.port("slots.>X.entry").origin.z - 100) < 1e-6        # slot ports move with the part


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} passed")
