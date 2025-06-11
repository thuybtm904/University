from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg, Min, Max, Count
from django.core.paginator import Paginator
from django.db import connection
from django.utils import timezone
from .models import (
    University, Major, UniversityAdmissionRequirement, Country, 
    Program, Criteria, Ranking, RankingSource, UniversityProgram
)
import json
import logging
from urllib.parse import unquote

logger = logging.getLogger(__name__)

def generate_comparison_data(universities, selected_major):
    """Generate comparison data for universities with selected major"""
    comparison_data = []
    
    for uni in universities:
        # Get program info for the selected major
        program = uni.universityprogram_set.filter(major__name=selected_major).first()
        
        # Get latest ranking
        latest_ranking = uni.ranking_set.order_by('-fyear').first()
        
        # Get admission requirements for this major/program
        requirements = {}
        if program:
            for req in uni.universityadmissionrequirement_set.filter(program=program.program):
                requirements[req.criteria.name] = {
                    'value': req.value,
                    'unit': req.criteria.unit if req.criteria else ''
                }
        
        uni_data = {
            'ten_truong': uni.name,
            'quoc_gia': uni.country.name if uni.country else 'Unknown',
            'nam_thanh_lap': uni.founded_year,
            'website': uni.website,
            'xep_hang_the_gioi': latest_ranking.frank if latest_ranking else None,
            'nguon_xep_hang': latest_ranking.ranking_sources.name if latest_ranking and latest_ranking.ranking_sources else 'N/A',
            'hoc_phi': program.tuition_fee if program else None,
            'thoi_gian_hoc': program.duration if program else None,
            'cap_do': program.program.level if program and program.program else None,
            'yeu_cau_tuyen_sinh': requirements
        }
        comparison_data.append(uni_data)
    
    return comparison_data

def generate_ai_analysis(comparison_data, selected_major):
    """Generate AI analysis for comparison"""
    if not comparison_data:
        return ""
    
    # Simple AI-like analysis based on comparison data
    analysis = f"PHÂN TÍCH SO SÁNH CHUYÊN NGÀNH {selected_major.upper()}\n\n"
    
    # Rankings comparison
    rankings = [(uni['ten_truong'], uni['xep_hang_the_gioi']) for uni in comparison_data if uni['xep_hang_the_gioi']]
    if rankings:
        rankings.sort(key=lambda x: x[1])
        analysis += "XẾP HẠNG THẾ GIỚI:\n"
        for i, (name, rank) in enumerate(rankings, 1):
            analysis += f"{i}. {name}: Top {rank}\n"
        analysis += f"\n➤ {rankings[0][0]} có xếp hạng cao nhất (Top {rankings[0][1]})\n\n"
    
    # Tuition comparison
    tuitions = [(uni['ten_truong'], uni['hoc_phi']) for uni in comparison_data if uni['hoc_phi']]
    if tuitions:
        tuitions.sort(key=lambda x: x[1])
        analysis += "CHI PHÍ HỌC TẬP:\n"
        for name, fee in tuitions:
            analysis += f"• {name}: ${fee:,.0f}/năm\n"
        analysis += f"\n➤ {tuitions[0][0]} có học phí thấp nhất (${tuitions[0][1]:,.0f})\n"
        analysis += f"➤ {tuitions[-1][0]} có học phí cao nhất (${tuitions[-1][1]:,.0f})\n\n"
    
    # Requirements analysis
    all_requirements = set()
    for uni in comparison_data:
        all_requirements.update(uni['yeu_cau_tuyen_sinh'].keys())
    
    if all_requirements:
        analysis += "YÊU CẦU TUYỂN SINH:\n"
        for req in sorted(all_requirements):
            analysis += f"• {req}:\n"
            for uni in comparison_data:
                if req in uni['yeu_cau_tuyen_sinh']:
                    req_info = uni['yeu_cau_tuyen_sinh'][req]
                    analysis += f"  - {uni['ten_truong']}: {req_info['value']}{req_info['unit']}\n"
            analysis += "\n"
    
    # Recommendations
    analysis += "KHUYẾN NGHỊ:\n"
    if rankings and tuitions:
        best_ranking = rankings[0][0]
        cheapest = tuitions[0][0]
        if best_ranking == cheapest:
            analysis += f"➤ {best_ranking} là lựa chọn tối ưu với xếp hạng cao và học phí hợp lý\n"
        else:
            analysis += f"➤ Chọn {best_ranking} nếu ưu tiên danh tiếng và chất lượng\n"
            analysis += f"➤ Chọn {cheapest} nếu ưu tiên tiết kiệm chi phí\n"
    
    analysis += "\n* Phân tích dựa trên dữ liệu có sẵn trong hệ thống"
    
    return analysis

