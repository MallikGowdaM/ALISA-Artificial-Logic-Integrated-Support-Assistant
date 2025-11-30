backend run = node server.js
frontend run = npm run dev

adb devices
adb tcpip 5555
adb connect <your-phone-ip>:5555
eg:adb connect 192.168.1.101:5555
adb devices
