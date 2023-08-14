# BSOD script

I found this endpoint in the windows API which can be called with the `ctypes` library, which goes by the name of
`NtRaiseHardError`, which basically triggers a BSOD.

I wrapped the function call in a separate function called `crasher()`

## How does this function work?

The function calls two other windows API calls: 
- RtAdjustPrivilege    
- RtRaiseHardError

lets look at both the functions separately

### RtAdjustPrivilege

Hard error cant be raised without the calling process to have a higher privilege. Here, we are essentially triggering a BSOD which
requires a shutdown/restart permission.

Hence, this code is used to elevate the process's privileges to have the shutdown privilege.

Parameters:
- `c_uint(19)`:       The privilege level to be adjusted. In this case, it corresponds to the `SeShutdownPrivilege` privilege, which allows the calling process to shut down the system.  
- `c_uint(1)`:        The new privilege state, which is set to `1` to enable the privilege.
- `c_uint(0)`:        The third parameter is not used and is set to `0`.
- `byref(c_int())`:   the last parameter is used to store the previous privilege state, but it's passed a null pointer (nullptr), so it won't be able to retrieve the previous state.


### RtRaiseHardError

This is the function that is responsible for raising the `Hard error`, or `BSOD`. Lets look at the parameters:



- `c_ulong(0xC0000094)`:  Its the status error code, corresponding to the DIVIDE_BY_ZERO_ERROR, which is self explanatory. Very harmless 
- `c_ulong(0)`:           The second parameter is not used and is set to 0.
- `nullptr`:              The third parameter is a pointer to a string that provides additional information about the error. We dont need that so its pointing to null.
- `null_ptr`:             The fourth parameter is a pointer to the context record, which has processor-specific context information,which we dont need.
- `c_uint(6)`:            The fifth parameter specifies the type of the hard error. 6 indicates shutdown type error.
- `byref(c_uint())`:      This parameter is used to store the response option selected by the user in response to the hard error.Here, nulltpr is used (c_uint()) and hence the response wont be retrievable.



So this wraps up the `crasher()` funciton. Now I wrote a simple `Tkinter` script that generates random equations and sometimes it will generrate an equation that will divide by zero. Thats when the `crasher()` function is called.
Very Fun!


### Note: If you wish to run the script without teh crasher() being called, just call the python script and append `debug`


