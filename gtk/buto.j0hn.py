#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import gtk
import random
import gobject

PLAYER = "  /\\\n[    ]"
ENEMIE = "/MM\\\n\~~/"
BLANK = " "*10 + "\n" + " "*10
EXPLOSION = "\   |   /\n/   |   \ "
BULLET = "||"

class MainWindow(gtk.Window):
    '''Main window'''
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Space Invaders")
        self.set_default_size(450,450)
        self.set_border_width(0)
        
        self.connect("destroy", gtk.main_quit)
        #self.connect("event", self.on_key_press)
        
        self.table = gtk.Table(20)
        self.table.set_border_width(5)
        
        self.grid = []
        self.score = 0
        self.lives = 3
        self.posY = 9
        self.posX = 0
        self.shootPosY = 8
        self.canShoot = True
        
        self.numEnemies = 0
        self.enemiesSpeed = 500
        
        x = 0
        y = 0

        for i in range(10):
            self.grid.append([])
            for j in range(10):
                if x == 10:
                    x = 0
                    y += 1

                label = gtk.Label(BLANK)
                label.shoot = False
                label.enemie = False
                label.posX = x
                label.posY = y
                
                self.grid[i].append(label)
                self.table.attach(label, x, x+1, y, y+1) 
                x += 1
        
        #score and lives labels
        self.scoreLabel = gtk.Label("Score: 0")
        self.livesLabel = gtk.Label("Lives: 3")
        self.scoreLivesVbox = gtk.VBox(spacing=5)
        self.scoreLivesVbox.pack_start(self.scoreLabel, False)
        self.scoreLivesVbox.pack_start(self.livesLabel, False)
        
        self.headerLabel = gtk.Label()
        header = "<big><b>Space Invaders</b></big>\n"
        header += "     <i>(gtk+ version)</i>"
        self.headerLabel.set_markup(header)
        
        #header
        self.headerHbox = gtk.HBox(spacing=5)
        self.headerHbox.set_border_width(5)
        self.headerHbox.pack_start(self.headerLabel, False)
        self.headerHbox.pack_end(self.scoreLivesVbox, False)
        
        #menubar
        self.menuBar = MenuBar()
        
        
        #Frames (just to look nicer :) )
        
        self.tableFrame = gtk.Frame()
        self.tableFrame.set_border_width(5)
        self.tableFrame.add(self.table)
        
        self.headerFrame = gtk.Frame()
        self.headerFrame.set_border_width(5)
        self.headerFrame.add(self.headerHbox)
        
        #add everything
        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.menuBar, False)
        self.vbox.pack_start(self.headerFrame, False)
        self.vbox.pack_start(self.tableFrame)
       
        for i in self.grid[0][3:7]:
            i.set_label(ENEMIE)
            i.enemie = True
            self.numEnemies += 1
                
        for i in self.grid[2][2:8]:
            i.set_label(ENEMIE)
            i.enemie = True
            self.numEnemies += 1

        self.add(self.vbox)
        self.show_all()
        label = "<big><b>Space Invaders</b></big> "
        label += "<i>(gtk+ version)</i>\n"
        label += "\n Controls:\n  - Arrow keys: Move ship\n"
        label += "  - Spacebar: Shoot\n\n"
        label += "Start game?\n"
        MenuDialog(self, label, self.startGame).run()

        self.grid[len(self.grid)-1][0].set_label(PLAYER)
        self.grid[len(self.grid)-1][0].grab_focus()

    def startGame(self):
        self.connect("event", self.on_key_press)
        self.moveEnemieTimeout = gobject.timeout_add(self.enemiesSpeed, \
                                   self.moveEnemies)
   
    def restart(self):
        self.hide()
        game = MainWindow()

    def do_shoot(self, posX, posY):
        if self.shootPosY != -1:
            prevShoot = self.grid[self.shootPosY+1][posX]
            newShoot = self.grid[self.shootPosY][posX]
            if prevShoot.get_label() == BULLET:
                prevShoot.set_label(BLANK)

            if newShoot.enemie:
                newShoot.set_label(EXPLOSION)
                newShoot.enemie = False
                self.score += 100
                self.scoreLabel.set_label("Score: " + str(self.score))
                self.numEnemies -= 1
                if self.numEnemies == 0:
                    self.restart()
            elif self.shootPosY == 0 and not newShoot.enemie:
                newShoot.set_label(BLANK)
                self.shootPosY = 8
                self.canShoot = True
                self.score -= 10
                self.scoreLabel.set_label("Score: " + str(self.score))
                return False
            elif newShoot.get_label() == EXPLOSION:
                newShoot.set_label(BLANK)
                self.shootPosY = 8
                self.canShoot = True
                return False
            else:
                newShoot.set_label(BULLET)
                self.shootPosY -= 1
        return True

    def moveEnemies(self):
        for row in self.grid[::-1]:
            for label in row[::-1]:
                if label.enemie:
                    if label.posX == self.posX and label.posY == self.posY:
                        self.restart()
                        return #game over
                    if label.posX == 9:
                        destX = 0
                        destY = label.posY + 1
                        
                        gobject.source_remove(self.moveEnemieTimeout)
                        if self.enemiesSpeed > 50:
                            self.enemiesSpeed -= 5
                        self.moveEnemieTimeout = gobject.timeout_add(self.enemiesSpeed, self.moveEnemies)
                        
                    else:
                        destX = label.posX + 1
                        destY = label.posY
                    
                    label.enemie = False
                    label.set_label(BLANK)
                    
                    nextLabel = self.grid[destY][destX]
                    nextLabel.set_label(ENEMIE)
                    nextLabel.enemie = True
                    
        return True

    def on_key_press(self, widget, event):
        if event.type == gtk.gdk.KEY_PRESS:
            if event.keyval == gtk.keysyms.space:
                if self.canShoot:
                    self.canShoot = False
                    gobject.timeout_add(200, self.do_shoot, self.posX, self.posY)
            elif event.keyval == gtk.keysyms.Right:
                if self.posX < 9:
                    self.grid[self.posY][self.posX].set_label(BLANK)
                    self.grid[self.posY][self.posX].grab_focus()
                    self.posX += 1
                    self.grid[self.posY][self.posX].set_label(PLAYER)

            elif event.keyval == gtk.keysyms.Left:
                if self.posX > 0:
                    self.grid[self.posY][self.posX].set_label(BLANK)
                    self.grid[self.posY][self.posX].grab_focus()
                    self.posX -= 1
                    self.grid[self.posY][self.posX].set_label(PLAYER)

