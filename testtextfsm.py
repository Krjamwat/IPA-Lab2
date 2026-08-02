import pytest
from netmiko import ConnectHandler

key_path = r'C:\Users\LAB308_XX\Downloads\windows_user_openssh_new'
username_login = 'window_user'

# ใส่ Management IP ของแต่ละอุปกรณ์ 
r1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.4', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
r2 = {'device_type': 'cisco_ios', 'ip': '172.31.1.5', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
s1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.3', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}

def test_r1_pc_description():
    with ConnectHandler(**r1) as ssh:
        ssh.enable()
        # เช็คพอร์ต Gi0/1 ของ R1
        output = ssh.send_command("show interfaces GigabitEthernet0/1 description", use_textfsm=True)
        assert "Connect to PC" in output[0]['description']

def test_r2_wan_description():
    with ConnectHandler(**r2) as ssh:
        ssh.enable()
        # เช็คพอร์ต Gi0/3 ของ R2
        output = ssh.send_command("show interfaces GigabitEthernet0/3 description", use_textfsm=True)
        assert "Connect to WAN" in output[0]['description']

def test_s1_pc_description():
    with ConnectHandler(**s1) as ssh:
        ssh.enable()
        # เช็คพอร์ต Gi0/2 ของ S1
        output = ssh.send_command("show interfaces GigabitEthernet0/2 description", use_textfsm=True)
        assert "Connect to PC" in output[0]['description']