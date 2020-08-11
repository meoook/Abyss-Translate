from django.test import TestCase

# Create your tests here.


aa = '  \t bbbbb \n  \r\n  '
bb = '|'

print(f'{bb}{aa}{bb}')
print(f'{bb}{aa.strip()}{bb}')