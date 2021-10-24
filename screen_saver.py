import pygame
from abc     import ABC, abstractmethod
from os.path import isfile as fileChecker

from .utility import create_surf, decrease_surf_alpha
from .timer   import CooldownManager
from .text    import TextManager


class Displayer(ABC):

    FPS = 30
    DARK_GREY = (30, 30, 30)
    pygame.init()

    window = pygame.display.set_mode((1300, 700))
    win_w, win_h = window.get_size()
    clock  = pygame.time.Clock()

    surf = pygame.Surface((win_w-150, win_h))
    surf_w, surf_h = surf.get_size()

    text = TextManager("Arial", (255, 255, 255), 60, AA=True, background=(0, 0, 0))
    cooldownManager = CooldownManager()

    _run = True

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self):
        pass
        
    @abstractmethod
    def handle_user_input(self):
        pass

    def show(self):
        while self._run:
            dt = self.clock.get_time() / self.FPS

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._run = False

                self.handle_user_input(event)

            self.update(dt)
            self.draw()

            self.clock.tick(self.FPS)
            pygame.display.update()


def SaveScreen(img_name, overwrite=True):

    # img_name will be filename of the saved image
    # overwrite will ensure only one copy of the file exist 
    # -> by overwriting the previously saved file with the same name as img_name

    def SaveScreenInner(OriginalClass):

        # all classes using this wrapper must inherit from the Displayer class
        if OriginalClass.__base__ != Displayer:
            raise NotImplementedError("displayer class must inherit the Displayer base class!")

        class SaveScreenWrapper:

            def __init__(self, *args, **kwargs):
                self.img_name = img_name
                self.overwrite = overwrite

                # color for the SAVED pop-up msg 
                # -> can be changed in the wrapped class on the fly 
                self._bg_color, self._txt_color = 'white', 'orange'

                self.init_save_screen()
                self.text.set_txt_surf('SAVED', background=self._bg_color, font_color=self._txt_color)

                self._file_counter = 0
                self._saving = False

                # initialize the wrapped class at the very end 
                # -> the 'show' function will automatically be triggered in the wrapped class's init
                OriginalClass.__init__(self, *args, **kwargs)

            def __getattr__(self, attr):
                '''all the attribute access of the wrapped class will be rerouted here'''
                orig_attr = getattr(OriginalClass, attr)
                if callable(orig_attr):
                    def decorated_func(*args, **kwargs):
                        result = orig_attr(self, *args)
                        # prevent original_class from becoming unwrapped
                        if result == OriginalClass:
                            return self

                        # if the update() function is called from the original class, 
                        # -> it will be rerouted here and be decorated with the updateSaveScreen() function
                        # --> use the update function of the wrapped class to update SaveScreen's internal timer
                        if orig_attr.__name__ == "update":
                            self.updateSaveScreen(*args, **kwargs)

                        # if the draw() function is called from the original class, 
                        # -> it will be rerouted here and be decorated with the drawSaveScreen() function
                        # --> use the draw function of the wrapped class to draw SaveScreen's pop-up msg
                        elif orig_attr.__name__ == "draw":
                            self.drawSaveScreen()

                        # if the handle_user_input() function is called from the original class, 
                        # -> it will be rerouted here and be decorated with the save_img() function
                        # --> use the handle_user_input function of the wrapped class 
                        #     to check whether or not to save the image and 
                        #     trigger other SaveScreen functions(UpdateSaveScreen & drawSaveScreen)
                        elif orig_attr.__name__ == "handle_user_input":
                            self.save_img()
                        else:
                            return result

                    return decorated_func
                else:
                    # just return the requested attribute if it is not what that's needed
                    return orig_attr

            def updateSaveScreen(self, dt):
                '''the internal timer for the SaveScreen class'''
                if self._saving:
                    self.cooldownManager.update(dt)
                    self.flash_surf = decrease_surf_alpha(self.flash_surf, 15)
                    if self.cooldownManager.peek_timer('flash'):
                        self.flash_surf.set_alpha(255)
                        self._saving = False

            def drawSaveScreen(self):
                '''pop-up msg for the SaveScreen class'''
                if self._saving:
                    self.window.blit(self.flash_surf, self.flash_rect.topleft)
                    pygame.draw.rect(self.window, self._bg_color, self.saved_border, border_radius=10)
                    self.window.blit(self.saved_text.surf, self.saved_rect.topleft)
                    pygame.draw.rect(self.window, self._txt_color, self.saved_border, 8, 10)

            def init_save_screen(self):
                # initialization for the pop-up msg
                # can be done in the __init__, but it looks cleaner this way, i guess :/
                self.flash_surf  = create_surf((self.win_w - 150, self.win_h), (255,255,255,255), pygame.SRCALPHA)
                self.flash_rect  = self.flash_surf.get_rect(x=(150//2), y=0)
                self.cooldownManager.configure_timer("flash", 35)
                
                self.saved_text     = self.text.create_txt('SAVED', underline=True, font_size=100)
                self.saved_rect     = self.saved_text.get_rect(center=(self.win_w//2, self.win_h//2))
                self.saved_border   = self.saved_rect.inflate(25, 25)

            def save_img(self):
                # check if the left ctrl button and the s button is pressed
                # if so, 
                # -> activate the internal timer of SaveScreen class
                # -> save the image 
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
                    if not self._saving:
                        self._saving = True
                        self.cooldownManager.activate_timer("flash")

                        # if overwriting is disabled, add a counter to img file's name
                        # increment it until a unique filename is found(non-existing)
                        # then, save the img file
                        if not self.overwrite:
                            while fileChecker(f"{self.img_name}_{self._file_counter}.png"):
                                self._file_counter += 1
                            pygame.image.save(self.surf, f"{self.img_name}_({self._file_counter}).png")
                            self._file_counter += 1              
                            return
                        pygame.image.save(self.surf, f"{self.img_name}.png") 

            @property
            def bg_color(self):
                return self._bg_color

            @property
            def txt_color(self):
                return self._txt_color

            @bg_color.setter
            def bg_color(self, color_name):
                self._bg_color = color_name
                self.text.set_txt_surf("SAVED", setAll=True, background=self._bg_color)

            @txt_color.setter
            def txt_color(self, color_name):
                self._txt_color = color_name
                self.text.set_txt_surf("SAVED", setAll=True, font_color=self._txt_color)

        SaveScreenWrapper.__name__ = OriginalClass.__name__

        return SaveScreenWrapper

    return SaveScreenInner