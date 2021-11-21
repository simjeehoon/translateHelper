import worker


class T:
    def __init__(self):
        self.i = 1

class B:
    def __init__(self, b):
        self.aa = b

    def go(self):
        self.aa.i = 20
        print(self.aa.i)

"""def bar():
    try:
        import Tkinter as tk
    except:
        import tkinter as tk

    import time

    class Clock():
        def __init__(self):
            self.root = tk.Tk()
            self.frame = tk.Frame(self.root)
            self.frame.pack(fill='y', side='left')
            self.scrbar = tk.Scrollbar(self.root)
            self.scrbar.pack(fill='y', side='right')
            for i in range(5):
                tk.Button(self.frame, text=f"button{i}").pack(side='top')
            self.scrbar.config(command=self.frame.)

        def update_clock(self):
            print("asdf")
            now = time.strftime("%H:%M:%S")
            self.label.configure(text=now)
            self.root.after(1000, self.update_clock)

    app = Clock()"""

if __name__ == '__main__':
    class A:
        def __init__(self,a,b):
            self.a= a
            self.b=b

        def __copy__(self):
            return self

    def f(a):
        a.a=10
        a.b=20

    c = A(1,2)
    b=c
    f(b)

    print(c.a, c.b)
