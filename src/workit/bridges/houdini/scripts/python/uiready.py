# Runs once Houdini's interface is ready (interactive sessions only).
try:
    import workit_houdini

    workit_houdini.start()
except Exception as error:  # never block Houdini's startup
    print("WorkitStudio did not start: %s" % error)
