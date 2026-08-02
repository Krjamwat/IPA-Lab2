from netmiko import ConnectHandler
from jinja2 import Template

key_path = r'C:\Users\LAB308_XX\Downloads\windows_user_openssh_new'
username_login = 'window_user'

# กำหนดข้อมูลอุปกรณ์
r1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.4', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
r2 = {'device_type': 'cisco_ios', 'ip': '172.31.1.5', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
s1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.3', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
all_devices = [r1, r2, s1]

# สร้าง Jinja2 Templates
s1_template = """
vlan {{ vlan_id }}
name {{ vlan_name }}
interface range {{ intf_range }}
switchport mode access
switchport access vlan {{ vlan_id }}
"""

ospf_template = """
router ospf {{ ospf_id }} vrf {{ vrf_name }}
{% for net in networks %}
network {{ net.ip }} {{ net.wildcard }} area {{ net.area }}
{% endfor %}
{% if default_route %}
default-information originate always
{% endif %}
exit
"""

r2_nat_template = """
ip route vrf {{ vrf_name }} 0.0.0.0 0.0.0.0 GigabitEthernet0/3 192.168.42.1
ip route vrf {{ vrf_name }} 172.31.1.0 255.255.255.0 Null0
access-list 1 permit any
ip nat inside source list 1 interface GigabitEthernet0/3 vrf {{ vrf_name }} overload
interface GigabitEthernet0/3
ip nat outside
exit
interface GigabitEthernet0/1
ip nat inside
exit
interface GigabitEthernet0/2
ip nat inside
exit
ip dns server
ip domain-lookup
ip name-server vrf {{ vrf_name }} 8.8.8.8
exit
"""

security_template = """
ip access-list standard MGT_ONLY
{% for permit in permits %}
permit {{ permit.ip }} {{ permit.wildcard }}
{% endfor %}
deny any
exit
line vty 0 4
access-class MGT_ONLY in
exit
"""

# กำหนดข้อมูลที่จะนำไปใส่ Template
s1_data = {'vlan_id': 101, 'vlan_name': 'Control_Data', 'intf_range': 'GigabitEthernet0/1 - 2'}

r1_ospf_data = {
    'ospf_id': 1, 'vrf_name': 'control-data', 'default_route': False,
    'networks': [
        {'ip': '192.168.1.0', 'wildcard': '0.0.0.255', 'area': 0},
        {'ip': '10.1.1.0', 'wildcard': '0.0.0.3', 'area': 0},
        {'ip': '1.1.1.1', 'wildcard': '0.0.0.0', 'area': 0}
    ]
}

r2_ospf_data = {
    'ospf_id': 1, 'vrf_name': 'control-data', 'default_route': True,
    'networks': [
        {'ip': '192.168.2.0', 'wildcard': '0.0.0.255', 'area': 0},
        {'ip': '10.1.1.0', 'wildcard': '0.0.0.3', 'area': 0},
        {'ip': '2.2.2.2', 'wildcard': '0.0.0.0', 'area': 0}
    ]
}

security_data = {
    'permits': [
        {'ip': '172.31.1.0', 'wildcard': '0.0.0.15'},
        {'ip': '10.30.6.0', 'wildcard': '0.0.1.255'}
    ]
}

# รวม Template และ Data เข้าด้วยกัน
# แยกคำสั่งด้วยการ split('\n') เพื่อให้ Netmiko อ่านเป็นทีละบรรทัด
s1_cfg = Template(s1_template).render(s1_data).strip().split('\n')
r1_cfg = Template(ospf_template).render(r1_ospf_data).strip().split('\n')

# R2 เอา OSPF มารวมกับ NAT
r2_cfg = Template(ospf_template).render(r2_ospf_data).strip().split('\n') 
r2_cfg += Template(r2_nat_template).render({'vrf_name': 'control-data'}).strip().split('\n')

sec_cfg = Template(security_template).render(security_data).strip().split('\n')

# ส่งคำสั่งเข้าอุปกรณ์ด้วย Netmiko
print(f"\n[1] กำลังตั้งค่า S1 ({s1['ip']})...")
with ConnectHandler(**s1) as ssh:
    ssh.enable()
    print(ssh.send_config_set(s1_cfg))
    ssh.save_config()

print(f"\n[2] กำลังตั้งค่า R1 ({r1['ip']})...")
with ConnectHandler(**r1) as ssh:
    ssh.enable()
    print(ssh.send_config_set(r1_cfg))
    ssh.save_config()

print(f"\n[3] กำลังตั้งค่า R2 ({r2['ip']})...")
with ConnectHandler(**r2) as ssh:
    ssh.enable()
    print(ssh.send_config_set(r2_cfg))
    ssh.save_config()

print("\n[4] กำลังตั้งค่า Security ACL เข้าสู่ทุกอุปกรณ์...")
for dev in all_devices:
    print(f" -> {dev['ip']}...")
    with ConnectHandler(**dev) as ssh:
        ssh.enable()
        ssh.send_config_set(sec_cfg)
        ssh.save_config()

print("\n--- เสร็จสิ้นการรันโค้ดด้วย Jinja2! ---")