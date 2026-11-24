# AMH-OS v10.3 Wi-Fi setup

This branch adds Wi-Fi station mode to both Arduino firmware sketches. Each ESP32 joins the same router independently; the S3-to-WROOM UART link remains unchanged.

## 1. Add your private Wi-Fi credentials

Do this separately in each sketch folder:

1. Copy `amh_wifi_secrets.example.h`.
2. Rename the copy to `amh_wifi_secrets.h`.
3. Edit the copied file and replace `YOUR_HOME_WIFI_NAME` and `YOUR_HOME_WIFI_PASSWORD`.
4. Keep the real `amh_wifi_secrets.h` files local. They are ignored by Git.

Folders:
- `firmware/arduino/main-esp32s3/AMH_OS_Main_S3/`
- `firmware/arduino/coprocessor-esp32/AMH_OS_Copro_WROOM/`

Use the same router credentials in both files. Do not paste Wi-Fi passwords into source code committed to GitHub.

## 2. Upload the WROOM coprocessor

- Open `AMH_OS_Copro_WROOM.ino`.
- Select **ESP32 Dev Module** and the WROOM's COM port.
- Upload, then open Serial Monitor at 115200 baud.
- Wait for the Wi-Fi connected message and note its IP address.

## 3. Upload the ESP32-S3 main controller

- Open `AMH_OS_Main_S3.ino`.
- Select **ESP32S3 Dev Module**, the correct COM port, 16 MB flash, and OPI PSRAM if those options are available for the board.
- Upload, then open Serial Monitor at 115200 baud.
- Wait for the Wi-Fi connected message and note its IP address.
- Confirm the coprocessor identity and periodic `Coprocessor link: OK` messages still appear.

## 4. Check coprocessor network status

The S3 currently performs the existing UART ping/identify exchange. The WROOM's UART `status` command now also reports `wifi_connected`, `wifi_ssid`, `wifi_ip`, and `wifi_rssi`.

## Scope of this milestone

This milestone enables both boards to join the home Wi-Fi network independently. It does **not** yet make Windows use the S3 as its internet adapter. USB RNDIS/NCM networking is a separate follow-up using the S3 native USB-OTG port and an ESP-IDF/TinyUSB networking implementation; it must be validated on the exact board and Windows driver before being advertised as working.
