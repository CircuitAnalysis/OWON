
def calc_valid_inputs(MIN_VAL, MAX_VAL, MANTISSA):
    """
    Produce a list of possible values between

    MIN_VAL and MAX_VAL using the MANTISSA exponent

    :param float MIN_VAL: Minimum value to start with

    :param float MAX_VAL: Maximum value to end with

    :param list MANTISSA: Exponent values to use

    :return list: List of possible values

    :example:
    >>> MIN_VAL = 2E-9
    >>> MAX_VAL = 10
    >>> MANTISSA = (1, 2, 5)
    >>> calc_valid_inputs(MIN_VAL, MAX_VAL, MANTISSA)

    [2e-09, 5e-09, 1e-08, 2e-08, 5e-08, 1e-07, 2e-07, 5e-07, 1e-06,
    2e-06, 5e-06, 1e-05, 2e-05, 5e-05, 0.0001, 0.0002, 0.0005, 0.001,
    0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]

    :note: In math the Mantissa is the fractional part\
    of the common base10 logarithm. From `Philipp Klaus/DS1054Z drivers.\
    <https://github.com/pklaus/ds1054z/blob/master/ds1054z/__init__.py>`_
    """
    values_valid = []

    # initialize with the decimal mantissa and exponent for min_val

    idx_mantissa = MANTISSA.index(int('{0:e}'.format(MIN_VAL)[0]))

    exponent = int('{0:e}'.format(MIN_VAL).split('e')[1])

    value = MIN_VAL
    while value <= MAX_VAL:
        values_valid.append(value)          #valid value found, add to list

        idx_mantissa += 1                   #construct the next value

        idx_mantissa %= len(MANTISSA)       #wrap MANTISSA to start if at end

        if idx_mantissa == 0: exponent += 1 #increment exponent for every wrap

        value = '{0}e{1}'.format(MANTISSA[idx_mantissa], exponent)
        value = float(value)
    return values_valid

# print(calc_valid_inputs(2E-3, 10, (1,2,5)))
# print(calc_valid_inputs(1e-9, 100, (1,2,5)))

def get_closest_value(input_value, MIN, MAX, MANTISSA):
    """
    Get the lowest difference value from calculated
    mantissa value.

    :param float input_value: target value

    :param int MIN: minimum setting allowed

    :param int MAX: maximum setting allowed

    :param list MANTISA: Scaling values typically (1,2,5)

    :example: Calculate lowest value for 0.250
    >>> get_closest_value(0.250, 2E-3, 10, (1,2,5)
    >>> 0.2
    """ 
    possible_values = calc_valid_inputs(MIN, MAX, MANTISSA)
    first_run       = 0
    lowest_value    = 0
    for value in possible_values:
        delta = abs(value - input_value)
        if not first_run:
            min_delta = delta
            first_run = 1
        if delta < min_delta:
            min_delta = delta
            lowest_value = value
        if delta == 0:
            return float(value)
    return lowest_value

def validate_input(target, vals_valid):
    """ 
    Input validation to find the lowest 
    delta between input value and a list
    of valid inputs.

    :param float target: data input for comparison

    :param list vals_valid: list of valid inputs

    :return float: lowest delta that exists in vals_valid

    :example:
    >>> allowable_values = [1, 2, 5, 10, 20]
    >>> validate_input(10.1, allowable_values)
    10
    """
    return min(vals_valid, key = lambda x:abs(x - target))

def check_index(target, dataset):
    """
    Get the index of an input within dataset

    :param float target: input to search for

    :param list dataset: sequence input to search in

    :return int: index where element exists 

    :example:
    >>> allowable_values = [1, 2, 5, 10, 20]
    >>> check_index(10, allowable_values)
    3

    :note: This function does not distinguish between\
    multiple occurances of the search term. It will\
    return the first occurance only.
    """
    return dataset.index(target)

def get_val_ceil(target, validated, vals_valid):
    """
    Get the next wholly-encompassing value of the input
    within the valid input list.

    :param float target: input command for comparison

    :param float validated: validated input for comparison

    :param list vals_valid: sequence of valid data 

    :return float: next wholly-encompassing value up to
    the maximum within the allowable values

    :example:
    >>> allowable_values = [1, 2, 5, 10, 20, 50]
    >>> target = 10.1
    >>> validated = 10
    >>> get_val_ceil(target, validated, allowable_values)
    20
    """
    if target <= validated:             #validated data encompasses our target
        return validated
    elif target > validated:            #validated data does not encompass our target
        if target > max(vals_valid):    #target exceeds max allowable value
            return validated
    else:                               #if available, return next larget value
        return vals_valid[check_index(validated, vals_valid) + 1]
