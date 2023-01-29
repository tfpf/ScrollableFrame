#! /usr/bin/python3 -B

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
        self._canvas.bind('<Enter>', self._on_enter)
        self._canvas.bind('<Leave>', self._on_leave)
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
        self._on_frame_expose_id = self.frame.bind('<Expose>', self._on_frame_expose)

        # Initially, the vertical scrollbar is a hair below its topmost
        # position. Move it to said position. No harm in doing the equivalent
        # for the horizontal scrollbar.
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

    ###########################################################################

    def _xview(self, *args, width=None):
        '''
Called when the horizontal scrollbar is moved. Called by some other callbacks
(`_on_canvas_configure` and `_on_frame_configure`) whenever it is necessary to
horizontally realign the contents of the canvas. Scroll the view only if the
contents are not completely visible. Otherwise, move the scrollbar to such a
position that they are horizontally centred.

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
Called when the canvas is resized. Update the scrollable region.

:param event: Configure event.
        '''

        self._canvas.configure(scrollregion=self._canvas.bbox(tk.ALL))
        self._xview(tk.SCROLL, 0, tk.UNITS, width=event.width)

    ###########################################################################

    def _on_frame_configure(self, event=None):
        '''
Called when the frame is resized or the canvas is scrolled. Update the
scrollable region.

This method is necessary to handle updates which may occur after the GUI loop
has started.

:param event: Configure event.
        '''

        self._canvas.configure(scrollregion=self._canvas.bbox(tk.ALL))
        self._xview(tk.SCROLL, 0, tk.UNITS)

    ###########################################################################

    def _on_frame_expose(self, event=None):
        '''
Called when the frame becomes visible. Call `_on_frame_configure` and then
disable this callback.

This method is necessary because if a scrollable frame is put into, say, a
notebook (as opposed to a toplevel window), and the canvas is wider than its
contents, then (on Linux) the contents are not initially horizontally centred.
(This issue is not observed on Windows, probably because its frame configure
events work differently.) Hence, I try to centre the contents again upon an
expose event.

:param event: Expose event.
        '''

        self._on_frame_configure()
        self.frame.unbind('<Expose>', self._on_frame_expose_id)

    ###########################################################################

    def _on_enter(self, event=None):
        '''
Called when the mouse pointer enters the canvas. Set up vertical scrolling with
the mouse wheel.

:param event: Enter event.
        '''

        self._on_mouse_scroll_up_linux = self.bind_all('<Button-4>', self._on_mouse_scroll)
        self._on_mouse_scroll_down_linux = self.bind_all('<Button-5>', self._on_mouse_scroll)
        self._on_mouse_scroll_macos_windows = self.bind_all('<MouseWheel>', self._on_mouse_scroll)

    ###########################################################################

    def _on_leave(self, event=None):
        '''
Called when the mouse pointer leaves the canvas. Unset vertical scrolling with
the mouse wheel.

:param event: Leave event.
        '''

        self.unbind_all('<Button-4>')
        self.unbind_all('<Button-5>')
        self.unbind_all('<MouseWheel>')

    ###########################################################################

    def _on_mouse_scroll(self, event):
        '''
Called when the mouse wheel is scrolled. Ask to scroll the view vertically.

:param event: Scroll event.
        '''

        system = platform.system()
        if system == 'Linux':
            if event.num == 4:
                self._yview(tk.SCROLL, -1, tk.UNITS)
            elif event.num == 5:
                self._yview(tk.SCROLL, 1, tk.UNITS)
        elif system == 'Darwin':
            self._yview(tk.SCROLL, -event.delta, tk.UNITS)
        elif system == 'Windows':
            self._yview(tk.SCROLL, -event.delta // 120, tk.UNITS)