class MenuDialog(gtk.Dialog):
    def __init__(self, parent, text, callback):
        title = "Gtk Space Invaders"
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, \
                  gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)

        gtk.Dialog.__init__(self, title, parent, flags, buttons)

        self.callback = callback

        self.hbox = gtk.HBox()

        self.label = gtk.Label()
        self.label.set_markup(text)
        self.vbox.pack_start(self.label)
        self.show_all()

    def run(self):
        option = gtk.Dialog.run(self)
        if option == gtk.RESPONSE_ACCEPT:
            self.callback()
        elif option == gtk.RESPONSE_REJECT:
            gtk.main_quit()

        self.destroy()

class MenuBar(gtk.MenuBar):
    '''Menubar from main window'''

    def __init__(self):

        gtk.MenuBar.__init__(self)

        # File Menu
        FileMenu = gtk.Menu()
        FileItem = gtk.MenuItem("_File")
        FileItem.set_submenu(FileMenu)

        quitItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quitItem.connect("activate", gtk.main_quit)

        # Help Menu
        HelpMenu = gtk.Menu()
        HelpItem = gtk.MenuItem("_Help")
        HelpItem.set_submenu(HelpMenu)

        aboutItem = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        aboutItem.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
        aboutItem.connect("activate", self.onAboutItem)

        FileMenu.add(quitItem)
        HelpMenu.add(aboutItem)

        self.add(FileItem)
        self.add(HelpItem)

    def onAboutItem(self, *args):
        self.about = gtk.AboutDialog()
        self.about.set_name("Space invaders")
        self.about.set_comments("(gtk+ version)")
        self.about.set_authors([ "j0hn (j0hn.com.ar@gmail.com)"])

        self.about.connect('response', lambda dialog, id: dialog.hide())
        self.about.run()


if __name__ == "__main__":
    MainWindow()
    gtk.main()
