from quantiphy import Quantity
import scale
# print(Quantity("110e-6 S"))
# 
# channel_list = [1,2,3,4]
# 
# if 4 not in channel_list:
#     print("Nope!")


def validate_time(input_time):
    """
    The time within the scope sometimes needs a decimal
    even though it is all zeros.
    
    This function provides the proper validated numbers
    and zero pads based on contents of time_dec.
    
    :param float input_time: Input time figure
    
    :return string: string representation of time
    """
    
    time_dec = [1e-9, 2e-9, 5e-9,
                1e-6, 2e-6, 5e-6,
                1e-3, 2e-3, 5e-3,
                1, 2, 5]
    
    time = scale.get_closest_value(input_time, 1e-9, 100, (1,2,5))  #get value
    
    time = Quantity("{} s".format(time))    #add units
    
    if time.real in time_dec:   #if we are a zero-pad number
        s = time.render(strip_zeros=False, prec=1)  #don't strip zeros, use single decimal precision
    else:
        s = time.render()   #standard number, no padding needed
    s = s.split(" ")    #remove the space, reassemble
    s = "".join(s)
    return s

# # print(validate_time(1))
# 
# coupling_modes = ["AC", "DC", "GND",
#                   "ac", "dc", "gnd"]
# for channel in [1,2,3,4]:
#     for coupling in coupling_modes:
#         print(coupling)


resp = "CH1"
ch_map = {"CH1":1, "CH2":2, "CH3":3, "CH4":4}
if resp in ch_map.keys():
    print("Yes")
print(ch_map.keys())
print(ch_map[resp])