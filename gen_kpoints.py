half_size = 4
full_size = half_size*2+1
scale = 1/half_size
with open("vasp_inputs/KPOINTS", "w") as file:
    file.write(f"KPOINTS {full_size}x{full_size}x{full_size}\n")
    file.write(str(full_size**3)+"\n")
    file.write("C\n")
    for i in range(-half_size, half_size+1):
        for j in range(-half_size, half_size+1):
            for k in range(-half_size, half_size+1):
                file.write(f"{i*scale:.5} {j*scale:.5} {k*scale:.5} 1.\n")
