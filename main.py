from modules.features import get_features
from modules.utils   import Utils
from time            import sleep, time

logger = Utils.get_logger()

if __name__ == "__main__":
    Utils.set_title({
            'Module': 'Main Menu'
        }, time())

    features = get_features()

    while True:
        logger.print_banner('Welcome to DMDPY')
        logger.delay_print(logger.center(features[1]))
        print()

        try:
            choice = logger.delay_input('Please select an option> ', 0.005)
            choice = int(choice)-1
        except ValueError as e:
            logger.error('Invalid choice...')
            sleep(0.5)
            continue

        task = Utils.get_val_from_index(features[0], choice)
        if task != False:
            task()
        else:
            logger.error('Invalid choice...')
            sleep(0.5)