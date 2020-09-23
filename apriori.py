import sys 
import re
import itertools as it

class Node: #creating a node class that represents each node in the prefix search tree
	
	def __init__(self, itemset, support): 
		self.itemset = itemset
		self.support = support
		self.confidence = 0
		self.parent = None

	def __eq__(self, other):
		if type(self) != type(other):
			return False
		if self.itemset == other.itemset and self.support == other.support and \
		 self.confidence == other.confidence and self.parent == other.parent:
			return True
		else:
			return False

	def __lt__(self, other):
		#return len(self.itemset) < len(other.itemset) #this works too, could be faster depending on application
		return self.support < other.support

	def __repr__(self):
		return "Itemset: {} --- Support: {}".format(self.itemset, self.support)

def process_data():
	f = open(sys.argv[1], "r")
	raw_data = f.readlines() # reading the file line by line
	f.close()
	db = []
	for line in raw_data:
		templine = line.split(',')
		if len(templine) >= 10: # I only want to include lines that have at least 10 items
			db.append(templine)	
	clean_db = []
	for i in range(len(db)):
		temp = []
		for j in range(len(db[i])):
			temp.append(re.search(r'[^\n]*', db[i][j]).group()) #getting rid of the \n character in items
		clean_db.append(temp)
	return clean_db

def get_itemset(D):  # generating I from D
	itemset = set()
	for i in range(len(D)):
		for j in range(len(D[i])):
			itemset.add(D[i][j])
	return itemset

def apriori(D, I, minsup): 
	C = {} # C and F are both dictionaries in my implementation
	F = {}
	root = Node("ROOT", 0) # creating a root node so that each singleton node has the same parent
	minsup = int(minsup * len(D)) # converting relative support to support
	for i in range(len(I)): #initializing the prefix tree with the singletons
		temp = Node([I[i]], 0)
		temp.parent = root
		C[make_key(temp.itemset)] = temp
	k = 1
	while len(C) != 0:
		compute_support(C, D, k)
		to_remove = [] 
		C_keys = sorted(list(C.keys())) 
		length = len(C_keys) #creating this length variable before the loop, since I will be deleting from C in the loop
		for i in range(length):
			if C[C_keys[i]].support >= minsup: #if itemset has enough support add it to F
				F[C_keys[i]] = C[C_keys[i]]
			else:
				C.pop(C_keys[i]) # otherwise remove X from C
		C = extend_prefix_tree(C, k)
		k = k + 1	
	return F


def compute_support(C, D, k): # note that I am passing in both c and k since they go together
	for i in range(len(D)): 
		k_combos = list(it.combinations(D[i], k)) 
		for j in range(len(k_combos)):
			if len(set(k_combos[j]).difference(set(D[i]))) == 0: # this is making sure that X is a subset of i(t)
			# Note: I made all k-subsets of X and must now filter out the ones that are in the tree
				if C.get(make_key(k_combos[j])) is not None: # this is making sure that X is in C^k
					C.get(make_key(k_combos[j])).support += 1


def extend_prefix_tree(C, k):
	ret_C = {} # this is the C that I am going to return at the end
	C_keys = sorted(list(C.keys())) # empirical tests show sorting these keys improves performance
	length = len(C_keys) 
	for i in range(length-1): # making sure to only create nodes once
		for j in range(i+1, length): 
			if C[C_keys[i]].parent == C[C_keys[j]].parent:
				new_node = Node(list(set(C[C_keys[i]].itemset).union(set(C[C_keys[j]].itemset))), 0) # creating a new node
				# which has as its itemset the union of its two parent nodes itemsets
				valid_child = True # only create a child if it is valid to do so
				combos = list(it.combinations(new_node.itemset, k))
				for m in range(len(combos)):
					if len(set(new_node.itemset).difference(set(combos[m]))) == len(set(new_node.itemset)) or \
						len(set(combos[m])) != len(set(new_node.itemset)) - 1: #conditions to make child not valid
						valid_child = False
						break
				if valid_child: # if valid create node as child of left parent (a)
					ret_C[make_key(new_node.itemset)] = new_node
					new_node.parent = C[C_keys[i]]
	return ret_C


def association_rules(F, minconf):
	F_keys = sorted(list(F.keys())) # using these keys to loop through all frequent itemsets
	length = len(F_keys) # again I am removing things so I store length in advance
	for i in range(length):
		if len(F[F_keys[i]].itemset) >= 2:
			A = [] # a list of all subsets of X of size 1 to |X-1|
			for j in range(1, len(F[F_keys[i]].itemset)):
				A.extend(list(it.combinations(F[F_keys[i]].itemset, j)))
			nodes_of_A = {}
			for k in range(len(A)): # now turning a list into a dictionary containing nodes for convenience
				nodes_of_A[make_key(A[k])] = F[make_key(A[k])]
				# sorting the nodes of A in non-increasing order of support (potentially better ways to sort)
			nodes_of_A = {k: v for k, v in sorted(nodes_of_A.items(), key=lambda item: item[1], reverse = True)}
			while len(nodes_of_A) != 0: # while there are still subsets of Z
				keys_of_A = list(nodes_of_A.keys())
				X = nodes_of_A[keys_of_A[0]] # setting the maximal support element of A to the variable X
				nodes_of_A.pop(keys_of_A[0])	# removing X from A	
				keys_of_A.remove(keys_of_A[0])
				Z = F[F_keys[i]] # extracting Z from F
				c = Z.support / X.support
				Y = F[make_key(list(set(Z.itemset).difference(set(X.itemset))))] # calculating Y from Z and X
				if c > minconf:
					print(str(",".join(X.itemset)) + " --> " + str(",".join(Y.itemset)))	
				else:
					potential_removals = []
					for l in range(1, len(X.itemset)):
						potential_removals.extend(list(it.combinations(X.itemset, l)))
					lenNode = len(keys_of_A)
					for m in range(lenNode): # removing subsets of X from A
						for n in range(len(potential_removals)):
							if len(set(nodes_of_A[keys_of_A[m]].itemset).difference(set(potential_removals[n]))) == 0:
								nodes_of_A.pop(keys_of_A[m])
								break
	

def make_key(lst): # this function makes keys such that it pastes a ":" between each sorted element in an itemset
	lst = sorted(lst)
	string = ""
	for i in range(len(lst)):
		string += lst[i] + ":"
	return string


def main():
	db = process_data()
	I = list(get_itemset(db))
	F = apriori(db, I, float(sys.argv[2]))
	association_rules(F, float(sys.argv[3]))


if __name__ == '__main__':
	main()

