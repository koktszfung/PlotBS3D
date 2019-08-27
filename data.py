import xml.etree.ElementTree as ElementTree
import numpy
from typing import List, Callable


def get_vasprun_root(vasprun_path: str) -> ElementTree:
    tree = ElementTree.parse(vasprun_path)
    return tree.getroot()


def get_bases_cartesian(vasprun_root: ElementTree) -> numpy.ndarray:
    return numpy.asarray([basis.text.split()
                          for basis in vasprun_root.findall("structure/crystal/varray")[0]], float)


def get_bases_reciprocal(vasprun_root: ElementTree) -> numpy.ndarray:
    return numpy.asarray([basis.text.split()
                          for basis in vasprun_root.findall("structure/crystal/varray")[1]], float)


def get_kpoints(vasprun_root: ElementTree) -> numpy.ndarray:
    return numpy.asarray([kpoint.text.split() for kpoint in vasprun_root.find("kpoints/varray")], float)


def transform_kpoints(kpoints: numpy.ndarray, bases: numpy.ndarray) -> numpy.ndarray:
    return numpy.array([numpy.sum([kpoint[i] * bases[i] for i in range(3)], 0) for kpoint in kpoints])


def get_eigenvalues(vasprun_root: ElementTree) -> numpy.ndarray:
    eigenvalues_tree_list = vasprun_root.findall("calculation/eigenvalues/array/set/set/set")
    return numpy.asarray([[eigenvalues.text.split()[0]
                           for eigenvalues in eigenvalues_tree]
                          for eigenvalues_tree in eigenvalues_tree_list], float)


def get_orbitals(vasprun_root: ElementTree) -> numpy.ndarray:
    procar_tree = vasprun_root.find("calculation/projected")
    if procar_tree is None:
        raise KeyError("procar not found")
    ions_tree_list = procar_tree.find("array/set/set/set").findall("set")
    ions = numpy.asarray([[ion.text.split()
                           for ion in ions_tree.findall("r")]
                          for ions_tree in ions_tree_list], float)
    bands = numpy.sum(ions, 1)
    orbitals = zip(bands[:, 0] != 0, numpy.any(bands[:, 1:4] != 0, 1), numpy.any(bands[:, 5:] != 0, 1))
    return numpy.array([2 if d else 0.5 if p and s else 1 if p else 0 if s else None for s, p, d in orbitals])


def get_band_indicecs(orbitals: numpy.ndarray, condition: Callable[[float], bool]) -> List[int]:
    return [key for key, val in enumerate(orbitals) if condition(val)]


class Reader:
    def __init__(self, vasprun_path: str):
        self.vasprun_root = get_vasprun_root(vasprun_path)

        self.bases_cartesian = get_bases_cartesian(self.vasprun_root)
        self.bases_reciprocal = get_bases_reciprocal(self.vasprun_root)

        self.kpoints = get_kpoints(self.vasprun_root)
        self.kpoints_cartesian = transform_kpoints(self.kpoints, self.bases_cartesian)
        self.kpoints_reciprocal = transform_kpoints(self.kpoints, self.bases_reciprocal)

        self.eigenvalues = get_eigenvalues(self.vasprun_root)

        self.orbitals = get_orbitals(self.vasprun_root)
