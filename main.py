import math
import turtle
import random

tick = 0.025
G = 1000
screenDimensions = [800, 600]
scale = 1
particles = []
start_pos = None
cameraPos = [0,0] #up down left right
isParticle = True
rightDragStart = None
rightDragged = False


screen = turtle.Screen()
screen.title("Gravitational Particle Simulator")
screen.bgcolor("black")
screen.setup(width=screenDimensions[0], height=screenDimensions[1])
screen.tracer(0)

class Particle:
    def __init__(self, mass, sVelocity, pos):
        self.mass = mass
        self.velocity = sVelocity.copy()
        self.pos = pos.copy()
        self.force = [0, 0]

        self.particle = turtle.Turtle()
        self.particle.penup()
        self.particle.shape("circle")
        self.particle.color("red")
        self.particle.shapesize(0.5)
        self.particle.goto(scale * (self.pos[0]+cameraPos[0]), scale * (self.pos[1]+cameraPos[1]))

    def resetForce(self):
        self.force = [0, 0]

    def move(self):
        accelX = self.force[0] / (self.mass + 1e-11)
        accelY = self.force[1] / (self.mass + 1e-11)
        self.velocity[0] += accelX * tick
        self.velocity[1] += accelY * tick
        self.pos[0] += self.velocity[0] * tick
        self.pos[1] += self.velocity[1] * tick
        self.particle.goto(scale * (self.pos[0]+cameraPos[0]), scale * (self.pos[1]+cameraPos[1]))

    def computeGravitationalAttraction(self, p2):
        dx = p2.pos[0] - self.pos[0]
        dy = p2.pos[1] - self.pos[1]
        rSquared = dx ** 2 + dy ** 2
        if rSquared == 0:
            return
        r = math.sqrt(rSquared)
        forceMagnitude = G * self.mass * p2.mass / rSquared
        fx = forceMagnitude * dx / r
        fy = forceMagnitude * dy / r
        self.force[0] += fx
        self.force[1] += fy
        p2.force[0] -= fx
        p2.force[1] -= fy

class Planet(Particle):
    def __init__(self, mass, sVelocity, pos, color, size):
        super().__init__(mass, sVelocity, pos)
        self.color = color
        self.size = size
        self.particle.color(self.color)
        self.particle.shapesize(self.size)

class Button:
    def __init__(self, label, x, y, width, height, callback):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback = callback

        # Create button shape
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.penup()
        self.turtle.goto(x - width / 2, y - height / 2)
        self.turtle.color("black", "gray")
        self.turtle.begin_fill()
        for _ in range(2):
            self.turtle.forward(width)
            self.turtle.left(90)
            self.turtle.forward(height)
            self.turtle.left(90)
        self.turtle.end_fill()

        # Create label
        self.text = turtle.Turtle()
        self.text.hideturtle()
        self.text.penup()
        self.text.goto(x, y - 6)
        self.text.color("white")
        self.text.write(label, align="center", font=("Arial", 10, "bold"))

        # Create invisible clickable area for callback
        self.click_area = turtle.Turtle()
        self.click_area.penup()
        self.click_area.goto(x, y)
        self.click_area.shape("square")
        self.click_area.shapesize(stretch_wid=height / 20, stretch_len=width / 20)
        self.click_area.fillcolor("")  # transparent
        self.click_area.color("")  # no border
        self.click_area.onclick(self.on_click)

    def on_click(self, x, y):
        self.callback()

def on_mouse_press(x, y):
    global start_pos
    start_pos = [x / scale, y / scale]

def on_mouse_release(x, y):
    global start_pos
    if start_pos is None:
        return
    end_pos = [x / scale, y / scale]
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    try:
        particles.append(Particle(1, [dx, dy], [start_pos[0]-cameraPos[0], start_pos[1]-cameraPos[1]]))
    except:
        print("Invalid input, particle not created.")
    start_pos = None

def onRightDrag(x, y):
    global rightDragStart, rightDragged
    rightDragStart = [x, y]
    rightDragged = False


def onRightDragMotion(x, y):
    global rightDragStart, cameraPos, rightDragged
    if rightDragStart is None:
        return
    dx = x - rightDragStart[0]
    dy = y - rightDragStart[1]

    cameraPos[0] += dx / scale
    cameraPos[1] += dy / scale

    rightDragStart = [x, y]
    rightDragged = True  # Mark that drag has occurred



