from enum import Enum

import pyvisa
from quantiphy import Quantity

import scale
import support

class State(Enum):
    """
    Enum for state selection

    Use State.<SETTING> for use with state methods
    """
    enable  = 1
    disable = 0

class Coupling(Enum):
    """
    Enum for channel coupling selection

    Use Coupling.<SETTING> with coupling methods
    """
    DC  = 'dc'
    dc  = 'dc'
    AC  = 'ac'
    ac  = 'ac'
    GND = 'gnd'
    gnd = 'gnd'

class Measurement(Enum):
    """
    Enum for measurement function selection

    Use Measurement.<SETTING> with measurement methods
    """
    vmax        = 'VMAX'
    vmin        = 'VMIN'
    vpp         = 'VPP'
    vtop        = 'VTOP'
    vbase       = 'VBASE'
    vamp        = 'VAMP'
    vavg        = 'VAVG'
    vrms        = 'VRMS'
    crms        = 'CRMS'
    overshoot   = 'OVER'
    preshoot    = 'PRES'
    pos_duty    = 'PDUT'
    neg_duty    = 'NDUT'
    period      = 'PER'
    freq        = 'FREQ'
    rise_time   = 'RTIM'
    fall_time   = 'FTIM'
    pos_width   = 'PWID'
    neg_width   = 'NWID'
    area        = 'AREA'
    cyc_area    = 'CAR'
    pos_puls    = 'PPUL'
    neg_puls    = 'NPUL'
    ris_edg_cnt = 'REDG'
    fal_edg_cnt = 'FEDG'

class Acquire(Enum):
    """
    Acquisition settings Enum

    Use Acquire.<SETTING> with trigger functions
    """
    sample  = 'SAMP'
    peak    = 'PEAK'

class Trigger(Enum):
    """
    Trigger settings Enum

    Use Trigger.<SETTING> with trigger functions
    """
    mode_edge   = 'EDGE'
    mode_video  = 'VID'
    mode_pulse  = 'PULS'
    mode_slope  = 'SLOP'

    source_ch1  = 'CH1'
    source_ch2  = 'CH2'
    source_ch3  = 'CH3'
    source_ch4  = 'CH4'

    couple_ac   = 'AC'
    couple_dc   = 'DC'
    couple_hf   = 'HF'

    slope_rise  = 'RISE'
    slope_fall  = 'FALL'

