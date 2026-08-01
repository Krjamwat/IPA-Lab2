from netmiko import ConnectHandler

key_path = r'C:\Users\LAB308_XX\Downloads\windows_user_openssh_new'
username_login = 'window_user'

# ใส่ Management IP ของแต่ละอุปกรณ์ 
r1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.4', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
r2 = {'device_type': 'cisco_ios', 'ip': '172.31.1.5', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
s1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.3', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}

all_devices = [r1, r2, s1]

# config S1
s1_cmds = [
    'vlan 101',
    'name Control_Data',
    'interface range GigabitEthernet0/1 - 2',
    'switchport mode access',
    'switchport access vlan 101'
]

# config R1
r1_cmds = [
    'router ospf 1 vrf control-data', #ตั้ง Ospf
    'network 192.168.1.0 0.0.0.255 area 0',
    'network 10.1.1.0 0.0.0.3 area 0',
    'network 1.1.1.1 0.0.0.0 area 0'
]

# config R2
r2_cmds = [
    'router ospf 1 vrf control-data',
    'network 192.168.2.0 0.0.0.255 area 0',
    'network 10.1.1.0 0.0.0.3 area 0',
    'network 2.2.2.2 0.0.0.0 area 0',
    'default-information originate always', #แจกเส้นทาง Default Route ให้กับ Router ตัวอื่นๆ ในวง OSPF
    'exit',

    'ip route vrf control-data 0.0.0.0 0.0.0.0 GigabitEthernet0/3 192.168.42.1',
    #PAT
    'access-list 1 permit any',
    'ip nat inside source list 1 interface GigabitEthernet0/3 vrf control-data overload',
    
    'interface GigabitEthernet0/3', # ขาที่ต่อกับ NAT Cloud
    'ip nat outside',
    'exit',
    
    'interface GigabitEthernet0/1',
    'ip nat inside',
    'exit',

    'interface GigabitEthernet0/2',
    'ip nat inside',
    'exit',

    'ip dns server',
    'ip domain-lookup',
    'ip name-server vrf control-data 8.8.8.8',
    'exit'
]

# -- ชุดคำสั่งรักษาความปลอดภัย (ใช้เหมือนกันทุกอุปกรณ์) --
# แก้ไข Network IP ของฝั่ง Management และ Lab306
security_cmds = [
    'ip access-list standard MGT_ONLY',
    'permit 172.31.1.0 0.0.0.15',       # Network วง Management
    'permit 10.30.6.0 0.0.1.255',   # Network วง Lab306
    'deny any',
    'exit',
    'line vty 0 4',
    'access-class MGT_ONLY in',
    'exit'
]

# Config S1
print(f"\n[1] กำลังตั้งค่า S1 ({s1['ip']}) - VLAN 101...")
with ConnectHandler(**s1) as ssh:
    ssh.enable()
    print(ssh.send_config_set(s1_cmds))
    ssh.save_config()

# Config R1
print(f"\n[2] กำลังตั้งค่า R1 ({r1['ip']}) - OSPF...")
with ConnectHandler(**r1) as ssh:
    ssh.enable()
    print(ssh.send_config_set(r1_cmds))
    ssh.save_config()

# Config R2
print(f"\n[3] กำลังตั้งค่า R2 ({r2['ip']}) - OSPF, Default Route & PAT...")
with ConnectHandler(**r2) as ssh:
    ssh.enable()
    print(ssh.send_config_set(r2_cmds))
    ssh.save_config()

# Config Security เข้าทุกอุปกรณ์โดยใช้ลูป
print("\n[4] กำลังตั้งค่า Security ACL เข้าสู่ทุกอุปกรณ์...")
for dev in all_devices:
    print(f" -> กำลังล็อก VTY port ของ {dev['ip']}...")
    with ConnectHandler(**dev) as ssh:
        ssh.enable()
        ssh.send_config_set(security_cmds)
        ssh.save_config()

print("\n--- เสร็จสิ้นกระบวนการทั้งหมด! ---")