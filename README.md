
**Testing of foobar2000 media player control in Home Assistant**      

**foobar2000 Setup:**    
This component requires modifications to your foobar2000 installation         
Check readme of [pyfoobar2k](https://gitlab.com/ed0zer-projects/pyfoobar2k) for more information.      


**Home Assistant Setup:**   
Place `foobar` directory into `<home_assistant_config_directory>/custom_components/`
This component depends on python library [pyfoobar2k](https://gitlab.com/ed0zer-projects/pyfoobar2k)    
Home Assistant will automatically install the library during startup.  

Minimal configuration example:  
```
media_player:  
  - platform: foobar  
    host: 192.168.1.100  
```

Full configuration example:    
```
media_player:  
  - platform: foobar
    host: 192.168.1.100
    port: 8888
    username: user
    password: pass
    turn_on_action:
      service: switch.turn_on
      data_template:
        entity_id: switch.foobar2k
    turn_off_action:
      service: switch.turn_off
      data_template:
        entity_id: switch.foobar2k
```


