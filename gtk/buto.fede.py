#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import gtk
import gobject
import random

class game(gtk.Window):
    
    def __init__(self):
        
        gtk.Window.__init__(self)
        self.set_title("buto???¡?¡¡?¡??¡?")
        self.connect("destroy", gtk.main_quit)
        self.set_default_size(350,250)
        self.set_border_width(15)
        
        self.die = False
        
        '''Create the buttons'''
        self.button1Line1 = gtk.Button()
        self.button2Line1 = gtk.Button()
        self.button3Line1 = gtk.Button()
        self.button4Line1 = gtk.Button()
        self.button5Line1 = gtk.Button()

        self.button1Line2 = gtk.Button()
        self.button2Line2 = gtk.Button()
        self.button3Line2 = gtk.Button()
        self.button4Line2 = gtk.Button()
        self.button5Line2 = gtk.Button()

        self.button1Line3 = gtk.Button()
        self.button2Line3 = gtk.Button()
        self.button3Line3 = gtk.Button()
        self.button4Line3 = gtk.Button()
        self.button5Line3 = gtk.Button()
        
        self.hboxLine1 = gtk.HBox(True, 4)
        self.hboxLine2 = gtk.HBox(True, 4)
        self.hboxLine3 = gtk.HBox(True, 4)

        self.hboxLine1.pack_start(self.button1Line1)
        self.hboxLine1.pack_start(self.button2Line1)
        self.hboxLine1.pack_start(self.button3Line1)
        self.hboxLine1.pack_start(self.button4Line1)
        self.hboxLine1.pack_start(self.button5Line1)

        self.hboxLine2.pack_start(self.button1Line2)
        self.hboxLine2.pack_start(self.button2Line2)
        self.hboxLine2.pack_start(self.button3Line2)
        self.hboxLine2.pack_start(self.button4Line2)
        self.hboxLine2.pack_start(self.button5Line2)

        self.hboxLine3.pack_start(self.button1Line3)
        self.hboxLine3.pack_start(self.button2Line3)
        self.hboxLine3.pack_start(self.button3Line3)
        self.hboxLine3.pack_start(self.button4Line3)
        self.hboxLine3.pack_start(self.button5Line3)
        
        self.vbox = gtk.VBox(True, 4)

        self.vbox.pack_start(self.hboxLine1)
        self.vbox.pack_start(self.hboxLine2)
        self.vbox.pack_start(self.hboxLine3)

        '''initial position of the car'''
        self.posX = 2
        #self.posY = 3
        #print "Initial position: " + str(self.posX) #\nX= " + str(self.posX) + "\nY= " + str(self.posY) + "\n"

        self.UpdatePosition(self.posX)

        self.add(self.vbox)
        
        self.show_all()

        self.connect("event", self.Event)
        #self.connect("key_press_event", lambda w,e: self.KeyPress(self,e))

        '''list of buttons'''
        self.buttonList = [[self.button1Line1,self.button1Line2,self.button1Line3],[self.button2Line1,self.button2Line2,self.button2Line3],[self.button3Line1,self.button3Line2,self.button3Line3],[self.button4Line1,self.button4Line2,self.button4Line3],[self.button5Line1,self.button5Line2,self.button5Line3]]        

        '''interval'''
        self.velocity = 800
        gobject.timeout_add(self.velocity, self.UpdateEnemies)
        
        '''Quantity of enemies'''
        #self.enemiesQuantity = [1,2,3,4,5]
        self.enemies = []
        self.enemiesFlag = 0
        self.SpawnEnemies()
    
    def SpawnEnemies(self):
        quantity = random.randrange(1,6)
        for i in range(1,quantity):
            position = random.randrange(0,5)
            #print position
            self.enemies.append([position,0])
            self.MoveEnemy(position,0)
        #print self.enemies

    def MoveEnemy(self,x,y):
        self.buttonList[x][y].set_label("V")
    

    def DeleteEnemy(self,x,y):
        #self.enemies.pop(enemy)
        #self.buttonList[self.enemies[enemy][0]][self.enemies[enemy][1]].set_label("")
        self.buttonList[x][y].set_label("")

    
    def UpdateEnemies(self):
    
        if (self.die == False):
        
            for i in self.enemies:
            
                if (i[1] < 2):
                
                    self.DeleteEnemy(i[0],i[1])
                    i[1] += 1
                    if ( i[0] == self.posX and i[1] == 2 ):
                        self.Die()
                        return False
                    else:
                        self.MoveEnemy(i[0],i[1])
                        
                elif (i[1] == 2):

                    if ( i[0] == self.posX ):
                        self.Die()
                        return False
                    else:
                        self.DeleteEnemy(i[0],i[1])
                        i[1] += 1
        
            if (self.enemiesFlag == 0):   
                self.SpawnEnemies()
                self.enemiesFlag = 1
            else:
                self.enemiesFlag = 0
                
                
            if (self.velocity <= 400):
                self.velocity -= 3
            elif (self.velocity <= 350):
                self.velocity -= 2
            elif (self.velocity <= 300):
                self.velocity -= 1
            elif (self.velocity <= 2):
                self.velocity = 1
            else:
                self.velocity -= 5
            
            gobject.timeout_add(self.velocity, self.UpdateEnemies)
            
            return False
            
        else:
            return False

    def UpdatePosition(self,x):
        
        buttonList = [self.button1Line3,self.button2Line3,self.button3Line3,self.button4Line3,self.button5Line3]
        
        if (buttonList[x].get_label() != "V" ):
        
            for i in range(0,5):
                if (buttonList[i].get_label() == "A"):       
                    buttonList[i].set_label("")
                    buttonList[i].set_sensitive(True)
            
            #buttonList[x].grab_focus()
            buttonList[x].set_label("A")
            buttonList[x].set_sensitive(False)
            
        else:
            self.Die()

    def Event(self,widget,event):
    
        if (self.die == False):
        
            if event.type == gtk.gdk.KEY_PRESS:
                if event.keyval == gtk.keysyms.Right:
                    if (self.posX < 4):
                        self.posX += 1
                    else:
                        self.posX = 4
                    self.UpdatePosition(self.posX)

                elif event.keyval == gtk.keysyms.Left:
                    if (self.posX > 0):
                        self.posX -= 1
                    else:
                        self.posX = 0
                    self.UpdatePosition(self.posX)
                
                
    def Die(self):
        self.die = True
        self.hide()
        Message("You loose nigga, play again?", "HAHAHAHA").show()

class Message(gtk.Dialog):
    
    def __init__(self, message, title):
        gtk.Dialog.__init__(self, title, None, \
                  gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT , \
                  (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, \
                   gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        
        self.set_resizable(False)
        self.set_has_separator(False)
        self.set_border_width(6)
        self.vbox.set_spacing(12)

        text = gtk.Label(message)
        
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE , gtk.ICON_SIZE_DIALOG)
        image.set_alignment(0.0, 0.5)

        hbox = gtk.HBox()
        hbox.set_spacing(12)
        hbox.set_border_width(6)
        hbox.pack_start(image)
        hbox.pack_start(text)

        self.vbox.pack_start(hbox)
        self.vbox.show_all()

    def show(self):
        option = gtk.Dialog.run(self)
        if option == gtk.RESPONSE_ACCEPT:
            game()
            self.destroy()
        else:
            gtk.main_quit()
        
        
if __name__ == "__main__":
    game()
    gtk.main()
