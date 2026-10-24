# Foobar2000 Media Player Control in Home Assistant

> [!WARNING]
> **This project is no longer maintained and the repository is archived.**
>
> Please use **[strepto42/foobar2k_custom_component](https://github.com/strepto42/foobar2k_custom_component)**
> ("Foobar 2000 Player") instead. It is in the HACS default catalog, is set up from the UI, supports
> media browsing and `play_media`, and uses the actively maintained
> [beefweb](https://github.com/hyperblast/beefweb) plugin (32- and 64-bit foobar2000) instead of foo_httpcontrol.
>
> **Migrating:**
>
> 1. In foobar2000, install the [beefweb](https://github.com/hyperblast/beefweb) component.
> 2. Remove the `platform: foobar2000` entries from your `configuration.yaml`.
> 3. In HACS, remove this repository (`talmuth/ha_foobar2k`) and its custom repository entry.
> 4. In HACS, search for and download **Foobar 2000 Player**, then restart Home Assistant.
> 5. Add it under **Settings → Devices & services → Add integration → Foobar 2000 Player**.
>
> The documentation below is kept for reference only.

This custom component allows Home Assistant to control the **Foobar2000** media player.

## 📌 Requirements

### 🔧 Foobar2000 Setup

This component requires modifications to your **Foobar2000** installation.
Refer to the [pyfoobar2k documentation](https://gitlab.com/ed0zer-projects/pyfoobar2k) for setup instructions.

## 🛠 Installation

### Manually

1. Place the `foobar2000` directory into:

   ```yaml
   <home_assistant_config_directory>/custom_components/
   ```

### Via [HACS](https://hacs.xyz/)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=talmuth&repository=ha_foobar2k&category=integration)

This component depends on the Python library [pyfoobar2k](https://gitlab.com/ed0zer-projects/pyfoobar2k).
Home Assistant will automatically install it during startup.

---

## ⚙️ Configuration Variables

| Variable          | Type              | Required | Default Value | Description                                                                       |
| ----------------- | ----------------- | -------- | ------------- | --------------------------------------------------------------------------------- |
| `host`            | `string`          | ✅ Yes    | —             | The hostname or IP address of the device running **Foobar2000**.                  |
| `port`            | `integer`         | ❌ No     | `8888`        | The port number used by the **foo_httpcontrol** plugin.                          |
| `name`            | `string`          | ❌ No     | `Foobar2000`  | The name displayed in the Home Assistant frontend.                                |
| `username`        | `string`          | ❌ No     | —             | The username for **foo_httpcontrol** authentication.                             |
| `password`        | `string`          | ❌ No     | —             | The password for **foo_httpcontrol** authentication.                             |
| `turn_on_action`  | `list`            | ❌ No     | —             | Home Assistant script sequence to call when `media_player.turn_on` is triggered.  |
| `turn_off_action` | `list`            | ❌ No     | —             | Home Assistant script sequence to call when `media_player.turn_off` is triggered. |
| `timeout`         | `integer`         | ❌ No     | `3`           | Connection timeout (in seconds) for connections to the Foobar2000 device.         |
| `volume_step`     | `integer` (1-100) | ❌ No     | `5`           | The amount of volume change when calling `volume_up` or `volume_down`.            |

---

## 📝 Configuration Examples

### ✅ Minimal Required Configuration

```yaml
media_player:
  - platform: foobar2000
    host: 192.168.1.100
```

### 🔹 Complete Configuration Example

```yaml
media_player:
  - platform: foobar2000
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

---

## 🏆 Credits

This project is based on work originally created by [@ed0zer](https://gitlab.com/ed0zer-projects/home-assistant/home-assistant-foobar2k).  
While the original code was not hosted on GitHub, it was published under the **MIT License**, and I greatly appreciate their contributions.

---

## 🎉 Support This Project

If you find this project helpful, consider supporting me:
[☕ Buy Me a Coffee](https://buymeacoffee.com/talmuth)

---
