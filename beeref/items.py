# This file is part of BeeRef.
#
# BeeRef is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BeeRef is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BeeRef.  If not, see <https://www.gnu.org/licenses/>.

"""Classes for items that are added to the scene by the user (images,
text).
"""

import base64
import logging

from PyQt6 import QtCore, QtGui, QtWidgets

from beeref.selection import SelectionItem


logger = logging.getLogger('BeeRef')


class BeePixmapItem(QtWidgets.QGraphicsPixmapItem):
    """Class for images added by the user."""

    def __init__(self, image, filename=None):
        super().__init__(QtGui.QPixmap.fromImage(image))
        logger.debug(f'Initialized image "{filename}" with dimensions: '
                     f'{self.width} x {self.height} at index {self.zValue()}')

        self.filename = filename
        self.scale_factor = 1
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlags.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlags.ItemIsSelectable)

    def setScale(self, factor):
        self.scale_factor = factor
        logger.debug(f'Setting scale for image "{self.filename}" to {factor}')
        super().setScale(factor)

    def set_pos_center(self, x, y):
        """Sets the position using the item's center as the origin point."""

        self.setPos(x - self.width * self.scale_factor / 2,
                    y - self.height * self.scale_factor / 2)

    @property
    def width(self):
        return self.pixmap().size().width()

    @property
    def height(self):
        return self.pixmap().size().height()

    def pixmap_to_str(self):
        """Convert the pixmap data to a base64-encoded PNG for saving."""
        barray = QtCore.QByteArray()
        buffer = QtCore.QBuffer(barray)
        buffer.open(QtCore.QIODevice.OpenMode.WriteOnly)
        img = self.pixmap().toImage()
        img.save(buffer, 'PNG')
        data = base64.b64encode(barray.data())
        return data.decode('ascii')

    @classmethod
    def qimage_from_str(self, data):
        """Read the image date from a base64-encoded PNG for loading."""
        img = QtGui.QImage()
        img.loadFromData(base64.b64decode(data))
        return img

    def to_bee_json(self):
        """For saving the item to BeeRefs native file format."""
        return {
            'cls': self.__class__.__name__,
            'scale': self.scale_factor,
            'pixmap': self.pixmap_to_str(),
            'pos': [self.pos().x(), self.pos().y()],
            'z': self.zValue(),
            'filename': self.filename,
        }

    @classmethod
    def from_bee_json(cls, obj):
        """For loading an item from BeeRefs native file format."""
        img = cls.qimage_from_str(obj['pixmap'])
        item = cls(img, filename=obj.get('filename'))
        if 'scale' in obj:
            item.setScale(obj['scale'])
        if 'pos' in obj:
            item.setPos(*obj['pos'])
        if 'z' in obj:
            item.setZValue(obj['z'])

        return item

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemSelectedChange:
            if value:
                logger.debug(f'Item selected {self.filename}')
                SelectionItem.activate_selection(self)
            else:
                logger.debug(f'Item deselected {self.filename}')
                SelectionItem.clear_selection(self)
        return super().itemChange(change, value)