def get_sample_universities():
    """Sample university data for fallback"""
    return [
        {
            'ma_truong': 'MIT',
            'ten_truong': 'Massachusetts Institute of Technology',
            'quoc_gia': 'US',
            'mo_ta': 'Top technical university known for innovation...',
            'xep_hang_the_gioi': 1,
            'hoc_phi': 57000,
            'co_hoc_bong': True,
            'hinh_anh': None
        },
        {
            'ma_truong': 'Harvard',
            'ten_truong': 'Harvard University', 
            'quoc_gia': 'US',
            'mo_ta': 'Prestigious Ivy League university...',
            'xep_hang_the_gioi': 2,
            'hoc_phi': 56000,
            'co_hoc_bong': True,
            'hinh_anh': None
        }
    ]
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    

def trang_chu(request):
    """Trang chủ hiển thị các trường đại học nổi bật"""
    try:
        # Check if database has data
        total_universities = University.objects.count()
        logger.info(f"Homepage: Found {total_universities} universities in database")
        
        if total_universities == 0:
            logger.warning("Homepage: Database has no universities!")
            # Use sample data when database is empty
            return render(request, 'university_app/trang_chu.html', {
                'truong_noi_bat': get_sample_universities(),
                'thong_ke': {'tong_truong': 0, 'tong_chuyen_nganh': 0, 'tong_quoc_gia': 0}
            })
        
        # Sử dụng Django ORM để lấy top 6 trường đại học
        top_universities = University.objects.select_related('country').order_by('founded_year')[:6]
        
        truong_noi_bat = []
        sample_rankings = [1, 2, 3, 5, 8, 12]
        
        for i, uni in enumerate(top_universities):
            # Lấy ranking theo thứ tự ưu tiên: QS -> THE -> ARWU -> any other
            preferred_sources = ['QS', 'THE', 'ARWU']
            best_ranking = None
            
            for source in preferred_sources:
                ranking = uni.ranking_set.filter(ranking_sources__name=source).order_by('-fyear').first()
                if ranking:
                    best_ranking = ranking
                    break
            
            # Nếu không có từ các nguồn ưu tiên, lấy ranking mới nhất
            if not best_ranking:
                best_ranking = uni.ranking_set.order_by('-fyear').first()
            
            # Lấy học phí trung bình từ các chương trình
            avg_tuition = uni.universityprogram_set.aggregate(avg_fee=Avg('tuition_fee'))['avg_fee']
            
            # Đảm bảo tên trường không rỗng
            university_name = uni.name.strip() if uni.name else (uni.short_name or 'Unknown University')
            if not university_name:
                university_name = uni.short_name or f'University ID {uni.id}'
            
            truong_data = {
                'ma_truong': uni.short_name or uni.name[:10],
                'ten_truong': university_name,
                'quoc_gia': uni.country.name if uni.country else 'Unknown',
                'mo_ta': (uni.description or 'No description')[:100] + '...',
                'xep_hang_the_gioi': best_ranking.frank if best_ranking else None,
                'hoc_phi': int(avg_tuition) if avg_tuition else None,
                'co_hoc_bong': True,
                'hinh_anh': None
            }
            truong_noi_bat.append(truong_data)
        
        # Thống kê tổng quan sử dụng Django ORM
        thong_ke = {
            'tong_truong': University.objects.count(),
            'tong_chuyen_nganh': Major.objects.count(),
            'tong_quoc_gia': Country.objects.count()
        }
        
        context = {
            'truong_noi_bat': truong_noi_bat,
            'thong_ke': thong_ke
        }
        
        return render(request, 'university_app/trang_chu.html', context)
        
    except Exception as e:
        logger.error(f"Lỗi trang chủ: {str(e)}")
        messages.error(request, "Có lỗi xảy ra khi tải trang chủ.")
        return render(request, 'university_app/trang_chu.html', {
            'truong_noi_bat': get_sample_universities(),
            'thong_ke': {'tong_truong': 0, 'tong_chuyen_nganh': 0, 'tong_quoc_gia': 0}
        })

