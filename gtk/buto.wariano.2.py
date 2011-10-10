import sys, gtk, time, random
l = c = m = 10
def onMinaPressed( button, x , y, campo ):
   if campo[ 'minas' ][ x ][ y ] == True:
       print 'Perdiste'
       sys.exit( 0 )
   else:
       button.set_label( str( campo[ 'numeros' ][ x ][ y ] ) )

def getCampo( filas = 10, columnas = 10, minas = 10 ):
   l = [ [ 0 for x in range( columnas ) ] for y in range( filas ) ]
   m = [ [ False for x in range( columnas ) ] for y in range( filas ) ]
   for x in range( minas ):
       (x , y) = ( random.randint( 0, columnas - 1 ), random.randint( 0, filas - 1 ) )
       while m[ y ][ x ] != False:
           (x , y) = ( random.randint( 0, columnas - 1 ), random.randint( 0, filas - 1 ) )
       m[ y ][ x ] = True
       for i in range( -1,1 ):
           for j in range( -1,1 ):
               l[ x + i ][ y + j ] += 1
   return { 'numeros' : l, 'minas' : m }

campo = getCampo( l, c, m )
w = gtk.Window()
w.set_title( 'HKmine' )
w.set_default_size( l * 15, c * 15 )
w.connect( 'delete-event', lambda *l: sys.exit( -1 ) )
v = gtk.VBox()
for y in range( l ):
   h = gtk.HBox()
   for x in range( c ):
       b = gtk.Button( '  ' )
       b.connect( 'clicked', onMinaPressed, x, y, campo )
       h.pack_start( b )
   v.pack_start( h )
w.add( v )
w.show_all()
gtk.main()
