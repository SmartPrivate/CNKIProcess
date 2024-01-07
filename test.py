from itertools import chain, combinations

test_list = ['a ', 'b', 'c', 'c']

new_list = [o for o in map(lambda o: o.replace(' ', ''), test_list)]
print(new_list)