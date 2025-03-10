from pymavlink import mavutil

try:
    master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    print("Подключение к дрону установлено!")
except Exception as e:
    print(f"Ошибка подключения: {e}")
    exit(1)

def set_mode_guided():
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        4
    )
    print("Режим GUIDED установлен.")

def arm():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    print("ARM ok")

def takeoff(altitude):
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, altitude)
    print(f"Команда 'takeoff' на высоту {altitude} м отправлена.")

def land():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0)
    print("Команда 'land' отправлена.")
