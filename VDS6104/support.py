import matplotlib.pyplot as plt
import pyvisa

def plot_x_data(x, y):
    fig, ax = plt.subplots()
    ax.set(title='Dataset')
    ax.plot(x, y)
    ax.grid()
    plt.show()
    
def get_available_instruments():
    """
    List of available instruments found as VISA resources
    
    :return list: Available instrument IDs
    """
    rm = pyvisa.ResourceManager()
    return(rm.list_resources())

def invert_endian(list_slice):
    """
    Reverses the endian of a list
    """
    data = list_slice
    data.reverse()
    return data

def u8_to_u32(list_slice):
    """
    Convert U8 (unsigned char) to U32 datatype
    """
    data = (list_slice[0] << 24) | (list_slice[1] << 16) | (list_slice[2] << 8) | (list_slice[3])
    return data

def convert_list_to_int(list_slice):
    """
    Convert a list of bytes to a different data type. 
    Currently supports return of 32 and 16 bit values
    
    :param list list_slice: list of 1-byte values
    
    :return int: converted datatype
    """
    list_slice = invert_endian(list_slice)
    
    if len(list_slice) == 4:   #return 32-bit
        return (list_slice[0] << 24) | (list_slice[1] << 16) | (list_slice[2] << 8) | (list_slice[3])
    elif len(list_slice) == 2: #return 16 bit
        return (list_slice[0] << 8) | (list_slice[1])
    
