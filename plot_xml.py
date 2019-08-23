import xml.etree.ElementTree as et
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from mpl_toolkits.mplot3d import Axes3D


# read vasprun.xml
tree = et.parse("vasp_outputs/si_diamond/vasprun.xml")
root = tree.getroot()

kpoints = np.asarray([kpoint.text.split() for kpoint in root.find("kpoints/varray")], float)

eigenvalues_tree_list = root.findall("calculation/eigenvalues/array/set/set/set")
eigenvalues = np.asarray([[eigenvalues.text.split()[0]
                           for eigenvalues in eigenvalues_tree]
                          for eigenvalues_tree in eigenvalues_tree_list], float)

print("kpoints shape", kpoints.shape)
print("eigenvalues shape", eigenvalues.shape)


# prepare data to plot
num_kpoints = kpoints.shape[0]
side = round(num_kpoints ** (1 / 3))

indices = np.arange(num_kpoints)
mask = (indices % side == 6)  # choose the z layer of sampled k-space

x, y = kpoints[mask][:, 0], kpoints[mask][:, 1]  # kpoints
zs = eigenvalues[mask]

print("x shape", x.shape)
print("y shape", y.shape)
print("z shape", zs[:, 0].shape)
print("zs shape", zs.shape)


# prepare matplotlib
fig = plt.figure()
ax = Axes3D(fig)
# band_range = range(0, zs.shape[1])
band_range = range(1, 3)


# scatter plot
# for i in band_range:
#     ax.scatter(x, y, zs[:, i])


# surface plot
xi = np.linspace(min(x), max(x), 36)
yi = np.linspace(min(y), max(y), 36)
triang = tri.Triangulation(x, y)
for i in band_range:
    interpolator = tri.LinearTriInterpolator(triang, zs[:, i])
    Xi, Yi = np.meshgrid(xi, yi)
    zi = interpolator(Xi, Yi)
    ax.plot_surface(Xi, Yi, zi,
                    cmap=plt.get_cmap("terrain"),
                    vmin=np.min(zi), vmax=np.max(zi))
    # ax.contourf(Xi, Yi, zi, zdir="z", cmap=plt.get_cmap("terrain"))


plt.show()
