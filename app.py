from core.converters.struct import *

import wx


class ConverterFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = "File Converter"
        self.size = (400, 200)
        self.current_file = None

        # Панель для размещения элементов
        panel = wx.Panel(self)

        # Создание элементов интерфейса
        self.create_widgets(panel)

        # Настройка окна
        self.SetTitle(self.title)
        self.SetSize(self.size)
        self.Show()

    def create_widgets(self, panel):
        # Слой для вертикального выравнивания
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Поле ввода пути к файлу
        self.file_path = wx.TextCtrl(panel)
        vbox.Add(self.file_path, 0, wx.EXPAND | wx.ALL, 5)

        # Кнопка выбора файла
        btn_browse = wx.Button(panel, label="Choose File")
        btn_browse.Bind(wx.EVT_BUTTON, self.onbrowse)
        vbox.Add(btn_browse, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Выпадающее меню для выбора типа конвертации
        # self.choice = wx.Choice(panel, choices=["MM to OPM", "OPM to MM"])
        # vbox.Add(self.choice, 0, wx.EXPAND | wx.ALL, 5)
        self.output_format = wx.TextCtrl(panel)
        vbox.Add(self.output_format, 0, wx.EXPAND | wx.ALL, 5)

        # Кнопка конвертации
        btn_convert = wx.Button(panel, label="Convert")
        btn_convert.Bind(wx.EVT_BUTTON, self.onconvert)
        vbox.Add(btn_convert, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(vbox)

    def onbrowse(self, event):
        # Диалоговое окно выбора файла
        dlg = wx.FileDialog(
            self,
            message="Choose a file",
            defaultDir=".",
            wildcard="All files (*.*)|*.*",
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.file_path.SetValue(path)
            self.current_file = path
        dlg.Destroy()

    def onconvert(self, event):
        # Проверка выбранного файла
        if not self.current_file:
            wx.MessageBox("Please select a file first!", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            # TODO: Определение типа конвертации
            converter = OpmToTxtConverter()

            converter.convert(self.current_file, self.output_format.Value)

            wx.MessageBox(
                "Conversion completed successfully!",
                "Success",
                wx.OK | wx.ICON_INFORMATION,
            )

        except Exception as e:
            wx.MessageBox(
                f"An error occurred: {str(e)}", "Error", wx.OK | wx.ICON_ERROR
            )


class ConverterApp(wx.App):
    def OnInit(self):
        frame = ConverterFrame(None, title="File Converter")
        self.SetTopWindow(frame)
        return True


if __name__ == "__main__":
    app = ConverterApp()
    app.MainLoop()
