import data
import plot

if __name__ == '__main__':
    p = plot.Plotter()

    axis = 1

    layer = 8
    r = data.Reader("vasp_outputs/sg1/696736_c_17.xml")
    band_indices = data.get_band_indicecs(r.orbitals, lambda x: x == 2)[-1:]
    p.add_bands_surface_plot(r.kpoints, r.eigenvalues, axis, layer, 64, band_indices)
    # p.add_bands_scatter_plot(r.kpoints, r.eigenvalues, axis, layer, band_indices)
    # p.add_kpoints_scatter_plot(r.kpoints, axis, layer)

    layer = 4
    r = data.Reader("vasp_outputs/sg1/696736_c.xml")
    band_indices = data.get_band_indicecs(r.orbitals, lambda x: x == 2)[-1:]
    p.add_bands_surface_plot(r.kpoints, r.eigenvalues, axis, layer, 64, band_indices, [15, 0, 0])
    # p.add_bands_scatter_plot(r.kpoints, r.eigenvalues, axis, layer, band_indices, [0, 0, 0])
    # p.add_kpoints_scatter_plot(r.kpoints, axis, layer, [15, 0, 0])

    p.show()
