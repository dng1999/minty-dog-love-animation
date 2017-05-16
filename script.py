import mdl
from display import *
from matrix import *
from draw import *

global num_frames
num_frames = 1
global basename
basename = 'simple'
global knobs
knobs = []

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    global num_frames
    global basename

    frames = -1
    bname = -1
    vary = -1
    index = 0
    for command in commands:
        if command[0] == 'frames':
            frames = index
        elif command[0] == 'basename':
            bname = index
        elif command[0] == 'vary':
            vary = index
        index += 1
    #        
    if vary > -1 and frames == -1:
        print "Error: Frames not specified."
        return
    #
    elif frames > -1 and bname == -1:
        print "Warning: Basename not specified."
        print "Basename has been set to default value: simple"
    #
    num_frames = int(commands[frames][1])
    basename = commands[bname][1]
        
"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    global knobs
    #print "======= second_pass"
    for i in range(num_frames):
        knobs.append({})
    for command in commands:
        if command[0] == 'vary':
            vary = command[1]
            start_frame = command[2]
            end_frame = command[3]
            start_val = float(command[4])
            end_val = float(command[5])
            increment = (end_val-start_val)/(end_frame-start_frame)
            curr_val = float(command[4])
            #print "vary",vary,start_frame,end_frame,start_val,end_val,increment
            for i in range(num_frames):
                if i >= start_frame and i<= end_frame:
                    knobs[i][vary] = curr_val
                    curr_val += increment
                    
def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )
    screen = new_screen()
    
    p = mdl.parseFile(filename)
    
    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return
    print symbols

    first_pass(commands)
    second_pass(commands, num_frames)

    for i in range(num_frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        #screen = new_screen()
        tmp = []
        step = 0.1
        for command in commands:
            #print command
            c = command[0]
            args = command[1:]

            if c == 'set':
                symbols[args[0]][0] = float(args[1])
            elif c == 'setknobs':
                keys = symbols.keys()
                for i in range(len(keys)):
                    symbols[keys[i]][1] = float(args[1])
            elif c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if args[3] != None:
                    a0 = args[0] * knobs[i][args[3]]
                    a1 = args[1] * knobs[i][args[3]]
                    a2 = args[2] * knobs[i][args[3]]
                    args = [a0,a1,a2,args[3]]
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if args[3] != None:
                    a0 = args[0] * knobs[i][args[3]]
                    a1 = args[1] * knobs[i][args[3]]
                    a2 = args[2] * knobs[i][args[3]]
                    args = [a0,a1,a2,args[3]]
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if args[2] != None:
                    a1 = args[1] * knobs[i][args[2]]
                    args = [args[0],a1,args[2]]
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        #save frame
        fname = 'anim/' + basename + "%03d"%i + '.ppm'
        
        save_ppm(screen, fname)
        clear_screen(screen)

    make_animation(basename)
