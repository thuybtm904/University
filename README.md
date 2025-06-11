# Website So Sánh Thông Tin Đầu Vào Các Trường Đại Học Nước Ngoài

## Giới Thiệu

Đây là một ứng dụng web được xây dựng bằng Django và SQL Server, cho phép người dùng tìm kiếm, so sánh thông tin chi tiết về các trường đại học nước ngoài bao gồm:

- **Thông tin cơ bản**: Xếp hạng thế giới, quốc gia, năm thành lập, website chính thức
- **Chương trình học**: Danh sách các chuyên ngành, cấp độ học, thời gian học, học phí
- **Yêu cầu tuyển sinh**: SAT, ACT, IELTS, TOEFL, GPA, PTE Academic, Cambridge CELA, Duolingo, GRE, GMAT, MCAT
- **So sánh thông minh**: Sử dụng AI để phân tích và đưa ra gợi ý so sánh giữa các trường

## Tính Năng Chính

### 🔍 Tìm Kiếm Nâng Cao
- Tìm kiếm theo tên trường, quốc gia, chuyên ngành
- Lọc theo xếp hạng, học phí, cấp độ học
- Tìm kiếm thời gian thực không cần nhấn nút tìm kiếm

### 📊 So Sánh Chi Tiết
- So sánh tối đa 5 trường cùng lúc
- Phân tích AI thông minh dựa trên dữ liệu thực tế
- Bảng so sánh chi tiết các tiêu chí quan trọng

### 🎓 Thông Tin Toàn Diện
- Hiển thị đầy đủ yêu cầu tuyển sinh cho từng chương trình
- Thông tin học phí, thời gian học, cấp độ
- Xếp hạng từ các nguồn uy tín (QS, THE, ARWU)

### 🤖 Phân Tích AI
- Gợi ý trường phù hợp dựa trên profile học sinh
- Phân tích điểm mạnh/yếu của từng trường
- So sánh chi tiết theo chuyên ngành cụ thể

## Cấu Trúc Dữ Liệu

Website sử dụng cơ sở dữ liệu SQL Server với các bảng chính:

- **universities**: Thông tin trường đại học
- **countries**: Quốc gia
- **programs**: Các chương trình học
- **majors**: Chuyên ngành
- **university_programs**: Liên kết trường-chương trình-chuyên ngành
- **rankings**: Xếp hạng từ các nguồn khác nhau
- **criteria**: Tiêu chí tuyển sinh
- **university_admission_requirements**: Yêu cầu tuyển sinh cụ thể

## Cài Đặt và Chạy

### Yêu Cầu Hệ Thống
- Python 3.8+
- SQL Server (với Windows Authentication)
- Windows OS (khuyến nghị)

### Hướng Dẫn Cài Đặt

1. **Clone dự án và chạy setup tự động:**
   ```cmd
   git clone <repository-url>
   cd LTW
   setup_and_run.bat
   ```

2. **Chạy lại server cho các lần sau:**
   ```cmd
   run_server.bat
   ```

### Cài Đặt Thủ Công (nếu cần)

1. **Cài đặt dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Cấu hình database trong settings.py:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'mssql',
           'NAME': 'University',
           'HOST': 'DESKTOP-7HBAE21',  # Thay đổi theo máy của bạn
           'OPTIONS': {
               'driver': 'ODBC Driver 17 for SQL Server',
               'extra_params': 'Trusted_Connection=yes;TrustServerCertificate=yes;',
           },
       }
   }
   ```

3. **Chạy server:**
   ```cmd
   python manage.py runserver
   ```

4. **Truy cập website:**
   Mở trình duyệt và vào `http://127.0.0.1:8000`

## Cấu Trúc Thư Mục

```
LTW/
├── manage.py                 # File chính Django
├── requirements.txt          # Danh sách thư viện
├── setup_and_run.bat       # Script cài đặt và chạy lần đầu
├── run_server.bat          # Script chạy server các lần sau
├── README.md               # File hướng dẫn này
├── university_project/     # Cấu hình Django chính
│   ├── settings.py        # Cấu hình database, middleware
│   ├── urls.py           # URL routing chính
│   └── wsgi.py          # WSGI configuration
├── university_app/        # Ứng dụng chính
│   ├── models.py         # Models định nghĩa database schema
│   ├── views.py          # Logic xử lý request/response
│   ├── urls.py          # URL routing cho app
│   ├── admin.py         # Cấu hình Django admin
│   ├── templates/       # Templates HTML
│   ├── services/        # Services (AI analysis)
│   └── templatetags/    # Custom template tags
├── static/               # Files CSS, JS, images
└── venv/                # Python virtual environment
```

## Sử Dụng Website

### Trang Chủ
- Hiển thị danh sách trường đại học hàng đầu
- Quick search và filters
- Thống kê tổng quan

### Tìm Kiếm
- Tìm kiếm nâng cao với nhiều bộ lọc
- Kết quả hiển thị dạng card với thông tin cơ bản
- Sắp xếp theo xếp hạng, học phí, tên

### Chi Tiết Trường
- Thông tin toàn diện về trường
- Danh sách chương trình và yêu cầu tuyển sinh
- Tìm kiếm thời gian thực trong chương trình
- Nút thêm vào so sánh

### So Sánh
- Quản lý danh sách so sánh (tối đa 5 trường)
- Chọn chuyên ngành để so sánh chi tiết
- Phân tích AI thông minh
- Bảng so sánh trực quan

## Công Nghệ Sử Dụng

- **Backend**: Django 4.2.7, Python 3.8+
- **Database**: SQL Server với mssql-django
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI Integration**: Custom AI analysis service
- **Authentication**: Windows Authentication cho SQL Server

## Lưu Ý Quan Trọng

1. **Database Connection**: Đảm bảo SQL Server đang chạy và có database "University"
2. **Windows Authentication**: Cần chạy trên Windows với user có quyền truy cập SQL Server
3. **ODBC Driver**: Cần cài đặt "ODBC Driver 17 for SQL Server"

## Liên Hệ và Hỗ Trợ

Nếu gặp vấn đề trong quá trình cài đặt hoặc sử dụng, vui lòng:

1. Kiểm tra lại requirements.txt và cài đặt đúng phiên bản
2. Đảm bảo SQL Server connection working
3. Xem log file django.log để debug lỗi

---

**Phiên bản**: 2.0  
**Cập nhật lần cuối**: Tháng 1/2025  
**Tác giả**: Django University Comparison Team