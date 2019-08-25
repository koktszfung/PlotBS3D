import os
from pymatgen.ext.matproj import MPRester
from pymatgen.io.vasp.sets import MPRelaxSet


def initialize_pseudo_potential():
    os.system('pmg config --add PMG_VASP_PSP_DIR C:/Users/user/PycharmProject/PlotBS3D/pseudo-potential')
    os.system('pmg config --add PMG_DEFAULT_FUNCTIONAL PW91')


def get_input_set(mprester: MPRester, mpnum: int) -> MPRelaxSet:
    return MPRelaxSet(mprester.get_structure_by_material_id(f"mp-{mpnum}"), potcar_functional="PW91")


def write_poscar_potcar(mpnum: int):
    mprester = MPRester('vI8phwVV3Ie6s4ke')
    write_dir = f"vasp_inputs/{mpnum}/"
    if not os.path.exists(write_dir):
        os.makedirs(write_dir)
    input_set = get_input_set(mprester, mpnum)
    input_set.poscar.write_file(write_dir+"POSCAR")
    input_set.potcar.write_file(write_dir+"POTCAR")


def main():
    sg1 = [14983, 23487, 24595, 24705, 25483]
    sg2 = [10559, 10560, 10621, 10838, 11462]
    for i in sg1:
        write_poscar_potcar(i)


if __name__ == '__main__':
    main()
