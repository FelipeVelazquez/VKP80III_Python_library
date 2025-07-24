# VKP80III_Python_Library

Library for the Custom® VKP80III kiosk printer.  
This library is based on the command manual.

## Current and Future Functions

- [x] Print function  
- [x] Change to Latin encoding (English by default)  
- [x] Set alignment  
- [x] Feed lines  
- [x] Set font size  
- [x] Cut and eject paper  
- [x] Print QR codes  
- [ ] Print barcodes  
- [ ] Get printer status  
- [ ] Read paper status  
- [ ] Check black mark paper  

## Configuration

Before using the library, make sure your printer is set to Virtual COM mode.

To do this, follow the physical configuration steps in the official manual.

Once the printer is configured in Virtual COM mode, you need to install the appropriate drivers.  
For example, for model `915DX011700300`  
(This is the model with both USB and RS232 interfaces. Make sure to check the correct model you are using.)  
You can download the following driver: [_Virtual COM driver for Linux system 1.03_](https://www.custom.biz/es_ES/producto/hardware/impresoras/impresoras-de-kioskos-de-tiques/vkp80iii)

## System Tested

Tested only on Raspbian.

## Installation on Raspbian

To install:

1. Extract the `.zip` file.  
2. Inside the extracted directory, untar the `.tgz` file.  
3. Inside the extracted tar directory, locate the `Makefile`.  
4. Run:  
   ```bash
   make EXTRA_CFLAGS="-I/lib/modules/$(uname -r)/build/include"
   ```
5. Copy the compiled `customvcom.ko` file:  
   ```bash
   sudo cp customvcom.ko /lib/modules/$(uname -r)/kernel/drivers/usb/serial/
   ```
6. Run:  
   ```bash
   sudo modprobe usbserial
   ```
7. Run:  
   ```bash
   sudo modprobe customvcom
   ```
8. Check if `/dev/ttyUSB0` appears in the `/dev/tty*` list.

## Cut and Eject Function

This function differs from traditional ESC/POS systems.  
Custom® printers use a hex command system based on Virtual COM (see the Configuration section).

## How to Use

Basic usage (print and cut a ticket):

```python
from vkp80iii_printer import VKP80IIIPrinter

# Connect to the printer using the appropriate port (e.g., /dev/ttyUSB0)
printer = VKP80IIIPrinter(port="/dev/ttyUSB0", baudrate=9600)

printer.open()

printer.reset()

printer.print_text("Hello World")

printer.feed_lines(3)

printer.cut_paper(mode='eject', length=10, timeout=3)
```

> [!NOTE]  
> The `cut_paper` function has four important arguments:  
> - `mode='eject'`: (`eject` or `retract`) — "eject" expels the ticket, "retract" pulls it back in.  
> - `length=6`: Indicates the number of steps (in mm) for ticket presentation.  
> - `blink=True`: Controls the blinking behavior of the paper mouth.  
> - `timeout=1`: Sets the timeout before automatic ejection.  
>  
> After the paper is presented and the timeout ends, the selected mode is executed.
