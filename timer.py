from dataclasses import dataclass, field


@dataclass
class Timer:

    cooldown: int = field(compare=False)
    persist: bool = field(compare=False)
    current_time: int = field(default=0)


    def __str__(self):
        return  f"current_time: {self.current_time}"


    def __repr__(self):
        return f"CD: {self.cooldown}, current_time: {self.current_time}, persist: {self.persist}"


class CooldownManager:

    def __init__(self):
        self._available_timer = {}
        self._active_timer = set()
        self.__ticked_timer = set()

    @property
    def active_timer(self):
        return self._active_timer
    
    @property
    def available_timer(self):
        return self._available_timer

    def configure_timer(self, name: str, cooldown: int, persist=False, auto_active=False):
        if name not in self._available_timer:
            self._available_timer[name] = Timer(cooldown, persist)
            if auto_active:
                self.activate_timer(name)
        else:
            raise Exception(f"Timer already exist: '{name}' -> {self._available_timer[name]}")

    def activate_timer(self, *name, activateAll=False):
        if not activateAll:
            for n in name:
                self.isAvailable(n)
                self._active_timer.add(n)  
        else:
            for name in self._available_timer.keys():
                self._active_timer.add(name)

    def deactivate_timer(self, *name, deactivateAll=False):
        if not deactivateAll:
            for n in name:
                self.isAvailable(n)   
                self._active_timer.remove(n)   
                timer = self._available_timer.get(n)
                timer.current_time = 0        
        else:
            for name in self._available_timer.keys():
                self._active_timer.remove(name)

    def peek_timer(self, *names):
        for name in names:
            self.isAvailable(name)
            if name in self.__ticked_timer:
                self.__ticked_timer.remove(name)
                return True
        return False

    def check_timer(self, name):
        self.isAvailable(name)
        timer = self._available_timer.get(name)
        return timer.cooldown - timer.current_time

    def isActive(self, *names):
        for name in names:
            self.isAvailable(name)
            if self._active_timer.get(name) == None:
                return False
        return True

    def update(self, dt):
        deactivated_timer = set()
        for name in self._active_timer:
            timer = self._available_timer.get(name)
            timer.current_time += dt
            if timer.current_time >= timer.cooldown:
                self.__ticked_timer.add(name)
                if not timer.persist:
                    deactivated_timer.add(name)
        
        self.deactivate_timer(*deactivated_timer)

    def isAvailable(self, name):
        if name not in self._available_timer and name not in self._active_timer:
            raise ValueError(f"timer provided is invalid: {name}")

    def __getitem__(self, name):
        self.isAvailable(name)  
        timer = self._available_timer.get(name)
        return timer.cooldown

    def __setitem__(self, name, newCooldown):
        self.isAvailable(name)
        timer = self._available_timer.get(name)
        timer.cooldown = newCooldown

    def __str__(self):
        return f"\nALL TIMERS: {self._available_timer}\nACTIVE TIMERS: {self._active_timer}\nINACTIVE TIMERS: {set(self._available_timer)-self._active_timer}"


def main():
    test = CooldownManager()
    test.configure_timer('skill', 1000000000, False, True)
    test.configure_timer('lmao', 100, False, True)
    test.activate_timer('skill', 'lmao')
    test.update(1000)


if __name__ == '__main__':
    main()