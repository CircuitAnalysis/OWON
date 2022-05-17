import unittest
import time

from quantiphy import Quantity
from owon_vds6104 import *

class TestOwonVDS6104(unittest.TestCase):
    """
    Unit testing methods for Owon VDS6104 driver

    :note: Test should be conducted with\
    freshly power-cycled device.\
    Some previously set settings may\
    cause test failures otherwise.
    """
    voltages = [2e-3, 5e-3, 10e-3,
                20e-3, 50e-3, 50e-3,
                100e-3, 200e-3, 500e-3,
                1, 2, 5]
    timebases = [1e-09, 2e-09, 5e-09,
                1e-08, 2e-08, 5e-08,
                1e-07, 2e-07, 5e-07,
                1e-06, 2e-06, 5e-06,
                1e-05, 2e-05, 5e-05,
                0.0001, 0.0002, 0.0005,
                0.001, 0.002, 0.005,
                0.01, 0.02, 0.05,
                0.1, 0.2, 0.5,
                1.0, 2.0, 5.0,
                10.0, 20.0, 50.0,
                100.0]

    channels = [1, 2, 3, 4]
    cmd_delay = 0.00 #to account for operation time if needed

    @classmethod
    def setUpClass(cls):
        cls.scope = OwonVDS6104("")

    def test_vertical(self):
        """
        Test all vertical display combinations for all channels
        """
        for channel in self.channels:
            for voltage in self.voltages:
                self.scope.set_scale(channel, voltage)

                time.sleep(self.cmd_delay)                  #ensure we don't flood device

                v_resp = self.scope.get_scale(channel)

                v_cmd = Quantity("{} v".format(voltage))

                self.assertEqual(v_resp.real, v_cmd.real)

    def test_horizontal(self):
        """
        Test all horizontal display combinations
        """
        for timebase in self.timebases:
            self.scope.timebase = timebase
            time.sleep(self.cmd_delay)
            cmd_time = Quantity("{}s".format(timebase))

            self.assertEqual(cmd_time.real, self.scope.timebase)

    def test_coupling(self):
        """
        Test upper and lowercase values of inputs for coupling for all channels
        """
        #upper, lower, enum?
        coupling_modes = ["AC", "DC", "GND",
                          "ac", "dc", "gnd"]
        for channel in self.channels:
            for coupling in coupling_modes:
                self.scope.set_coupling(channel, coupling)
                time.sleep(self.cmd_delay)
                self.assertEqual(coupling.upper(), self.scope.get_coupling(channel))

    def test_measurement_source(self):
        """
        Test the measurement source function
        """
        for channel in self.channels:
            self.scope.measurement_source = channel
            time.sleep(self.cmd_delay)
            self.assertEqual("CH{}".format(channel), self.scope.measurement_source)

    def test_measurement_time(self):
        """
        Test the measurement gate time function
        Uses assertAlmostEqual to round to 2 decimal places only.
        """
        for time in [0.02, 0.03, 0.04, 0.05,
                     0.2, 0.5, 1, 2, 5]:
            self.scope.time_measurement = time
            self.assertAlmostEqual(time, self.scope.time_measurement, places = 2)

    def test_bandwidth_limit(self):
        """
        Test the bandwidth limit functionality for all channels
        """
        for channel in self.channels:
            self.scope.set_bw_limit(channel, State.enable)
            self.assertEqual(True, self.scope.get_bw_limit(channel))
            time.sleep(self.cmd_delay)
            self.scope.set_bw_limit(channel, State.disable)
            self.assertEqual(False, self.scope.get_bw_limit(channel))

    def test_channel_dispay(self):
        """
        Test the display functionality for all channels
        """
        for channel in self.channels:
            self.scope.set_channel_state(channel, State.enable)
            response = self.scope.get_channel_state(channel)
            self.assertEqual(response, True)

            time.sleep(self.cmd_delay)
            self.scope.set_channel_state(channel, State.disable)
            response = self.scope.get_channel_state(channel)
            self.assertEqual(response, False)
            time.sleep(self.cmd_delay)

    def test_trigger_holdoff(self):
        """
        Test the trigger holdoff functionality
        """
        #Workaround for setting property value
        #Assignments not supported in lambda
        #and assertRaises only supports function methods
        def property_workaround(value):
            self.scope.trig_holdoff = value

        pass_case = ['100e-9', 100e-9, 250e-9, 1, '1', 10]
        failure_case = ['11', 10.25, -25, -15]

        for period in pass_case:
            self.scope.trig_holdoff = period
            time.sleep(self.cmd_delay)
            self.assertEqual(float(period), self.scope.trig_holdoff)

        for period in failure_case:
            self.assertRaises(ValueError, property_workaround, period)
            time.sleep(self.cmd_delay)

    def test_trig_coupling(self):
        """
        Test trigger coupling
        """
        for coupling in ['AC', 'DC', 'HF',
                         'ac', 'dc', 'hf',
                         Trigger.couple_ac,
                         Trigger.couple_dc,
                         Trigger.couple_hf]:
            self.scope.trig_coupling = coupling
            if isinstance(coupling, str):
                self.assertEqual(coupling.upper(), self.scope.trig_coupling)
            else:
                self.assertEqual(coupling.value.upper(), self.scope.trig_coupling)

    def test_memory_depth(self):
        """
        Test single channel memory depth

        :note: Larger memory modes are only\
        supported with single channel enabled
        """
        self.scope.timebase = 1e-9

        self.scope.set_channel_state(1, State.enable)
        self.scope.set_channel_state(2, State.disable)
        self.scope.set_channel_state(3, State.disable)
        self.scope.set_channel_state(4, State.disable)
        available_depths = ['1K', '10K', '100K',
                            '1M', '10M', '25M',
                            '50M', '100M', '250M']
        for depth in available_depths:
            self.scope.memory_depth = depth
            self.assertEqual(depth, self.scope.memory_depth)

    def test_timebase_offset(self):
        """
        Test timebase offset functionality
        """
        offsets = [1, 2, 3, 4, 5, 6, 7, 8]
        for offset in offsets:
            self.scope.timebase_offset = offset
            self.assertEqual(offset, self.scope.timebase_offset)

    def test_trig_mode(self):
        """
        Test trigger modes
        """
        available_modes = [Trigger.mode_edge,
                           Trigger.mode_video,
                           Trigger.mode_pulse,
                           Trigger.mode_slope]

        for mode in available_modes:
            self.scope.trig_mode = mode
            self.assertEqual(mode, self.scope.trig_mode)

    def test_trig_source(self):
        """
        Test trigger source
        """
        sources = [1, 2, 3, 4,
                   Trigger.source_ch1,
                   Trigger.source_ch2,
                   Trigger.source_ch3,
                   Trigger.source_ch4]

        ch_map = {'CH1':1, 'CH2':2,
                  'CH3':3, 'CH4':4}
        for source in sources:
            self.scope.trig_source = source
            if isinstance(source, int):
                self.assertEqual(source, self.scope.trig_source)
            else:
                self.assertEqual(ch_map[source.value], self.scope.trig_source)

    def test_vertical_offset(self):
        """
        Test vertical offsets
        """
        offsets = [-1, -2, -3, -4,
                   1, 2, 3, 4]
        channels = [1, 2, 3, 4]
        for channel in channels:
            for offset in offsets:
                self.scope.set_vertical_offset(channel, offset)
                self.assertEqual(offset, self.scope.get_vertical_offset(channel))
