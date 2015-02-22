from __future__ import print_function
from .detector import SignalDetector
from .signal import EpicsSignal
from epics import caget, caput
from hashlib import md5
from time import time


class AreaDetector(SignalDetector):
    def __init__(self, basename, *args, **kwargs):
        super(AreaDetector, self).__init__(*args, **kwargs)
        self._basename = basename

        signals = []
        signals.append(self._ad_signal('cam1:Acquire', '_acquire'))
        signals.append(self._ad_signal('cam1:AcquireTime', '_acquire_time'))
        signals.append(self._ad_signal('cam1:NumImages', '_num_images'))
        signals.append(self._ad_signal('cam1:ImageMode', '_image_mode'))

        # Add Stats Signals

        for n in range(1, 6):
            signals.append(self._ad_signal('Stats{}:Total'.format(n),
                                           '_total{}'.format(n),
                                           rw=False))

        for sig in signals:
            self.add_signal(sig)

        self._acq_signal = self._acquire

    def _ad_signal(self, suffix, alias, **kwargs):
        """Return a signal made from areaDetector database"""
        return EpicsSignal('{}{}_RBV'.format(self._basename, suffix),
                           write_pv='{}{}'.format(self._basename, suffix),
                           name='{}{}'.format(self.name, alias),
                           alias=alias, **kwargs)

    def configure(self, **kwargs):
        """Configure areaDetctor detector"""

        # Stop Acquisition
        self._old_acquire = self._acquire.get()
        self._acquire.put(0, wait=True)

        # Set the image mode to multiple
        self._old_image_mode = self._image_mode.get()
        self._image_mode.put(1, wait=True)

    def deconfigure(self, **kwargs):
        """DeConfigure areaDetector detector"""
        self._image_mode.put(self._old_image_mode, wait=True)
        self._acquire.put(self._old_acquire, wait=False)


class AreaDetectorHDF5(AreaDetector):
    def __init__(self, *args, **kwargs):
        super(AreaDetectorHDF5, self).__init__(*args, **kwargs)
        self._file_plugin = 'HDF1:'
        self._file_path = '/GPFS/xf23id/xf23id1/test_2'

    def _write_plugin(self, name, value, wait=True):
        caput('{}{}{}'.format(self._basename, self._file_plugin, name),
              value, wait=wait)

    def _read_plugin(self, name):
        return caget('{}{}{}_RBV'.format(self._basename,
                                         self._file_plugin, name))

    def configure(self, *args, **kwargs):
        super(AreaDetectorHDF5, self).configure(*args, **kwargs)

        self._filename = md5('{}{}'.format(time(), self._basename)).hexdigest()

        self._write_plugin('FilePath', self._file_path)
        self._write_plugin('FileName', self._filename)
        if self._read_plugin('FilePathExists') == 0:
            raise Exception('File Path does not exits on server')
        self._write_plugin('AutoIncrement', 1)
        self._write_plugin('FileNumber', 0)
        self._write_plugin('FileTemplate', '%s%s_%3.3d.h5')
        self._write_plugin('NumCapture', 0)
        self._write_plugin('AutoSave', 1)
        self._write_plugin('FileWriteMode', 2)
        self._write_plugin('EnableCallbacks', 1)
        self._write_plugin('Capture', 1, wait=False)

    def deconfigure(self, *args, **kwargs):
        super(AreaDetectorHDF5, self).deconfigure(*args, **kwargs)
        self._write_plugin('Capture', 0, wait=False)
