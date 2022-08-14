x = 'hs1122r'
print(x.translate({ord(i) : None for i in 'hsr'}))
