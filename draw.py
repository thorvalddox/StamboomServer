__author__ = 'Thorvald'

import core
from itertools import chain
import random
import os.path

#from imageinfo import get_image_info

try:
    import Image
except ImportError:
    from PIL import Image


class DrawJavaScript:
    """
    A wrapper to draw a family tree using javascript. Different methods will create different shapes.
    The methods get_html_canvas and get_html_script return all the data needed on the html script.
    Put get_html_canvas on the place where you want to show the tree and get_html_script in the script section.
    You can also use get_html, which already contains a script section.
    """
    def __init__(self, dimensions):
        self.commands = []
        self.clickevents = []
        self.mouseoverevents = []
        self.dimensions = dimensions

    def get_html_canvas(self):
        """
        returns the needed html code to create the canvas
        :return:
        """
        return """
        <canvas id="FamilyTreeCanvas" width="{}" height="{}" style="border:1px solid #c3c3c3;">
        Your browser does not support the HTML5 canvas tag.
        </canvas>""".format(*self.dimensions)

    def get_html_script(self):  # put this between the <script> tag
        """
        returns the javascript code needed to build the tree
        :return:
        """
        return """
        var c = document.getElementById("FamilyTreeCanvas");
        var ctx = c.getContext("2d");
        """ + "\n".join(self.commands) + """
            c.addEventListener("mousemove", on_mousemove, false);
            c.addEventListener("click", on_click, false);
        function getOffsetRect(elem) {
            var box = elem.getBoundingClientRect()

            var body = document.body
            var docElem = document.documentElement

            var scrollTop = window.pageYOffset || docElem.scrollTop || body.scrollTop
            var scrollLeft = window.pageXOffset || docElem.scrollLeft || body.scrollLeft

            var clientTop = docElem.clientTop || body.clientTop || 0
            var clientLeft = docElem.clientLeft || body.clientLeft || 0

            var top  = box.top +  scrollTop - clientTop
            var left = box.left + scrollLeft - clientLeft

            return { top: Math.round(top), left: Math.round(left) }
        }
        function on_mousemove (ev) {
            var x, y;

            // Get the mouse position relative to the canvas element.
            if (ev.layerX || ev.layerX == 0) { //for firefox
            x = ev.pageX;
            y = ev.pageY;
            }
            x-=getOffsetRect(c).left;
            y-=getOffsetRect(c).top;
            document.body.style.cursor = "";

        """ + "\n".join(self.mouseoverevents) + """
        }
        function on_click(ev) {
            var x, y;

            // Get the mouse position relative to the canvas element.
            if (ev.pageX || ev.pageX == 0) { //for firefox
            x = ev.pageX;
            y = ev.pageY;
            }
            x-=getOffsetRect(c).left;
            y-=getOffsetRect(c).top;
            console.info(x +","+y + "(" + ev.pageX + "," + ev.pageY + ")" + c.offsetLeft + "," + c.offsetTop);

        """ + "\n".join(self.clickevents) + """
        }
        """

    def get_html(self):
        return(
            """
            {}
            <script>
            {}
            </script>
            """.format(self.get_html_canvas(),self.get_html_script())
        )

    def draw_line(self, *coords):  # x1 y1 x2 y2
        """
        Adds a line between to points
        :param coords: x1 y1 x2 y2
        :return:
        """
        self.commands.append("""
        ctx.moveTo({},{});
        ctx.lineTo({},{});
        ctx.stroke();
        """.format(*coords))

    def draw_rectangle(self, x1, y1, x2, y2, back_color=None):
        """
        draws a rectangle between the given coordinates
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param back_color:
        :return:
        """
        if back_color is not None:
            self.commands.append("""
                ctx.fillStyle = '{}';
                ctx.fillRect({},{},{},{});
            """.format(back_color, x1, y1, x2 - x1, y2 - y1))
        self.draw_line(x1, y1, x1, y2)
        self.draw_line(x2, y1, x2, y2)
        self.draw_line(x1, y1, x2, y1)
        self.draw_line(x1, y2, x2, y2)

    def draw_text(self, x, y, text, size=12):
        """
        draw a text at the given position. The position is the mid-top of the text
        :param x:
        :param y:
        :param text:
        :param size:
        :return:
        """
        self.commands.append("""
        ctx.font = "{}px Arial";
        ctx.fillStyle = 'black';
        ctx.textAlign="center";
        ctx.fillText("{}",{},{});
        """.format(size, text, x, y))

    def add_mouse_pointer(self, x1, y1, x2, y2):
        """
        Changes the mouse pointer to a pointer style (like over hyperlinks) in the given rectangle
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return:
        """
        self.mouseoverevents.append("""
        if(x>={} && x <= {} && y>={} && y<= {}){{
            document.body.style.cursor = "pointer";
        }}
        """.format(x1, x2, y1, y2))

    def add_mouse_link(self, link, x1, y1, x2, y2):
        """
        Makes an area of the canvas into an hyperlink. Clicking in the rectangle will link you to
        the given page.
        :param link:
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return:
        Note: The hyperlink will not show up as link. Therefor use the function add_mouse_pointer
        """
        self.clickevents.append("""
        if(x>={} && x <= {} && y>={} && y<= {}){{
            window.location = "{}"
        }}
        """.format(x1, x2, y1, y2, link))

    def draw_image(self, image, x, y, width, height):
        """
        Draws an image at a given place with given dimensions
        :param image: path of the image
        :param x:
        :param y:
        :param width:
        :param height:
        :return:
        """
        delim_array = image.split('.', 1)
        path = "%s_%dx%d.%s" % (delim_array[0], width, height, delim_array[1])
        if not os.path.exists("StamboomServer/static/" + path):
            im = Image.open("StamboomServer/static/" + image)
            old_width, old_height = im.size
            w_scale = float(width) / old_width
            h_scale = float(height) / old_height
            if (w_scale < 1) or (h_scale < 1):
                # Image needs to be scaled
                scale = min(w_scale, h_scale)
                new_width = int(scale * old_width)
                new_height = int(scale * old_height)
                newimage = im.resize((new_width, new_height), Image.ANTIALIAS)
                newimage.save("StamboomServer/static/" + path, im.format)
            else:
                im.save("StamboomServer/static/" + path, im.format)

        self.commands.append("""
            var imageObj{0} = new Image();

              imageObj{0}.onload = function() {{
                var scale = Math.min({3}/imageObj{0}.naturalWidth,{4}/imageObj{0}.naturalHeight)
                ctx.drawImage(imageObj{0}, {1}-(imageObj{0}.naturalWidth*scale-{3})/2, {2}, imageObj{0}.naturalWidth*scale, imageObj{0}.naturalHeight*scale);
              }};

              imageObj{0}.src = '/static/{5}';
        """.format(random.randrange(2 ** 64), x, y, width, height, path))

    def draw_person(self, person, x, y, width, height, border, textsize):
        """
        Draws a person at a given position with given dimensions
        :param person:
        :param x:
        :param y:
        :param width:
        :param height:
        :param border: border between image and rectangle
        :param textsize:
        :return:
        """
        xdif = width / 2 - border
        ydif = height / 2 - border
        self.draw_rectangle(x - xdif, y - ydif, x + xdif, y + ydif, "white")
        self.draw_text(x, y + ydif - 4-2*(textsize+1), person.name,textsize)
        self.draw_text(x, y + ydif - 4-(textsize+1), "*" * bool(person.birth) + person.birth,textsize)
        self.draw_text(x, y + ydif - 4, "+" * bool(person.dead) + person.dead,textsize)
        self.add_mouse_pointer(x - xdif, y - ydif, x + xdif, y + ydif)
        self.add_mouse_link("/stamboom/edit/" + person.uname, x - xdif, y - ydif, x + xdif, y + ydif)
        nw, nh = width - 3 * border, height - 3 * border - 3*textsize
        self.draw_image(person.image, x - xdif + border/ 2, y - ydif + border / 2, nw, nh)



