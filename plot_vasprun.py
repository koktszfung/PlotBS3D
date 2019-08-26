import xml.etree.ElementTree as ElementTree
import numpy
from matplotlib import pyplot, tri
from mpl_toolkits.mplot3d import Axes3D
from typing import Union, List


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


def get_kpoints_cartesian(vasprun_root: ElementTree) -> numpy.ndarray:
    bases = get_bases_cartesian(vasprun_root)
    kpoints = get_kpoints(vasprun_root)
    return numpy.array([numpy.sum([kpoint[i] * bases[i] for i in range(3)], 0) for kpoint in kpoints])


def get_kpoints_reciprocal(vasprun_root: ElementTree) -> numpy.ndarray:
    bases = get_bases_reciprocal(vasprun_root)
    kpoints = get_kpoints(vasprun_root)
    return numpy.array([numpy.sum([kpoint[i] * bases[i] for i in range(3)], 0) for kpoint in kpoints])


def get_eigenvalues(vasprun_root: ElementTree) -> numpy.ndarray:
    eigenvalues_tree_list = vasprun_root.findall("calculation/eigenvalues/array/set/set/set")
    return numpy.asarray([[eigenvalues.text.split()[0]
                           for eigenvalues in eigenvalues_tree]
                          for eigenvalues_tree in eigenvalues_tree_list], float)


def get_maxorbitals(vasprun_root: ElementTree) -> numpy.ndarray:
    procar_tree = vasprun_root.find("calculation/projected")
    if procar_tree is None:
        print("procar not found, return none instead")
        return numpy.array([])
    ions_tree_list = procar_tree.find("array/set/set/set").findall("set")
    ions = numpy.asarray([[ion.text.split()
                           for ion in ions_tree.findall("r")]
                          for ions_tree in ions_tree_list], float)
    return numpy.array([0 if numpy.all(ion[:, 1:] == 0)
                        else 1 if numpy.all(ion[:, 4:] == 0)
                        else 2 for ion in ions])


def get_mask(total: int, axis: int, layer: int) -> numpy.ndarray:
    side = round(total ** (1 / 3))
    if layer > side:
        print("layer out of range, return none instead")
        return numpy.array([])
    indices = numpy.arange(total)
    if axis == 0:
        return numpy.floor(indices / side / side) == layer
    elif axis == 1:
        return numpy.floor(indices / side) % side == layer
    elif axis == 2:
        return indices % side == layer
    else:
        print("axis out of range, return none instead")
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
    else:
        print("axis out of range, return none instead")
        return numpy.array([]), numpy.array([]), numpy.array([])


def get_kx_ky_kz(kpoints: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray, numpy.ndarray):
    return kpoints[:, 0], kpoints[:, 1], kpoints[:, 2]


def add_kpoints_scatter_plot(axes3d: Axes3D,
                             kpoints: numpy.ndarray,
                             axis: int = None, layer: int = None,
                             offset: Union[List[float], numpy.ndarray] = None):
    kx, ky, kz = get_kx_ky_kz(kpoints)
    if axis is not None and layer is not None:
        mask = get_mask(kpoints.shape[0], axis, layer)
        if axis == 0:
            kx, ky, kz = ky[mask], kz[mask], kx[mask]
        elif axis == 1:
            kx, ky, kz = kz[mask], kx[mask], ky[mask]
        elif axis == 2:
            kx, ky, kz = kx[mask], ky[mask], kz[mask]
        else:
            print("axis out of range, plot none instead")
            kx, ky, kz = numpy.array([]), numpy.array([]), numpy.array([])
    if offset is not None:
        kx += offset[0]
        ky += offset[1]
        kz += offset[2]
    axes3d.scatter(kx, ky, kz)


def add_bands_scatter_plot(axes3d: Axes3D,
                           kpoints: numpy.ndarray, eigenvalues: numpy.ndarray,
                           axis: int, layer: int, band_indices: Union[List[int], range],
                           offset: Union[List[float], numpy.ndarray] = None):
    x, y, zs = get_x_y_zs(kpoints, eigenvalues, axis, layer)
    if offset is not None:
        x += offset[0]
        y += offset[1]
        zs += offset[2]
    for b in band_indices:
        axes3d.scatter(x, y, zs[:, b])


def add_bands_wireframe_plot(axes3d: Axes3D,
                             kpoints: numpy.ndarray, eigenvalues: numpy.ndarray,
                             axis: int, layer: int, band_indices: Union[List[int], range], resolution: int,
                             offset: Union[List[float], numpy.ndarray] = None):
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
        b_range = max(band_indices) - min(band_indices)
        color = (max(band_indices) - b)/b_range/1.5
        axes3d.plot_wireframe(x_meshgrid, y_meshgrid, z_mesggrid, colors=(color, color, color))


def add_bands_surface_plot(axes3d: Axes3D,
                           kpoints: numpy.ndarray, eigenvalues: numpy.ndarray,
                           axis: int, layer: int, band_indices: Union[List[int], range], resolution: int,
                           offset: Union[List[float], numpy.ndarray] = None):
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


def main():
    fig = pyplot.figure()
    axes3d = Axes3D(fig)

    vasprun_root = get_vasprun_root("vasp_outputs/sg1/696736_c.xml")
    kpoints = get_kpoints_reciprocal(vasprun_root)
    eigenvalues = get_eigenvalues(vasprun_root)

    band_indices = range(eigenvalues.shape[1] - 6, eigenvalues.shape[1])
    axis, layer = 2, 4

    add_bands_surface_plot(axes3d, kpoints, eigenvalues, axis, layer, band_indices, 27)
    # add_bands_wireframe_plot(axes3d, kpoints, eigenvalues, axis, layer, band_indices, 27)
    # add_bands_scatter_plot(axes3d, kpoints, eigenvalues, axis, layer, band_indices)
    # add_kpoints_scatter_plot(axes3d, kpoints, axis, layer)

    pyplot.axis("equal")
    pyplot.show()


if __name__ == '__main__':
    main()
