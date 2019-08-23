half_size = 4
full_size = half_size*2+1
with open("KPOINTS", "w") as file:
    file.write(f"KPOINTS {full_size}x{full_size}x{full_size}\n")
    file.write(str(full_size**3)+"\n")
    file.write("R\n")
    for i in range(-half_size, half_size+1):
        for j in range(-half_size, half_size+1):
            for k in range(-half_size, half_size+1):
                file.write(f"{i/half_size*3:.5} {j/half_size*3:.5} {k/half_size*3:.5} 1.\n")
