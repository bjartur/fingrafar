from random import uniform
from tempfile import mktemp
from os import path, mkdir
import time

from pywinauto import Application

class Generator():

    def _init_(self):
        pass

    def bla(self):
        self.generate()
        #fetch image from clipboard

    def generate(self):
        app = Application(backend='uia').start('SFinGeDemo/SFinGe.exe')
        main = app.Dialog

        main.Generate.click()
        app.OpenDialog['Select sensor area and resolution'].OK.click()

        dialog = main.Dialog


        # def randomize_slider(slider):
        #     slider.set_value(uniform(slider.min_value, slider.max_value))

        dialog.Generate.click()
        dialog.Next.click()
        dialog.Next.click()
        dialog.Button5.click() #Start ridge generation
        dialog.Next.click()

        dialog.Next.click()
        dialog.Next.click()
        dialog.Next.click()

        dialog.Next.click()
        dialog.Next.click()
        dialog.Next.click()
        dialog.Finish.click()

        full_path = mktemp('.bmp')
        directory, filename = path.split(full_path)
        fg_tmp = path.join(directory, 'fingerprint_generator')
        if not path.exists(fg_tmp):
            mkdir(fg_tmp)

        main['Save image to file'].click()
        save_dialog = main.Dialog
        save_dialog.child_window(title="File name:", control_type="Edit")\
            .wait('visible').set_edit_text(fg_tmp)
        save_dialog.Save.click()
        time.sleep(1)
        save_dialog.child_window(title="File name:", control_type="Edit")\
            .wait('visible').set_edit_text(filename)
        save_dialog.Save.click()
        time.sleep(1)
        main.Exit.click()

        file = open(path.join(fg_tmp, filename), 'rb')

        return file

if __name__ == '__main__':
    Generator().generate()
