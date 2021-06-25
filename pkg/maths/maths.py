#Atoi stands for ASCII to Integer Conversion
def atoi(string):
    res = 0

    # Iterate through all characters of
    #  input and update result
    for i in range(len(string)):
        res = res * 10 + (ord(string[i]) - ord('0'))

    return res

#Adjustment contains rule of three for calculating an integer given another integer representing a percentage
def Adjustment(a, b):
	return (a * b) / 100