def tim_kiem(request):
    """Trang tìm kiếm trường đại học"""
    try:
        # Check if database has data
        total_universities = University.objects.count()
        logger.info(f"Search page: Found {total_universities} universities in database")
        
        if total_universities == 0:
            logger.warning("Search page: Database has no universities!")
            messages.warning(request, "Cơ sở dữ liệu chưa có dữ liệu. Đang hiển thị dữ liệu mẫu.")
            # Return empty lists when database is empty
            return render(request, 'university_app/tim_kiem.html', {
                'danh_sach_truong': [],
                'danh_sach_quoc_gia': [],
                'danh_sach_chuyen_nganh': []
            })
        
        # Lấy danh sách trường đại học sử dụng Django ORM
        universities = University.objects.select_related('country').order_by('name')
        
        # Lấy danh sách quốc gia
        countries = Country.objects.values_list('name', flat=True).order_by('name')
        logger.info(f"Các quốc gia: {list(countries)}")
        # Lấy danh sách chuyên ngành
        majors = Major.objects.order_by('name')
        
        # Chuẩn bị data cho template
        danh_sach_truong = []
        for uni in universities:
            danh_sach_truong.append({
                'ten_truong': uni.name,
                'short_name': uni.short_name,
                'country_name': uni.country.name if uni.country else 'Unknown',
                'founded_year': uni.founded_year
            })
        
        danh_sach_chuyen_nganh = []
        for major in majors:
            danh_sach_chuyen_nganh.append({
                'ma_chuyen_nganh': major.id,
                'ten_chuyen_nganh': major.name
            })
        
        context = {
            'danh_sach_truong': danh_sach_truong,
            'danh_sach_quoc_gia': list(countries),
            'danh_sach_chuyen_nganh': danh_sach_chuyen_nganh
        }
        
        return render(request, 'university_app/tim_kiem.html', context)
        
    except Exception as e:
        logger.error(f"Lỗi trang tìm kiếm: {str(e)}")
        return render(request, 'university_app/tim_kiem.html', {
            'danh_sach_truong': [],
            'danh_sach_quoc_gia': [],
            'danh_sach_chuyen_nganh': []
        })

