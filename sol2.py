lowvalue = int(input('Enter the lowest value'));
upvalue = int(input('Enter the upper value'));
print ('The prime numbers:');
for number in range (lowvalue + 1):
    if number > 1:
      for i in range (2, number):
        if (number % i) == 0:
          break;
      else:
         print (number);
