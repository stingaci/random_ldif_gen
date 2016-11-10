Run like:
	ldif_ran_gen.py -b "dc=example,dc=net" -o init.ldif -n 100

b - base OU
o - output ldif file
n - number of total entries (80% will be users, 20% will be groups)

* Note that this tool also creates the top level domain (dc=example,dc=net in this case).