def ket_qua_tim_kiem(request):
    """API trả về kết quả tìm kiếm"""
    try:
        # Lấy tham số tìm kiếm
        tu_khoa = request.GET.get('tu_khoa', '').strip()
        quoc_gia = request.GET.get('quoc_gia', '').strip()
        chuyen_nganh_id = request.GET.get('ma_chuyen_nganh', '').strip()
        trang = int(request.GET.get('trang', 1))
        
        # Query cơ bản
        queryset = University.objects.select_related('country')
        
        # Lọc theo từ khóa
        if tu_khoa:
            queryset = queryset.filter(
                Q(name__icontains=tu_khoa) | 
                Q(short_name__icontains=tu_khoa)
            )
        
        # Lọc theo quốc gia
        if quoc_gia:
            queryset = queryset.filter(country__name=quoc_gia)
        
        # Lọc theo chuyên ngành
        if chuyen_nganh_id:
            try:
                # Lọc các trường có chương trình với chuyên ngành này
                queryset = queryset.filter(
                    universityprogram__major_id=int(chuyen_nganh_id)
                ).distinct()
            except ValueError:
                pass
        
        # Sắp xếp
        queryset = queryset.order_by('name')
        
        # Phân trang
        paginator = Paginator(queryset, 6)
        page_obj = paginator.get_page(trang)
        
        # Chuẩn bị dữ liệu trả về
        danh_sach_truong = []
        for uni in page_obj:
            # Lấy ranking trung bình
            avg_ranking = uni.ranking_set.aggregate(avg_rank=Avg('frank'))['avg_rank']
            
            # Lấy danh sách chuyên ngành
            majors = uni.universityprogram_set.select_related('major').values_list('major__name', flat=True).distinct()
            
            # Đảm bảo tên trường không rỗng
            university_name = uni.name.strip() if uni.name else (uni.short_name or 'Unknown University')
            if not university_name:
                logger.warning(f"University with ID {uni.id} has empty name, using short_name or default")
                university_name = uni.short_name or f'University ID {uni.id}'
            
            danh_sach_truong.append({
                'ma_truong': uni.short_name or uni.name[:10],
                'ten_truong': university_name,
                'quoc_gia': uni.country.name if uni.country else 'Unknown',
                'xep_hang_the_gioi': int(avg_ranking) if avg_ranking else 'N/A',
                'chuyen_nganh': ', '.join(list(majors)[:3]) + ('...' if len(majors) > 3 else '')
            })
        
        return JsonResponse({
            'danh_sach_truong': danh_sach_truong,
            'phan_trang': {
                'trang_hien_tai': page_obj.number,
                'tong_trang': paginator.num_pages,
                'tong_ket_qua': paginator.count,
                'co_trang_truoc': page_obj.has_previous(),
                'co_trang_sau': page_obj.has_next()
            }
        })
        
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm: {str(e)}")
        return JsonResponse({
            'error': 'Có lỗi xảy ra khi tìm kiếm',
            'danh_sach_truong': [],
            'phan_trang': {
                'trang_hien_tai': 1,
                'tong_trang': 0,
                'tong_ket_qua': 0,
                'co_trang_truoc': False,
                'co_trang_sau': False
            }
        })

