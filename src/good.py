import subprocess
import time
from pymavlink import mavutil

def send_body_velocity(master, vx, vy, vz, duration):
    for _ in range(duration):
        master.mav.set_position_target_local_ned_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111000111,
            0, 0, 0,
            vx, vy, vz,
            0, 0, 0,
            0, 0
        )
        time.sleep(1)

def set_altitude(master, target_alt):
    print(f"Подъём до {target_alt} метров...")
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    lat = msg.lat / 1e7
    lon = msg.lon / 1e7

    master.mav.set_position_target_global_int_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b0000111111111000,
        int(lat * 1e7), int(lon * 1e7), target_alt,
        0, 0, 0,
        0, 0, 0,
        0, 0
    )

    while True:
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        current_alt = msg.relative_alt / 1000.0
        print(f"Текущая высота: {current_alt:.1f} м")
        if abs(current_alt - target_alt) < 1:
            break
        time.sleep(1)

def land_drone(master):
    print("Посадка...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, 0, 0, 0
    )

def altitude_mode(master):
    print("Режим ALTITUDE: отключение моторов (падение)...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 0, 0, 0, 0, 0, 0, 0
    )

def rotate_drone(master, angle):
    print(f"Поворот на {angle} градусов...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0, angle, 20, 1, 1, 0, 0, 0
    )

def move_forward(master, distance):
    print(f"Полёт вперёд на {distance} метров...")
    speed = 1.0
    duration = int(distance / speed)
    send_body_velocity(master, speed, 0, 0, duration)

def connect_to_drone():
   
    print("Подключение к дрону...")
    master = mavutil.mavlink_connection('udp:127.0.0.1:14551')
    master.wait_heartbeat()
    print("Подключение установлено!")
    return master

def arm_drone(master):
    print("Вооружение дрона...")
    master.arducopter_arm()
    master.motors_armed_wait()
    print("Дрон вооружён!")

def disarm_drone(master):
    print("Разоружение дрона...")
    master.arducopter_disarm()
    master.motors_disarmed_wait()
    print("Дрон разоружён!")

def takeoff(master, altitude):
    print(f"Взлёт на {altitude} метров...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, altitude
    )
    time.sleep(10)

def main():
    master = connect_to_drone()

    print("Установка режима GUIDED...")
    master.set_mode("GUIDED")
    time.sleep(1)

    while True:
        print("\nВыбери команду:")
        print("arm / disarm / takeoff / rotate / forward / altitude / climb / mode / exit")
        print(">>", end="", flush=True)
        command = input().strip().lower()


        if command == "arm":
            arm_drone(master)

        elif command == "disarm":
            disarm_drone(master)

        elif command == "takeoff":
            alt = float(input("Укажи высоту взлёта (м): ").strip())
            takeoff(master, alt)

        elif command == "rotate":
            angle = float(input("Укажи угол поворота от 0 до 360: ").strip())
            rotate_drone(master, angle)

        elif command == "forward":
            distance = float(input("Укажи расстояние (м): ").strip())
            move_forward(master, distance)

        elif command == "altitude":
            while True:
                print("СПАСИБО ВАРТАН")
                time.sleep(1)

        elif command == "climb":
            target_alt = float(input("Укажи желаемую высоту (м): ").strip())
            set_altitude(master, target_alt)

        elif command == "mode":
            mode = input("Укажи режим (GUIDED / LAND): ").strip().upper()
            master.set_mode(mode)
            print(f"Режим сменён на {mode}")

        elif command == "exit":
            print("Завершение работы.")
            break

        else:
            print("Неизвестная команда!")

if __name__ == "__main__":
    main()
    