class BuildTree:
    """
    This object calculates the position of all the people and the correct connections, displayed
    on the canvas
    """
    def __init__(self, tree):
        self.tree = tree
        self.coords = {p: (-1,-1) for p in self.tree.people_linked}
        self.headsize = {}
        self.tailsize = {}
        self.xpos = {p: 0 for p in self.tree.get_representation(self.tree.head)[0]}
        for l in self.make_top_layers():
            for p in l:
                self.transfer_xpos(p)
        self.build_coords()

    def make_layers(self):
        """
        Returns an iterator of iterators containing people.
        Each iterator contains the people who have to be displayed on a layer,
        in the correct order, starting with the top layer.
        This iterator does not contain the spouses. If you want to include the spouses,
        use make_top_layers() instead
        :return:
        """
        generator = [self.tree.head]
        try:
            while generator:
                # print([self.tree.get_representation(p) for p in generator])
                # print(list(zip(*[self.tree.get_representation(p) for p in generator])))

                layer, nextgen = zip(*(self.tree.get_representation(p) for p in generator))
                yield chain(*layer)
                generator = chain(*nextgen)
        except ValueError:
            return

    def make_top_layers(self):
        """
        Returns an iterator of iterators containing people. Each iterator contains the people who have to be displayed on a layer,
        in the correct order, starting with the top layer.
        :return:
        """
        generator = [self.tree.head]
        try:
            while generator:
                # print([self.tree.get_representation(p) for p in generator])
                # print(list(zip(*[self.tree.get_representation(p) for p in generator])))
                layer, nextgen = zip(*(self.tree.get_representation(p) for p in generator))
                yield generator
                generator = list(chain(*nextgen))
        except ValueError:
            return

    def get_headsize(self, person):
        """
        returns the size of the head (person and spouses) of the family this person is
        :param person:
        :return:
        """
        if person not in self.headsize:
            self.headsize[person] = self.calc_headsize(person)
        return self.headsize[person]

    def get_tailsize(self, person):
        if person not in self.tailsize:
            self.tailsize[person] = self.calc_tailsize(person)
        return self.tailsize[person]

    def calc_headsize(self, person):
        toplenght = len(self.tree.get_representation(person)[0])
        return max(toplenght, self.get_tailsize(person))

    def calc_tailsize(self, person):
        return sum(self.get_headsize(p) for p in self.tree.get_representation(person)[1])

    def get_xpos(self, person):
        if person not in self.xpos:
            raise Exception("{} Not Indexed Yet".format(person.name))
        return self.xpos[person]

    def transfer_xpos(self, person):
        currentpos = self.get_xpos(person) + (self.get_headsize(person) - self.get_tailsize(person)) / 2
        for p in self.tree.get_representation(person)[1]:
            for s in self.tree.get_representation(p)[0]:
                #print(person.name, p.name, s.name, "->", currentpos)
                self.xpos[s] = currentpos
            currentpos += self.get_headsize(p)

    def build_coords(self):
        for index, layer in enumerate(self.make_top_layers()):
            for person in layer:
                tops = list(self.tree.get_representation(person)[0])
                s = len(tops)
                for i, p in enumerate(tops):
                    #print(p, person)
                    self.coords[p] = (self.xpos[person] + self.get_headsize(person) / 2 + i - s / 2, index)

    def get_pos(self, person, width, height):
        return ((i + 1 / 2) * w for i, w in zip(self.coords[person], (width, height)))

    def get_width(self, width):
        return self.get_headsize(self.tree.head) * width

    def get_height(self, height):
        return 4 * height

    def draw_family(self, draw:DrawJavaScript, fam:core.Family, width, height, border):
        xdif = width / 2 - border
        ydif = height / 2 - border
        if not all(self.check_valid(p) for p in fam.parents):
            return
        if len(fam.parents) == 2:
            p1, p2 = fam.parents
            px1, py1 = self.get_pos(p1, width, height)
            px2, py2 = self.get_pos(p2, width, height)
            draw.draw_line(min(px1, px2) + xdif, py1, max(px1, px2) - xdif, py2)
            px = (px1 + px2) // 2
            py = py1
        elif len(fam.parents) == 1:
            p1, = fam.parents
            px, py = self.get_pos(p1, width, height)
        else:
            raise Exception("Incorrect amoutn of parents")
        if fam.children:
            cy = list(self.get_pos(fam.children[0], width, height))[1]
            cyInter = (py + cy) // 2
            draw.draw_line(px, py + ydif * (len(fam.parents) == 1), px, cyInter)
            for c in fam.children:
                if not self.check_valid(c):
                    continue
                cx, _ = self.get_pos(c, width, height)
                draw.draw_line(px, cyInter, cx, cyInter)
                draw.draw_line(cx, cyInter, cx, cy - ydif)
    def check_valid(self,person):
        return(self.coords[person] != (-1,-1))

def draw_people(tree, width=170, height=200, border=15, textsize=12):
    s = BuildTree(tree)
    d = DrawJavaScript((s.get_width(width), s.get_height(height)))
    for f in tree.families:
        s.draw_family(d, f, width, height, border)
    for p in tree.people_linked:
        if s.check_valid(p):
            d.draw_person(p, *s.get_pos(p, width, height), width=width, height=height, border=border, textsize=textsize)
    return d


def main():
    f = core.FamilyTree()
    f.from_code("data.log")
    b = BuildTree(f)
    for l in b.make_layers():
        print(list(l))


if __name__ == "__main__":
    main()
