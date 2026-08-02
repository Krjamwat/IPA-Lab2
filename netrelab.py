import re
from netmiko import ConnectHandler

key_path = r'C:\Users\LAB308_XX\Downloads\windows_user_openssh_new'
username_login = 'window_user'

# ใส่ Management IP ของแต่ละอุปกรณ์ 
r1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.4', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
r2 = {'device_type': 'cisco_ios', 'ip': '172.31.1.5', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}

target_routers = [r1, r2]

# Regex หา Interface ที่มีคำว่า up และ up อยู่ท้ายบรรทัด
intf_pattern = re.compile(r'^(\S+)\s+(\S+)\s+\w+\s+\w+\s+up\s+up', re.MULTILINE)

# Regex หาคำว่า "uptime is ..." เพื่อดึงเวลา
uptime_pattern = re.compile(r'uptime is (.*?)$', re.MULTILINE)

print("เริ่มกระบวนการตรวจสอบ R1 และ R2 ด้วย Regular Expression...")

for dev in target_routers:
    print(f"\n{'='*50}")
    print(f"ดึงข้อมูลจาก Router: {dev['ip']} ...")
    
    with ConnectHandler(**dev) as ssh:
        ssh.enable()
        
        # ส่งคำสั่งไปดึงข้อมูลดิบๆออกมาก่อน
        sh_ver = ssh.send_command("show version")
        sh_ip_int = ssh.send_command("show ip interface brief")
        
        # หา Uptime
        uptime_match = uptime_pattern.search(sh_ver)
        if uptime_match:
            print(f"[*] Device Uptime : {uptime_match.group(1)}")
        else:
            print("[*] Device Uptime : ไม่พบข้อมูล")
            
        # หา Active Interfaces
        print("[*] Active Interfaces :")
        active_ints = intf_pattern.findall(sh_ip_int) # หาผลลัพธ์ที่ตรงกับเงื่อนไขทั้งหมด
        
        if active_ints:
            for intf in active_ints:
                intf_name = intf[0] # ชื่อพอร์ต
                intf_ip = intf[1]   # หมายเลข IP
                print(f"    - {intf_name:<20} (IP: {intf_ip})")
        else:
            print("    - ไม่พบพอร์ตที่กำลัง Active")
            
    print(f"{'='*50}")

print("\n--- เสร็จสิ้นการดึงข้อมูล! ---")