class OwonVDS6104:
    """
    Owon VDS6104 Driver using pyVISA for communications
    """
    def __init__(self, address):
        self.address = "USB0::0x5345::0x1235::2052100::INSTR"
        self.resource = pyvisa.ResourceManager()
        self.instrument = self.resource.open_resource(self.address)
        self.verbose_level = State.enable

        self.mantissa = (1, 2, 5)
        self.timebase_min = 1e-9
        self.timebase_max = 100

        self.scale_min = 2e-3
        self.scale_max = 5

        #20ms is minimum time interval {20ms-} pg 42 SDK docs
        self.min_measurement_time = 0.02

        self.scale_init()
        self.channel_list = [1,2,3,4]

    def send(self, command):
        """
        Wrapper for pyVISA instrument.write with
        conversion to string

        :param command: Input command to send to pyVISA
        """
        self.instrument.write(str(command))

    @property
    def timebase(self):
        """
        Get the oscilloscope timebase
        """
        resp = Quantity(self.query(":HORI:SCAL?"))
        return resp.real

    @timebase.setter
    def timebase(self, time_base):
        """
        Set the oscilloscope timebase

        :param float time_base: Horizontal division timebase
            Value can be expressed as an exponent, float, or int
            Valid inputs: "1e-6", "1", "0.001"

        :note: The time within the scope sometimes needs a decimal\
            even though it is all zeros.\
            This function provides the proper validated numbers\
            and zero pads based on contents of time_dec.
        """

        time_dec = [1e-9, 2e-9, 5e-9,
                    1e-6, 2e-6, 5e-6,
                    1e-3, 2e-3, 5e-3,
                    1, 2, 5]

        time_base = scale.get_closest_value(time_base, 1e-9, 100, (1,2,5))  #get value
        time_base = Quantity("{} s".format(time_base))    #add units

        if time_base.real in time_dec:   #if we are a zero-pad number
            time_base = time_base.render(strip_zeros=False, prec=1)
        else:
            time_base = time_base.render()   #standard number, no padding needed
        time_base = time_base.split(" ")     #remove the space, reassemble
        time_base = "".join(time_base)

        #note: instrument does not support writing in scientific notation
        #input must follow format :HORI:SCAL <time><units> where
        #there is no space between time and units and the s is lower case
        self.instrument.write(":HORI:SCAL {}".format(time_base))

    def set_coupling(self, channel, mode):
        """
        Set the oscilloscope channel coupling mode

        :param int channel: channel number [1,2,3,4]

        :param string coupling: coupling mode ['ac', 'dc', 'gnd']
        :note: Enum Coupling.[mode] also supported
        """
        if isinstance(mode, str):
            mode = mode.lower()

        if channel not in self.channel_list:
            raise Exception("Set Coupling Errror: invalid channel")

        if mode in ('ac', Coupling.AC, Coupling.ac):
            self.instrument.write(":CH{}:COUP AC".format(channel))

        elif mode in ('dc', Coupling.DC, Coupling.dc):
            self.instrument.write(":CH{}:COUP DC".format(channel))

        elif mode in ('gnd', Coupling.DC, Coupling.dc):
            self.instrument.write(":CH{}:COUP GND".format(channel))

    def get_coupling(self, channel):
        if channel not in self.channel_list:
            raise Exception("Get Coupling Errror: invalid channel")
        return self.query(":CH{}:COUP?".format(channel))

    def set_channel_state(self, channel, mode):
        """
        Configure display state of channels

        :param int channel: [1,2,3,4] Channel selection

        :param int mode: State.enable or State.disable
        """
        if channel in self.channel_list:
            if mode == State.enable:
                self.send(":CH{}:DISP ON".format(channel))
            elif mode == State.disable:
                self.send(":CH{}:DISP OFF".format(channel))
            else:
                raise Exception("Invalid state!")
        else:
            raise Exception("Invalid channel!")

    def get_channel_state(self, channel):
        """
        Get the display state of channel

        :param int channel: Channel selection [1,2,3,4]

        :return bool: State of channel display
        """

        resp = self.query(":CH{}:DISP?".format(channel))
        return bool(resp == "ON")

    @property
    def memory_depth(self):
        """
        Get current memory depth of device
        """
        return self.query(":ACQ:DEPMEM?")

    @memory_depth.setter
    def memory_depth(self, depth):
        #TODO: This function might benefit from either enums
        #or an addition method to enter values such as 1e3, etc
        available_depths = ['1K', '10K', '100K',
                            '1M', '10M', '25M',
                            '50M', '100M', '250M']
        if depth in available_depths:
            self.send(":ACQ:DEPMEM {}".format(depth))
        else:
            raise Exception("Invalid memory depth selected. " +
            "Supported depths: 1K, 10K, 100K, 1M, 10M, 25M " +
            "50M, 100M, 250M")

    @property
    def precision(self) -> int:
        """
        Get ADC Precision

        :return int: [8, 12, 14]
        """
        return int(self.query(":ACQ:PREC?"))

    @precision.setter
    def precision(self, num_bits):
        """
        Set ADC precision

        :note: The 6104P supports 12 and 14-bit\
        modes, however, the 6104 only supports 8-bit

        :param int num_bits: [8, 12, 14]
        """
        available_precisions = [8, 12, 14]

        if num_bits in available_precisions:
            self.send(":ACQ:PREC {}".format(num_bits))
        else:
            raise Exception("Invalid precision selected. "+
                            "Supported values: 8, 12, 14")

    @property
    def timebase_offset(self) -> float:
        """
        Get the current timebase offset in divisions

        :return float: Horizontal offset
        """
        return float(self.query(":HORI:OFFS?"))

    @timebase_offset.setter
    def timebase_offset(self, offset):
        """
        Set the horizontal trigger position from the timebase

        :note: Example:
            - move rightwards (negative division no.): - memory depth / 2 / \
            (sampling rate x time base)\
            - move leftwards (positive division no.): 50 000 000 / \
            (sampling rate x time base)\
            If the current main time base set at 500 us/div, \
            assume the horizontal movement is 2 division, the\
            horizontal offsets time will be 1.000 ms.

        :param float offsets: Offset of horizontal scale, in divisions
        """
        self.instrument.write(":HORI:OFFS {}".format(str(offset)))

    def get_trig_status(self):
        """
        Get the current trigger status

        :return string: "AUTO", "STOP", "SCAN" or "TRIG"
        """
        return self.query(":TRIG:STATUS?")

    def force_trig(self):
        """
        Command device to force an aquistion trigger
        """
        self.send("TRIG:FORC")

    def trig_set_half(self):
        """
        Set the trigger level to vertical mid-point
        """
        self.send("TRIG:HALF")

    @property
    def trig_set_level(self):
        """
        Gets the trigger level

        :return string:
        """
        return self.query(":TRIGGER:SINGLE:EDGE:LEVEL?")

    @trig_set_level.setter
    def trig_set_level(self, level):
        """
        Set trigger level

        :param string: trigger level in volts
        """
        self.send(":TRIGGER:SINGLE:EDGE:LEVEL {}".format(level))

    @property
    def trig_mode(self) -> Enum:
        """
        Get the trigger mode

        :return Enum: Trigger.mode_<MODE>\
        where mode is edge, video, pulse, or slope
        """
        resp_map = {"EDGE":Trigger.mode_edge,
                    "VIDeo":Trigger.mode_video,
                    "PULSe":Trigger.mode_pulse,
                    "SLOPe":Trigger.mode_slope}

        resp = self.query(":TRIG:SING:MODE?")

        return resp_map[resp]

    @trig_mode.setter
    def trig_mode(self, mode):

        if mode == Trigger.mode_edge:
            self.send(":TRIG:SING:MODE EDGE")
        elif mode == Trigger.mode_video:
            self.send(":TRIG:SING:MODE VID")
        elif mode == Trigger.mode_pulse:
            self.send(":TRIG:SING:MODE PULS")
        elif mode == Trigger.mode_slope:
            self.send(":TRIG:SING:MODE SLOP")
        else:
            raise Exception("Invalid trigger mode!")

    @property
    def trig_holdoff(self) -> float:
        """
        Get the trigger holdoff time, in seconds

        :return float: Trigger holdoff time, seconds
        """
        return float(self.query(":TRIG:SING:HOLD?"))

    @trig_holdoff.setter
    def trig_holdoff(self, hold_time):
        """
        Sets the trigger holdoff time

        :param float hold_time: holdoff time in seconds
        :note: Supports holdoffs from 100ns (100e-9) to 10s
        """
        if (float(hold_time) >= 100e-9) and (float(hold_time) <= 10):
            self.send(":TRIG:SING:HOLD {}".format(float(hold_time)))
        else:
            raise ValueError("Invalid trigger holdoff time!")

    @property
    def trig_source(self):
        """
        Gets the trigger source

        :return int: Channel of trigger source [1,2,3,4]
        """
        resp = self.query(":TRIG:SING:EDGE:SOUR?")

        ch_map = {"CH1":1, "CH2":2, "CH3":3, "CH4":4}

        if resp in ch_map.keys():
            return ch_map[resp]
        raise Exception("Instrument error: invalid input received!")

    @trig_source.setter
    def trig_source(self, source):

        if source in (1, Trigger.source_ch1):
            self.send(":TRIG:SING:EDGE:SOUR CH1")
        elif source in (2, Trigger.source_ch2):
            self.send(":TRIG:SING:EDGE:SOUR CH2")
        elif source in (3, Trigger.source_ch3):
            self.send(":TRIG:SING:EDGE:SOUR CH3")
        elif source in (4, Trigger.source_ch4):
            self.send(":TRIG:SING:EDGE:SOUR CH4")
        else:
            raise ValueError("Invalid trigger source!")

    @property
    def trig_coupling(self):
        """
        Gets the trigger coupling

        :return string: "DC", "AC", "HF"
        """
        return self.query(":TRIG:SING:EDGE:COUP?")

    @trig_coupling.setter
    def trig_coupling(self, mode):
        """
        Set trigger coupling

        :param enum mode: Trigger.couple_ac, Trigger.couple_dc, Trigger.couple_hf
        """
        if mode in ('ac', 'AC', Trigger.couple_ac):
            self.send(":TRIG:SING:EDGE:COUP AC")
        elif mode in ('dc', 'DC', Trigger.couple_dc):
            self.send(":TRIG:SING:EDGE:COUP DC")
        elif mode in ('hf', 'HF', Trigger.couple_hf):
            self.send(":TRIG:SING:EDGE:COUP HF")
        else:
            raise ValueError("Invalid trigger coupling!")

    def autoset(self):
        """
        Perform autoset

        :note: This function can take a considerable\
        amount of time. It should be used in\
        conjuction with get_autoset_progress
        """
        self.send(":AUT")

    def get_autoset_progress(self):
        """
        Gets autoset progress

        :return int: [1-100] percent
        """
        return int(self.query(":AUT:PROG?"))

    def self_calibrate(self):
        """
        Perform self calibration
        """
        self.send(":CAL")

    def get_calibration_progress(self):
        """
        Get self-calibration progress
        :return int:[1-100] percent
        """
        return self.query(":CAL:PROG?")

    def run(self):
        """
        Start running device
        """
        self.send(":RUN")

    def stop(self):
        """
        Stop running device
        """
        self.send(":STOP")

    def scale_init(self):
        self._timebase = scale.calc_valid_inputs(self.timebase_min,
                                                 self.timebase_max,
                                                 self.mantissa)

    def set_scale(self, channel, voltage):
        """
        Set the vertical division scale

        :param int channel:

        :param float scale:
        """
        if channel not in self.channel_list:
            raise Exception("Invalid channel selected")

        voltage = scale.get_closest_value(voltage,
                                          self.scale_min,
                                          self.scale_max,
                                          self.mantissa)
        voltage = Quantity("{} v".format(voltage))
        voltage = str(voltage).replace(' ', '')
        self.instrument.write(":CH{}:SCAL {}".format(channel, voltage))

    def get_scale(self, channel) -> float:
        """
        Get the current vertical division scale for channel

        :param int: channel: [1,2,3,4] Channel selection

        :return float: Voltage of selected channel scale
        """
        if channel not in self.channel_list:
            raise Exception("Invalid channel selected")
        resp = Quantity(self.instrument.query(":CH{}:SCAL?".format(channel)))
        return resp.real

    def query(self, command):
        """
        Send query to instrument, strip newlines
        """
        return self.instrument.query(str(command)).strip()

    def ident(self):
        """
        Query instrument for identification

        :return string: Identity from instrument
        """
        return self.query("*IDN?")

    def verbose(self, text):
        if self.verbose_level == State.enable:
            print(str(text))
        else:
            pass

    def check_model(self):
        """
        Verify the model of the selected instrument matches
        what is expected.

        :return string: "OWON <model no.> <serial number> VX.XX.XX"
        """
        identity = self.ident()
        identity = identity.strip()
        identity = identity.split(' ')

        if identity[0] == "OWON" and identity[1] == "VDS6104":
            mfg        = identity[0]
            model      = identity[1]
            serial     = identity[2]
            version    = identity[3]

            str_fmt = "Manufacturer:{} Model:{} S/N:{} Version:{}".format(mfg,
                                                                          model,
                                                                          serial,
                                                                          version)
            return str_fmt
        raise Exception("Device is not supported. " +
                        "Check the device model, address, or try again.")

    @property
    def measurement_source(self):
        """
        Get the measurement source for calculation functions
        """
        return self.query(":MEAS:SOUR?")

    @measurement_source.setter
    def measurement_source(self, channel):
        """
        Set the measurement source for calculation functions
        """
        if channel in self.channel_list:
            self.send(":MEAS:SOUR CH{}".format(channel))
        else:
            raise Exception("Invalid channel selected for measurement!")

    @property
    def state_measurement(self):
        return self.query(":MEAS:DISP?")

    @state_measurement.setter
    def state_measurement(self, mode):
        """
        Enable or disable the display of measurements

        :param enum mode: State.enable or State.disable
        """
        if mode is State.enable:
            self.send(":MEAS:DISP ON")
        elif mode is State.disable:
            self.send(":MEAS:DISP OFF")
        else:
            raise Exception("Invalid mode for measurement")

    def check_measurement_overflow(self):
        """
        Check for ADC overflow condition

        :return bool: Status of ADC overflow
        """
        resp = self.query(":MEAS:OVER?")

        return bool(resp == "TRUE")

    @property
    def time_measurement(self) -> float:
        """
        Gate interval of signal measurement function

        :return float: gate time interval
        """
        return float(self.query(":MEAS:TIM?"))

    @time_measurement.setter
    def time_measurement(self, time_interval):
        if time_interval >= self.min_measurement_time:
            self.send(":MEAS:TIM {}".format(time_interval))
        else:
            raise Exception("Invalid time interval set!")

    #TODO: Implementation of dual channel measurements
    def measure(self, channel, function):
        """
        measurement function that supports many different
        hardware measurements.

        :param int channel: [1,2,3,4] Channel to perform measurement on

        :param enum function:
            measurement.<function> where <function> can be:
           - vmax        - maximum value, volts
           - vmin        - minimum value, volts
           - vpp         - peak to peak, volts
           - vtop        - top value, volts
           - vamp        - amplitude value, volts
           - vavg        - average value, volts
           - vrms        - rms value, volts
           - crms        - cycle rms value, volts
           - overshoot   - overshoot, percent
           - preshoot    - preshoot, percent
           - pos_duty    - positive duty cycle, percent
           - neg_duty    - negative duty cycle, percent
           - period      - cycle time, seconds
           - frequency   - frequency, hertz
           - rise_time   - rise time, seconds
           - fall_time   - fall time, seconds
           - pos_width   - positive pulse width time, seconds
           - neg_width   - negative pulse width time, seconds
           - area        - area, volt-seconds
           - cyc_area    - cycle area, volt-seconds
           - pos_puls    - positive pulse count, integer
           - neg_puls    - negative pulse count, integer
           - ris_edg_cnt - number of rising edges, integer
           - neg_edg_cnt - number of falling edges, number
        :return string: string representation of measurement
        """
        self.measurement_source = channel
        self.state_measurement = State.enable

        function_map = {Measurement.vmax        :"VMAX",
                        Measurement.vmin        :"VMIN",
                        Measurement.vpp         :"VPP",
                        Measurement.vtop        :"VTOP",
                        Measurement.vbase       :"VBASE",
                        Measurement.vamp        :"VAMP",
                        Measurement.vrms        :"VRMS",
                        Measurement.crms        :"CRMS",
                        Measurement.overshoot   :"OVER",
                        Measurement.preshoot    :"PRES",
                        Measurement.pos_duty    :"PDUT",
                        Measurement.neg_duty    :"NDUT",
                        Measurement.period      :"PER",
                        Measurement.freq        :"FREQ",
                        Measurement.rise_time   :"RTIM",
                        Measurement.fall_time   :"FTIM",
                        Measurement.pos_width   :"PWID",
                        Measurement.neg_width   :"NWID",
                        Measurement.area        :"AREA",
                        Measurement.cyc_area    :"CAR",
                        Measurement.pos_puls    :"PPUL",
                        Measurement.neg_puls    :"NPUL",
                        Measurement.ris_edg_cnt :"REDG",
                        Measurement.fal_edg_cnt :"FEDG"
                        }
        if function in function_map.keys():
            query_msg = ":MEAS:{}?".format(function_map[function])
            return self.query(query_msg)
        raise Exception("Invalid measurement selected!")

    def get_vertical_offset(self, channel) -> float:
        """
        Get vertical offset of the channel

        :param int channel: Channel number [1,2,3,4]

        :return float: offset, in divisions
        :note: voltage can be calculated by offset * scale_voltage
        """

        if channel in self.channel_list:
            return float(self.query(":CH{}:OFFS?".format(channel)))
        raise Exception("Invalid channel selected!")

    def set_vertical_offset(self, channel, offset):
        """
        Set vertical offset for input channel

        :param int channel: Channel number [1,2,3,4]

        :note: Range of allowable values varies with scale:
            - 2mV:   -1000 to 1000
            - 5mV:   -400  to 400
            - 10mV:  -200  to 200
            - 20mV:  -100  to 100
            - 50mV:  -40   to 40
            - 100mV: -200  to 200
            - 500mV: -40   to 40
            - 1V:    -40   to 40
            - 2V:    -20   to 20
            - 5V:    -8    to 8
        """
        if channel in self.channel_list:
            self.send(":CH{}:OFFS {}".format(channel, offset))
        else:
            raise Exception("Invalid channel!")

    def set_bw_limit(self, channel, mode):
        """
        Set bandwidth limit. Supports only 20MHz limit.

        :param int channel: [1,2,3,4] Channel of limit

        :param enum mode: [State.enable, State.disable]
        :example:
            >>> set_bw_limit(1, State.enable)
        """
        if channel in self.channel_list:
            if mode is State.enable:
                self.send(":CH{}:BAND 20M".format(channel))
            elif mode is State.disable:
                self.send(":CH{}:BAND OFF".format(channel))
            else:
                raise Exception("Invalid mode!")

    def get_bw_limit(self, channel):
        """
        Get bandwidth limit of channel

        :param int channel: [1,2,3,4] Channel to get

        :return bool: True if enabled, False otherwise
        """
        if channel in self.channel_list:
            resp = self.query(":CH{}:BAND?".format(channel))
            return bool(resp == "20M")
        raise Exception("Invalid channel!")

    def capture(self, channel):
        """
        Perform a waveform capture of channel

        :param int channel: Channel to capture from

        :return list, list: time, wave in float format

        :note: time output is calculated based upon\
        the scale_time parameter. wave is calculated\
        based upon the scale and offset values from\
        ADC counts.
        """
        #Check memory depth
        #Enable channel?
        # #     self.instrument.write(":ACQ:DEPMEM 1M")
        # voltage = (count/6400 - zero_offset) * volt_scale
        # We probably want to include a probe attenuation factor multiplier, too.

        scale_time = self.timebase
        scale_voltage = self.get_scale(channel)
        offset_divisons = self.get_vertical_offset(channel)
        volt_wave = list()
        time = list()
        if channel in self.channel_list:
            self.send(":WAV:BEG CH{}".format(channel))
            self.send("WAV:RANG 0,1000") #TODO: Change programmatically?
            adc_wave = self.instrument.query_binary_values(":WAV:FETC?", datatype = 'h')
            self.send(":WAV:END") #end capture
        for index, value in enumerate(adc_wave):
            volt_wave.append((float(value) / 6400 - offset_divisons) * scale_voltage)
            time.append(scale_time * index)
        return time, volt_wave

    @property
    def acquire_mode(self):
        """
        Get the acquisition mode

        :return string:
        """
        return self.query(":ACQ:MODE?")

    @acquire_mode.setter
    def acquire_mode(self, mode):
        """
        Set the acquistion mode of device

        :param enum mode: Acquire.peak or Acquire.sample
        """
        if mode == Acquire.peak:
            self.send(":ACQ:MODE PEAK")
        elif mode == Acquire.sample:
            self.send(":ACQ:MODE SAMP")

if __name__ == "__main__":
    scope = OwonVDS6104("")
#     scope.set_coupling(1, 'DC')
#     scope.set_scale(1, 200e-3)
#     scope.timebase      = 1e-6
#     scope.memory_depth  = '1K'
#     scope.precision     = 8
#     scope.set_vertical_offset(1, 0)

#     time, wave = scope.capture(1)
#     support.plot_x_data(time, wave)
    print(scope.measure(1, Measurement.vrms))
    print(scope.measure(2, Measurement.vrms))