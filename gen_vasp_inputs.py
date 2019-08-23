import os
from pymatgen.ext.matproj import MPRester
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.io.vasp.inputs import Incar, Poscar, Potcar, Kpoints, VaspInput
from pymatgen.symmetry.bandstructure import HighSymmKpath


APIkey = 'vI8phwVV3Ie6s4ke'  # update the key when necessary
mpr = MPRester(APIkey)


class VaspInputs:

    def __init__(self, mp_id):

        self.mp_id = mp_id

        self.structure = mpr.get_structure_by_material_id(self.mp_id)
        self.primitive_structure = self.structure.get_primitive_structure()

        self.input_set = MPRelaxSet(self.structure)
        self.input_set.potcar_functional = 'PW91'

    def write_inputs(self):
        self.input_set.write_input('vasp_inputs/'+self.mp_id+'/', make_dir_if_not_present=True)


if __name__ == '__main__':
    # Every time when changing running environment, need uncomment the following two lines
    # os.system('pmg config --add PMG_VASP_PSP_DIR C:/Users/user/PycharmProject/PlotBS3D/pseudo-potential')
    # os.system('pmg config --add PMG_DEFAULT_FUNCTIONAL PW91')

    inputs = VaspInputs('mp-696736')
    inputs.write_inputs()
