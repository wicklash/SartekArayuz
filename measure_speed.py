
import serial
import time
import sys

# Simülatör COM2'ye yazıyor, biz COM1'den (veya argümanla verilen porttan) okumalıyız
READ_PORT = 'COM1' 
if len(sys.argv) > 1:
    READ_PORT = sys.argv[1]

def measure_throughput():
    print(f"Port {READ_PORT} üzerinden veri hızı ölçülüyor...")
    print("Lütfen simülatörün (COM2) açık olduğundan emin olun.")
    
    try:
        ser = serial.Serial(READ_PORT, 19200, timeout=1) # Baudrate okumada önemsizdir ama 19200 verelim
    except Exception as e:
        print(f"HATA: {READ_PORT} portu açılamadı: {e}")
        print("İpucu: Eğer simülatör çalışmıyorsa veri gelmeyecektir.")
        return

    start_time = time.time()
    byte_count = 0
    duration = 5.0  # 5 saniyelik test

    print(f"{duration} saniye boyunca veri toplanıyor...")
    
    try:
        while (time.time() - start_time) < duration:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                byte_count += len(data)
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

    elapsed = time.time() - start_time
    bytes_per_sec = byte_count / elapsed
    bits_per_sec = bytes_per_sec * 8

    print("-" * 30)
    print(f"Port: {READ_PORT}")
    print(f"Toplam Süre: {elapsed:.2f} sn")
    print(f"Toplam Veri: {byte_count} byte")
    print("-" * 30)
    print(f"HIZ: {bytes_per_sec:.2f} Byte/s")
    print(f"HIZ: {bits_per_sec:.2f} bit/s (bps)")
    print("-" * 30)

if __name__ == "__main__":
    measure_throughput()
