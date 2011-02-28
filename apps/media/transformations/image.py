# -*- coding: utf-8 -*-

from .base import FileTransformation
import Image

from ImageFile import Parser as ImageFileParser

from apps.utils.stringio import StringIO

class ImageResize(FileTransformation):
    def _apply(self, source, destination):
        parser = ImageFileParser()
        parser.feed(source.file.read())
        source_image = parser.close()
        crop_box = ImageResize.cropbox(source_image.size,
                                       (self.width, self.height))
        image = source_image.crop(crop_box)
        image = image.resize((self.width, self.height), Image.ANTIALIAS)
        buffer = StringIO()
        image.save(buffer, self.format)
        buffer.reset()
        if destination.file:
            write = destination.file.replace
        else:
            write = destination.file.put

        write(buffer, content_type = 'image/%s' % self.format)

        destination.save()
        return destination

    @staticmethod
    def cropbox(image, thumb):
        imagewidth, imageheight = image
        thumbwidth, thumbheight = thumb

        # determine scale factor
        fx = float(imagewidth)/thumbwidth
        fy = float(imageheight)/thumbheight
        f = fx if fx < fy else fy

        # calculate size of crop area
        cropheight, cropwidth = int(thumbheight*f), int(thumbwidth*f)

        # center the crop area on the source image
        dx = (imagewidth - cropwidth)/2
        dy = (imageheight - cropheight)/2

        # return bounding box of crop area
        return dx, dy, cropwidth + dx, cropheight + dy