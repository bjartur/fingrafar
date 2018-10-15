from random import uniform, randrange
from tempfile import mktemp
from os import path, mkdir
import time
import ctypes
from ctypes import wintypes
import fingerprint_class

from pywinauto import Application

class Generator():

    def randomize_slider(self, slider):
        slider.set_value(uniform(slider.min_value(), slider.max_value()))

    def randomize_combobox(self, combobox, number_of_items):
        combobox.Open.click()
        combobox.type_keys('{UP}' * 5) # start at the top
        combobox.type_keys('{DOWN}' * randrange(0, number_of_items))
        #combobox.Close.click()

    class_positions = {
            "arch": 0
           ,"left loop": 1
           ,"right loop": 2
           ,"whorl":3
           ,"tented arch": 4
    }

    def randomize_fingerprint_class(self, combobox):
        combobox.Open.click()
        combobox.type_keys('{UP}' * 5)
        combobox.type_keys('{DOWN}' * \
            class_positions[fingerprint_class.random()]
        )
        

    def generate(self):
        app = Application(backend='uia').start('SFinGeDemo/SFinGe.exe')
        main = app.Dialog

        #Open generation form
        main.Generate.click()
        main.Dialog.OK.click()
        form = main.Dialog

        #Step 1 - Fingerprint mask generation
        form.Generate.click() #generate random mask
        finger_selection = form.child_window(
            auto_id='1024',
            control_type='ComboBox'
        )
        #TODO: always select thumb
        form.Next.click()

        #Step 2 - Directional map generation
        self.randomize_fingerprint_class(
            form.child_window(
                title='Fingerprint class',
                control_type='ComboBox'
            )
        )
        self.randomize_slider(form.child_window(
            title='Direction perturbation',
            control_type='Slider'
        ))
        form.Generate.click() #generate random directional map
        form.Next.click()

        #Step 3 - Density map and ridge pattern generation
        self.randomize_slider(form.child_window(
            title='Seeds',
            control_type='Slider'
        ))
        self.randomize_slider(form.child_window(
            auto_id='1112', #Ridge density
            control_type='Slider'
        ))
        #TODO: randomize pores inclusion
        form.Button5.click() #Start ridge generation
        form.Next.click()

        #Step 4 - Permanent scratches
        #rendered automatically, so nothing we need to to here
        form.Next.click()

        #Step 5 - Finger contact region
        #TODO: keep displacement close to 0, both vertical
        self.randomize_slider(form.child_window(
            title='Displacement',
            auto_id='1171', #vertical displacement
            control_type='Slider'
        ))
        #TODO: and horizontal
        self.randomize_slider(form.child_window(
            auto_id='1170', #horizontal displacement
            control_type='Slider'
        ))
        form.Apply.click()
        form.Next.click()

        #Step 6 - Pressure/Dryness
        #TODO: avoid extreme pressure/dryness
        self.randomize_slider(form.child_window(
            auto_id='1104', #pressure/dryness
            control_type='Slider'
        ))
        form.Apply.click()
        form.Next.click()

        #Step 7 - Fingerprint distortion
        self.randomize_slider(form.child_window(
            title='Rotation',
            control_type='Slider'
        ))
        self.randomize_slider(form.child_window(
            title='Translation',
            auto_id='1171', #vertical translation
            control_type='Slider'
        ))
        self.randomize_slider(form.child_window(
            auto_id='1170', #horizontal translation
            control_type='Slider'
        ))
        self.randomize_slider(form.child_window(
            title='Skin Elasticity',
            control_type='Slider'
        ))
        form.Apply.click()
        form.Next.click()

        #Step 8 - Noising and rendering
        #TODO: limit ridge noise to below 50%
        self.randomize_slider(form.child_window(
            title='Ridges', #ridge noise
            control_type='Slider'
        ))
        self.randomize_slider(form.child_window(
            title='Prominence', #ridge prominence
            control_type='Slider'
        ))
        self.randomize_slider(form.child_window(
            title='Valleys', #valley noise
            control_type='Slider'
        ))
        self.randomize_slider(form.child_window(
            title='Scratches',
            control_type='Slider'
        ))
        form.Next.click()

        #Step 9 - Fingerprint rotation and translation and apply
        #TODO: make rotation alwasy 0
        self.randomize_slider(form.child_window(
            title='Rotation',
            control_type='Slider'
        ))
        #TODO: make translation always 0, both vertical
        self.randomize_slider(form.child_window(
            title='Translation',
            auto_id='1171', #vertical translation
            control_type='Slider'
        ))
        #TODO: and horizontal
        self.randomize_slider(form.child_window(
            auto_id='1170', #horizontal translation
            control_type='Slider'
        ))
        form.Apply.click()
        form.Next.click()

        #Step 10 - Background and contrast
        #TODO: select always Background='None'
        self.randomize_combobox(form.child_window(
            title='Background',
            control_type='ComboBox'
        ), number_of_items=3)
        #TODO: skip background noise randomization
        self.randomize_slider(form.child_window(
            title='Noise', #background noise
            control_type='Slider'
        ))
        #TODO: make contrast alwasy 0
        self.randomize_slider(form.child_window(
            title='Contrast',
            control_type='Slider'
        ))
        #TODO: limit gamma to below 40%
        self.randomize_slider(form.child_window(
            title='Gamma',
            control_type='Slider'
        ))
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
