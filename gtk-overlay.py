#!/usr/bin/python3

import gi
import cairo
import os
import logging

logging.basicConfig(level=int(os.environ.get("LOG_LEVEL", logging.INFO)))

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore


# stub
def on_button_clicked(widget):
    logging.info(f"on_button_clicked from {widget}")


handlers = {f.__name__: f for f in [on_button_clicked]}

def draw_hint(x, y, text, ctx: cairo.Context, padding=5, font_size=15):

    ctx.select_font_face("sans-serif")
    ctx.set_font_size(font_size)
    (xbearing, ybearing, width, height, dx, dy) = ctx.text_extents(text)
    #  print(xbearing, ybearing, width, height, dx, dy)

    ctx.set_source_rgb(0.2, 0.2, 0.6)
    ctx.rectangle(x - padding, y - padding, width + 2 * padding, height + 2 * padding)
    ctx.fill()

    ctx.move_to(x, y - ybearing)
    ctx.set_source_rgb(1, 1, 1)
    ctx.show_text(text)


def draw_hints_rec(widget, ctx, hint_iter):
    logging.debug(f"draw_hints_rec for {widget.get_name()}")
    if isinstance(widget, Gtk.Button):
        alloc = widget.get_allocation()
        hint_text = next(hint_iter)
        draw_hint(alloc.x, alloc.y, hint_text, ctx)
    else:
        if isinstance(widget, Gtk.Container):
            for child in widget.get_children():
                draw_hints_rec(child, ctx, hint_iter)


def hint_canvas_do_draw(area, ctx: cairo.Context, window):
    logging.debug("hint_canvas_do_draw")
    hint_iter = map(chr, range(ord("A"), ord("Z") + 1))
    draw_hints_rec(window, ctx, hint_iter)

def print_tree(widget, depth=0):
    print("  " * depth + widget.get_name())
    if isinstance(widget, Gtk.Container):
        for child in widget.get_children():
            print_tree(child, depth=depth + 1)


def inject_overlay(window):
    overlay = Gtk.Overlay()

    #  modify tree
    grid = window.get_child()
    window.remove(grid)
    overlay.add(grid)
    window.add(overlay)

    #  add css
    area = Gtk.DrawingArea()
    overlay.add_overlay(area)
    area.connect("draw", hint_canvas_do_draw, window)


def main():
    builder = Gtk.Builder()
    builder.add_from_file("./gtk-overlay.ui")

    builder.connect_signals(handlers)

    window = builder.get_object("main-window")
    window.connect("destroy", Gtk.main_quit)
    

    #  blokuje kliknięcia...
    inject_overlay(window)

    provider = Gtk.CssProvider()
    provider.load_from_path("./gtk-overlay.css")
    apply_css(window, provider)

    window.show_all()
    Gtk.main()


def apply_css(widget, provider):
    logging.debug(f"add css to {widget}")
    Gtk.StyleContext.add_provider(
        widget.get_style_context(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    if isinstance(widget, Gtk.Container):
        widget.forall(apply_css, provider)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        pass
