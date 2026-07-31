import paramiko
import time

# ระบุ IP ของ R0, R1, R2, S0, S1 
devices = [
    "172.31.1.1", # R0
    "172.31.1.2", # S0
    "172.31.1.3", # S1
    "172.31.1.4", # R1
    "172.31.1.5"  # R2
]

# ดึง Private Key ที่เราสร้างไว้จากเครื่อง PC
private_key_path = r'C:\Users\LAB308_XX\Downloads\windows_user' # เปลี่ยนพาธให้ตรง
key = paramiko.RSAKey.from_private_key_file(private_key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

for ip in devices:
    print(f"Connecting to {ip}...")
    try:
        # สั่ง Connect โดยใช้ pkey แทนการใช้ password
        client.connect(hostname=ip, username='window_user', pkey=key, look_for_keys=False, allow_agent=False)
        print(f"[{ip}] Login Success using Public Key!")
        
        # ทดสอบส่งคำสั่ง
        stdin, stdout, stderr = client.exec_command('show ip int brief')
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print(f"[{ip}] Failed to connect: {e}")