# Recommended connector layout and signal description #

We recommend using 2x5 pinhead (keyed if there is a space for the plastic part on the board. The pin assignment is here (each signal is on pin pair to allow chaining):

**V+:** Power supply for bus-powered devices. keep in 7-15V range (valid input range for 7805, LE50... chips).

**GND:** Common ground signal

**BUS\_H:** High bus line

**BUS\_L:** Low bus line

**NC:** not connected (kind of keying, if you rotate the cable, it will not harm anything)

![http://robbus.googlecode.com/svn/trunk/images/robbus_connector.png](http://robbus.googlecode.com/svn/trunk/images/robbus_connector.png)

You can easily use 10-wire ribbon cable and connectors to interconnect the modules.

We have discussed using RS-45 connector as the standard one but it is almost impossible to route pair of these connectors on single-plated board.