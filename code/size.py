import sys
import math

def determine_icon_size(d, s=64):
    if d == 1:
        return s
    discriminant = math.sqrt(math.pow(s * 2, 2) - 4 * (math.pow(s, 2) * (1-d)))
    return int(max(-2*s + discriminant, -2*s - discriminant)/ 2.0)

if __name__ == "__main__":
	print(determine_icon_size(int(sys.stdin.readline().strip())))	
