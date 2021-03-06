#!/usr/bin/env python2.7
'''A simple test for :class:`EpicsSignal`'''

import time

import config
from ophyd import (EpicsSignal, Signal)
from ophyd.utils.epics_pvs import record_field


def callback(sub_type=None, timestamp=None, value=None, **kwargs):
    logger.info('[callback] [%s] (type=%s) value=%s', timestamp, sub_type,
                value)

    # Test that the monitor dispatcher works (you cannot use channel access in
    # callbacks without it)
    logger.info('[callback] caget=%s', rw_signal.get())

logger = config.logger

motor_record = config.motor_recs[0]
val = record_field(motor_record, 'VAL')
rbv = record_field(motor_record, 'RBV')

rw_signal = EpicsSignal(rbv, write_pv=val)
rw_signal.subscribe(callback, event_type=rw_signal.SUB_VALUE)
rw_signal.subscribe(callback, event_type=rw_signal.SUB_SETPOINT)

rw_signal.value = 2
time.sleep(1.)
rw_signal.value = 1
time.sleep(1.)

# You can also create a Python Signal:
sig = Signal(name='testing', value=10)
logger.info('Python signal: %s', sig)
