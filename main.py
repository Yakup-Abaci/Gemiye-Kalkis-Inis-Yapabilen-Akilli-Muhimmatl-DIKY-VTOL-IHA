import time


from KamikazeDrone.drone_codes.KamikazeDrone import KamikazeDrone


def main():
    drone = KamikazeDrone()
    drone.set_servo(1, 1100)


if __name__ == "__main__":
    main()
