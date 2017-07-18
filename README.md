connector-client
================

A Python client providing a quasi-framework for users wanting to integrate their personal IoT project / device with the SEPL platform.

Written in Python3 and relying on the `websockets` module.

----------

**Environment variables**
> 
> `CONNECTOR_LOOKUP_URL` (default:
> 'http://fgseitsrancher.wifa.intern.uni-leipzig.de:8093/lookup')
> 
> `CONNECTOR_DEVICE_REGISTRATION_PATH` (default: 'discovery')
> 
> `CONNECTOR_HTTPS` (default: None)
> 
> `CONNECTOR_USER` (default: '')
> 
> `CONNECTOR_PASSWORD` (default: '')
> 
> `LOGLEVEL` (default: 'info')


**Basic client structure**

    from modules.logger import root_logger
    from connector.connector import Connector
    from connector.message import Message
    from connector.device import Device
    
    logger = root_logger.getChild(__name__)
    
    
    # your code


    if __name__ == '__main__':
        connector = Connector()
        
        # start your code


Basic Usage
-----------

**Send a message to the platform**
> 
>     Connector.send() 
> 
> Requires a `Message` object as argument.
> 

**Receive a message from the platform**
> 
>     Connector.receive()
> 
> Blocks and returns when a message is received from the platform.
> Returned object is a `Message` object containing the payload and
> metadata.
> 

**Register a device to the platform**
> 
>     Connector.register()
> 
> Requires a `Device` object as argument.
> 

 **Remove a device from the platform**
> 
>     Connector.unregister()
> 
> Requires a `Device` object as argument.


Create a device
-----------------

**Device structure**

> `id` local id of a device.
> 
> `type` type of a device.
> 
> `name` name of a device.

**Example**

    my_device = Device('unique device id', 'device type', 'device name')


Create a message
----------------
*Non-final implementation of Message, breaking changes imminent.*

**Message structure**

> `device_id` local id of a device.
> 
> `timestamp` message timestamp set by platform (receive) / connector (send).
> 
> `endpoint` local endpoint set by platform.
> 
> `payload_header` payload metadata.
> 
> `payload` message content.

**Example**

    my_message = Message()
    my_message.device_id = 'unique device id'
    my_message.payload_header = "'Content-Type': 'application/json'"
    my_message.payload = "{'unit': 'kW', 'value': '1.43'}"


Advanced configuration
----------------------

For time-critical applications it's possible to use callbacks for client-code execution. When creating a `Connector` object two optional arguments (`con_callbck`, `discon_callbck`) can be used to start / resume or halt / pause execution.

`con_callbck` will be executed when a connection to the SEPL platform has been established.

`discon_callbck` will be executed if the connection to the SEPL platform is closed / lost.

**Example**

    def resumeThread():
       pass
    
    def pauseThread():
       pass
       
       
    connector = Connector(con_callbck=resumeThread, discon_callbck=pauseThread)


