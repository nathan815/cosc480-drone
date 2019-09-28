import traceback
from os import environ
from time import sleep

from drone import TelloDrone
from drone_data import DroneData
from video import Video

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from joysticks import JoystickButtonHandler, joystick_controller_from_name


# Entry Point of Actual Program
def run(pilot = None):
    print("Welcome to Drone Control!")

    if pilot:
        print("\n---\nPilot Info\n" + str(pilot) + "\n---\n")

    pygame.init()
    pygame.joystick.init()

    num_joysticks = pygame.joystick.get_count()

    if num_joysticks > 0:
        print('Available Joysticks:')
    else:
        print("Error: No joysticks detected")
        return

    joystick_id = 0
    joysticks = []
    for i in range(0, num_joysticks):
        js = pygame.joystick.Joystick(i)
        joysticks.append(js)
        print(i, '-', js.get_name())

    if num_joysticks > 1:
        joystick_id = int(input("Select joystick (0-" + str(num_joysticks - 1) + "): "))

    joystick = joysticks[joystick_id]
    joystick.init()
    joystick_name = joystick.get_name()
    print("Selected Joystick: ", joystick_id, '-', joystick_name, "\n")

    joystick_controller_mapping = joystick_controller_from_name(joystick_name)
    while joystick_controller_mapping is None:
        print("Controller type not recognized.")
        manual_name = input("Select controller (PS3, PS3Alt, PS4, F310, XboxOne, Taranis, FightPad): ")
        joystick_controller_mapping = joystick_controller_from_name(manual_name)

    joystick_handler = JoystickButtonHandler(joystick_controller_mapping)

    drone = TelloDrone()

    drone_data = DroneData(pilot)
    drone.subscribe(drone.EVENT_FLIGHT_DATA, drone_data.event_handler)
    drone.subscribe(drone.EVENT_LOG, drone_data.event_handler)

    video = Video(drone, drone_data)

    try:
        video.start()

        print("Connecting to drone...")
        drone.connect()
        drone.wait_for_connection(60.0)
        print("Connected to drone!")

        while True:
            sleep(0.01)
            for e in pygame.event.get():
                joystick_handler.handle_event(drone, e)
            video.draw()
            #print('Left X', drone.left_x, 'Left Y', drone.left_y, 'Right X', drone.right_x, 'Right Y', drone.right_y)
    finally:
        video.quit()
        drone.land()
        drone.quit()


def start_drone_control(pilot = None):
    try:
        run(pilot)
    except KeyboardInterrupt as ex:
        print("Goodbye.")
    except Exception as ex:
        print("Caught Exception:", ex)
        traceback.print_exc()


if __name__ == '__main__':
    start_drone_control()
