

offsets = {'START':             {'OFFSET':0,    'TYPE':'U32'},
           'CHECK':             {'OFFSET':4,    'TYPE':'U32'},
           'DYNAMIC_CHECK':     {'OFFSET':8,    'TYPE':'U16'},
           'INFO_SIZE':         {'OFFSET':10,   'TYPE':'U16'},
           'RUN_STATUS':        {'OFFSET':12,   'TYPE':'U16'},
           'ADC_PRECISION':     {'OFFSET':14,   'TYPE':'U16'},
           'CH_NUMS':           {'OFFSET':16,   'TYPE':'U16'},
           'WAVE_DATA_SIZE':    {'OFFSET':18,   'TYPE':'U32'},
           'FRAME_NUMS':        {'OFFSET':22,   'TYPE':'U16'},
           'FFT_VALID':         {'OFFSET':24,   'TYPE':'U16'},
           'FFT_SIZE':          {'OFFSET':26,   'TYPE':'U32'},
           'DRAW_MODE':         {'OFFSET':30,   'TYPE':'U16'},
           'ROLL_MODE':         {'OFFSET':32,   'TYPE':'U16'},
           'ROLL_DATA_SIZE':    {'OFFSET':34,   'TYPE':'U32'},
           'FREQ_CH1':          {'OFFSET':38,   'TYPE':'U'},
           'FREQ_CH2':          {'OFFSET':42,   'TYPE':'U'},
           'FREQ_CH3':          {'OFFSET':46,   'TYPE':'U'},
           'FREQ_CH4':          {'OFFSET':50,   'TYPE':'U'},
           'REF_FREQ_CH1':      {'OFFSET':54,   'TYPE':'U'},
           'REF_FREQ_CH2':      {'OFFSET':58,   'TYPE':'U'},
           'REF_FREQ_CH3':      {'OFFSET':62,   'TYPE':'U'},
           'REF_FREQ_CH4':      {'OFFSET':66,   'TYPE':'U'},
           'ADC_OVER_FLAG':     {'OFFSET':70,   'TYPE':'U'},
           'ADC_MIN_CH1':       {'OFFSET':72,   'TYPE':'U'},
           'ADC_MIN_CH2':       {'OFFSET':74,   'TYPE':'U'},
           'ADC_MIN_CH3':       {'OFFSET':76,   'TYPE':'U'},
           'ADC_MIN_CH4':       {'OFFSET':78,   'TYPE':'U'},
           'ADC_MAX_CH1':       {'OFFSET':80,   'TYPE':'U'},
           'ADC_MAX_CH2':       {'OFFSET':82,   'TYPE':'U'},
           'ADC_MAX_CH3':       {'OFFSET':84,   'TYPE':'U'},
           'ADC_MAX_CH4':       {'OFFSET':86,   'TYPE':'U'},
           'ADC_AVG_CH1':       {'OFFSET':88,   'TYPE':'U'},
           'ADC_AVG_CH2':       {'OFFSET':90,   'TYPE':'U'},
           'ADC_AVG_CH3':       {'OFFSET':92,   'TYPE':'U'},
           'ADC_AVG_CH4':       {'OFFSET':94,   'TYPE':'U'},
           'TRIG_TYPE':         {'OFFSET':96,   'TYPE':'U'},
           'VOLTSCALE_CH1':     {'OFFSET':260,  'TYPE':'U'},
           'VOLTSCALE_CH2':     {'OFFSET':262,  'TYPE':'U'},
           'VOLTSCALE_CH3':     {'OFFSET':264,  'TYPE':'U'},
           'VOLTSCALE_CH4':     {'OFFSET':266,  'TYPE':'U'},
           'ZERO_CH1':          {'OFFSET':268,  'TYPE':'U'},
           'ZERO_CH2':          {'OFFSET':272,  'TYPE':'U'},
           'ZERO_CH3':          {'OFFSET':276,  'TYPE':'U'},
           'ZERO_CH4':          {'OFFSET':280,  'TYPE':'U'}
        }

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# print(offsets.keys())    

# class DotDict(dict):
#     """dot.notation access to dictionary attributes"""
#     def __getattr__(self, *args):
#         val = dict.get(*args)
#     if type(dict) is dict:
#         return dotdict(dict) 
#     else:
#         __setattr__ = dict.__setitem__
#         __delattr__ = dict.__delitem__

# print(m.START.OFFSET)
#https://stackoverflow.com/questions/2352252/how-to-use-dicts-in-mako-templates
#From user Lukasz
class Bunch(dict):
    def __init__(self, d):
        dict.__init__(self, d)
        self.__dict__.update(d)

def to_bunch(d):
    r = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = to_bunch(v)
        r[k] = v
    return Bunch(r)

m = to_bunch(offsets)
# print(dir(m))
print(m.__dict__.keys())

class offset():
    """
    Offsets for OwonVDS6104 oscilloscope
    """
    START            = 0
    CHECK            = 4
    DYNAMIC_CHECK    = 8
    INFO_SIZE        = 10
    RUN_STATUS       = 12
    ADC_PRECISION    = 14
    CH_NUMS          = 16
    WAVE_DATA_SIZE   = 18
    FRAME_NUMS       = 22
    FFT_VALID        = 24
    FFT_SIZE         = 26
    DRAW_MODE        = 30
    ROLL_MODE        = 32
    ROLL_DATA_SIZE   = 34
    FREQ_CH1         = 38
    FREQ_CH2         = 42
    FREQ_CH3         = 46
    FREQ_CH4         = 50
    REF_FREQ_CH1     = 54
    REF_FREQ_CH2     = 58
    REF_FREQ_CH3     = 62
    REF_FREQ_CH4     = 66  
    ADC_OVER_FLAG    = 70
    ADC_MIN_CH1      = 72
    ADC_MIN_CH2      = 74
    ADC_MIN_CH3      = 76
    ADC_MIN_CH4      = 78    
    ADC_MAX_CH1      = 80
    ADC_MAX_CH2      = 82
    ADC_MAX_CH3      = 84
    ADC_MAX_CH4      = 86
    ADC_AVG_CH1      = 88
    ADC_AVG_CH2      = 90
    ADC_AVG_CH3      = 92
    ADC_AVG_CH4      = 94    
    TRIG_TYPE        = 96
    VOLTSCALE_CH1    = 260
    VOLTSCALE_CH2    = 262
    VOLTSCALE_CH3    = 264
    VOLTSCALE_CH4    = 266
    ZERO_CH1         = 268
    ZERO_CH2         = 272
    ZERO_CH3         = 276
    ZERO_CH4         = 280