import sys
import re
import itertools as it


def comb(m, lst):
	if m == 0: return [[]]
		return [[x] + suffix for i, x in enumerate(lst)
			for suffix in comb(m - 1, lst[i + 1:])]



lst = ["cookies", "apples", "bananas"]

print(list(it.combinations(lst, 2)))

def make_keys(lst):
	lst.sort()
	string = ""
	for i in range(len(lst)):
		string += lst[i] + ":"
	return string


# print(make_keys((lst)))



#print(comb(3, [1,2,3,4,5]))


def process_data():
	f = open(sys.argv[1], "r")
	raw_data = f.readlines()
	f.close()

	db = []
	for line in raw_data:
		templine = line.split(',')
		if len(templine) >= 10:
			db.append(templine)	

	clean_db = []
	for i in range(len(db)):
		temp = []
		for j in range(len(db[i])):
			temp.append(re.search(r'[^\n]*', db[i][j]).group()) #getting rid of the \n character in items
		clean_db.append(temp)

	f2 = open("tenitemgroceries.csv", "w")
	f2.write(str(clean_db))
	f2.close()

	#print(clean_db)

	return clean_db


def main():
	#process_data()
	pass
	



if __name__ == '__main__':
	main()



