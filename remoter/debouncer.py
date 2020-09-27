import datetime


# FIXME: does homeassistant have some utility to do this for us?

class Debouncer:

    def __init__(self):
        self.LAST_BUTTON = None
        self.LAST_BUTTON_TIME = None

    def debounce(self, event):
        """Return True if we should ignore this event.
        We do that if it's the same button we last saw, and we last saw it a
        very short time ago.
        """
        retval = False
        name = event.data["button_name"]
        thistime = event.time_fired
        lasttime = self.LAST_BUTTON_TIME
        if (
            name == self.LAST_BUTTON
            and lasttime
            and (thistime - lasttime) < datetime.timedelta(milliseconds=300)
        ):
            retval = True
        self.LAST_BUTTON = name
        self.LAST_BUTTON_TIME = thistime
        return retval
