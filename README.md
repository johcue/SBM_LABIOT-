# SBM - Smart Beverage Machine

SBM (Smart Beverage Machine) is a gesture-controlled beverage dispenser designed to provide a hygienic, efficient, and engaging solution for serving beverages. Using gesture recognition and automation, it minimizes physical interaction, making it ideal for various settings.

## Table of Contents
- [How Does It Work?](#how-does-it-work)
- [Why SBM?](#why-sbm)
- [Demo](#demo)
- [Installation and Usage](#installation-and-usage)
- [Contributors](#contributors)

## How Does It Work?

SBM integrates several technologies to deliver a seamless experience:

### Software
- **Python**: For gesture detection, workflow control, and database management using MySQL.
- **MQTT**: Facilitates communication between devices and gesture detection systems.
- **Arduino**: Manages the hardware components, including controlling the liquid pumps, the camera server, and the LCD user interface.

### Hardware
- **ESP32-CAM**: Captures gestures for control input.
- **Relays**: Manages the operation of pumps.
- **LCD Display**: Provides a user interface for status and settings.
- **Pumps**: Dispenses beverages.
- **Power Module, Breadboard, and Jumpwires**: For reliable power delivery and connectivity.
- **Wall Connector**: Supplies main power.

### Workflow
1. **Gesture Detection**: The ESP32-CAM captures user gestures.
2. **Data Processing**: Python handles gesture interpretation and controls the workflow.
3. **Hardware Control**: Arduino firmware ensures proper operation of pumps, the LCD interface, and overall system coordination.
4. **Beverage Dispensing**: Pumps are activated based on user input, and the LCD displays real-time updates.

## Why SBM?

- **Hygiene**: Reduces physical contact, promoting a safer beverage dispensing process.
- **Efficiency**: Automates operations, saving time and effort.
- **Engaging**: Utilizes modern technology to create an innovative user experience.

## Demo

Check out the demo of SBM in action:  
[GitHub Repository Demo](https://github.com/johcue/SBM_LABIOT-)

## Installation and Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/johcue/SBM_LABIOT-

## Contributors
- Johan Chicue
- Martin Cardaci

## Deployment
Pre req.
- Deploy a MYSQL Server
- View Demo video to use  e.g.> Start 5 five left hand /// then select (right hand).. Index = Coffe .. Index+Medium finger = Late OR... Fist = Milk

1. PowerON the SBM 

2. Run newpython/test2 - MySQL.py

(If you need to change some on Arduino Sketch > CameraWebServer_Bombs/CameraWebServer_Bombs.ino)

Supervised by **Prof. Massimo Ficco**
**Lab of IoT, University of Salerno, IT**



