import nose
import pkgutil
import easemob_flow.testing

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
            path=easemob_flow.testing.__path__,
            prefix="easemob_flow.testing."):
        if ispkg:
            continue
        if modname in excludes:
            continue
        argv.append(modname)
    nose.run(argv=argv)


if __name__ == "__main__":
    main()
