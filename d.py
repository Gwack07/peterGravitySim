import turtle

def right_click(x, y):
    print("Right click at", x, y)

screen = turtle.Screen()
screen.onclick(right_click, btn=2)  # btn=3 means right-click

print("Right-click test started. Try right-clicking the window.")
screen.mainloop()
