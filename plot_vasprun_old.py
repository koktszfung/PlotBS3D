import xml.etree.ElementTree as et
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from mpl_toolkits.mplot3d import Axes3D


def get_kpoints_eigenvalues(vasprun_path):
    tree = et.parse(vasprun_path)
    root = tree.getroot()

    kpoints = np.asarray([kpoint.text.split() for kpoint in root.find("kpoints/varray")], float)

    eigenvalues_tree_list = root.findall("calculation/eigenvalues/array/set/set/set")
    eigenvalues = np.asarray([[eigenvalues.text.split()[0]
                               for eigenvalues in eigenvalues_tree]
                              for eigenvalues_tree in eigenvalues_tree_list], float)

    print("kpoints shape", kpoints.shape)
    print("eigenvalues shape", eigenvalues.shape)
    return kpoints, eigenvalues


def get_mask_const_x(num_kpoints, x):
    side = round(num_kpoints ** (1 / 3))
    if x >= side:
        print("index out of range")
    indices = np.arange(num_kpoints)
    return np.floor(indices / side / side) == x


def get_mask_const_y(num_kpoints, y):
    side = round(num_kpoints ** (1 / 3))
    indices = np.arange(num_kpoints)
    return np.floor(indices / side) % side == y


def get_mask_const_z(num_kpoints, z):
    side = round(num_kpoints ** (1 / 3))
    if z >= side:
        print("index out of range")
    indices = np.arange(num_kpoints)
    return indices % side == z


def plot_bs_from_kpoints_eigenvalues(kpoints, eigenvalues, dim_const, const, band_indices, resolution):
    fig = plt.figure()
    ax = Axes3D(fig)
    num_kpoints = kpoints.shape[0]
    half_size = int(round(num_kpoints**(1/3))/2)
    if dim_const == 0:
        mask = get_mask_const_x(num_kpoints, const)
        x, y = kpoints[mask][:, 1], kpoints[mask][:, 2]
        ax.set_title(f"x = {const-half_size}, bands: {band_indices}")
        ax.set_xlabel("y")
        ax.set_ylabel("z")
    elif dim_const == 1:
        mask = get_mask_const_y(num_kpoints, const)
        x, y = kpoints[mask][:, 2], kpoints[mask][:, 0]
        ax.set_title(f"y = {const-half_size}, bands: {band_indices}")
        ax.set_xlabel("z")
        ax.set_ylabel("x")
    else:
        mask = get_mask_const_z(num_kpoints, const)
        x, y = kpoints[mask][:, 0], kpoints[mask][:, 1]
        ax.set_title(f"z = {const-half_size}, bands: {band_indices}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    zs = eigenvalues[mask]

    x_linspace = np.linspace(min(x), max(x), resolution)
    y_linspace = np.linspace(min(y), max(y), resolution)
    triang = tri.Triangulation(x, y)
    for i in band_indices:
        interpolator = tri.LinearTriInterpolator(triang, zs[:, i])
        x_meshgrid, y_meshgrid = np.meshgrid(x_linspace, y_linspace)
        zi = interpolator(x_meshgrid, y_meshgrid)
        ax.plot_surface(x_meshgrid, y_meshgrid, zi,
                        cmap=plt.get_cmap("terrain"),
                        vmin=np.min(zi), vmax=np.max(zi))

    plt.show()


# def plot_kpoints(kpoints):
#     fig = plt.figure()
#     ax = Axes3D(fig)
#     x, y, z = kpoints[:, 0], kpoints[:, 1], kpoints[:, 2]
#     ax.scatter(x, y, z)
#     plt.show()


def plot_kpoints(kpoints, mask=None):
    if mask is None:
        mask = [True, ]*kpoints.shape[0]
    fig = plt.figure()
    ax = Axes3D(fig)
    x, y, z = kpoints[mask][:, 0], kpoints[mask][:, 1], kpoints[mask][:, 2]
    ax.scatter(x, y, z, c=z, cmap=plt.get_cmap("rainbow"))
    plt.show()


if __name__ == '__main__':
    k, e = get_kpoints_eigenvalues("vasp_outputs/si_diamond/vasprun.xml")
    side = round(k.shape[0]**(1/3))
    num_bands = e.shape[1]
    # plot_bs_from_kpoints_eigenvalues(k, e, 0, 4, range(e.shape[1] - 6, e.shape[1]), 18)
    # plot_bs_from_kpoints_eigenvalues(k, e, 1, 4, range(e.shape[1] - 6, e.shape[1]), 18)
    # plot_bs_from_kpoints_eigenvalues(k, e, 2, 4, range(e.shape[1] - 6, e.shape[1]), 18)
    # for i in range(side):
    #     plot_bs_from_kpoints_eigenvalues(k, e, 2, i, range(e.shape[1] - 6, e.shape[1]), 18)

    plot_kpoints(k)
