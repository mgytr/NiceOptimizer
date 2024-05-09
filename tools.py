from subprocess import check_output, Popen, PIPE
import winreg
import re

hklm = winreg.HKEY_LOCAL_MACHINE
hkcu = winreg.HKEY_CURRENT_USER
dword = winreg.REG_DWORD
a = winreg.KEY_ALL_ACCESS


def setServiceStartup(name, disable=True, direct=False):
    if not direct:
        name = check_output(f'''powershell -c "Get-Service -Name '{name}' | Select-Object -ExpandProperty Name"''', shell=True).decode().strip()

    check_output(f'''powershell -c "Set-Service -Name '{name}' -StartupType {"Disabled" if disable else "Automatic"}"''', shell=True)
def srvRunning(name):
    status = check_output(f'''powershell -c "Get-Service -Name '{name}' | Select-Object -ExpandProperty Status"''', shell=True).decode().strip()

    return status == 'Running'
def getStatusDefender():
    with Popen('powershell -c "Get-MpPreference | Select-Object -Property ExclusionPath -ExpandProperty ExclusionPath"', shell=True, stdout=PIPE) as p:
        out1 = p.stdout.read().decode().splitlines()
    with Popen('powershell -c "Get-MpComputerStatus"', shell=True, stdout=PIPE, stderr=PIPE) as p:
        out = p.stdout.read().decode()

    values = {line.split(':')[0].strip(): line.split(':')[1].strip() for line in out.split('\n') if line and len(line.split(':')) == 2}
    t = 'True'
     # match "<any letter uppercase>:\*"(e.g. "C:\*") OR "\\<anything>"
    regex = re.compile('^[A-Z]:\\\*|\\\\.*')
    l = [values['AntispywareEnabled'] == t, values['AntivirusEnabled'] == t, values['RealTimeProtectionEnabled'] == t, values['BehaviorMonitorEnabled'] == t, values['IoavProtectionEnabled'] == t
            ] + [True for line in out1 if line and regex.match(line)]
    return l