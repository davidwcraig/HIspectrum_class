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
        """Set the roi using mouse events"""
        fig, ax = plt.subplots()
        ax.plot(self.velo, self.flux)
        ctr = self.meta['V21SYS']
        ax.set_xlim(ctr-500, ctr+500)
        fig.suptitle("Setting ROI")
        def onclick1(event):
            if event.button == 3:
                self.roi_right = event.xdata 
            elif event.button == 1:
                self.roi_left = event.xdata
            else:
                return
                
            print(self.roi_left, self.roi_right)
        cid = fig.canvas.mpl_connect('button_press_event', onclick1)
        plt.show() # think this blocks until the canvas is dropped 
        fig.canvas.mpl_disconnect(cid)
        # actually set the indices for the region:
        self.roi = (self.velo > self.roi_left) & (self.velo < self.roi_right)

    def mouse_returnx(self):
        fig, ax = plt.subplots()
        ax.plot(self.velo, self.flux)
        ctr = self.meta['V21SYS']
        ax.set_xlim(ctr-500, ctr+500)
        def onclick(event):
            if event.button == 1:
                print(event.xdata)
                self.lastx = event.xdata
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()
