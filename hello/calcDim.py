import math
import sys

def getDimension(scale):
	rhs = (math.sqrt(4096 - 4*(1024*(1 - scale))) / 2.0)
	return (-32 + rhs, -32 - rhs)


if __name__ == "__main__":
	print(getDimension(int(sys.stdin.readline().strip())))
