from owon_vds6104 import *
import support

# def getSampleRate(outputs, bits, samplingPoints, timeBase):
#     # see programming manual page 58
#     maxSampleRates = {'single':{'8':1E9, '12': 500E6, '14':125E6}, 
#                      'dual'  :{'8':1E9, '12': 500E6, '14':125E6},
#                      'quad'  :{'8':1E9, '12': 500E6, '14':125E6}}
#     maxRate = maxSampleRates[outputs][bits]
#     samplingPointsPerDiv = {'1k':50, '10k':500, '100k':5E3,'1M':50E3,'10M':500E3,'25M':1.25E6,'50M':2.5E6,'100M':5E6,'250M':12.5E6}
#     samplePts = samplingPointsPerDiv[samplingPoints]
#     if maxRate > samplePts / timeBase:
#         return samplePts / timeBase
#     else:
#         return maxRate

# THESE SETTINGS ARE TO CAPTURE A 1KHz, 1Vp WAVEFORM
# DIRECTLY WITH BNC (1X PROBE)

scope = OwonVDS6104("USB0::0x5345::0x1235::2052100::INSTR")
print(scope.ident()) # Identify Device
scope.timebase = 200e-6 # Set Time Scale
scope.timebase_offset = 0 # Set Time Offset
scope.set_scale(1, 200e-3) # Set CH1 Voltage Scale
print("CH1 Scale: ", scope.get_scale(1))
scope.set_vertical_offset(1, 0) # Set CH1 Voltage Offset
scope.set_coupling(1, 'DC') # Set CH1 coupling
scope.trig_source = 1 # Set Trigger Channel
scope.trig_set_level = 0 # Set Trigger Level
scope.trig_coupling = 'DC' # Set Trigger Coupling
scope.set_channel_state(1, State.enable) # Enable CH1

# Capture Waveform Data
scope.acquire_mode = Acquire.sample
scope.memory_depth = '1K'
scope.precision = 8
time, wave = scope.capture(1)

support.plot_x_data(time, wave)
print("VPP = ", scope.measure(1, Measurement.vpp))

print("COMPLETED!")