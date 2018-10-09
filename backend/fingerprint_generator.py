from random import uniform

from pywinauto import Application

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

main['Copy image to clipboard'].click()

main.Exit.click()
