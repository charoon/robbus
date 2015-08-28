# Service packet #

Service packet has currently used for changing node address, to verify node presence and to retrieve data structure sizes (ping).

## Ping ##
To verify node presence, you can send ping (echo) packet with following structure (the payload is optional and must not be longer than max allowed payload for either request or response. At least 3 bytes are guaranteed.

```
<0x01><address><0x01 + payload length><'e'><whatever you want><checksum>
```

The response is

```
<0x01><address + 128><0x01 + payload length><'e'><whatever you want><checksum>
```

## Data description ##
This command allows you to check required request and response payload sizes. You send following request

```
<0x01><address><0x01><'d'><checksum>
```

and the response will be

```
<0x01><address + 128><0x02><request data size><response data size><checksum>
```



## Address change ##
The initial node address is hardcoded in program (in fiole robbus\_config.h). However you can override it and change. The value will be permanently stored in EEPROM memory (in reference implementation on addresses 0x04 - 'R' flag and 0x05 - address itself). To change the address send a packet with following structure. Note that the address on the bus must be unique.

```
<0x01><current address><0x04><'a'><new address><current address><current address XOR new address><checksum>
```

The response is (in case the change passed, nothing otherwise)

```
<0x01><old address + 128><0x02><'a'><new address><checksum>
```