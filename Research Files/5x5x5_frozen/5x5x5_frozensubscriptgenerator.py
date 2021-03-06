#!/usr/bin/env python

if __name__ == '__main__':
    temperature = 50
    for i in range(1,21):
        temp = temperature * i
        if temp == 1000:
            temp_string = "99_1000"
        else:
            temp_string = str(temp)
        f = open("PyTestSub_{}k".format(temp_string), "w+")
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --ntasks=8\n")
        f.write("#SBATCH --export=ALL\n")
        f.write("#SBATCH --out=Foundry-%j.out")
        f.write("#SBATCH --time=0-00:15:00\n")
        f.write("#SBATCH --mail-user=amlfhg@umsystem.edu\n")
        #f.write("#SBATCH --mail-type=ALL\n")
        f.write("module load lammps\n")
        f.write("mpirun ~/bin/lmp_mpi < 5x5x5_{}k_frozen_py.lmp > 5_{}k_frozen.dat".format(temp_string, temp_string))
        f.close()
