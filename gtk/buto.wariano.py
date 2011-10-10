import sys
import gtk
import random
import gobject

class Block(gtk.Label):
    CLEAN = '<span foreground="#000000" font_desc="monospace">O</span>'
    BLOCK =  '<span foreground="#cccccc" font_desc="monospace">#</span>'
    FOOD =  '<span foreground="#0000FF" font_desc="monospace">~</span>'

    def __init__(self):
        gtk.Label.__init__(self)
        self.set_clean()
    
    def is_clean(self):
        return self.get_label() == Block.CLEAN

    def is_block(self):
        return self.get_label() == Block.BLOCK
    
    def is_food(self):
        return self.get_label() == Block.FOOD

    def set(self, markup):
        self.set_markup(markup)
        
    def set_clean(self):
        self.set(Block.CLEAN)

    def set_block(self):
        self.set(Block.BLOCK)

    def set_food(self):
        self.set(Block.FOOD)

class Grid(gtk.Table):
    TEXT = '<span foreground="#FFFF00">%s</span>'
    def __init__(self, height=25, width=80):
        gtk.Table.__init__(self, height, width, True)
        self.height = height
        self.width = width

        self.labels = []

        for i in range(height):
            lst = []
            for j in range(width):
                block = Block()
                lst.append(block)
                self.attach(block, j, j + 1, i, i + 1)

            self.labels.append(lst)

        self.show_all()

    def __getitem__(self, index):
        return self.labels[index]

    def draw_text(self, text, x, y):
        for (i, xx) in enumerate(range(x, x + len(text))):
            self[y][xx].set_markup(Grid.TEXT % (text[i], ))

class Map(Grid):
    def __init__(self, height=25, width=80):
        Grid.__init__(self, height, width)
        self.score = 0
        self.blocks = []
        self.blocks += [(0, y) for y in range(height)]
        self.blocks += [(width - 1, y) for y in range(height)]
        self.blocks += [(x, 0) for x in range(width)]
        self.blocks += [(x, height - 1) for x in range(width)]

        self.food = None
        self.generate_food()

        self.draw_blocks()

    def draw_blocks(self):
        for (x, y) in self.blocks:
            self.draw_block(x, y)

    def draw_block(self, x, y):
        self[y][x].set_block()

    def generate_coords(self):
        return (random.randint(0, self.width - 1), 
            random.randint(0, self.height - 1))

    def generate_free_coords(self):
        '''generate coords on a free space'''
        (x, y) = self.generate_coords() 
        # have a nice time waiting if all are blocks :)
        # when you are full of blocks you will die eventually
        # if you use this for other things, you will enter on an infinite
        # loop searching for a free space, but hey! this is a buto!
        while self.collide(x, y):
            (x, y) = self.generate_coords()

        return (x, y)

    def collide(self, x, y):
        '''return true if collide with something on the map'''
        return (x, y) in self.blocks or (x, y) == self.food

    def generate_food(self):
        self.food = self.generate_free_coords()

    def generate_block(self):
        block = self.generate_free_coords()
        self.draw_block(*block)
        self.blocks.append(block)

    def draw_food(self):
        (x, y) = self.food

        self[y][x].set_food()
    
    def draw_score(self):
        score = "SCORE: %d" % (self.score,)
        self.draw_text(score, self.width - len(score), 0)

class Viboda(object):
    BODY = '<span foreground="#00FF00" font_desc="monospace">O</span>'

    def __init__(self, x, y, x_dir=1, y_dir=0):
        self.x = x
        self.y = y
        self.x_dir = x_dir
        self.y_dir = y_dir
        self.parts = [(x, y)]
                
    def process(self, grow=False):
        last_part = self.parts[-1]

        for i in range(len(self.parts))[::-1]:
            if i > 0:
                self.parts[i] = self.parts[i - 1]

        (x, y) = self.parts[0]
        self.parts[0] = (x + self.x_dir, y + self.y_dir)

        if grow:
            self.parts.append(last_part)

    def collision(self):
        if self.parts[0] in self.parts[1:]:
            return True
        
        return False

    def __getitem__(self, index):
        return self.parts[index]        

    def __len__(self):
        return len(self.parts)

class Game(object):
    def __init__(self):
        self.window = gtk.Window()
        self.window.modify_bg(gtk.STATE_NORMAL, 
            gtk.gdk.color_parse("#000000"))
        self.window.get_settings().\
            set_string_property('gtk-font-name', 'monospace 10','')

        self.map = Map()
        self.viboda = Viboda(40, 12, 1, 0)
        self.window.add(self.map)
        self.window.connect("delete-event", gtk.main_quit)
        self.window.connect("key-press-event", self._on_key_press)

        self.up = self.down = self.left = self.right = False
        self.right = True

        self.window.show()

    def _on_key_press(self, window, event):
        if event.keyval == gtk.keysyms.Up and not self.down:
            self.up = True
            self.down = False
            self.left = False
            self.right = False

            self.viboda.x_dir = 0
            self.viboda.y_dir = -1
        elif event.keyval == gtk.keysyms.Down and not self.up:
            self.down = True
            self.up = False
            self.left = False
            self.right = False

            self.viboda.x_dir = 0
            self.viboda.y_dir = 1
        elif event.keyval == gtk.keysyms.Left and not self.right:
            self.left = True
            self.right = False
            self.down = False
            self.up = False
            
            self.viboda.x_dir = -1
            self.viboda.y_dir = 0
        elif event.keyval == gtk.keysyms.Right and not self.left:
            self.right = True
            self.left = False
            self.down = False
            self.up = False
            
            self.viboda.x_dir = 1
            self.viboda.y_dir = 0
        
    def start(self):
        text = "Mariano's buto (codename \"Viboda\")"
        self.map.draw_text(text, (self.map.width - len(text)) / 2, 
            self.map.height / 2)
        gobject.timeout_add(5000, self._really_start)

    def _really_start(self):
        text = "                                    "
        self.map.draw_text(text, (self.map.width - len(text)) / 2, 
            self.map.height / 2)
        gobject.timeout_add(150, self.process)
        self.map.draw_food()
        self.map.draw_score()

    def process(self):
        grow = False
        (last_x, last_y) = self.viboda[-1]
        (x, y) = self.viboda[0]

        if self.map[y + self.viboda.y_dir][x + self.viboda.x_dir].\
                is_block():
            self.loose()
            return False
        elif self.map[y + self.viboda.y_dir][x + self.viboda.x_dir].\
            is_food():
            grow = True
            self.map.generate_food()
            self.map.generate_block()
            self.map.draw_food()
            self.map.score += 1
            self.map.draw_score()
        if self.viboda.collision():
            self.loose()
            return False
        
        self.viboda.process(grow)
        (x, y) = self.viboda[0]
        
        self.map[y][x].set(Viboda.BODY)
        self.map[last_y][last_x].set_clean()

        return True

    def loose(self):
        text = "Looser"
        self.map.draw_text(text, (self.map.width - len(text)) / 2, 
            self.map.height / 2)
        
        gobject.timeout_add(5000, self.quit)

    def quit(self):
        sys.exit(0)
                
g = Game()
g.start()
gtk.main()
