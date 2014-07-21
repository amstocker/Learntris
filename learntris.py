'''
::AUTHOR::
Andrew Stocker

::DESCRIPTION::
My implementation of Learntris for use with the Learntris test suite developed by the
#LearnProgramming community.

::LAST MODIFIED::
July 21, 2014

::NOTES::

'''
import sys
from copy import deepcopy
from random import randint



################################################################################
### LEARNTRIS ##################################################################


class Learntris:
    def __init__(self, width, height):
        self.titletext = 'Learntris (c) 1992 Tetraminex, Inc.\nPress start button to begin.'
        self.pausetext = 'Paused\nPress start button to continue.'
        
        self.w = width
        self.h = height
        
        self.grid = self.new_grid(self.w, self.h)

        self.score = 0
        self.clearedlines = 0

        self.shape_names = 'IOTJLSZ'
        self.active_tetramino = None
        self.active_coord = [0,0]
        self.add_active_tetramino(self.shape_names[randint(0, len(self.shape_names)-1)])

        self.intitle = False
        self.inpause = False
        self.paused_once = False  # wat


    def read_stdin(self):
        line = sys.stdin.readline().rstrip()

        commands = filter(lambda x: x not in ' ', list(line))

        i = 0
        LIM = len(commands)
        while i < LIM:
            cmd = commands[i]
            
            # newline control
            if cmd == ';':
                print

            # title and pause screen controls
            elif cmd == '@':
                self.intitle = True
            elif cmd == '!':
                if self.intitle:
                    self.intitle = False
                elif not self.paused_once:
                    self.paused_once = True
                else:
                    self.inpause = not self.inpause
            
            # grid controls
            elif cmd == 'p':        # print grid
                if self.intitle:
                    print self.titletext
                elif self.inpause:
                    print self.pausetext
                else:
                    self.print_static_grid()
            elif cmd == 'P':        # print with active tetramino
                self.print_active_grid()
            elif cmd == 'g':        # get grid from stdin
                self.read_grid()
            elif cmd == 'c':        # clear grid
                self.grid = self.new_grid(self.w, self.h)
            elif cmd == 's':        # step grid
                self.step()

            # query controls
            elif cmd == '?':
                next_cmd = commands[i+1]
                if next_cmd == 's':
                    print self.score
                elif next_cmd == 'n':
                    print self.clearedlines
                else:
                    print '>>>Invalid command:', cmd, next_cmd, 'in', commands

                i += 1

            # tetramino controls
            elif cmd in self.shape_names:
                self.add_active_tetramino(cmd)
            elif cmd == 't':
                self.active_tetramino.print_grid()

            # active tetramino movement controls
            elif cmd in '()<>vV':
                self.move_active_tetramino(cmd)
                if cmd == 'V':
                    self.place_active_tetramino()
                
            # exit
            elif cmd == 'q':
                return 0

            else:
                print '>>>Invalid command:', cmd, 'in', commands
            
            i += 1
            
        return True


    def new_grid(self, w, h):
        return {(i,j):'.' for i in xrange(w) for j in xrange(h)}

    
    def print_static_grid(self):
        w, h, grid = self.w, self.h, self.grid
        print '\n'.join([' '.join([grid[(i,j)] for i in xrange(w)]) for j in xrange(h)])

        
    def print_active_grid(self):
        w, h = self.w, self.h
        
        active = self.active_tetramino
        si, sj = self.active_coord

        info_dict = active.info_dict
        coords = info_dict['grid']
        color = info_dict['color']

        tmp_grid = deepcopy(self.grid)
        
        for i, j in coords:
            tmp_grid[(si+i, sj+j)] = color.upper()

        print '\n'.join([' '.join([tmp_grid[(i,j)] for i in xrange(w)]) for j in xrange(h)])


    def read_grid(self):
        lineindex = 0
        valid_chars = '.rgbcymo'
        
        while lineindex < self.h:
            line = sys.stdin.readline().rstrip()

            # split line and check for valid length
            linesplit = line.split(' ')
            
            if len(linesplit) != self.w:
                return

            # read items in line and check if item in valid characters list
            for i, c in enumerate(linesplit):
                if i < self.w:
                    if c.lower() not in valid_chars or len(c)>1:
                        return
                    self.grid[(i, lineindex)] = c
            
            lineindex += 1


    def add_active_tetramino(self, shape):
        self.active_tetramino = Tetramino(shape)
        active = self.active_tetramino
        
        gridsize = active.info_dict['gridsize'][0]  # tetramino grid height and width are the same
        
        self.active_coord[0] = 4 if gridsize < 3 else 3
        self.active_coord[1] = 0


    def move_active_tetramino(self, cmd):  
        next_active = deepcopy(self.active_tetramino)
        next_active_coord = deepcopy(self.active_coord)
            
        def check_and_do_move():
            next_active_grid = next_active.info_dict['grid']
            for ai, aj in next_active_grid:
                if not 0 <= next_active_coord[0]+ai < self.w:
                    return False
                if not next_active_coord[1]+aj < self.h:
                    return False
                if not self.grid[(next_active_coord[0]+ai, next_active_coord[1]+aj)] == '.':
                    return False

            self.active_tetramino = deepcopy(next_active)
            self.active_coord = deepcopy(next_active_coord)

            return True
        
        if cmd == ')':
            next_active.rotate('cw')
        elif cmd == '(':
            next_active.rotate('ccw')
        elif cmd == '<':
            next_active_coord[0] -= 1
        elif cmd == '>':
            next_active_coord[0] += 1
        elif cmd == 'v':
            next_active_coord[1] += 1
        elif cmd == 'V':
            while 1:
                next_active_coord[1] += 1
                valid = check_and_do_move()
                if not valid:
                    return

        check_and_do_move()
            
            
    def place_active_tetramino(self):
        active = self.active_tetramino
        active_coord = self.active_coord
        active_grid = active.info_dict['grid']
        color = active.info_dict['color']

        for ai, aj in active_grid:
            self.grid[(active_coord[0]+ai, active_coord[1]+aj)] = color

        self.add_active_tetramino(self.shape_names[randint(0, len(self.shape_names)-1)])
                

    def step(self):

        def clear_row(j):
            for i in xrange(self.w):
                self.grid[(i,j)] = '.'
        
        # check for full rows
        for j in xrange(self.h):
            row = ''.join([self.grid[(i,j)] for i in xrange(self.w)])
            if '.' not in row:
                clear_row(j)
                self.score += 100
                self.clearedlines += 1