def so_sanh(request):
    """Trang so sánh trường đại học với session-based comparison"""
    try:
        context = {}
        
        # Lấy danh sách so sánh từ session
        comparison_list = request.session.get('comparison_list', [])
        
        # FIX: Handle clear all functionality
        if 'clear_all' in request.GET:
            request.session['comparison_list'] = []
            comparison_list = []
            messages.success(request, 'Đã xóa toàn bộ danh sách so sánh.')
        
        # Xử lý thêm trường vào so sánh
        if 'add_university' in request.GET:
            university_name = unquote(request.GET.get('add_university', '').strip())
            logger.info(f"Attempting to add university to comparison: '{university_name}'")
            
            if university_name:
                # Kiểm tra xem trường có tồn tại trong database không
                try:
                    university_exists = University.objects.filter(
                        Q(name=university_name) | Q(short_name=university_name)
                    ).exists()
                    
                    if not university_exists:
                        logger.warning(f"University '{university_name}' not found in database")
                        messages.error(request, f'Không tìm thấy trường "{university_name}" trong cơ sở dữ liệu.')
                    elif university_name not in comparison_list:
                        if len(comparison_list) < 5:
                            comparison_list.append(university_name)
                            request.session['comparison_list'] = comparison_list
                            logger.info(f"Added '{university_name}' to comparison list. Total: {len(comparison_list)}")
                            messages.success(request, f'Đã thêm "{university_name}" vào danh sách so sánh.')
                        else:
                            messages.warning(request, 'Bạn chỉ có thể so sánh tối đa 5 trường.')
                    else:
                        messages.info(request, f'"{university_name}" đã có trong danh sách so sánh.')
                except Exception as e:
                    logger.error(f"Error checking university existence: {str(e)}")
                    messages.error(request, 'Có lỗi xảy ra khi kiểm tra thông tin trường.')
        
        # Xử lý xóa trường khỏi so sánh
        if 'remove_university' in request.GET:
            university_name = unquote(request.GET.get('remove_university', '').strip())
            if university_name in comparison_list:
                comparison_list.remove(university_name)
                request.session['comparison_list'] = comparison_list
                messages.success(request, f'Đã xóa "{university_name}" khỏi danh sách so sánh.')
        
        # FIX: Get common majors for universities in comparison list
        common_majors = []
        selected_major = request.GET.get('ma_chuyen_nganh', '').strip()
        comparison_results = {}
        ai_analysis = ""
        
        if len(comparison_list) >= 2:
            # Find universities in the comparison list
            universities_in_comparison = University.objects.filter(
                Q(name__in=comparison_list) | Q(short_name__in=comparison_list)
            )
            
            if universities_in_comparison.exists():
                # Get all majors for the first university
                first_uni = universities_in_comparison.first()
                first_uni_majors = set(
                    first_uni.universityprogram_set.values_list('major__name', flat=True)
                )
                
                # Find majors that exist in ALL universities
                for uni in universities_in_comparison:
                    uni_majors = set(
                        uni.universityprogram_set.values_list('major__name', flat=True)
                    )
                    first_uni_majors = first_uni_majors.intersection(uni_majors)
                
                # Get the actual major objects
                if first_uni_majors:
                    common_majors = Major.objects.filter(name__in=first_uni_majors).order_by('name')
                
                # If major is selected, generate comparison
                if selected_major and selected_major in first_uni_majors:
                    comparison_results = generate_comparison_data(universities_in_comparison, selected_major)
                    ai_analysis = generate_ai_analysis(comparison_results, selected_major)
        
        # Lấy thông tin chi tiết các trường trong danh sách so sánh
        danh_sach_truong = []
        if comparison_list:
            logger.info(f"Looking up universities for comparison: {comparison_list}")
            
            # Tìm kiếm bằng cả name và short_name
            universities = University.objects.filter(
                Q(name__in=comparison_list) | Q(short_name__in=comparison_list)
            ).select_related('country').prefetch_related(
                'ranking_set__ranking_sources',
                'universityprogram_set__major',
                'universityprogram_set__program',
                'universityadmissionrequirement_set__criteria',
                'universityadmissionrequirement_set__program'
            )
            
            logger.info(f"Found {universities.count()} universities for comparison")
            
            for uni in universities:
                # Lấy ranking
                rankings = {}
                for ranking in uni.ranking_set.all():
                    source_name = ranking.ranking_sources.name if ranking.ranking_sources else 'Unknown'
                    if source_name not in rankings:
                        rankings[source_name] = []
                    rankings[source_name].append({
                        'year': ranking.fyear,
                        'rank': ranking.frank
                    })
                
                # Lấy chương trình học
                programs = {}
                for prog in uni.universityprogram_set.all():
                    program_name = prog.program.name if prog.program else 'Unknown'
                    if program_name not in programs:
                        programs[program_name] = []
                    programs[program_name].append({
                        'major': prog.major.name if prog.major else 'Unknown',
                        'tuition_fee': prog.tuition_fee,
                        'duration': prog.duration
                    })
                
                # Lấy yêu cầu tuyển sinh
                requirements = {}
                for req in uni.universityadmissionrequirement_set.all():
                    criteria_name = req.criteria.name if req.criteria else 'Unknown'
                    program_name = req.program.name if req.program else 'General'
                    
                    if program_name not in requirements:
                        requirements[program_name] = {}
                    
                    requirements[program_name][criteria_name] = {
                        'value': req.value,
                        'unit': req.criteria.unit if req.criteria else ''
                    }
                
                danh_sach_truong.append({
                    'ten_truong': uni.name,
                    'quoc_gia': uni.country.name if uni.country else 'Unknown',
                    'nam_thanh_lap': uni.founded_year,
                    'website': uni.website,
                    'mo_ta': uni.description,
                    'rankings': rankings,
                    'programs': programs,
                    'requirements': requirements
                })
        
        # Lấy danh sách tất cả trường để chọn
        all_universities = University.objects.values_list('name', flat=True).order_by('name')
        
        
        
        # Chuẩn bị dữ liệu biểu đồ xếp hạng (ranking chart)
        ranking_chart_data = {}
        for truong in danh_sach_truong:
            ten_truong = truong['ten_truong']
            for nguon, entries in truong['rankings'].items():
                if nguon not in ranking_chart_data:
                    ranking_chart_data[nguon] = {}
                ranking_chart_data[nguon][ten_truong] = sorted(entries, key=lambda x: x['year'])

        # Chuẩn bị dữ liệu học phí
        tuition_chart_data = {}
        for truong in danh_sach_truong:
            ten_truong = truong['ten_truong']
            tuition_chart_data[ten_truong] = {}
            for program_name, majors in truong['programs'].items():
                for major in majors:
                    major_name = major['major']
                    tuition = major['tuition_fee']
                    if major_name not in tuition_chart_data[ten_truong]:
                        tuition_chart_data[ten_truong][major_name] = []
                    tuition_chart_data[ten_truong][major_name].append(tuition)

        
        
        
        context = {
            'danh_sach_truong': danh_sach_truong,
            'comparison_list': comparison_list,
            'comparison_count': len(comparison_list),
            'show_comparison_interface': len(comparison_list) > 0,
            'all_universities': list(all_universities),
            'common_majors': common_majors,  # FIX: Add common majors to context
            'ma_chuyen_nganh_chon': selected_major,  # Selected major
            'truong_duoc_chon': comparison_results,  # Comparison results
            'ket_qua_ai': ai_analysis,  # AI analysis
            'da_co_ket_qua': bool(comparison_results),  # Has comparison results
            'ten_chuyen_nganh': selected_major,  # Major name for display
            'ranking_chart_data': ranking_chart_data,
            'tuition_chart_data': tuition_chart_data,

        }
        
        return render(request, 'university_app/so_sanh.html', context)
        
    except Exception as e:
        logger.error(f"Lỗi trang so sánh: {str(e)}")
        messages.error(request, "Có lỗi xảy ra khi tải trang so sánh.")
        return render(request, 'university_app/so_sanh.html', {
            'danh_sach_truong': [],
            'comparison_list': [],
            'comparison_count': 0,
            'show_comparison_interface': False,
            'all_universities': [],
            'common_majors': [],
            'truong_duoc_chon': [],
            'ket_qua_ai': "",
            'da_co_ket_qua': False,
            'ten_chuyen_nganh': ""
        })

