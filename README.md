[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
|Naufal Daffa Alfa Zain |5025241066 |     D      |
|Muhamad Aziz Romdhoni |5025241071 |      D     |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```
https://youtu.be/j6pUfNls7HM
```

## Penjelasan Program
Program ini merupakan aplikasi terminal berbasis TCP yang terdiri dari empat jenis server dan satu program client. Semua server memiliki fitur yang sama, yaitu mengirim pesan antar client (broadcast message), melihat daftar file yang ada di server, mengupload file ke server, serta mendownload file dari server. Perbedaan utama dari keempat server tersebut adalah cara mereka menangani banyak client yang terhubung secara bersamaan. Ada server yang hanya melayani satu client, ada yang menggunakan thread, dan ada juga yang menggunakan mekanisme event seperti select dan poll.

### client.py

`client.py` berfungsi sebagai program yang digunakan oleh user untuk berinteraksi dengan server melalui terminal. Jika user mengetik teks biasa, maka teks tersebut akan dikirim sebagai pesan chat ke server. Server kemudian akan meneruskan pesan tersebut ke client lain yang sedang terhubung. Jika user mengetik perintah khusus seperti `/list, /upload, atau /download`, maka client akan menjalankan fitur yang sesuai dengan perintah tersebut. Di dalam client juga terdapat thread khusus untuk menerima data dari server. Ini memungkinkan client tetap bisa menerima pesan broadcast atau file download, walaupun user sedang mengetik sesuatu di terminal.

Function penting:

- `send_packet(sock, packet)`
Function ini digunakan untuk mengirim data dari client ke server dalam format JSON. Semua request dari client, seperti pesan chat, permintaan daftar file, upload file, dan download file, dikirim melalui function ini.
- `receive(sock)`
Function ini berjalan pada thread terpisah dan bertugas menerima respon dari server. Jika server mengirim pesan broadcast, pesan tersebut akan langsung ditampilkan di terminal. Jika server mengirim file, function ini juga akan menyimpan file tersebut ke folder client_downloads.
- `upload(sock, path)`
Function ini digunakan saat user menjalankan perintah /upload. Client akan membaca file dari komputer lokal, lalu mengirim informasi file dan isi file ke server.

### server-sync.py

`server-sync.py` adalah versi server yang paling sederhana. Server ini hanya bisa melayani satu client pada satu waktu. Jika satu client sedang melakukan suatu proses, misalnya upload file, maka client lain harus menunggu sampai proses tersebut selesai sebelum bisa dilayani oleh server.

Function penting:

- `send_packet(sock, packet)`
Function ini digunakan untuk mengirim respon dari server ke client dalam format JSON, misalnya pesan chat, daftar file, atau informasi bahwa proses upload telah selesai.
- `list_files()`
Function ini membaca isi folder server_files, kemudian mengembalikan daftar file yang tersedia di server.
- `handle_client(conn, addr)`
Function ini merupakan bagian utama yang menangani komunikasi dengan client. Di dalam function ini server membaca request dari client dan menentukan apakah client mengirim pesan chat, meminta daftar file, melakukan upload file, atau mendownload file.

### server-thread.py

Pada server ini, setiap client yang terhubung akan ditangani oleh thread yang berbeda. Dengan cara ini, beberapa client dapat berinteraksi dengan server secara bersamaan tanpa harus menunggu satu sama lain. Server juga menyimpan daftar client yang sedang aktif, sehingga jika ada client yang mengirim pesan chat, pesan tersebut dapat dikirim ke semua client lain yang sedang terhubung.

Function penting:

- `send_packet(client, packet)`
Function ini digunakan untuk mengirim data ke satu client. Karena server menggunakan banyak thread, proses pengiriman dibungkus dengan lock agar tidak terjadi benturan data saat beberapa thread mengirim data secara bersamaan.
- `broadcast(packet)`
Function ini bertugas mengirim pesan ke semua client yang sedang terhubung. Fitur chat antar client sangat bergantung pada function ini.
- `handle_client(conn, addr)`
Function ini berjalan di thread masing-masing client. Di dalamnya server membaca request dari client dan menjalankan perintah seperti chat, melihat daftar file, upload, atau download file.
- `send_file(client, path, name)`
Function ini digunakan saat client meminta download file. Server akan mengirim informasi file terlebih dahulu, kemudian mengirim isi file tersebut ke client.

### server-select.py

Server ini menggunakan modul select untuk memantau banyak koneksi socket secara bersamaan tanpa perlu membuat thread untuk setiap client. Server akan terus mengecek socket mana yang siap untuk dibaca atau ditulis, lalu memprosesnya dalam satu loop utama. Dengan cara ini, server tetap dapat melayani banyak client secara bersamaan dengan penggunaan resource yang lebih efisien dibandingkan membuat banyak thread.

Function penting:

- `packet_bytes(packet)`
Function ini mengubah data JSON menjadi bentuk bytes, sehingga data tersebut bisa dimasukkan ke antrean pengiriman client.
- `handle_packet(client, packet, clients)`
Function ini bertugas memproses packet yang diterima dari client, seperti pesan chat, permintaan daftar file, upload file, atau download file.
- `process_input(client, clients)`
Function ini memproses data yang diterima dari client. Jika client sedang mengupload file, data akan langsung ditulis ke file di server. Jika tidak, data akan diproses sebagai packet JSON biasa.
- `flush_output(client)`
Function ini mengirim data yang sudah ada di antrean output client, ketika socket sudah siap untuk melakukan pengiriman data.

### server-poll.py

`server-poll.py` memiliki konsep yang hampir sama dengan `server-select.py`, tetapi menggunakan mekanisme poll. Tujuannya tetap sama, yaitu memantau banyak koneksi client secara bersamaan dalam satu proses server, tanpa harus membuat thread untuk setiap client. Perbedaannya hanya terletak pada cara sistem mendeteksi event pada socket, karena poll menggunakan file descriptor untuk mengidentifikasi koneksi.

Function penting:

- `packet_bytes(packet)`
Function ini mengubah packet JSON menjadi bytes sebelum dikirim melalui socket.
- `handle_packet(client, packet, clients)`
Function ini memproses request dari client, seperti pesan chat, melihat daftar file, upload file, atau download file.
- `process_input(client, clients)`
Function ini memproses data yang diterima dari client, baik berupa pesan chat biasa maupun data file saat proses upload.
- `close_client(clients, by_fd, poller, sock)`
Function ini digunakan ketika koneksi client selesai atau terputus, sehingga socket tersebut dapat dihapus dari daftar client aktif dan dari sistem pemantauan poll.

### Fitur Transfer File

File yang diupload oleh client akan disimpan di folder `server_files` pada server. Jika client melakukan download file, maka file tersebut akan disimpan di folder `client_downloads` pada sisi client. Proses upload dan download dapat langsung terlihat hasilnya saat program dijalankan.

### Cara Menjalankan Program

1. Pertama, jalankan salah satu server, misalnya:

`python3 server-thread.py`

2. Kemudian jalankan client pada terminal lain:

`python3 client.py`

3. Beberapa command yang bisa digunakan pada client:
```
test pesan
/list
/upload client_downloads/g1-upload.txt
/download g1-upload.txt
```
Perintah pertama akan mengirim pesan chat biasa, sedangkan perintah lainnya digunakan untuk melihat daftar file di server, mengupload file, dan mendownload file dari serve

## Screenshot Hasil
### 1. Server-sync.py
- Broadcast massages
<img width="1920" height="1080" alt="Screenshot 2026-03-25 212758" src="https://github.com/user-attachments/assets/5a836e3b-09dc-48e8-a87d-6f2830695f34" />
Broadcast message tidak bisa dilakukan pada server synchronous karena server hanya menangani satu client dalam satu waktu.
<br><br>
- /list
<img width="1920" height="1080" alt="Screenshot 2026-03-25 212910" src="https://github.com/user-attachments/assets/68654c72-5841-49eb-bf45-ad48642f51c2" />
<br><br>
- /upload
<img width="1920" height="1080" alt="Screenshot 2026-03-25 212946" src="https://github.com/user-attachments/assets/b3a5557d-4be8-4862-ba49-f5ea1879b89c" />
<br><br>
- /download
<img width="1920" height="1080" alt="Screenshot 2026-03-25 213004" src="https://github.com/user-attachments/assets/780aab95-6845-4e9b-bc1d-51c85178eecc" />

### 2. Server-thread.py
- Broadcast massages
<img width="1920" height="1080" alt="Screenshot 2026-03-25 213144" src="https://github.com/user-attachments/assets/9ed8b528-bdfe-4dc7-8b55-027dfac0ec01" />
<br><br>
- /list
<img width="1920" height="1080" alt="Screenshot 2026-03-25 213223" src="https://github.com/user-attachments/assets/a235e51f-2c8c-49c2-a849-fc4d817df396" />
<br><br>
- /upload
<img width="1920" height="1080" alt="Screenshot 2026-03-25 213250" src="https://github.com/user-attachments/assets/69026665-805a-491c-89ee-0894c60ef405" />
<br><br>
- /download
<img width="1920" height="1080" alt="Screenshot 2026-03-25 213306" src="https://github.com/user-attachments/assets/de830fc3-4c67-4576-b8cb-9ecf334cc4ed" />

### 3. Server-select.py
- Broadcast massages
<img width="1920" height="1080" alt="Screenshot 2026-03-25 213948" src="https://github.com/user-attachments/assets/de9253ca-c118-4a3b-81c5-530caddf8ed2" />
<br><br>
- /list
<img width="1920" height="1080" alt="Screenshot 2026-03-25 214009" src="https://github.com/user-attachments/assets/323421ca-8674-4ea1-b67e-a4f17b003046" />
<br><br>
- /upload
<img width="1920" height="1080" alt="Screenshot 2026-03-25 214029" src="https://github.com/user-attachments/assets/cbc3968e-f038-4cbe-9de0-09f908e294ae" />
<br><br>
- /download
<img width="1920" height="1080" alt="Screenshot 2026-03-25 214042" src="https://github.com/user-attachments/assets/b93f9c6b-982f-4eb5-a17b-aaec43659c8b" />

### 4. Server-poll.py
![WhatsApp Image 2026-03-25 at 22 02 14](https://github.com/user-attachments/assets/679f969e-2fa7-4861-b387-6e4e6ad02e62)
