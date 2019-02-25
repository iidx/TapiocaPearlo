import struct 
s = b"\x0e\x00\x00\x00\x04\x00\x00\x00U\x00\x00\x000000000000000000{\"Result\":\"1\",\"ResultMessage\":\"100\",\"ReturnValue\":[],\"TS\":1526289981}"
sz = len(s)-16
print(sz)
print(struct.unpack('<4sLLL'+str(sz)+'s', s))