
### Foobar2000 media player control in Home Assistant      

##### Foobar2000 Setup 
This component requires modifications to your foobar2000 installation         
Check readme of [pyfoobar2k](https://gitlab.com/ed0zer-projects/pyfoobar2k) for more information.      


##### Home Assistant Setup
Place `foobar` directory into `<home_assistant_config_directory>/custom_components/`
This component depends on python library [pyfoobar2k](https://gitlab.com/ed0zer-projects/pyfoobar2k)    
Home Assistant will automatically install the library during startup.  

#### Configuration Variables

**host**
>*(string)(Required)*      
The hostname or IP address of the device that is running Foobar2000.

**port**
>*(integer)(Optional)*     
The port number Foobar2000 foo_httpcontrol plugin listens on.  
>>*Default value:*  
8888

**name**
>*(string)(Optional)*    
The name of the device used in the frontend.  
>>*Default value:*  
Foobar2000  

**username**  
>*(string)(Optional)*    
The username of Foobar2000 foo_httpcontrol plugin.  

**password**  
>*(string)(Optional)*    
The password of Foobar2000 foo_httpcontrol plugin.  

**turn_on_action**
>*(list)(Optional)*  
Home Assistant script sequence to call when media_player.turn_on is called.  

**turn_off_action**
>*(list)(Optional)*  
Home Assistant script sequence to call when media_player.turn_off is called.  

**timeout**  
>*(integer)(Optional)*  
Connection timeout for connections to Foobar2000 device.  
>>*Default value:*  
3  

**volume_step**
>*(integer)(Optional)(1 to 100)*  
Amount of volume to change when calling volume_up and volume_down.  
>>*Default value:*  
5  
    
    
##### A Minimal required configuration example:  
```
media_player:  
  - platform: foobar  
    host: 192.168.1.100  
```

##### A Complete configuration example:       
```
media_player:  
  - platform: foobar
    name: Foobar2000
    host: 192.168.1.100
    port: 8888
    timeout: 3
    username: user
    password: pass
    volume_step: 5
    turn_on_action:
      service: switch.turn_on
      data_template:
        entity_id: switch.foobar2k
    turn_off_action:
      service: switch.turn_off
      data_template:
        entity_id: switch.foobar2k
```  
If you like this project [Buy Me A Beer?](https://buymeacoffee.com/ed0zer)