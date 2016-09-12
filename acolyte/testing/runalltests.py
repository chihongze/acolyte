import nose
import pkgutil
import acolyte.testing

excludes = set()


def main():
    argv = [
        "",
        (
            "--cover-package="
            "girlfriend.workflow,"
            "girlfriend.data,"
            "girlfriend.util"
        ),
    ]
    for importer, modname, ispkg in pkgutil.walk_packages(
            path=acolyte.testing.__path__,
            prefix="acolyte.testing."):
        if ispkg:
            continue
        if modname in excludes:
            continue
        argv.append(modname)
    nose.run(argv=argv)


if __name__ == "__main__":
    main()
