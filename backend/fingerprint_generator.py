from random import uniform, randrange
import tempfile
import os
import time
import ctypes
from ctypes import wintypes
import fingerprint_class
import subprocess

from pywinauto import Application, findwindows
directory = tempfile.gettempdir()
filename = 'fingerprint.bmp'
file_path = os.path.join(directory, filename)


class Generator():

    def randomize_slider(self, slider, min_perc=0, max_perc=100):
        #we have confirmed that all sliders range from 0 to 100
        slider.set_value(uniform(min_perc, max_perc))

    def randomize_combobox(self, combobox, number_of_items):
        self.select_combobox_top(combobox, number_of_items)
        combobox.type_keys('{DOWN}' * randrange(0, number_of_items))

    class_positions = {
            "arch": 0
           ,"left loop": 1
           ,"right loop": 2
           ,"whorl":3
           ,"tented arch": 4
    }

    def randomize_fingerprint_class(self, combobox):
        self.select_combobox_top(combobox, 5)
        combobox.type_keys('{DOWN}' * \
            self.class_positions[fingerprint_class.random()]
        )

    def select_combobox_top(self, combobox, number_of_items):
        combobox.type_keys('{UP}' * (number_of_items-1))

    def randomize_checkbox(self, checkbox):
        current_state = checkbox.get_toggle_state()
        value_to_set = randrange(0,2)
        if value_to_set != current_state:
            checkbox.toggle()

    def familicide(self):
        subprocess.run(["taskkill", "/f", "/im", "SFinGe.exe"])

    def generate(self):
        start_time = time.time()

        if 1 < len(findwindows.find_elements(title="SFinGe - Synthetic Fingerprint Generator - Demo Version")):
            self.familicide()

        app = Application(backend='uia').start('SFinGeDemo/SFinGe.exe')
        main = app.Dialog

        #Open generation form
        main.Generate.click()
        main.Dialog.OK.click()
        form = main.Dialog

        #Step 1 - Fingerprint mask generation
        self.select_combobox_top(form.child_window(
            auto_id='1024',
            control_type='ComboBox'
        ), number_of_items=5) #always select thumb
        form.Generate.click() #generate random mask
        #form.type_keys('%n')
        form.Next.click()

        #Step 2 - Directional map generation
        self.randomize_fingerprint_class(form.child_window(
            title='Fingerprint class',
            control_type='ComboBox'
        ))
        self.randomize_slider(form.child_window(
            title='Direction perturbation',
            control_type='Slider'
        ))
        form.Generate.click() #generate random directional map
        #form.type_keys('%n')
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
        self.randomize_checkbox(form.child_window(
            title='Add pores',
            control_type='CheckBox'
        ))
        #form.type_keys('%s') #Start ridge generation
        #form.type_keys('%n') #form.Next.click()
        form.Button5.click()
        form.Next.click()

        #Step 4 - Permanent scratches
        #rendered automatically, so nothing we need to to here
        #form.type_keys('%n')
        form.Next.click()

        #Step 5 - Finger contact region
        self.randomize_slider(form.child_window(
            title='Displacement',
            auto_id='1171', #vertical displacement
            control_type='Slider'
        ), min_perc=40, max_perc=60)
        self.randomize_slider(form.child_window(
            auto_id='1170', #horizontal displacement
            control_type='Slider'
        ), min_perc=40, max_perc=60)
        #form.type_keys('%a')
        form.Apply.click()
        #form.type_keys('%n')
        form.Next.click()

        #Step 6 - Pressure/Dryness
        self.randomize_slider(form.child_window(
            auto_id='1104', #pressure/dryness
            control_type='Slider'
        ), min_perc=16, max_perc=84)
        #form.type_keys('%a')
        form.Apply.click()
        #form.type_keys('%n')
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
        #form.type_keys('%a')
        form.Apply.click()
        #form.type_keys('%n')
        form.Next.click()

        #Step 8 - Noising and rendering
        self.randomize_slider(form.child_window(
            title='Ridges', #ridge noise
            control_type='Slider'
        ), max_perc=50)
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
        #form.type_keys('%n')
        form.Next.click()

        #Step 9 - Fingerprint rotation and translation
        #form.type_keys('%a')
        form.Apply.click()
        #form.type_keys('%n')
        form.Next.click()

        #Step 10 - Background and contrast
        self.select_combobox_top(form.child_window(
            title='Background',
            control_type='ComboBox'
        ), number_of_items=3)
        self.randomize_slider(form.child_window(
            title='Gamma',
            control_type='Slider'
        ), max_perc=40)
        #form.Generate.click()
        #form.type_keys('{ENTER}')
        form.Finish.click()

        #Save image to file
        global directory, filename, file_path
        main['Save image to file'].click()
        save_dialog = main.Dialog
        #save_dialog.type_keys(directory)
        save_dialog.child_window(title='File name:', control_type='Edit')\
            .wait('visible').set_edit_text(directory)
        #save_dialog.type_keys('%s')
        save_dialog.Save.click()
        time.sleep(1)
        already_existed = os.path.exists(file_path)
        #save_dialog.type_keys(filename)
        save_dialog.child_window(title='File name:', control_type='Edit')\
            .wait('visible').set_edit_text(filename)
        #save_dialog.type_keys('%s')
        save_dialog.Save.click()
        if already_existed:
            #save_dialog.Dialog.type_keys('%y') #yes
            save_dialog.Dialog.Yes.wait('visible').click()
        time.sleep(1)

        #Close application
        main.Exit.click()

        end_time = time.time()
        log = open('performance.log', 'a')
        log.write(repr(end_time - start_time) + '\n')

if __name__ == '__main__':
    Generator().generate()