def chi_tiet_truong(request, ten_truong):
    """Trang chi tiết thông tin trường đại học"""
    try:
        # Decode URL
        ten_truong = unquote(ten_truong)
        
        # Get pagination and search parameters
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('search', '').strip()
        
        # Debug: Log the search
        logger.info(f"Searching for university: '{ten_truong}'")
        
        # Check if we have any universities in database
        total_universities = University.objects.count()
        logger.info(f"Total universities in database: {total_universities}")
        
        if total_universities == 0:
            logger.warning("Database has no universities!")
            messages.error(request, "Cơ sở dữ liệu chưa có dữ liệu trường đại học.")
            return render(request, 'university_app/loi.html', {
                'error_message': "Cơ sở dữ liệu chưa có dữ liệu trường đại học. Vui lòng liên hệ quản trị viên."
            })
        
        # Try to find university with exact name match
        try:
            university = University.objects.select_related('country').prefetch_related(
                'ranking_set__ranking_sources',
                'universityprogram_set__major',
                'universityprogram_set__program',
                'universityadmissionrequirement_set__criteria',
                'universityadmissionrequirement_set__program'
            ).get(name=ten_truong)
        except University.DoesNotExist:
            # Try to find with short_name
            try:
                university = University.objects.select_related('country').prefetch_related(
                    'ranking_set__ranking_sources',
                    'universityprogram_set__major',
                    'universityprogram_set__program',
                    'universityadmissionrequirement_set__criteria',
                    'universityadmissionrequirement_set__program'
                ).get(short_name=ten_truong)
            except University.DoesNotExist:
                # Log available universities for debugging
                available_universities = list(University.objects.values_list('name', flat=True)[:10])
                logger.error(f"University '{ten_truong}' not found. Available universities: {available_universities}")
                raise University.DoesNotExist(f"No University matches the query: {ten_truong}")
        
        # Lấy thông tin xếp hạng
        rankings = {}
        latest_rankings = {}
        
        for ranking in university.ranking_set.all():
            source_name = ranking.ranking_sources.name if ranking.ranking_sources else 'Unknown'
            
            if source_name not in rankings:
                rankings[source_name] = []
            
            rankings[source_name].append({
                'year': ranking.fyear,
                'rank': ranking.frank
            })
            
            # Lưu ranking mới nhất
            if source_name not in latest_rankings or ranking.fyear > latest_rankings[source_name]['year']:
                latest_rankings[source_name] = {
                    'year': ranking.fyear,
                    'rank': ranking.frank
                }
        
        # Sắp xếp rankings theo năm
        for source in rankings:
            rankings[source].sort(key=lambda x: x['year'], reverse=True)
        
        # Lấy best ranking theo thứ tự ưu tiên để hiển thị chính
        preferred_sources = ['QS', 'THE', 'ARWU']
        best_ranking_info = None
        
        for source in preferred_sources:
            if source in latest_rankings:
                best_ranking_info = {
                    'source': source,
                    'rank': latest_rankings[source]['rank'],
                    'year': latest_rankings[source]['year']
                }
                break
        
        # Nếu không có từ các nguồn ưu tiên, lấy cái đầu tiên
        if not best_ranking_info and latest_rankings:
            first_source = list(latest_rankings.keys())[0]
            best_ranking_info = {
                'source': first_source,
                'rank': latest_rankings[first_source]['rank'],
                'year': latest_rankings[first_source]['year']
            }
        
        # Lấy thông tin chương trình học với yêu cầu tuyển sinh
        programs = []
        programs_by_level = {}
        total_programs = 0
        average_tuition = 0
        total_tuition_count = 0
        
        # Get all programs for this university
        university_programs = university.universityprogram_set.all()
        
        # Apply search filter if search query exists
        if search_query:
            university_programs = university_programs.filter(
                Q(program__name__icontains=search_query) |
                Q(major__name__icontains=search_query) |
                Q(program__level__icontains=search_query)
            )
        
        for prog in university_programs:
            level = prog.program.level if prog.program and prog.program.level else 'Other'
            
            # Get admission requirements for this program
            program_requirements = []
            for req in university.universityadmissionrequirement_set.filter(program=prog.program):
                program_requirements.append({
                    'criteria': req.criteria.name if req.criteria else 'Unknown',
                    'value': req.value,
                    'unit': req.criteria.unit if req.criteria else ''
                })
            
            # Add to flattened list for template
            program_data = {
                'program_name': prog.program.name if prog.program else 'Unknown',
                'major_name': prog.major.name if prog.major else 'Unknown',
                'tuition_fee': prog.tuition_fee,
                'duration': prog.duration,
                'level': level,
                'requirements': program_requirements  # Add admission requirements
            }
            programs.append(program_data)
            
            # Calculate average tuition
            if prog.tuition_fee:
                average_tuition += prog.tuition_fee
                total_tuition_count += 1
            
            # Keep the by_level structure for other uses
            if level not in programs_by_level:
                programs_by_level[level] = []
            programs_by_level[level].append(program_data)
            total_programs += 1
        
        # Calculate final average tuition (based on all programs, not just search results)
        all_programs = university.universityprogram_set.all()
        all_tuitions = [p.tuition_fee for p in all_programs if p.tuition_fee]
        if all_tuitions:
            average_tuition = sum(all_tuitions) / len(all_tuitions)
        else:
            average_tuition = None
        
        # Add pagination for programs (2 per page)
        from django.core.paginator import Paginator
        paginator = Paginator(programs, 2)  # 2 programs per page
        page_obj = paginator.get_page(page_number)
        
        # Lấy yêu cầu tuyển sinh
        admission_requirements = {}
        
        for req in university.universityadmissionrequirement_set.all():
            program_name = req.program.name if req.program else 'General'
            
            if program_name not in admission_requirements:
                admission_requirements[program_name] = []
            
            admission_requirements[program_name].append({
                'criteria': req.criteria.name if req.criteria else 'Unknown',
                'value': req.value,
                'unit': req.criteria.unit if req.criteria else ''
            })
        
        # Chuẩn bị context
        context = {
            'university': {
                'ten_truong': university.name,
                'ten_viet_tat': university.short_name,
                'quoc_gia': university.country.name if university.country else 'Unknown',
                'nam_thanh_lap': university.founded_year,
                'website': university.website,
                'mo_ta': university.description
            },
            'xep_hang': latest_rankings,
            'best_ranking': best_ranking_info,  # Add best ranking for consistent display
            'lich_su_xep_hang': rankings,
            'chuong_trinh_hoc': programs_by_level,
            'programs': page_obj,  # FIX: Add paginated programs
            'tong_chuong_trinh': total_programs,
            'average_tuition': average_tuition,  # FIX: Add average tuition
            'yeu_cau_tuyen_sinh': admission_requirements,
            'has_pagination': paginator.num_pages > 1,  # Add pagination flag
            'search_query': search_query,  # Add search query for template
            'comparison_list': request.session.get('comparison_list', [])
        }
        
        return render(request, 'university_app/chi_tiet_truong.html', context)
        
    except University.DoesNotExist:
        messages.error(request, f"Không tìm thấy thông tin trường '{ten_truong}'")
        return render(request, 'university_app/loi.html', {
            'error_message': f"Không tìm thấy thông tin trường '{ten_truong}'"
        })
    except Exception as e:
        logger.error(f"Lỗi chi tiết trường: {str(e)}")
        messages.error(request, "Có lỗi xảy ra khi tải thông tin trường.")
        return render(request, 'university_app/loi.html', {
            'error_message': "Có lỗi xảy ra khi tải thông tin trường."
        })

