import os
from os import listdir
from PIL import Image, ImageTk
from numpy import asarray
from numpy import expand_dims
from keras_facenet import FaceNet
import pickle, sqlite3
import cv2
import numpy as np
# import tensorflow as tf
import tkinter as tk
import re 
from datetime import datetime
import luu_thoi_gian_cham_cong as tgcc
# --------------------------Tao folder -------------------------------------
current_directory = os.getcwd()
folder='Images1/'
# Khởi tạo cơ sở dữ liệu người dùng

file_sql = "DuLieuNguoiDung1.db"
datafile = os.path.join(current_directory, file_sql)
ketNoiData = sqlite3.connect(datafile)
cursor = ketNoiData.cursor()
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS Person(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT
    );
''')
#----------------------------Tao mo hinh----------------------------
HaarCascade = cv2.CascadeClassifier(cv2.samples.findFile(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'))
MyFaceNet = FaceNet()
# detector_MTCNN = MTCNN()


#-----------------------------Luu anh vao folder-----------------------------
global so_luong_anh
so_luong_anh = 0
global database 
database = {}
global co_dung
co_dung = False
global ktm 
ktm = []
global co_ktm
co_ktm = 0
#----------------------------Khai bao cac ham co ban--------------------------
# Bat camera
def start_camera(panel):
    global cap
    cap = cv2.VideoCapture(0)
    update_frame(cap, panel)
# Cap nhat khung hinh
def update_frame(cap, panel):
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (500, 500))
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
    panel.after(10, update_frame, cap, panel)
# Đóng mỗi camera
def close_camera():
    # Thực hiện giải phóng tất cả các tài nguyên liên quan đến camera
    cv2.destroyAllWindows()
    # Nếu camera đang mở, đóng nó lại
    if 'cap' in locals() or 'cap' in globals():
        cap.release()
        print("Đã đóng camera.")
# Dung camera
def stop_camera():
    win.destroy()

def exit_program(event):
    if event.keysym == "Escape":
        win.quit()  # Thoát khỏi vòng lặp mainloop()    
#  Kiem tra xem camera co dang mo hay khong 
def check_and_close_camera():
    global co_dung
    co_dung = True
    global cap
    cap = cv2.VideoCapture(0)  
    # Mở camera
    # Kiểm tra xem camera có đang mở không
    if cap.isOpened():
        print("Camera đang bật. Tắt camera...")
        cap.release()  # Tắt camera
        print("Camera đã được tắt.")
    else:
        print("Camera không bật hoặc không thể truy cập.")   
#############################################################################################################################################
# ----------------------------------------- Window 2 (Them nhan vien) ----------------------------------------------------------

# Tao 1 cua so moi và thuc hien goi ham
def open_new_window():

    # Ẩn cửa sổ gốc
    win.withdraw()
    
    # Tạo cửa sổ mới
    new_window = tk.Toplevel(win)
    new_window.title("ADD NEW EMPLOYEE")  # Đặt tiêu đề cho cửa sổ mới
    new_window.geometry("800x500")
    
    # Đường dẫn đến ảnh nền
    background_image_path = "anh_main.png"

    # Load ảnh nền
    background_image = Image.open(background_image_path)
    background_image = background_image.resize((800, 500), Image.LANCZOS)  # Đảm bảo ảnh phù hợp với kích thước khung
    background_photo = ImageTk.PhotoImage(background_image)

    # Tạo một nhãn để chứa ảnh nền
    background_label = tk.Label(new_window, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    # Lưu tham chiếu đến ảnh nền để ngăn nó bị giải phóng bộ nhớ
    new_window.background_photo = background_photo

    #Khoi tao khu camera 2
    video_frame2 = tk.Frame(new_window, width=500, height=450)
    video_frame2.place(x=10, y=10)
    video_label2 = tk.Label(video_frame2)
    video_label2.pack()    

    label2 = tk.Label(new_window, text="Thêm thông tin nhân viên.", font=("Helvetica", 10, "bold"))
    label2.place(x=600, y=50)

    # Label để hiển thị thông báo lỗi
    error_label = tk.Label(new_window, text="", fg="red", font=("Helvetica", 10, "bold"))
    error_label.place(x=600, y=210)
    # Label để hiển thị thông báo thêm ảnh mới thành công
    add_new_ok = tk.Label(new_window, text="", fg="red", font=("Helvetica", 10, "bold"))
    add_new_ok.place(x=600, y=280)
    # Label hiện thị thông báo training thành công
    train_ok = tk.Label(new_window, text="", fg="red", font=("Helvetica", 10, "bold"))
    train_ok.place(x=600, y=350)

    #Label nhap ten
    label2 = tk.Label(new_window, text="Nhập tên nhân viên.", font=("Helvetica", 10, "bold"))
    label2.place(x=600, y=120)

    # Tao o nhap ten nhan vien
    e_name = tk.Entry(new_window, width=20, font=("Helvetica", 10, "bold"))
    e_name.place(x=600, y=170)


# Nut mo camera
    start_button = tk.Button(new_window, text="THÊM MỚI",width=10, font=("Helvetica", 10, "bold"), command=lambda: (get_name(e_name, error_label, video_label2, add_new_ok)))
    start_button.place(x=610, y=420)
# Nut Training Model
    train_button = tk.Button(new_window, text="TRAIN",width=10, font=("Helvetica", 10, "bold"),command=lambda: training_nhan_vien(train_ok))
    train_button.place(x=700, y=420)
# Thoat cua so
    stop_button = tk.Button(new_window, text="CLOSE",width=10, font=("Helvetica", 10, "bold"), command=lambda: close_new_window(new_window))
    stop_button.place(x=660, y=450)    

#------------------------------- Kiểm tra tên người dùng có đúng hay không----------------------------
def get_name(e_name, error_label, panel, add_new_ok):
    global cap
    cap = cv2.VideoCapture(0)
    employee_name = e_name.get().strip()
    employee_name = employee_name.title()
    error_message = ""
    
    # Kiểm tra xem tên có chứa số không
    if any(char.isdigit() for char in employee_name):
        error_message += "Tên không được chứa số."
    
    # Kiểm tra xem tên có ít nhất một ký tự chữ cái không
    if not any(char.isalpha() for char in employee_name):
        error_message += "Tên phải chứa ít nhất một ký tự chữ cái."
    
    # Kiểm tra xem tên có nhiều hơn 2 dấu cách giữa các từ không
    if len(re.findall(r'\s{2,}', employee_name)) > 0:
        error_message += "Tên không được chứa nhiều hơn hai dấu cách giữa các từ."
    
    # Hiển thị thông báo lỗi nếu có
    if error_message:
        error_label.config(text=error_message + "\n" + employee_name, fg="red")
    else:
        error_message = " "
        error_label.config(text="Nhập tên nhân viên thành công!" + "\n" + employee_name, fg="green")
        print("Tên nhân viên:", employee_name)

        # Them du lieu vao database, DuLieuNguoiDung
        # Thực hiện xử lý thêm người dùng vào hệ thống ở đây
        cursor.execute("INSERT INTO Person (name) VALUES (?)", (employee_name,))
        ketNoiData.commit()
        # Lấy ID của người dùng vừa thêm vào
        cursor.execute("SELECT last_insert_rowid()")
        user_id = cursor.fetchone()[0]
# Sau khi thực hiện các lệnh tìm kiếm, hiện thị thong tin nhan vien thì bật camera
        luu_anh(cap, employee_name, user_id, panel, add_new_ok)
        xoa_ky_tu(e_name)

# -----------------Ham luu anh cho folder train----------------------------------------
def luu_anh(cap, user_name, user_id, panel, add_new_ok):
    # user_name = user_name.replace(" ", "_")
    new_folder = f"{user_name}_{user_id}"
    user_folder = folder + new_folder
    os.makedirs(user_folder, exist_ok=True)
    global so_luong_anh
    # Đường dẫn đến mô hình và file cấu hình của OpenCV DNN
    model_path = "opencv_face_detector_uint8.pb"
    config_path = "opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
    ret, frame = cap.read()
    if ret:
        # Kiểm tra xem đã đủ thời gian chưa để xử lý frame mới
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (500, 500))    
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0), False, False)
        net.setInput(blob)
        detections = net.forward()
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.8:
                so_luong_anh = so_luong_anh + 1  
                box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                (startX, startY, endX, endY) = box.astype("int")
    # Chỉnh lại độ các cạnh của box
    # Tính toán kích thước tăng thêm
                delta_x = int(0.4 * (endX - startX))
                delta_y = int(0.4 * (endY - startY))
    # Cộng thêm 20% vào các biến
                startX -= delta_x
                startY -= delta_y
                endX += delta_x
                endY += delta_y - 20
    # Giới hạn lại các giá trị để không vượt quá kích thước hình ảnh
                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(frame.shape[1], endX)
                endY = min(frame.shape[0], endY)
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2) 
                cv2.putText(frame, f"Anh {so_luong_anh}", (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                if so_luong_anh > 5:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    img_path = os.path.join(user_folder, f'{user_name}.{user_id}.{so_luong_anh}.jpg')
                    cv2.imwrite(img_path, frame[startY:endY, startX:endX])
                
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.config(image=imgtk) 
    panel.after(200, luu_anh, cap, user_name, user_id, panel, add_new_ok)
    if so_luong_anh < 40:
        pass
    else :
        add_new_ok.config(text="Thêm mới ảnh thành công", fg="green")
        cap.release()
        cv2.destroyAllWindows()


#-------------------------Ham training nhan vien-------------------------------------
def training_nhan_vien(train_ok):
    database3 = {}
    if os.path.isfile("data1.pkl"):
        myfile = open("data1.pkl", "rb")
        database3 = pickle.load(myfile)
        myfile.close() 
    ids, names = get_info_final(cursor)
    name_folder_anh = f"{names}_{ids}"
    path = folder + name_folder_anh
    database1 = []
    for filename in list(os.listdir(path)):
        image_path = os.path.join(path, filename)  # Tạo đường dẫn đầy đủ đến tệp ảnh
        gbr1 = cv2.imread(image_path)  # Đọc tệp ảnh bằng đường dẫn đầy đủ
        wajah = HaarCascade.detectMultiScale(gbr1,1.1,4)
        if len(wajah)>0:
            x1, y1, width, height = wajah[0]         
        else:
            x1, y1, width, height = 1, 1, 10, 10
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height            
        gbr = cv2.cvtColor(gbr1, cv2.COLOR_BGR2RGB)
        gbr = Image.fromarray(gbr)                  # konversi dari OpenCV ke PIL
        gbr_array = asarray(gbr)
        face = gbr_array[y1:y2, x1:x2]                        
        face = Image.fromarray(face)                       
        face = face.resize((160,160))
        face = asarray(face)
        face = expand_dims(face, axis=0)
        signature = MyFaceNet.embeddings(face)
        database1.append(signature)
    # Tính trung bình giá trị của các vector
    average_embedding = np.mean(database1, axis=0)    
    database3[os.path.splitext(name_folder_anh)[0]]=average_embedding
    print(database3)
    myfile = open("data1.pkl", "wb")
    pickle.dump(database3, myfile)
    myfile.close()
    train_ok.config(text="Đào tạo mô hình thành công", fg="green")     


#---------------------------Get info nhan vien-------------------------------------
def get_info_final(cursor):
    cursor.execute("SELECT ID, Name FROM Person ORDER BY ID DESC LIMIT 1")
    last_row = cursor.fetchone()
    if last_row:
        last_id, last_name = last_row
        print("ID cuối cùng:", last_id)
        print("Tên cuối cùng:", last_name)
        return last_id, last_name
    else:
        print("Không có dữ liệu trong bảng Person.") 

#-------------------Ham xoa ky tự trong emtry-------------------------------
def xoa_ky_tu(e_name):
    # Kiểm tra nếu e_name đã có dữ liệu
    if len(e_name.get()) > 0:
        # Xoá dữ liệu trong entry
        e_name.delete(0, 'end')

#------------------Tạo nút để đóng cửa sổ mới và hiện lại cửa sổ gốc---------------------
def close_new_window(new_window):
    global cap
    cap = cv2.VideoCapture(0)
    if cap is not None:
        cap.release()
        new_window.destroy()
        win.deiconify()  # Hiện lại cửa sổ gốc khi cửa sổ mới bị đóng  
    else :      
        new_window.destroy()
        win.deiconify()  # Hiện lại cửa sổ gốc khi cửa sổ mới bị đóng    

###########################################################################################################################################
# ------------------------------------------WINDOW MAIN--------------------------------------------------------------------------------------------

win = tk.Tk()
# Khoi tao khung giao dien
win.title("Quản lý nhân sự")
win.geometry("800x500")
#---------------------------------------------------------------------------------------------

# Đường dẫn đến ảnh nền
background_image_path = "main3.jfif"

# Load ảnh nền
background_image = Image.open(background_image_path)
background_image = background_image.resize((800, 500), Image.LANCZOS)  # Đảm bảo ảnh phù hợp với kích thước khung
background_photo = ImageTk.PhotoImage(background_image)

# Tạo một nhãn để chứa ảnh nền
background_label = tk.Label(win, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
#--------------------------------------------------------------------------------------------------------------

# Khoi tao vị tri hiển thị thong tin nhan vien
label1 = tk.Label(win, text="Thông tin chấm công.", font=("Helvetica", 15, "bold"))
label1.place(x=550, y=50)

# khoi tao vi tri camera 
video_frame = tk.Frame(win, width=600, height=600)
video_frame.place(x=10, y=10)
video_label = tk.Label(video_frame)
video_label.pack()


#------------------Phan biet khuon mat-------------------------
def cham_cong(panel, cham_Congok):   
    global co_dung 
    co_dung = False
    database2 = {}
    myfile = open("data1.pkl", "rb")
    database2 = pickle.load(myfile)
    myfile.close()
    stop_flag = False
    # Đường dẫn đến mô hình và file cấu hình của OpenCV DNN
    model_path = "opencv_face_detector_uint8.pb"
    config_path = "opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
    global cap
    cap = cv2.VideoCapture(0) 
    def update_frame1(cham_Congok):
        global co_dung
        global ktm
        global co_ktm
        if co_dung:
            return 
        if stop_flag:
            return  # Nếu biến cờ là True, thoát khỏi hàm    
        ret, frame = cap.read() 
        font = cv2.FONT_HERSHEY_COMPLEX
        x1, x2, y1, y2 = 1, 1, 10, 10  # Việc tạo khung hiện báo cáo 
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (500, 500))    
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
            net.setInput(blob)
            detections = net.forward()
            # Lấy kích thước của hình ảnh
            (h, w) = frame.shape[:2]
            dict = None
            # Xử lý các khuôn mặt được phát hiện
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.8:  # Chỉ xem xét các phát hiện có độ tin cậy lớn hơn 0.5
                    # Tính toán tọa độ của khuôn mặt trong hình ảnh gốc
                    x1 = int(detections[0, 0, i, 3] * frame.shape[1])
                    y1 = int(detections[0, 0, i, 4] * frame.shape[0])
                    x2 = int(detections[0, 0, i, 5] * frame.shape[1])
                    y2 = int(detections[0, 0, i, 6] * frame.shape[0])

                    # Kiểm tra và điều chỉnh tọa độ nếu cần
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(frame.shape[1], x2)
                    y2 = min(frame.shape[0], y2)

                    # Kiểm tra tính hợp lệ của tọa độ trước khi cắt ảnh
                    if x1 < x2 and y1 < y2:
                        # Chuyển đổi màu cho khuôn mặt đầu tiên
                        face = cv2.cvtColor(frame[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
                        if face.size > 0:
                            face = Image.fromarray(face)  # Chuyển đổi từ OpenCV sang PIL
                            # Resize khuôn mặt về kích thước mong muốn
                            face = face.resize((160, 160))
                            # Chuyển đổi thành mảng
                            face_array = asarray(face)
                            face = expand_dims(face_array, axis=0)
                            signature = MyFaceNet.embeddings(face)
                            min_dist=100
                            identity=' '
                            for key, value in database2.items() :
                                name = key.split('_')[0]
                                id = key.split('_')[1] 
                                dist = np.linalg.norm(value-signature)
                                # print("Gia tri tong khoang cach: ",dist)
                                if dist < min_dist:
                                    if dist < 0.9:
                                        min_dist = dist
                                        identity = key
                                        if (identity != 'Khong Biet_1'):
                                            ktm.append(identity)
                                            co_ktm += 1
                                            
                                        # tgcc.update_time_for_id(id, name)
                                    else :
                                        identity = 'Unknown'
                            if(co_ktm == 10):
                                print("Gia tri co: ",co_ktm)
                                tgcc.kiemtra_so_lan_xuat_hien(ktm)
                                return
                            print("Ten du doan: ", identity, " Gia tri dist: ", dist)
                            cv2.putText(frame,identity, (100,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                            cv2.rectangle(frame,(x1,y1),(x2,y2), (0,255,0), 2)                            
                        else:
                            pass
                    else:
                        pass
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            panel.imgtk = imgtk
            panel.config(image=imgtk) 
        panel.after(100, update_frame1, cham_Congok)
    update_frame1(cham_Congok)




#------------------------------------GỌI HÀM WINDOW 1--------------------------------------------
# Nut cham cong
start_button = tk.Button(win, text="CHẤM CÔNG",width=10, font=("Helvetica", 10, "bold"), command=lambda: (cham_cong(video_label, cham_Congok)) )
start_button.place(x=590, y=420)

# Lable hiển thị chấm công nhân viên thành công 
cham_Congok = tk.Label(win, text="", fg="red", font=("Helvetica", 10, "bold"))
cham_Congok.place(x=600, y=280)
# Nut thoat
stop_button = tk.Button(win, text="THOÁT",width=10, font=("Helvetica", 10, "bold"), command=lambda: stop_camera())
stop_button.place(x=690, y=420)

# Nut them nhan vien
stop_button = tk.Button(win, text="ADD NEW EMPLOYEE",width=20, font=("Helvetica", 10, "bold"), command=lambda: (check_and_close_camera(), open_new_window()))
stop_button.place(x=605, y=450)
# Liên kết sự kiện nhấn phím với hàm exit_program
win.bind("<Key>", exit_program)
win.mainloop()
