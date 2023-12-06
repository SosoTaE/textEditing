class TextBox:
    def __init__(self, text="", font_size=30, font_name="arial.ttf", color=(0, 0, 0), width=200, height=200,
                 direction="column", verticalAlign="center", horizontalAlign="center",
                 gap=5, boxStyle=None, boxColor=(0, 0, 0), radius=0):
        self.__width = width
        self.__height = height
        self.__direction = direction
        self.__verticalAlign = verticalAlign
        self.__horizontalAlign = horizontalAlign
        self.__gap = gap
        self.__text_array = []
        self.__sum_of_texts_height = 0
        self.__sum_of_texts_width = 0
        self.__text = text
        self.__font_size = font_size
        self.__font_name = font_name
        self.__color = color
        self.__box_style = boxStyle
        self.__box_color = boxColor
        self.__radius = radius

        self.__functions_object = {
            "center": self.__center,
            "start": self.__start,
            "end": self.__end
        }

        self.__text_adder(text=self.__text)

    def __text_adder(self, text):
        w, h = self.calculate_text_size(text=text, font_size=self.__font_size, font_name=self.__font_name)
        if w < self.__width:
            self.__addText(text=text, font_name=self.__font_name, font_size=self.__font_size, color=self.__color)
            return

        if text.count(" "):
            arr = text.split(" ")
            subtext = arr[0]
            index = 1
            while index < len(arr):
                if self.calculate_text_size(text=" ".join([subtext, arr[index]]), font_size=self.__font_size,
                                            font_name=self.__font_name)[0] > self.__width:
                    self.__text_adder(text=subtext)
                    subtext = arr[index]
                else:
                    subtext = " ".join([subtext, arr[index]])
                index += 1

            self.__text_adder(text=subtext)

        else:
            try:
                i = 1
                while self.calculate_text_size(text=text[:i], font_size=self.__font_size,
                                               font_name=self.__font_name)[0] < self.__width:
                    i += 1

                i -= 1
                self.__addText(text=text[:i], font_name=self.__font_name, font_size=self.__font_size,
                               color=self.__color)
                self.__text_adder(text[i:])
            except Exception:
                pass

    def __addText(self, text, font_size, font_name, color):
        self.__text_array.append([text, font_size, font_name, color])

        width, height = self.calculate_text_size(text, font_size, font_name)

        if self.__direction == "column":
            self.__sum_of_texts_height += height
        elif self.__direction == "row":
            self.__sum_of_texts_width += width

    def __center(self, full_width, object_width):
        return (full_width - object_width) // 2

    def __start(self, full_width, object_width):
        return 0

    def __end(self, full_width, object_width):
        return full_width - object_width

    def create_box(self, draw):
        rect_x = 0
        rect_y = 0
        rect_width = self.__width
        rect_height = self.__height
        corner_radius = self.__radius
        color = self.__box_color
        # Draw the rounded corners on the mask
        draw.ellipse((0, 0, corner_radius * 2, corner_radius * 2), fill=color)
        draw.ellipse((rect_width - corner_radius * 2, 0, rect_width, corner_radius * 2), fill=color)
        draw.ellipse((0, rect_height - corner_radius * 2, corner_radius * 2, rect_height), fill=color)
        draw.ellipse((rect_width - corner_radius * 2, rect_height - corner_radius * 2, rect_width, rect_height),
                     fill=color)

        # Draw the rectangles to fill in the sides on the mask
        draw.rectangle((corner_radius, 0, rect_width - corner_radius, rect_height), fill=color)
        draw.rectangle((0, corner_radius, rect_width, rect_height - corner_radius), fill=color)

    def compose(self):
        self.__sum_of_texts_height += (len(self.__text_array) - 1) * self.__gap
        self.__sum_of_texts_width += (len(self.__text_array) - 1) * self.__gap

        array = []
        box = Image.new("RGB", size=(self.__width, self.__height), color=(0, 0, 0))
        draw = ImageDraw.Draw(box, mode="RGB")

        if self.__box_style is not None:
            self.create_box(draw)

        Y = 0
        X = 0
        for text, font_size, font_name, color in self.__text_array:
            font = ImageFont.truetype(font_name, font_size)
            width, height = self.__get_text_dimensions(text, font)
            w, h = width, height
            if self.__direction == "column":
                h = self.__sum_of_texts_height
            elif self.__direction == "row":
                w = self.__sum_of_texts_width
            x = self.__functions_object[self.__horizontalAlign](box.width, w) + X
            y = self.__functions_object[self.__verticalAlign](box.height, h) + Y

            if self.__direction == "column":
                Y += height + self.__gap
            elif self.__direction == "row":
                X += width + self.__gap

            # array.append([(x, y), text, color, font])
            draw.text(xy=(x, y), text=text, fill=self.__color, font=font)

        i = 0
        while i < self.__height:
            j = 0
            while j < self.__width:
                color = box.getpixel(xy=(j, i))
                if color != (0, 0, 0):
                    array.append([(j, i), color])
                j += 1
            i += 1

        return array

    def calculate_text_size(self, text, font_size, font_name):
        font = ImageFont.truetype(font_name, font_size)

        return self.__get_text_dimensions(text, font)

    def __get_text_dimensions(self, text_string, font):
        ascent, descent = font.getmetrics()
        text_width = font.getmask(text_string).getbbox()[2]
        text_height = font.getmask(text_string).getbbox()[3] + descent

        return text_width, text_height


