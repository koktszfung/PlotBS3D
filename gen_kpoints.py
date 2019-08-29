import numpy
import data


def write_kpoints_cubic(half_size: int, coord_style: chr, out_file_path):
    full_size = half_size * 2 + 1
    scale = 1 / half_size
    with open(out_file_path, "w") as file:
        file.write(f"KPOINTS cubic {half_size}x{half_size}x{half_size}\n")
        file.write(str(full_size ** 3) + "\n")
        file.write(f"{coord_style}\n")
        for i in range(-half_size, half_size + 1):
            for j in range(-half_size, half_size + 1):
                for k in range(-half_size, half_size + 1):
                    file.write(f"{i*scale:.5} {j*scale:.5} {k*scale:.5} 1.\n")


def write_kpoints_from_file(in_file_path: str, out_file_path: str):
    vasprun_root = data.get_vasprun_root(in_file_path)
    kpoints = data.get_kpoints(vasprun_root)
    with open(out_file_path, "w") as file:
        file.write(f"KPOINTS {in_file_path}\n")
        file.write(str(kpoints.shape[0]) + "\n")
        file.write("R\n")
        for kpoint in kpoints:
            file.write(f"{kpoint[0]:.5} {kpoint[1]:.5} {kpoint[2]:.5} 1.\n")


def main():
    # write_kpoints_cubic(4, 'R', "vasp_inputs/KPOINTS")
    write_kpoints_from_file("vasp_outputs/sg1/696736_c.xml", "vasp_inputs/KPOINTS")


if __name__ == '__main__':
    main()
