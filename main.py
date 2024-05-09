import sys
import os
f_logs = None
if hasattr(sys, "_MEIPASS"): # if the script is started from an executable file
    
    f_logs = open("logs.txt", "a")
    os.chdir(sys._MEIPASS)
from contextlib import redirect_stdout, redirect_stderr

def script():
    import eel
    # import webview
    import webview
    import threading
    #import windows registry api
    import winreg
    from time import sleep
    from subprocess import Popen, PIPE, check_output, run
    import tools
    from string import ascii_uppercase
    from io import StringIO


    hklm = winreg.HKEY_LOCAL_MACHINE
    hkcu = winreg.HKEY_CURRENT_USER
    dword = winreg.REG_DWORD
    binary = winreg.REG_BINARY
    a = winreg.KEY_ALL_ACCESS
    
    eel.init('app')

    def disThrottling(view=False, disable=True):
        # Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power and there make key PowerThrottling
        # and set value to 0

        with winreg.OpenKey(hklm, R'SYSTEM\CurrentControlSet\Control\Power', access=a) as regkey:
            if not view:
                try:
                    winreg.CreateKey(regkey, 'PowerThrottling')
                except:
                    pass
                with winreg.OpenKey(regkey, 'PowerThrottling', access=a) as subkey:
                    winreg.SetValueEx(subkey, 'PowerThrottlingOff', 0, dword, 1 if disable else 0)
            else:
                try:
                    with winreg.OpenKey(hklm, R'SYSTEM\CurrentControlSet\Control\Power\PowerThrottling', access=a) as subkey:
                        value, _ = winreg.QueryValueEx(subkey, 'PowerThrottlingOff')
                    return value == 1
                except FileNotFoundError:
                    return False

    def disTelemetry(view=False, disable=True):
        # (hkcu, R'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection',
        #             'AllowTelemetry', 0, dword)
        with winreg.OpenKey(hkcu, R'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies', access=a) as regkey:
            if not view:
                try:
                    winreg.CreateKey(regkey, 'DataCollection')
                except:
                    pass
                with winreg.OpenKey(regkey, 'DataCollection', access=a) as subkey:
                    winreg.SetValueEx(subkey, 'AllowTelemetry', 0, dword, 0 if disable else 1)
            else:
                try:
                    with winreg.OpenKey(hkcu, R'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection', access=a) as subkey:
                        value, _ = winreg.QueryValueEx(subkey, 'AllowTelemetry')
                except FileNotFoundError:
                    return False
                
        if not view:
            tools.setServiceStartup('DiagTrack', disable=disable, direct=True)
            tools.setServiceStartup('dmwappushservice', disable=disable, direct=True)
            tools.setServiceStartup('Wecsvc', disable=disable, direct=True)
            tools.setServiceStartup('WerSvc', disable=disable, direct=True)

        else:
            diagtrack = tools.srvRunning('DiagTrack')
            dmwappushservice = tools.srvRunning('dmwappushservice')
            wecsvc = tools.srvRunning('Wecsvc')
            wersvc = tools.srvRunning('WerSvc')

            return any([diagtrack, dmwappushservice, wecsvc, wersvc, value == 0])
        
    def disSysRestore(view=False, disable=True):
        # (hklm, R'SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore',
        #             'DisableSR', 0, dword)
        with winreg.OpenKey(hklm, R'SOFTWARE\Policies\Microsoft\Windows NT', access=a) as regkey:
            if not view:
                try:
                    winreg.CreateKey(regkey, 'SystemRestore')
                except:
                    pass
                with winreg.OpenKey(regkey, 'SystemRestore', access=a) as subkey:
                    if not disable:
                        try: winreg.DeleteValue(subkey, 'DisableSR')
                        except FileNotFoundError: pass
                    else: winreg.SetValueEx(subkey, 'DisableSR', 0, dword, 1)
            else:
                try:
                    with winreg.OpenKey(hklm, R'SOFTWARE\Policies\Microsoft\Windows NT\SystemRestore', access=a) as subkey:
                        value, _ = winreg.QueryValueEx(subkey, 'DisableSR')
                
                    return value == 1
                except FileNotFoundError:
                    return False
                

    def disFstp(view=False, disable=True):
        #(hklm, R'SYSTEM\CurrentControlSet\Control\Session Manager\Power',
        #             'HiberbootEnabled', 0, dword)


        with winreg.OpenKey(hklm, R'SYSTEM\CurrentControlSet\Control\Session Manager\Power', access=a) as regkey:
            #winreg.SetValueEx(regkey, 'HiberbootEnabled', 0, dword, 0)
            if not view:
                winreg.SetValueEx(regkey, 'HiberbootEnabled', 0, dword, 0 if disable else 1)
            else:
                value, _ = winreg.QueryValueEx(regkey, 'HiberbootEnabled')
                return value == 0
    def reduceShutdownTime(view=False, disable=True):
        # (hklm, R'SYSTEM\CurrentControlSet\Control',
        #             'WaitToKillServiceTimeout', 0, dword)
        with winreg.OpenKey(hklm, R'SYSTEM\CurrentControlSet\Control', access=a) as regkey:
            if not view:
                winreg.SetValueEx(regkey, 'WaitToKillServiceTimeout', 0, dword, 2000 if disable else 5000)
            else:
                value, _ = winreg.QueryValueEx(regkey, 'WaitToKillServiceTimeout')
                return value == 2000

    def disableAnimations(view=False, disable=True):
        with winreg.OpenKey(hkcu, R'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects', access=a) as regkey:
            if not view:


                if disable:
                    winreg.SetValueEx(regkey, 'VisualFXSetting', 0, winreg.REG_DWORD, 2)
                    with winreg.OpenKey(hkcu, R'Control Panel\Desktop', access=a) as subkey:
                        winreg.SetValueEx(regkey, 'UserPreferencesMask', 0, binary, b'\x9e\x12\x01\x80\x10\x00\x00\x00')
                else:
                    try:
                        winreg.SetValueEx(regkey, 'VisualFXSetting', 0, winreg.REG_DWORD, 0)
                        with winreg.OpenKey(hkcu, R'Control Panel\Desktop', access=a) as subkey:
                            winreg.SetValueEx(regkey, 'UserPreferencesMask', 0, binary, b'\x9e\x1e\x07\x80\x12\x00\x00\x00')
                    except FileNotFoundError:
                        pass
            else:
                try:

                    value, _ = winreg.QueryValueEx(regkey, 'VisualFXSetting')
                    with winreg.OpenKey(hkcu, R'Control Panel\Desktop', access=a) as subkey:
                        mask, _ = winreg.QueryValueEx(subkey, 'UserPreferencesMask')
                    
                    return value == 2 and mask == b'\x9e\x12\x01\x80\x10\x00\x00\x00'
                except FileNotFoundError:
                    return False
    """paths = [f'{letter}:\\*' for letter in ascii_uppercase]+['\\\\*\\*', '\\\\*\\*\\*', '\\\\*']


    def disableDefender(view=False, disable=True):

        "Add-MpPreference -ExclusionPath 'C:\*'"
        
        if not view:
            if disable:
                for x in paths:
                    Popen(f'''powershell -inputformat none -NonInteractive -Command "Add-MpPreference -ExclusionPath '{x}'"''', shell=True)
                Popen('powershell -c "Set-MpPreference -DisableRealtimeMonitoring $true"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisableBehaviorMonitoring $true"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisableBlockAtFirstSeen $true"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisableIOAVProtection $true"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisablePrivacyMode $true"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -SubmitSamplesConsent 2"', shell=True, stdout=PIPE, stderr=PIPE)
            else:
                for x in paths:
                    Popen(f'''powershell -inputformat none -NonInteractive -Command "Remove-MpPreference -ExclusionPath '{x}'"''', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisableRealtimeMonitoring $false"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisableBehaviorMonitoring $false"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisableBlockAtFirstSeen $false"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisableIOAVProtection $false"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -DisablePrivacyMode $false"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $false"', shell=True, stdout=PIPE, stderr=PIPE)
                Popen('powershell -c "Set-MpPreference -SubmitSamplesConsent 1"', shell=True, stdout=PIPE, stderr=PIPE)

        else:
            return tools.getStatusDefender().count(False) >= 7
    """
    def disableDefender(view=False, disable=True):
        # (hklm, R'SOFTWARE\Policies\Microsoft\Windows Defender',
        #             'DisableAntiSpyware', 0, dword)
        with winreg.OpenKey(hklm, R'SOFTWARE\Policies\Microsoft\Windows Defender', access=a) as regkey:
            if not view:
                
                if disable:
                    winreg.SetValueEx(regkey, 'DisableAntiSpyware', 0, dword, 1)
                    winreg.SetValueEx(regkey, 'DisableRealtimeMonitoring', 0, dword, 1)
                    with winreg.OpenKey(regkey, 'Real-Time Protection', access=a) as subkey:
                        winreg.SetValueEx(subkey, 'DisableBehaviorMonitoring', 0, dword, 1)
                        winreg.SetValueEx(subkey, 'DisableOnAccessProtection', 0, dword, 1)
                        winreg.SetValueEx(subkey, 'DisableScanOnRealtimeEnable', 0, dword, 1)
                else:
                    
                    winreg.SetValueEx(regkey, 'DisableAntiSpyware', 0, dword, 0)
                    winreg.SetValueEx(regkey, 'DisableRealtimeMonitoring', 0, dword, 0)
                    with winreg.OpenKey(regkey, 'Real-Time Protection', access=a) as subkey:
                        winreg.SetValueEx(subkey, 'DisableBehaviorMonitoring', 0, dword, 0)
                        winreg.SetValueEx(subkey, 'DisableOnAccessProtection', 0, dword, 0)
                        winreg.SetValueEx(subkey, 'DisableScanOnRealtimeEnable', 0, dword, 0)




            else:
                try:
                    with winreg.OpenKey(regkey, 'Real-Time Protection', access=a) as subkey:
                        v1, _ = winreg.QueryValueEx(regkey, 'DisableAntiSpyware')
                        v2, _ = winreg.QueryValueEx(regkey, 'DisableRealtimeMonitoring')
                        
                        v3, _ = winreg.QueryValueEx(subkey, 'DisableBehaviorMonitoring')
                        v4, _ = winreg.QueryValueEx(subkey, 'DisableOnAccessProtection')
                        v5, _ = winreg.QueryValueEx(subkey, 'DisableScanOnRealtimeEnable')

                    return v1 == 1 and v2 == 1 and v3 == 1 and v4 == 1 and v5 == 1
                except FileNotFoundError:
                    return False


    @eel.expose
    def applyTweaks(tweaks):
        for tweak, action in tweaks.items():
            actions[tweak](view=False, disable=action)
        return True
            
    actions = {
        'disFstp': disFstp,
        'disTelemetry': disTelemetry,
        'disThrottling': disThrottling,
        'disSysRestore': disSysRestore,
        'reduceShutdownTime': reduceShutdownTime,
        'disableAnimations': disableAnimations,
        'disDefender': disableDefender
    }

    @eel.expose
    def getStatus(action):
        return actions[action](view=True)

    @eel.expose
    def restart():
        Popen('shutdown /r /t 0', shell=True, stdout=PIPE, stderr=PIPE)

    @eel.expose
    def logout():
        Popen('shutdown /l', shell=True, stdout=PIPE, stderr=PIPE)

    @eel.expose
    def restartExplorer():
        Popen('taskkill /f /im explorer.exe && start explorer.exe', shell=True, stdout=PIPE, stderr=PIPE)

    def main():
        def eel_start():
            eel.start('index.html',mode=None, port=1892, shutdown_delay=0.0)
        eel_thread = threading.Thread(target=eel_start)
        eel_thread.daemon = True
        eel_thread.start()
        webview.create_window("NiceOptimizer", "http://localhost:1892/index.html", )
        webview.start()#debug=True)

    if __name__ == '__main__':
        main()
if f_logs:
    with redirect_stdout(f_logs), redirect_stderr(f_logs):
        script()
else:
    script()
