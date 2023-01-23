#! /usr/bin/python3 -B

import itertools
import platform
import tkinter as tk
import tkinter.ttk as ttk

__all__ = ['ScrollableFrameTk']

###############################################################################

class ScrollableFrameTk(ttk.Frame):
    '''
Container with horizontal and vertical scrolling capabilities. Widgets must be
added to its `frame` attribute.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Scrollable canvas. This is the widget which actually manages
        # scrolling. Using the grid geometry manager ensures that the
        # horizontal and vertical scrollbars do not meet.
        self._canvas = tk.Canvas(self)
        self._canvas.bind_all('<Button-4>', self._on_mouse_scroll)
        self._canvas.bind_all('<Button-5>', self._on_mouse_scroll)
        self._canvas.bind_all('<MouseWheel>', self._on_mouse_scroll)
        self._canvas.bind('<Configure>', self._on_canvas_configure)
        self._canvas.grid(row=0, column=0, sticky=tk.NSEW)

        xscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._xview)
        xscrollbar.grid(row=1, column=0, sticky=tk.EW)
        yscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._yview)
        yscrollbar.grid(row=0, column=1, sticky=tk.NS)
        self._canvas.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame = ttk.Frame(self._canvas)
        self._window = self._canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)
        self.frame.bind('<Configure>', self._on_frame_configure)

        # Initially, the vertical scrollbar is a hair below its topmost
        # position. Move it to said position. No harm in doing the equivalent
        # for the horizontal scrollbar.
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

    ###########################################################################

    def _xview(self, *args, width=None):
        '''
Called when the horizontal scrollbar is moved. Called indirectly when the
canvas or frame is resized. Scroll the view only if it is not completely
visible. Otherwise, move the scrollbar to such a position that the contents of
the canvas are horizontally centred.

:param args: Tuple which can be passed to `tkinter.Canvas.xview`.
:param width: Width of the canvas.
        '''

        if self._canvas.xview() != (0.0, 1.0):
            self._canvas.xview(*args)
        else:
            width = width or self._canvas.winfo_width()

            # To move the contents of the canvas to the centre, I call this
            # function with a negative argument. I don't know if this hack is
            # supported (because the Tcl/Tk manual pages say that it must be a
            # fraction between 0 and 1), but it works!
            self._canvas.xview_moveto((1 - width / self.frame.winfo_width()) / 2)

    ###########################################################################

    def _yview(self, *args):
        '''
Called when the vertical scrollbar is moved. Called indirectly when the mouse
wheel is scrolled. Scroll the view only if it is not completely visible.

:param args: Tuple which can be passed to `tkinter.Canvas.yview`.
        '''

        if self._canvas.yview() != (0.0, 1.0):
            self._canvas.yview(*args)

    ###########################################################################

    def _on_canvas_configure(self, event):
        '''
Called when the canvas is resized. Update the scrollable region. Perform a
dummy horizontal scroll in order to trigger horizontal realignment.

:param event: Configure event.
        '''

        self._canvas.configure(scrollregion=self._canvas.bbox(tk.ALL))
        self._xview(tk.SCROLL, 0, tk.UNITS, width=event.width)

    ###########################################################################

    def _on_frame_configure(self, event):
        '''
Called when the frame is resized. Update the scrollable region. Perform a dummy
horizontal scroll in order to trigger horizontal realignment.

This method is necessary to handle updates which may occur after the GUI loop
has started.

:param event: Configure event.
        '''

        self._canvas.configure(scrollregion=self._canvas.bbox(tk.ALL))
        self._xview(tk.SCROLL, 0, tk.UNITS)

    ###########################################################################

    def _on_mouse_scroll(self, event):
        '''
Called when the mouse wheel is scrolled. Asks to scroll the view vertically.

:param event: Scroll event.
        '''

        system = platform.system()
        if system == 'Linux':
            if event.num == 4:
                self._yview(tk.SCROLL, -1, tk.UNITS)
            elif event.num == 5:
                self._yview(tk.SCROLL, 1, tk.UNITS)
        elif system == 'Darwin':
            self._yview(tk.SCROLL, int(-1 * event.delta), tk.UNITS)
        elif system == 'Windows':
            self._yview(tk.SCROLL, int(-1 * event.delta / 120), tk.UNITS)

###############################################################################

def main():
    '''
Demonstrate how to use a scrollable frame.
    '''

    root = tk.Tk()
    root.title('`ScrollableFrameTk` Demo')

    # Create a scrollable frame.
    scrollable_frame = ScrollableFrameTk(root)

    # Add widgets to the `frame` attribute of the scrollable frame, not to the
    # scrollable frame itself.
    dim = 10
    for (i, j) in itertools.product(range(dim), range(dim)):
        ttk.Label(scrollable_frame.frame, text=f'Label\n({i}, {j})').grid(row=i, column=j, padx=10, pady=10)

    scrollable_frame.pack(expand=True, fill=tk.BOTH)
    root.mainloop()

###############################################################################

if __name__ == '__main__':
    main()
