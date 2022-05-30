import random
def random_phone():
    s=""
    for i in range(9):
        s+=str(random.randint(0, 9))
    return s
print(random_phone())