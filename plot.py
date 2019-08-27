import numpy
from matplotlib import pyplot, tri
from mpl_toolkits.mplot3d import Axes3D
from typing import Union, List


def get_mask(total: int, axis: int, layer: int) -> numpy.ndarray:
    side = round(total ** (1 / 3))
    if layer < 0 or layer >= side:
        raise IndexError(f"layer {layer} exceeds maximum of {side - 1}")
    indices = numpy.arange(total)
    if axis == 0:
        return numpy.floor(indices / side / side) == layer
    elif axis == 1:
        return numpy.floor(indices / side) % side == layer
    elif axis == 2:
        return indices % side == layer
    else:
        raise IndexError(f"axis {axis} exceeds maximum of 2")


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
        raise IndexError(f"axis {axis} exceeds maximum of 2")


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
            raise IndexError(f"axis {axis} exceeds maximum of 2")
    if offset is not None:
        kx += offset[0]
        ky += offset[1]
        kz += offset[2]
    axes3d.scatter(kx, ky, kz)


def add_bands_scatter_plot(axes3d: Axes3D,
                           kpoints: numpy.ndarray, eigenvalues: numpy.ndarray,
                           axis: int, layer: int,
                           band_indices: Union[List[int], range],
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
                             axis: int, layer: int, resolution: int,
                             band_indices: Union[List[int], range, numpy.ndarray],
                             offset: Union[List[float], numpy.ndarray] = None):
    x, y, zs = get_x_y_zs(kpoints, eigenvalues, axis, layer)
    if offset is not None:
        x += offset[0]
        y += offset[1]
        zs += offset[2]
    triang = tri.Triangulation(x, y)

    x_linspace = numpy.linspace(min(x), max(x), resolution)
    y_linspace = numpy.linspace(min(y), max(y), resolution)

    b_range = max(band_indices) - min(band_indices) if len(band_indices) > 1 else 1
    for b in band_indices:
        interpolator = tri.LinearTriInterpolator(triang, zs[:, b])
        x_meshgrid, y_meshgrid = numpy.meshgrid(x_linspace, y_linspace)
        z_mesggrid = interpolator(x_meshgrid, y_meshgrid)
        color = (max(band_indices) - b)/b_range/1.5
        axes3d.plot_wireframe(x_meshgrid, y_meshgrid, z_mesggrid, colors=(color, color, color))


def add_bands_surface_plot(axes3d: Axes3D,
                           kpoints: numpy.ndarray, eigenvalues: numpy.ndarray,
                           axis: int, layer: int, resolution: int,
                           band_indices: Union[List[int], range, numpy.ndarray],
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


class Plotter:
    def __init__(self,
                 kpoints: numpy.ndarray = None, eigenvalues: numpy.ndarray = None,
                 axis: int = None, layer: int = None, resolution: int = None,
                 band_indices: Union[List[int], range, numpy.ndarray] = None):
        self.figure = pyplot.figure()
        self.axes3d = Axes3D(self.figure)
        self.kpoints = kpoints
        self.eigenvalues = eigenvalues
        self.axis = axis
        self.layer = layer
        self.resolution = resolution
        self.band_indices = band_indices

    def add_kpoints_scatter_plot(self,
                                 kpoints: numpy.ndarray = None,
                                 axis: int = None, layer: int = None,
                                 offset: Union[List[float], numpy.ndarray] = None):
        if kpoints is None:
            kpoints = self.kpoints
        if axis is None:
            axis = self.axis
        if layer is None:
            layer = self.layer
        if kpoints is None:
            raise ValueError("argument missing")
        add_kpoints_scatter_plot(self.axes3d, kpoints, axis, layer, offset)

    def add_bands_scatter_plot(self,
                               kpoints: numpy.ndarray = None, eigenvalues: numpy.ndarray = None,
                               axis: int = None, layer: int = None,
                               band_indices: Union[List[int], range] = None,
                               offset: Union[List[float], numpy.ndarray] = None):
        if kpoints is None:
            kpoints = self.kpoints
        if eigenvalues is None:
            eigenvalues = self.eigenvalues
        if axis is None:
            axis = self.axis
        if layer is None:
            layer = self.layer
        if band_indices is None:
            band_indices = self.band_indices
        if kpoints is None or eigenvalues is None or axis is None or layer is None or band_indices is None:
            raise ValueError("argument missing")
        add_bands_scatter_plot(self.axes3d, kpoints, eigenvalues, axis, layer, band_indices, offset)

    def add_bands_wireframe_plot(self,
                                 kpoints: numpy.ndarray = None, eigenvalues: numpy.ndarray = None,
                                 axis: int = None, layer: int = None, resolution: int = None,
                                 band_indices: Union[List[int], range, numpy.ndarray] = None,
                                 offset: Union[List[float], numpy.ndarray] = None):
        if kpoints is None:
            kpoints = self.kpoints.copy()
        if eigenvalues is None:
            eigenvalues = self.eigenvalues
        if axis is None:
            axis = self.axis
        if layer is None:
            layer = self.layer
        if resolution is None:
            resolution = self.resolution
        if band_indices is None:
            band_indices = self.band_indices
        if kpoints is None or eigenvalues is None or axis is None or layer is None or resolution is None\
                or band_indices is None:
            raise ValueError("argument missing")
        add_bands_wireframe_plot(self.axes3d, kpoints, eigenvalues, axis, layer, resolution, band_indices, offset)

    def add_bands_surface_plot(self,
                               kpoints: numpy.ndarray = None, eigenvalues: numpy.ndarray = None,
                               axis: int = None, layer: int = None, resolution: int = None,
                               band_indices: Union[List[int], range, numpy.ndarray] = None,
                               offset: Union[List[float], numpy.ndarray] = None):
        if kpoints is None:
            kpoints = self.kpoints
        if eigenvalues is None:
            eigenvalues = self.eigenvalues
        if axis is None:
            axis = self.axis
        if layer is None:
            layer = self.layer
        if resolution is None:
            resolution = self.resolution
        if band_indices is None:
            band_indices = self.band_indices
        if kpoints is None or eigenvalues is None or axis is None or layer is None or resolution is None\
                or band_indices is None:
            raise ValueError("argument missing")
        add_bands_surface_plot(self.axes3d, kpoints, eigenvalues, axis, layer, resolution, band_indices, offset)

    @staticmethod
    def show():
        pyplot.axis("equal")
        pyplot.show()