def danh_sach_truong_api(request):
    """API trả về danh sách tên trường cho autocomplete"""
    try:
        universities = University.objects.values_list('name', flat=True).order_by('name')
        return JsonResponse(list(universities), safe=False)
    except Exception as e:
        logger.error(f"Lỗi API danh sách trường: {str(e)}")
        return JsonResponse([], safe=False)

def clear_comparison(request):
    """Xóa danh sách so sánh"""
    request.session['comparison_list'] = []
    messages.success(request, "Đã xóa danh sách so sánh.")
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'status': 'success'})
    else:
        # If not AJAX, redirect back to comparison page
        from django.shortcuts import redirect
        return redirect('university_app:so_sanh')

def toggle_comparison(request, university_name):
    """Thêm/xóa trường khỏi danh sách so sánh"""
    try:
        university_name = unquote(university_name)
        comparison_list = request.session.get('comparison_list', [])
        
        if university_name in comparison_list:
            comparison_list.remove(university_name)
            action = 'removed'
        else:
            if len(comparison_list) < 5:
                comparison_list.append(university_name)
                action = 'added'
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bạn chỉ có thể so sánh tối đa 5 trường.'
                })
        
        request.session['comparison_list'] = comparison_list
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'count': len(comparison_list)
        })
        
    except Exception as e:
        logger.error(f"Lỗi toggle comparison: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Có lỗi xảy ra.'
        })

def luu_ket_qua_so_sanh(request):
    """Lưu kết quả so sánh"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            tieu_de = data.get('tieu_de', 'So sánh trường đại học')
            ket_qua_ai = data.get('ket_qua_ai', '')
            
            # Lưu vào session hoặc database
            saved_comparisons = request.session.get('saved_comparisons', [])
            saved_comparisons.append({
                'tieu_de': tieu_de,
                'ket_qua_ai': ket_qua_ai,
                'thoi_gian': str(timezone.now())
            })
            request.session['saved_comparisons'] = saved_comparisons
            
            return JsonResponse({
                'success': True,
                'message': 'Đã lưu kết quả so sánh thành công!'
            })
        except Exception as e:
            logger.error(f"Lỗi lưu kết quả so sánh: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Có lỗi xảy ra khi lưu kết quả.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Phương thức không được hỗ trợ.'
    })
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    