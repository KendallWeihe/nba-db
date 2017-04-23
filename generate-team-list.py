import os
import pdb

files = os.listdir("./seasons/2017/")

teams = []
for f in files:
    teams.append(f[:f.index(".")])

f = open("teams.txt", "w")
for t in teams:
    f.write("%s\n" % t)

f.close()
