import xml.etree.ElementTree as ElementTree
import numpy
from matplotlib import pyplot, tri
from mpl_toolkits.mplot3d import Axes3D
from typing import Union, List


def get_kpoints_eigenvalues(vasprun_path: str):
    tree = ElementTree.parse(vasprun_path)
    root = tree.getroot()

    kpoints = numpy.asarray([kpoint.text.split() for kpoint in root.find("kpoints/varray")], float)

    eigenvalues_tree_list = root.findall("calculation/eigenvalues/array/set/set/set")
    eigenvalues = numpy.asarray([[eigenvalues.text.split()[0]
                               for eigenvalues in eigenvalues_tree]
                              for eigenvalues_tree in eigenvalues_tree_list], float)
    return kpoints, eigenvalues


def get_mask(total: int, axis: int, layer: int) -> numpy.ndarray:
    side = round(total ** (1 / 3))
    if layer > side:
        return numpy.array([])
    indices = numpy.arange(total)
    if axis == 0:
        return numpy.floor(indices / side / side) == layer
    elif axis == 1:
        return numpy.floor(indices / side) % side == layer
    elif axis == 2:
        return indices % side == layer
    else:
        return numpy.array([])


def get_x_y_zs(kpoints: numpy.ndarray, eigenvalues: numpy.ndarray,
               axis: int, layer: int) -> (numpy.ndarray, numpy.ndarray, numpy.ndarray):
    mask = get_mask(kpoints.shape[0], axis, layer)
    if axis == 0:
        return kpoints[mask][:, 1], kpoints[mask][:, 2], eigenvalues[mask]
    elif axis == 1:
        return kpoints[mask][:, 2], kpoints[mask][:, 0], eigenvalues[mask]
    elif axis == 2:
        return kpoints[mask][:, 0], kpoints[mask][:, 1], eigenvalues[mask]


def get_kx_ky_kz(kpoints: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray, numpy.ndarray):
    return kpoints[:, 0], kpoints[:, 1], kpoints[:, 2]


def add_bands_surface_plot(axes3d: Axes3D,
                           kpoints: numpy.ndarray, eigenvalues: numpy.ndarray,
                           axis: int, layer: int, band_indices: Union[List[int], range], resolution: int,
                           offset: Union[List[int], numpy.ndarray] = None):
    x, y, zs = get_x_y_zs(kpoints, eigenvalues, axis, layer)
    if offset is not None:
        x += offset[0]
        y += offset[1]
        zs += offset[2]

    triang = tri.Triangulation(x, y)
    x_linspace = numpy.linspace(min(x), max(x), resolution)
    y_linspace = numpy.linspace(min(y), max(y), resolution)
    for b in band_indices:
        interpolator = tri.LinearTriInterpolator(triang, zs[:, b])
        x_meshgrid, y_meshgrid = numpy.meshgrid(x_linspace, y_linspace)
        z_mesggrid = interpolator(x_meshgrid, y_meshgrid)
        axes3d.plot_surface(x_meshgrid, y_meshgrid, z_mesggrid,
                            cmap=pyplot.get_cmap("terrain"),
                            vmin=numpy.min(z_mesggrid), vmax=numpy.max(z_mesggrid))


def add_kpoints_scatter_plot(axes3d: Axes3D,
                             kpoints: numpy.ndarray,
                             axis: int = None, layer: int = None,
                             offset: numpy.ndarray = None):
    kx, ky, kz = get_kx_ky_kz(kpoints)
    if axis is not None and layer is not None:
        mask = get_mask(kpoints.shape[0], axis, layer)
        kx, ky, kz = kx[mask], ky[mask], kz[mask]
    if offset is not None:
        kx += offset[0]
        ky += offset[1]
        kz += offset[2]

    axes3d.scatter(kx, ky, kz)


if __name__ == '__main__':
    fig = pyplot.figure()
    ax = Axes3D(fig)

    k, e = get_kpoints_eigenvalues("vasp_outputs/si_diamond/vasprun.xml")
    add_kpoints_scatter_plot(ax, k, 2, 4)
    add_bands_surface_plot(ax, k, e, 2, 4, range(e.shape[1]), 18)

    pyplot.axis("equal")
    pyplot.show()
