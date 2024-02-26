def listenToTheDialogOnceNew():
    import ctypes
    import win32con
    import win32gui
    import subprocess
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    isDone = False

    def foreach_window(hwnd, lParam):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        # if IsWindowVisible(hwnd):
        # This is the window label

        # Get the class name of the window
        class_name = ctypes.create_unicode_buffer(
            256)  # Adjust the length for your needs
        ctypes.windll.user32.GetClassNameW(hwnd, class_name, 256)

        if (class_name.value == '#32770' and buff.value == 'Open'):
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            print('có')

        # PostMessage(GetDlgItem(hwnd, 1148),
        #             0x0100, 0x0D, 0)

        return True

    while isDone == False:
        win32gui.EnumWindows(foreach_window, None)
        break

        # EnumWindows(EnumWindowsProc(foreach_window), 0)
listenToTheDialogOnceNew()