class PhotoTextComposer:
    def __init__(self, image):
        if isinstance(image, str):
            self.__image = Image.open(image).convert("RGBA")
        if isinstance(image, Image.Image):
            self.__image = image.convert("RGBA")
        else:
            raise TypeError("image should be str or Image type")
        self.__text_array = []
        self.__height = 0
        self.__text_boxs = []

    def addTextBox(self, text, font_size, font_name, color, xy, width=200, height=200, direction="column",
                   verticalAlign="center",
                   horizontalAlign="center", gap=5, boxStyle="default", boxColor=(255, 255, 255), radius=0):
        obj = TextBox(text, font_size, font_name, color, width, height, direction, verticalAlign, horizontalAlign, gap,
                      boxStyle, boxColor, radius)
        self.__text_boxs.append([obj, xy])

    def calculate_text_size(self, text, font_size, font_name):
        font = ImageFont.truetype(font_name, font_size)

        return self.__get_text_dimensions(text, font)

    def __get_text_dimensions(self, text_string, font):
        ascent, descent = font.getmetrics()
        text_width = font.getmask(text_string).getbbox()[2]
        text_height = font.getmask(text_string).getbbox()[3] + descent

        return text_width, text_height

    def addTextToCenter(self, text, xy, font_size=30, font_name="arial.ttf", color=(0, 0, 0), textBox=None):
        if textBox is None:
            textBox = (self.__image.width, self.__image.height)
        font = ImageFont.truetype(font_name, font_size)
        size = self.__get_text_dimensions(text, font)

        width, height = size

        if textBox[0] > width:
            self.__height += height
            self.__text_array.append([text, xy, font_size, font_name, color, size, textBox])
            return

        if text.count(" "):
            arr = text.split(" ")
            subtext = arr[0]
            index = 1
            while index < len(arr):
                if self.calculate_text_size(text=" ".join([subtext, arr[index]]), font_size=font_size,
                                            font_name=font_name)[0] > textBox[0]:
                    self.addTextToCenter(subtext, None, font_size, font_name, color, textBox)
                    subtext = arr[index]
                else:
                    subtext = " ".join([subtext, arr[index]])
                index += 1

            self.addTextToCenter(subtext, None, font_size, font_name, color)

        else:
            while self.calculate_text_size(text, font_size=font_size, font_name=font_name)[0] > textBox[0]:
                font_size -= 1

            self.addTextToCenter(text, None, font_size, font_name, color, textBox)

    def build_image(self, gap=5):
        draw = ImageDraw.Draw(self.__image)
        for obj, xy in self.__text_boxs:
            array = obj.compose()
            for coordinate, color in array:
                XY = (xy[0] + coordinate[0], xy[1] + coordinate[1])
                try:
                    self.__image.putpixel(XY, color)
                except Exception:
                    pass

        return self.__image

    def image(self):
        return self.__image


if __name__ == "__main__":
    from PIL import Image, ImageFont, ImageDraw

    image = Image.new("RGB", (540, 960), color=(0, 0, 0))

    editor = PhotoTextComposer(image)
    editor.addTextBox(text=f"is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.", font_name="arial.ttf", font_size=30, color=(255, 200, 255), xy=(0, 0), width=540,
                      height=960, direction="column", verticalAlign="center", horizontalAlign="center", gap=5,
                      boxStyle="default", boxColor=(255, 0, 255), radius=20)
    editor.build_image()
    editor.image().show()
