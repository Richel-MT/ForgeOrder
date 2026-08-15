


def executeCommand(args):


    if args.fix:
        from .fix import fix
        fix()

    if args.reset_root:
        from app.init import initRootUser
        initRootUser(reset=True)
    

    return args.exit

        