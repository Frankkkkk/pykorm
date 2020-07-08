class MotherClass:
    @classmethod
    def yeah(cls):
        return cls.toto


class Factory():
    def __init__(self):
        self.cache = {}

    def factor(self, thing):
        if thing in self.cache:
            return self.cache[thing]

        class Ret(MotherClass):
            toto = thing
            def __name__(self):
                return f'Class{thing}'
        self.cache[thing] = Ret
        return Ret


f = Factory()
ft1 = f.factor('t1')()
ft1bis = f.factor('t1')()
ft2 = f.factor('t2')()



print(ft1.yeah())
print(ft1bis.yeah())
print(ft2.yeah())

print(ft1)
print(ft1bis)
print(ft2)

print(ft1.__class__ == ft1bis.__class__)
print(ft1.__class__ == ft2.__class__)