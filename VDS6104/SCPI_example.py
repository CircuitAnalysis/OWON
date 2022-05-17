import pyvisa
import matplotlib.pyplot as plt

address = "USB0::0x5345::0x1235::2052100::INSTR"
resource = pyvisa.ResourceManager()
instrument = resource.open_resource(address)

def getSampleRate(outputs, bits, samplingPoints, timeBase):
    # see programming manual page 58
    maxSampleRates = {'single':{'8':1E9, '12': 500E6, '14':125E6}, 
                     'dual'  :{'8':1E9, '12': 500E6, '14':125E6},
                     'quad'  :{'8':1E9, '12': 500E6, '14':125E6}}
    maxRate = maxSampleRates[outputs][bits]
    samplingPointsPerDiv = {'1k':50, '10k':500, '100k':5E3,'1M':50E3,'10M':500E3,'25M':1.25E6,'50M':2.5E6,'100M':5E6,'250M':12.5E6}
    samplePts = samplingPointsPerDiv[samplingPoints]
    if maxRate > samplePts / timeBase:
        return samplePts / timeBase
    else:
        return maxRate

# THESE SETTINGS ARE TO CAPTURE A 1KHz, 1Vp WAVEFORM
# DIRECTLY WITH BNC (1X PROBE)

# Identify Device
resp = instrument.query("*IDN?")
print(resp)

# Set Time Scale
instrument.write(":HORIZONTAL:SCALE 200uS")

# Set Time Offset
instrument.write(":HORIZONTAL:OFFSET 0")

# Set CH1 Voltage Scale
instrument.write(":CH1:SCALE 200mV")
resp = instrument.query(":CH1:SCALE?")
print(resp)

# Set CH1 Voltage Offset
instrument.write(":CH1:OFFSET 0V")

# Set CH1 coupling
instrument.write(":CH1:COUPLING DC")

# Set Trigger Channel
instrument.write(":TRIGGER:SINGLE:EDGE:SOURCE CH1")

# Set Trigger Level
instrument.write(":TRIGGER:SINGLE:EDGE:LEVEL 0V")

# Set Trigger Coupling
instrument.write(":TRIGGER:SINGLE:EDGE:COUPLING DC")

# Enable CH1
instrument.write(":CH1:DISP ON")

# Capture Waveform Data
instrument.write(":ACQUIRE:MODE SAMPLE")
instrument.write(":ACQUIRE:DEPMEM 1K")
instrument.write(":ACQUIRE:PRECISION 8")
instrument.write(":WAVEFORM:BEGIN CH1")
instrument.write(":WAVEFORM:RANGE 0,1000")
data = instrument.query_binary_values(":WAVEFORM:FETCH?", datatype = 'h')
instrument.write(":WAVEFORM:END")

timeData = []
CH1VoltageData = []
sr = getSampleRate('single', '8', '1k', 200E-6)
print('sample rate: ', sr)
CH1ZeroOffset = 0
CH1VoltageScale = 0.2
for i in range(1000):
    d = data[i]
    timeData.append(float(i)/sr)
    # channel voltage = ( channel ADC data / 6400 - channel zero offset) * channel volt scale
    CH1VoltageData.append((float(d) / 6400 - CH1ZeroOffset) * CH1VoltageScale)

# Use MatPlotLib to plot the waveforms 
fig, ax = plt.subplots()

ax.set(xlabel='time (S)', ylabel='voltage (V)', title='WAVEFORM')

ax.plot(timeData, CH1VoltageData, "-g", label="CH1")

ax.grid()
plt.legend(loc="upper left")
plt.xlim([0, timeData[999]])
# verticalHeight = VOLT_MULT[VOLTS_PER_DIVISION] * VOLT_DIVISIONS / 2
# plt.ylim([-verticalHeight, verticalHeight])
plt.show()

print("COMPLETED!")