import gtk
import math
import pango
import gobject
import random

WIDTH = HEIGHT = 400
GSIZE = 10

# config
FPS = 8
RANDOMIOS = 40 # percent of random (!)

class Asd(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        
        self.status = gtk.Label()
        self.vbox = gtk.VBox()

        self.fixed = gtk.Fixed()
        self.fixed.set_has_window(True)
        self.fixed.set_size_request(WIDTH, HEIGHT)
        
        self.stuff = []
        
        self.human = Human()
        self.register(self.human)
        self.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.connect('key-press-event', self.human.on_event)
        self.connect('key-release-event', self.human.on_event)
        
        self.vbox.pack_start(self.status)
        self.vbox.pack_start(self.fixed)
        self.add(self.vbox)
        self.show_all()

        gobject.timeout_add(int(1000 / FPS), self.cycle)

    def cycle(self):
        '''Called when the widget draws itself'''
        import time
        start = time.time()
        # lazy grid based collision detection. 
        grid = {}
        collisions = []

        for thing in self.stuff[:]:
            if not thing.interact() or \
               not check_collisions(thing, grid, collisions):
                self.kill(thing)
                continue
            self.fixed.move(thing, *thing.pos)

        for pos in collisions:
            var = list(set([isinstance(x, EvilThing) for x in grid[pos]]))
            if len(var) == 1 and not var[0]:
                continue
            
            for thing in grid[pos]:
                self.kill(thing)
        
        if self.human.alive:
            if random.randint(0, 100) < RANDOMIOS:
                self.register(Randomio())
            if random.randint(0, 100) < RANDOMIOS:
                self.register(Gironio())
        elif not self.stuff:
            self.destroy()
        
        self.status.set_text("%s things alive" % len(self.stuff))

        duration = time.time() - start
        if duration > 0.1:
            print duration

        return True
    
    def register(self, thing):
        self.fixed.put(thing, *thing.pos)
        self.stuff.append(thing)
        thing.show()
        thing.win = self

    def kill(self, thing):
        if thing in self.stuff:
            self.stuff.remove(thing)
            thing.destroy()
            thing.alive = False
            thing.pos = WIDTH / 2, int(HEIGHT * 1.5)


def check_collisions(thing, grid, collisions):
    '''this is the fast variant, uses only the upper-left corner'''
    x, y = thing.pos
    if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
        # if it gets out of the widget, we kill it
        return False

    gridpos = (y / GSIZE) * (WIDTH / GSIZE) + (x / GSIZE)
    
    if not gridpos in grid:
        grid[gridpos] = []
    grid[gridpos].append(thing)
    
    if len(grid[gridpos]) == 2:
        collisions.append(gridpos)
    return True

def check_collisions_slow(thing, grid, collisions):
    '''this is the slow variant, uses get_pixel_extents()'''
    ink, logical = thing.get_layout().get_pixel_extents()
    x1 = logical[0] + thing.pos[0]
    y1 = logical[1] + thing.pos[1]
    x2 = logical[2] + x1
    y2 = logical[3] + y1
    
    if x1 < 0 or x1 > WIDTH or y1 < 0 or y1 > HEIGHT or \
       x2 < 0 or x2 > WIDTH or y2 < 0 or y2 > HEIGHT:
        # if it gets out of the widget, we kill it
        return False

    grid_positions = set()
    for x, y in (x1, y1), (x1, y2), (x2, y1), (x2, y2):
        grid_positions.add((y / GSIZE) * (WIDTH / GSIZE) + x / GSIZE)

    for gridpos in grid_positions:
        if not gridpos in grid:
            grid[gridpos] = []
        grid[gridpos].append(thing)
    
        if len(grid[gridpos]) == 2:
            collisions.append(gridpos)
    return True
        

class Thing(gtk.Label):
    '''Abstract base for sprites'''

    def __init__(self):
        gtk.Label.__init__(self)
        self.pos = (WIDTH / 3, HEIGHT / 3)
        self.win = None
        self.alive = True

    def interact(self):
        pass

class RotatingThing(Thing):
    def __init__(self):
        Thing.__init__(self)
        self.angle = 0
        self.speed = 0

    # maths :D
    def rotate(self):
        if self.speed > 1:
            angle = math.radians(self.angle + 180)
            self.pos = int(self.pos[0] + math.sin(angle) * self.speed), \
                       int(self.pos[1] + math.cos(angle) * self.speed)
        else:
            self.speed = 0

        self.set_angle(self.angle)

class Human(RotatingThing):
    def __init__(self):
        RotatingThing.__init__(self)
        self.set_markup("<b>A</b>")
        self.pos = (WIDTH / 3 * 2, HEIGHT / 3 * 2)

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.space_pressed = False
        
        self.bombs = 10

    def interact(self):
        # counterclockwise
        if self.left_pressed:
            self.angle = (self.angle + 10) % 360

        if self.right_pressed:
            self.angle = self.angle - 10
            if self.angle < 0:
                self.angle += 360

        if self.up_pressed:
            self.speed = math.log10(self.speed + 2) * 5
        elif self.speed > 1:
            self.speed = math.log10(self.speed) * 5
        else:
            self.speed = 0
        
        if self.space_pressed:
            self.bomb(0, 2)
            self.bomb(30, 5)
            self.bomb(-30 , 5)
            self.bomb(15, 15)
            self.bomb(-15 , 15)
            self.bomb(50, 30)
            self.bomb(-50 , 30)

        self.bombs += 0.2

        self.rotate()
        return True

    def bomb(self, angle, require=0):
        if self.win and int(self.bombs) > require:
            self.win.register(Bomb(self, angle))
            self.bombs -= 1
        
    def on_event(self, widget, event):
        if event.type == gtk.gdk.KEY_PRESS:
            newval = True
        elif event.type == gtk.gdk.KEY_RELEASE:
            newval = False
        else:
            return
        
        if event.keyval == gtk.keysyms.Left:
            self.left_pressed = newval
        elif event.keyval == gtk.keysyms.Right:
            self.right_pressed = newval
        elif event.keyval == gtk.keysyms.Up:
            self.up_pressed = newval
        elif event.keyval == gtk.keysyms.space:
            self.space_pressed = newval


class Bomb(RotatingThing):
    def __init__(self, parent, angle):
        RotatingThing.__init__(self)
        self.set_text("^")

        self.pos = parent.pos
        self.angle = parent.angle + angle
        self.speed = 2
        self.rotate()

    def interact(self):
        self.rotate()
        return True

class EvilThing(RotatingThing):
    pass

class Randomio(EvilThing):
    def __init__(self):
        EvilThing.__init__(self)
        self.pos = (random.randint(int(WIDTH * 0.1), int(WIDTH * 0.9)),
                    random.randint(int(HEIGHT * 0.1), int(HEIGHT * 0.3)))
        self.set_text("?")

    def interact(self):
        if self.win:
            hx, hy = self.win.human.pos
            x, y = self.pos
            try:
                dx = int(math.log10(abs(hx - x)))
                dy = int(math.log10(abs(hy - y)))
            except:
                dx = dy = 0
            self.pos = (random.randint(x - 5, x + 5) + dx,
                        random.randint(y - 5, y + 5) + dy)
        return True

class Gironio(EvilThing):
    def __init__(self):
        RotatingThing.__init__(self)
        self.set_text("@")

        self.pos = (random.randint(int(WIDTH * 0.1), int(WIDTH * 0.9)),
                    random.randint(int(HEIGHT * 0.1), int(HEIGHT * 0.3)))
        self.angle = random.randint(0, 360)
        self.meaninglessangle = random.randint(0, 360)
        self.speed = 4
        self.rotate()

    def interact(self):
        if self.win:
            x = float(self.win.human.pos[0] - self.pos[0])
            y = self.win.human.pos[1] - self.pos[1]
            #self.pos = (self.pos[0] + x /2, self.pos[1] + y/2)
            if x:
                self.angle = math.degrees(1/math.tan(y/x)) + 180
                if self.angle < 0:
                    self.angle += 360
                elif self.angle > 360:
                    self.angle -= 360
                self.angle = int(self.angle)
        self.rotate()
        return True


def main():
    win = Asd()
    win.connect('destroy', gtk.main_quit)
    gtk.main()

if __name__ == '__main__':
    main()

