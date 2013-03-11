from dataloader import load_data
from migrationcheck import LocalBuildoutConfigReader


def debug(system_versions):
    """Debug config to load a specific system version or step into config
    reading.
    """

    version = system_versions[('teamraum', '4.x')]
    local_parser = LocalBuildoutConfigReader(version.render(),
                                             system_versions).get_config()
    print set(local_parser.items('versions'))


if __name__ == "__main__":
    debug(load_data())