def onRightClick(x, y):
    global isParticle
    try:
        mass = float(screen.textinput("Mass", "Enter mass:"))
        vel_x = float(screen.textinput("Velocity X", "Enter initial X velocity:"))
        vel_y = float(screen.textinput("Velocity Y", "Enter initial Y velocity:"))

        if isParticle == True:
            new_particle = Particle(mass, [vel_x, vel_y], [x / scale, y / scale])
        else:
            colour = str(screen.textinput("Colour", "Enter Colour:"))
            size = float(screen.textinput("Size", "Enter Size:"))
            new_particle = Planet(mass, [vel_x, vel_y], [x / scale, y / scale],colour, size)
        particles.append(new_particle)
    except:
        print("Invalid input, particle not created.")
    screen.listen()

def increaseTick():
    global tick
    tick *= 2
    print(f"Tick increased to {tick}")

def decreaseTick():
    global tick
    tick *= 0.5
    print(f"Tick decreased to {tick}")

def flipTick():
    global tick
    tick *= -1
    print(f"Tick flipped to {tick}")

def increaseScale():
    global scale
    scale *= 2
    print(f"Scale increased to {scale}")

def decreaseScale():
    global scale
    scale *= 0.5
    print(f"Scale decreased to {scale}")

def randomParticle():
    global particles
    for i in range(0,100):
        particles.append(Particle(random.randint(0, 100000), [random.uniform(-10000, 10000),random.uniform(-10000, 10000)], [random.uniform(-100, 100),random.uniform(-100, 100)]))

def left():
    global cameraPos
    cameraPos[0] -= 1
    print(f"Camera pos left {cameraPos}")

def right():
    global cameraPos
    cameraPos[0] += 1
    print(f"Camera pos right {cameraPos}")

def up():
    global cameraPos
    cameraPos[1] += 1
    print(f"Camera pos up {cameraPos}")

def down():
    global cameraPos
    cameraPos[1] -= 1
    print(f"Camera pos down {cameraPos}")

def particlePlanetSwap():
    global isParticle
    isParticle = not isParticle

def canvasWorldCoords(event):
    x = event.x - screen.window_width() // 2
    y = screen.window_height() // 2 - event.y
    return x, y

def handleMousePress(event):
    print("left click detected at", event.x, event.y)
    x, y = canvasWorldCoords(event)
    on_mouse_press(x, y)

def handleMouseRelease(event):
    x, y = canvasWorldCoords(event)
    on_mouse_release(x, y)

def handleRightClick(event):
    global rightDragged
    print("Right click detected at", event.x, event.y)
    if rightDragged:
        print("Right click ignored due to prior drag.")
        return
    x, y = canvasWorldCoords(event)
    onRightClick(x, y)



def handleRightDragStart(event):
    x, y = canvasWorldCoords(event)
    onRightDrag(x, y)

def handleRightDragMotion(event):
    x, y = canvasWorldCoords(event)
    onRightDragMotion(x, y)


keybinds = {
    'p': increaseScale,
    'l': decreaseScale,
    'Up': increaseTick,
    'Down': decreaseTick,
    'space': flipTick,
    'r':randomParticle,
    'w':up,
    'a':left,
    'd':right,
    's':down,
    'o':particlePlanetSwap
}
buttons = [
    Button("Scale +", 300, 250, 80, 40, increaseScale),
    Button("Scale -", 300, 200, 80, 40, decreaseScale),
    Button("Tick +", 300, 150, 80, 40, increaseTick),
    Button("Tick -", 300, 100, 80, 40, decreaseTick),
    Button("Flip Tick", 300, 50, 80, 40, flipTick),
    Button("Random", 300, 0, 80, 40, randomParticle),
    Button("↑", -300, 100, 40, 40, up),
    Button("↓", -300, 0, 40, 40, down),
    Button("←", -350, 50, 40, 40, left),
    Button("→", -250, 50, 40, 40, right),
    Button("Toggle P/P", 300, -50, 80, 40, particlePlanetSwap),
]

def update():
    for p in particles:
        p.resetForce()

    for i in range(len(particles)):
        for j in range(i):
            particles[i].computeGravitationalAttraction(particles[j])

    for p in particles:
        p.move()

    screen.update()
    screen.ontimer(update, int(abs(tick) * 1000)) 

canvas = screen.getcanvas()
canvas.bind("<ButtonPress-1>", handleMousePress)
canvas.bind("<ButtonRelease-1>", handleMouseRelease)
canvas.bind("<ButtonRelease-2>", handleRightClick)
canvas.bind("<ButtonPress-2>", handleRightDragStart)
canvas.bind("<B2-Motion>", handleRightDragMotion)

canvas.bind("<ButtonPress-1>", handleMousePress)
canvas.bind("<ButtonRelease-1>", handleMouseRelease)
canvas.bind("<Control-ButtonRelease-1>", handleRightClick)
canvas.bind("<Control-ButtonPress-1>", handleRightDragStart)
canvas.bind("<Control-B1-Motion>", handleRightDragMotion)

for key, func in keybinds.items():
    screen.onkey(func, key)

screen.listen()
update()
turtle.mainloop()