################################################################################
### TETRAMINO CLASS ############################################################


class Tetramino:
    def __init__(self, shape):
        if shape not in 'IOTJLSZ':
            raise TypeError
        
        self.shape_name = shape

        self.shape_lookup = {'I':{'color':      'c',
                                  'gridsize':   (4,4),
                                  'grid':       [(0,1), (1,1), (2,1), (3,1)]
                                  },
                             'O':{'color':      'y',
                                  'gridsize':   (2,2),
                                  'grid':       [(0,0), (1,0), (0,1), (1,1)]
                                  },
                             'T':{'color':      'm',
                                  'gridsize':   (3,3),
                                  'grid':       [(1,0), (0,1), (1,1), (2,1)]
                                  },
                             'J':{'color':      'b',
                                  'gridsize':   (3,3),
                                  'grid':       [(0,0), (0,1), (1,1), (2,1)]
                                  },
                             'L':{'color':      'o',
                                  'gridsize':   (3,3),
                                  'grid':       [(2,0), (0,1), (1,1), (2,1)]
                                  },
                             'S':{'color':      'g',
                                  'gridsize':   (3,3),
                                  'grid':       [(1,0), (2,0), (0,1), (1,1)]
                                  },
                             'Z':{'color':      'r',
                                  'gridsize':   (3,3),
                                  'grid':       [(0,0), (1,0), (1,1), (2,1)]
                                  }
                             }

        # configure representation grid
        self.info_dict = self.shape_lookup[shape]
        self.w, self.h = self.info_dict['gridsize']


    def print_grid(self):
        grid = {(i,j):'.' for i in xrange(self.w) for j in xrange(self.h)}
        for coord in self.info_dict['grid']:
            grid[coord] = self.info_dict['color']

        w, h = self.w, self.h
        print '\n'.join([' '.join([grid[(i,j)] for i in xrange(w)]) for j in xrange(h)])

        
    def rotate(self, direc):
        tmp_grid = []

        for coord in self.info_dict['grid']:
            i, j = coord
            if direc == 'cw':
                new_i = (self.h-1)-j
                new_j = i
            elif direc == 'ccw':
                new_i = j
                new_j = (self.w-1)-i
            tmp_grid.append( (new_i, new_j) )

        self.info_dict['grid'] = tmp_grid



################################################################################
### MAIN LOOP ##################################################################


def start(width, height):
    # Learntris grid
    learntris = Learntris(width, height)

    # runtime loop
    run_status = True
    while run_status:
        run_status = learntris.read_stdin()


start(10, 22)



