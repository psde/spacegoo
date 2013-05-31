
foo = [1, 2, 3]
bar = [3, 2, 1]

baz = [a+b for a,b in zip(foo, bar)]
print baz
print map(lambda x,y: x+y, foo,bar)