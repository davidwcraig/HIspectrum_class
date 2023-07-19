"""
HIspectrum - a simple plot and analysis class for APPSS HI spectra.
David Craig		2023-0-17
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table

class HIspectrum:
    """Class for line profile spectra"""
    def __init__(self, filename):
        """Create Spectrum instance from filename with astropy.table.Table"""
        tdata = Table.read(filename)
        self.flux = np.array(tdata['FLUX'])
        self.velo = np.array(tdata['VHELIO'])
        self.freq = np.array(tdata['FREQUENCY'])
        self.blin = np.array(tdata['BASELINE'])
        self.meta = tdata.meta #ordered dict
        self.obname = self.meta['OBJECT']
        self.roi_left, self.roi_right = 0.0,0.0 #boundaries of roi
        self.roi = None #indices (array) region of interest for data reduction
        self.lastx = -999.0 # last x location clicked in spectrum
            
    def display(self, vlim=[None, None], f_name=None, v21=True):
        """plot the Spectrum, vlim is velo limits. If f_name is specified, save figure there."""
        fig, ax1 = plt.subplots()
        ax1.plot(self.velo, self.flux)
        fig.suptitle('Object: {:s}'.format(self.obname))
        ax1.set_xlabel('Velocity')
        ax1.set_ylabel('Flux')
        if v21:
            ctr = self.meta['V21SYS']
            vlim = [ctr-500, ctr+500]  #500 km/s either side
        ax1.set_xlim(vlim)
        if self.roi is not None:
            plt.plot(self.velo[self.roi], self.flux[self.roi], color="red")
            plt.fill_between(self.velo[self.roi], self.flux[self.roi], color='red', alpha=0.2)
        if f_name is not None:
            plt.savefig(f_name)
        # TODO: try to put a fig closeer here with a callback?
        plt.show()
            
        
    def set_name(self, name):
        """Set the name of the Spectrum object for display"""
        self.obname = name
    def set_roi(self, vr_lo, vr_hi):
        """Set the region of interest for the Spectrum: a numpy fancy index"""
        self.roi = (self.velo > vr_lo) & (self.velo < vr_hi)
        
    def integrate_roi(self):
        """Integrate the Spectrum's region of interest, typically the line profile"""
        if self.roi is not None:
            I = np.trapz(self.flux, self.velo)
            if self.velo[-1] < self.velo[0]: #check for reversed v array
                I = -I
                print("NOTE correcting sum for reversed v axis.")
        else:
            print("Region of interest undefined!")
            I = None
        return I
    
    def mouse_roi(self):
        """Set the region of interest (roi) for integration, etc. by mouse."""
        lastx1, lastx2 = -999.0, -999.0 # value of last mouse click
        m_accept = False
        m_done = False
        """Set the roi using mouse events"""
        fig, ax = plt.subplots()
        ax.plot(self.velo, self.flux)
        ctr = self.meta['V21SYS']
        ax.set_xlim(ctr-500, ctr+500)
        fig.suptitle("Setting ROI")
        def onclick1(event):
            nonlocal lastx1, lastx2, m_done
            if event.button == 1:
                print("Clicked x1: ", event.xdata)
                lastx1 = event.xdata
            elif event.button == 3:
                print("Clicked x2: ", event.xdata)
                lastx2 = event.xdata
            elif event.button == 2:
                print('Saving bounds!')
                plt.close() # close the window
                m_done = True
            else:
                pass # needed?

        cid = fig.canvas.mpl_connect('button_press_event', onclick1)
        # Give the user help:
        print("""Left mouse click to set lower v,
        Right mouse click to set upper v,
        Center click to accept""")
        plt.show() # think this blocks until the canvas is dropped 
        fig.canvas.mpl_disconnect(cid)
        self.roi = (self.velo > lastx1) & (self.velo < lastx2)
        # actually set the indices for the region:
        if m_done:
            print("ROI bounds set for {:s} {:5.1f} to {:5.1f}".format(self.obname,lastx1,lastx2))
            self.display() # display again. Should show ROI
            return


    def mouse_returnx(self):
        """simply returns the last clicked x value, test method."""
        lastx = -999.0
        fig, ax = plt.subplots()
        ax.plot(self.velo, self.flux)
        ctr = self.meta['V21SYS']
        ax.set_xlim(ctr-500, ctr+500)
        def onclick(event):
            nonlocal lastx
            if event.button == 1:
                print(event.xdata)
                lastx = event.xdata
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()
        return lastx  # I think this will only finish on close.
