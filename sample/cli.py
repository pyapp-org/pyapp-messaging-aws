from pyapp.app import CliApplication

APP = CliApplication()


def main(args=None):
    APP.dispatch(args)
