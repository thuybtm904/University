from django.shortcuts import render

def handler404(request, exception):
    return render(request, 'university_app/loi.html', {
        'ma_loi': 404,
        'thong_diep_loi': 'Không tìm thấy trang',
        'mo_ta_loi': 'Trang bạn tìm kiếm không tồn tại hoặc đã được di chuyển.'
    }, status=404)

def handler500(request):
    return render(request, 'university_app/loi.html', {
        'ma_loi': 500,
        'thong_diep_loi': 'Lỗi máy chủ',
        'mo_ta_loi': 'Có lỗi xảy ra trên máy chủ. Đội ngũ kỹ thuật đã được thông báo về sự cố này.'
    }, status=500)
