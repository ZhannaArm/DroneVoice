import subprocess
import time
from pymavlink import mavutil

print("Запуск MAVProxy...")
mavproxy_process = subprocess.Popen(
    ["mavproxy.py", "--master=127.0.0.1:14550", "--out=127.0.0.1:14551"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

time.sleep(5)

print("Подключение к дрону...")
master = mavutil.mavlink_connection('udp:127.0.0.1:14551')

print("Ожидание heartbeat...")
master.wait_heartbeat()
print("Подключение установлено!")

print("Установка режима GUIDED...")
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4
)

print("Вооружение дрона...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

print("Взлет на высоту 10 метров...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 10)

time.sleep(10)

print("Посадка...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0)

print("Завершение работы...")
mavproxy_process.terminate()

