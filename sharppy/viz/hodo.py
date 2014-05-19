import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *


__all__ = ['backgroundHodo', 'plotHodo']


class backgroundHodo(QtGui.QFrame):
    '''
    Handles the plotting of the backgroun frame.
    '''
    def __init__(self):
        super(backgroundHodo, self).__init__()
        self.initUI()

    def initUI(self):
        '''
        Initialize the User Interface

        '''
        ## set the interface variables for width, height, padding, etc.
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 0
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.center_hodo()
        self.ring_increment = 10
        self.rings = range(self.ring_increment, 200+self.ring_increment,
                           self.ring_increment)
        self.label_font = QtGui.QFont('Helvetica', 9)

    def center_hodo(self):
        '''
        Center the hodograph in the window. Can/Should be overwritten.

        '''
        self.centerx = self.wid / 2; self.centery = self.hgt / 2
        self.hodomag = 160.
        self.scale = (self.brx - self.tlx) / self.hodomag

    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        self.initUI()

    def paintEvent(self, e):
        '''
        Handles painting the frame background.
        '''
        ## initialize a QPainter object.
        qp = QtGui.QPainter()
        qp.begin(self)
        ## draw the wind speed rings
        for spd in self.rings: self.draw_ring(spd, qp)
        ## draw the frame axes
        self.draw_axes(qp)
        self.draw_frame(qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draw frame around object.
        --------
        qp: QtGui.QPainter object

        '''
        ## initialize a white pen to draw the frame
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 2)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the frame borders
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)

    def draw_axes(self, qp):
        '''
        Draw the X, Y Axes.
        --------
        qp: QtGui.QPainter object

        '''
        ## initialize a white pen to draw the frame axes
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 2)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the frame axes
        qp.drawLine(self.centerx, self.tly, self.centerx, self.bry)
        qp.drawLine(self.tlx, self.centery, self.brx, self.centery)

    def draw_ring(self, spd, qp):
        '''
        Draw a range ring.
        --------
        spd: wind speed
        qp: QtGui.QPainter object

        '''
        ## set the ring color and get the u and v components of a
        ## 0 direction vector with speed spd.
        color = "#555555"
        uu, vv = tab.utils.vec2comp(0, spd)
        vv *= self.scale
        ## create a center point
        center = QtCore.QPointF(self.centerx, self.centery)
        ## initialize a pen to draw with
        pen = QtGui.QPen(QtGui.QColor(color), 1)
        pen.setStyle(QtCore.Qt.DashLine)
        qp.setPen(pen)
        ## draw the range ring
        qp.drawEllipse(center, vv, vv)
        qp.setFont(self.label_font)
        ## reset the pen to draw with. Color is set to black and width zero
        ## because we actually don't want to draw and lines yet.
        pen = QtGui.QPen(QtGui.QColor('#000000'), 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        offset = 5; width = 15; hght = 15;
        ## crete some rectangles
        top_rect = QtCore.QRectF(self.centerx+offset,
                    self.centery+vv-offset, width, hght)
        bottom_rect = QtCore.QRectF(self.centerx+offset,
                    self.centery-vv-offset, width, hght)

        right_rect = QtCore.QRectF(self.centerx+vv-offset,
                    self.centery+offset, width, hght)
        left_rect = QtCore.QRectF(self.centerx-vv-offset,
                    self.centery+offset, width, hght)
        ## draw some invisible rectangles
        qp.drawRect(top_rect); qp.drawRect(right_rect)
        qp.drawRect(bottom_rect); qp.drawRect(left_rect)
        ## now make the pen white and draw text using
        ## the invisible rectangles
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"))
        qp.setPen(pen)
        qp.setFont(self.label_font)
        qp.drawText(top_rect, QtCore.Qt.AlignCenter, str(int(spd)))
        qp.drawText(right_rect, QtCore.Qt.AlignCenter, str(int(spd)))
        qp.drawText(bottom_rect, QtCore.Qt.AlignCenter, str(int(spd)))
        qp.drawText(left_rect, QtCore.Qt.AlignCenter, str(int(spd)))

    def hodo_to_pix(self, ang, spd):
        '''
        Function to convert a (direction, speed) to (x, y) coordinates.
        --------
        ang: wind direction
        spd: wind speed

        '''
        uu, vv = tab.utils.vec2comp(ang, spd)
        xx = self.centerx + (uu * self.scale)
        yy = self.centery + (vv * self.scale)
        return xx, yy

    def uv_to_pix(self, u, v):
        '''
        Function to convert (u, v) to (x, y) coordinates.
        --------
        u: the u wind component
        v: the v wind component

        '''
        xx = self.centerx + (u * self.scale)
        yy = self.centery - (v * self.scale)
        return xx, yy




class plotHodo(backgroundHodo):
    '''
    Plots the data on the hodograph.
    '''
    def __init__(self, hght, u, v, **kwargs):
        super(plotHodo, self).__init__()
        ## initialize the variables needed to plot the hodo.
        self.hght = hght
        self.u = u; self.v = v
        ## if you want the storm motion vector, you need to
        ## provide the profile.
        self.prof = kwargs.get('prof', None)
        self.srwind = self.prof.srwind
        self.ptop = self.prof.etop
        self.pbottom = self.prof.ebottom

    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        super(plotHodo, self).resizeEvent(e)

    def paintEvent(self, e):
        '''
        Handles the plotting of the data in the frame.
        '''
        super(plotHodo, self).paintEvent(e)
        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self)
        ## draw the hodograph
        self.draw_hodo(qp)
        ## draw the storm motion vector
        self.drawSMV(qp)
        qp.end()
    
    def drawSMV(self, qp):
        '''
        Draws the storm motion vector.
        --------
        qp: QtGui.QPainter object
        '''
        ## set a pen with white color, width 1, solid line.
        penwidth = 1
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## check and make sure there is no missing data
        try:
            mask = np.maximum( self.u, self.v )
            hght = self.hght[~mask]
            u = self.u[~mask]; v = self.v[~mask]
            ## calculate the left and right storm motion vectors
            rstu,rstv,lstu,lstv = self.srwind
            rstu = rstu[~mask]; rstv = rstv[~mask]
            lstu = lstu[~mask]; lstv = lstv[~mask]
        ## otherwise the data is fine
        except:
            hght = self.hght
            u = self.u; v = self.v
            rstu,rstv,lstu,lstv = self.srwind
        ## convert the left and right mover vector components to pixel values
        ruu, rvv = self.uv_to_pix(rstu,rstv)
        luu, lvv = self.uv_to_pix(lstu, lstv)
        ## calculate the center points of the storm motion vectors
        center_rm = QtCore.QPointF(ruu,rvv)
        center_lm = QtCore.QPointF(luu,lvv)
        ## draw circles around the sorm motion vectors
        qp.drawEllipse(center_rm, 5, 5)
        qp.drawEllipse(center_lm, 5, 5)
        ## get the effective inflow layer
        ptop, pbottom = self.ptop, self.pbottom
        ## make sure the effective inflow layer exists
        if ptop is np.ma.masked and pbottom is np.ma.masked:
            pass
        else:
            ## get the interpolated wind at the bottom and top
            ## of the effective inflow layer
            utop,vtop = tab.interp.components(self.prof, ptop)
            ubot,vbot = tab.interp.components(self.prof, pbottom)
            ## convert these values to pixels
            uutop, vvtop = self.uv_to_pix(utop, vtop)
            uubot, vvbot = self.uv_to_pix(ubot, vbot)
            ## set a pen
            pen = QtGui.QPen(QtGui.QColor("#00FFFF"), penwidth)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ## draw lines showing the effective inflow layer
            qp.drawLine(center_rm.x(), center_rm.y(), uubot, vvbot)
            qp.drawLine(center_rm.x(), center_rm.y(), uutop, vvtop)

    def draw_hodo(self, qp):
        '''
        Plot the Hodograph.
        --------
        qp: QtGui.QPainter object

        '''
        ## check for masked daata
        try:
            mask = np.maximum(self.u.mask, self.v.mask)
            z = self.hght[~mask]
            u = self.u[~mask]
            v = self.v[~mask]
        ## otherwise the data is fine
        except:
            z = self.hght
            u = self.u
            v = self.v
        ## convert the u and v values to x and y pixels
        xx, yy = self.uv_to_pix(u, v)
        ## define the colors for the different hodograph heights
        low_level_color = QtGui.QColor("#FF0000")
        mid_level_color = QtGui.QColor("#00FF00")
        upper_level_color = QtGui.QColor("#FFFF00")
        trop_level_color = QtGui.QColor("#00FFFF")
        ## define a pen to draw with
        penwidth = 2
        pen = QtGui.QPen(low_level_color, penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        ## loop through the profile. Loop through shape - 1 since
        ## i + 1 is indexed
        for i in range(xx.shape[0]-1):
            ## draw the hodograph in the lowest 3km
            if z[i] < 3000:
                if z[i+1] < 3000:
                    pen = QtGui.QPen(low_level_color, penwidth)
                else:
                    pen = QtGui.QPen(low_level_color, penwidth)
                    ## get the interpolated wind at 3km
                    tmp_u = tab.interp.generic_interp_hght(3000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(3000, z, v)
                    ## get the pixel value
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    ## draw the hodograph
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    pen = QtGui.QPen(mid_level_color, penwidth)
                    qp.setPen(pen)
                    qp.drawLine(tmp_x, tmp_y, xx[i+1], yy[i+1])
                    continue
            ## draw the hodograph in the 3-6km range
            elif z[i] < 6000:
                if z[i+1] < 6000:
                    pen = QtGui.QPen(mid_level_color, penwidth)
                else:
                    pen = QtGui.QPen(mid_level_color, penwidth)
                    tmp_u = tab.interp.generic_interp_hght(6000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(6000, z, v)
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    pen = QtGui.QPen(upper_level_color, penwidth)
                    qp.setPen(pen)
                    qp.drawLine(tmp_x, tmp_y, xx[i+1], yy[i+1])
                    continue
            ## draw the hodograph in the 6-9km layer
            elif z[i] < 9000:
                if z[i+1] < 9000:
                    pen = QtGui.QPen(upper_level_color, penwidth)
                else:
                    pen = QtGui.QPen(upper_level_color, penwidth)
                    tmp_u = tab.interp.generic_interp_hght(9000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(9000, z, v)
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    pen = QtGui.QPen(trop_level_color, penwidth)
                    qp.setPen(pen)
                    qp.drawLine(tmp_x, tmp_y, xx[i+1], yy[i+1])
                    continue
            ## draw the hodograph in the 9-12km layer
            elif z[i] < 12000:
                if z[i+1] < 12000:
                    pen = QtGui.QPen(trop_level_color, penwidth)
                else:
                    pen = QtGui.QPen(low_level_color, penwidth)
                    tmp_u = tab.interp.generic_interp_hght(12000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(12000, z, v)
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    break
            else:
                break
            qp.setPen(pen)
            qp.drawLine(xx[i], yy[i], xx[i+1], yy[i+1])