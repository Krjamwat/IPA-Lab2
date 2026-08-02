from netmiko import ConnectHandler

key_path = r'C:\Users\LAB308_XX\Downloads\windows_user_openssh_new'
username_login = 'window_user'

# ใส่ Management IP ของแต่ละอุปกรณ์ 
r1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.4', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
r2 = {'device_type': 'cisco_ios', 'ip': '172.31.1.5', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}
s1 = {'device_type': 'cisco_ios', 'ip': '172.31.1.3', 'username': username_login, 'use_keys': True, 'key_file': key_path, 'secret': 'class'}

def configure_description(device, device_name):
    print(f"\n--- กำลังประมวลผลอุปกรณ์ {device_name} ---")
    with ConnectHandler(**device) as ssh:
        ssh.enable()
        
        # ดึงข้อมูล CDP Neighbor มาเป็น Dictionary
        # ผลลัพธ์จะเป็น List ของ Dictionary เช่น [{'neighbor': 'R2', 'local_interface': 'Gig 0/1', 'neighbor_interface': 'Gig 0/1', ...}]
        cdp_output = ssh.send_command("show cdp neighbors", use_textfsm=True)

        print("\n[DEBUG] ข้อมูลที่ดึงได้คือ:", cdp_output, "\n")
        config_commands = []
        
        # วนลูปสร้างคำสั่ง Description จากข้อมูล CDP
        if isinstance(cdp_output, list):
            for neighbor in cdp_output:
                # พอร์ตฝั่งเรา
                local_intf = neighbor['local_interface'].replace(' ', '')
                
                # พอร์ตปลายทาง (เอา platform มาต่อกับ neighbor_interface เพื่อให้ได้คำว่า Gig0/1)
                remote_intf = neighbor['platform'] + neighbor['neighbor_interface']
                
                # ชื่ออุปกรณ์ปลายทาง (ตัด .ipa.com ทิ้ง)
                remote_name = neighbor['neighbor_name'].split('.')[0]
                
                desc = f"Connect to {remote_intf} of {remote_name}"
                config_commands.extend([
                    f"interface {local_intf}",
                    f"description {desc}"
                ])

        if device_name == 'R1':
            config_commands.extend([
                "interface GigabitEthernet0/1", # R1 ต่อกับ PC1 ที่พอร์ต Gi0/1
                "description Connect to PC"
            ])
        elif device_name == 'R2':
            config_commands.extend([
                "interface GigabitEthernet0/3", # R2 ต่อกับ NAT (WAN) ที่พอร์ต Gi0/3
                "description Connect to WAN"
            ])
        elif device_name == 'S1':
            config_commands.extend([
                "interface GigabitEthernet0/2", # S1 ต่อกับ PC2 ที่พอร์ต Gi0/2
                "description Connect to PC"
            ])

        # ส่งคำสั่งตั้งค่าเข้าไปในอุปกรณ์
        if config_commands:
            print("คำสั่งที่จะส่ง:")
            for cmd in config_commands: print(f"  {cmd}")
            ssh.send_config_set(config_commands)
            ssh.save_config()

if __name__ == "__main__":
    configure_description(r1, 'R1')
    configure_description(r2, 'R2')
    configure_description(s1, 'S1')