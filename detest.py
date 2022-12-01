
class T:
    def self_decorator(func_to_decorate):
        def wrap(*args):
            print("before")
            func_to_decorate(*args)
            print("after")
        return wrap

    @self_decorator
    def test(self):
        print("execute body of function")

t = T()
t.test()
