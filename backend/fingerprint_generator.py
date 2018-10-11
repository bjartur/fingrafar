from random import uniform
from tempfile import mktemp
from os import path, mkdir
import time

from pywinauto import Application

class Generator():

    def randomize_slider(self, slider):
        slider.set_value(uniform(slider.min_value(), slider.max_value()))

    def generate(self):
        app = Application(backend='uia').start('SFinGeDemo/SFinGe.exe')
        main = app.Dialog

        #Open generation form
        main.Generate.click()
        main.Dialog.OK.click()
        form = main.Dialog

        #Step 1 - Fingerprint mask generation
        form.Generate.click() #generate random mask
        #TODO: randomize finger selection
        form.Next.click()

        #Step 2 - Directional map generation
        comboBox = form.child_window(
            title='Fingerprint class',
            control_type='ComboBox'
        ) # now what?
        slider = form.child_window(
            title='Direction perturbation',
            control_type='Slider'
        )
        self.randomize_slider(slider)
        form.Generate.click() #generate random directional map
        form.Next.click()

        #Step 3 - Density map and ridge pattern generation
        #TODO: randomize seeds, ridge density, and pores inclusion
        form.Button5.click() #Start ridge generation
        form.Next.click()

        #Step 4 - Permanent scratches
        #rendered automatically, so nothing we need to to here
        form.Next.click()

        #Step 5 - Finger contact region
        #TODO: randomize displacement and apply
        form.Next.click()

        #Step 6 - Pressure/Dryness
        #TODO: randomize pressure and apply
        form.Next.click()

        #Step 7 - Fingerprint distortion
        #TODO: randomize rotation, translation and skin elasticity and apply
        form.Next.click()

        #Step 8 - Noising and rendering
        #TODO: randomize ridges, valleys and scratches and render
        form.Next.click()

        #Step 9 - Fingerprint rotation and translation and apply
        form.Next.click()

        #Step 10 - Background and contrast
        #TODO: randomize background, noise, contrast and gamma
        form.Generate.click() #generate background
        form.Finish.click()

        #Save image to file
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

        #Close application
        main.Exit.click()

        #return file handle
        return open(path.join(fg_tmp, filename), 'rb')

if __name__ == '__main__':
    Generator().generate()
