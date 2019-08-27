import data
import plot

if __name__ == '__main__':
    p = plot.Plotter()

    axis, layer = 2, 4

    r = data.Reader("vasp_outputs/sg1/696736_c.xml")
    band_indices = data.get_band_indicecs(r.orbitals, lambda x: x <= 1)[-1:]
    p.add_bands_surface_plot(r.kpoints_reciprocal, r.eigenvalues, axis, layer, 27, band_indices)
    p.add_bands_scatter_plot(r.kpoints_reciprocal, r.eigenvalues, axis, layer, band_indices)

    r = data.Reader("vasp_outputs/sg1/696736_c_17.xml")
    band_indices = data.get_band_indicecs(r.orbitals, lambda x: x <= 1)[-1:]
    p.add_bands_surface_plot(r.kpoints_reciprocal, r.eigenvalues, axis, layer, 51, band_indices,
                             [2.5, 0, 0])
    p.add_bands_scatter_plot(r.kpoints_reciprocal, r.eigenvalues, axis, layer, band_indices,
                             [2.5, 0, 0])

    p.show()
