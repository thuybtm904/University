import json
import requests
from django.conf import settings
from django.db.models import Q
from typing import List, Dict, Any
import logging
from ..models import University, UniversityProgram, UniversityAdmissionRequirement, Major, Country, Ranking

logger = logging.getLogger(__name__)

class AIAnalysisService:
    """Dịch vụ AI so sánh và tư vấn trường đại học"""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', 'your-openai-api-key-here')

    def so_sanh_truong_dai_hoc(self, danh_sach_truong: List[Dict], chuyen_nganh: str) -> Dict[str, Any]:
        """
        So sánh các trường đại học dựa trên chuyên ngành
        
        Args:
            danh_sach_truong: Danh sách trường để so sánh
            chuyen_nganh: Chuyên ngành cần so sánh
        
        Returns:
            Dict chứa kết quả so sánh, điểm số, và biểu đồ
        """
        try:
            # Lấy dữ liệu trường từ database
            truong_phu_hop = self._lay_du_lieu_truong_tu_db(danh_sach_truong, chuyen_nganh)
            
            # Chuẩn bị dữ liệu cho AI
            du_lieu_so_sanh = self._chuan_bi_du_lieu_so_sanh(chuyen_nganh, truong_phu_hop)
            
            # Gọi AI API (nếu có)
            if self.api_key and self.api_key != 'your-openai-api-key-here':
                ket_qua_ai = self._goi_openai_api(du_lieu_so_sanh)
            else:
                ket_qua_ai = self._so_sanh_mac_dinh(chuyen_nganh, truong_phu_hop)
            
            # Tính điểm cho các trường
            bang_diem = self._tinh_diem_truong(truong_phu_hop)
            
            # Tạo dữ liệu biểu đồ
            ket_qua_bieu_do = self._tao_du_lieu_bieu_do(bang_diem)
            
            return {
                'ket_qua_ai': ket_qua_ai,
                'bang_diem': bang_diem,
                'ket_qua_bieu_do': ket_qua_bieu_do,
                'truong_tot_nhat': self._tim_truong_tot_nhat(bang_diem),
                'khuyen_nghi': self._tao_khuyen_nghi(chuyen_nganh, bang_diem),
                'truong_duoc_chon': truong_phu_hop,
                'ten_chuyen_nganh': chuyen_nganh
            }
            
        except Exception as e:
            logger.error(f"Lỗi trong quá trình so sánh: {str(e)}")
            return self._ket_qua_mac_dinh(chuyen_nganh)

    def _lay_du_lieu_truong_tu_db(self, danh_sach_truong: List[Dict], chuyen_nganh: str) -> List[Dict]:
        """Lấy dữ liệu trường từ database dựa trên danh sách trường và chuyên ngành"""
        truong_phu_hop = []
        for truong in danh_sach_truong:
            ten_truong = truong.get('ten_truong', '').lower().strip()
            university = University.objects.filter(name__icontains=ten_truong).first()
            if not university:
                continue
            
            # Lấy chương trình phù hợp với chuyên ngành
            university_program = UniversityProgram.objects.filter(
                university=university,
                major__name__icontains=chuyen_nganh
            ).first()
            if not university_program:
                continue
            
            # Lấy yêu cầu tuyển sinh
            yeu_cau_tuyen_sinh = {}
            requirements = UniversityAdmissionRequirement.objects.filter(
                university=university,
                program=university_program.program
            )
            for req in requirements:
                yeu_cau_tuyen_sinh[req.criteria.name] = req.value
            
            # Lấy xếp hạng mới nhất
            xep_hang = Ranking.objects.filter(university=university).order_by('-fyear').first()
            
            truong_data = {
                'ten_truong': university.name,
                'quoc_gia': university.country.name if university.country else 'N/A',
                'xep_hang_the_gioi': xep_hang.frank if xep_hang else 0,
                'hoc_phi': university_program.tuition_fee or 0,
                'nam_thanh_lap': university.founded_year or 0,
                'thoi_gian_hoc': university_program.duration or 'N/A',
                'cap_do': university_program.program.level or 'N/A',
                'yeu_cau_tuyen_sinh': yeu_cau_tuyen_sinh,
                'website': university.website or '',
                'ty_le_chap_nhan': truong.get('ty_le_chap_nhan', 0),  # Lấy từ input hoặc mặc định
                'co_hoc_bong': truong.get('co_hoc_bong', False)  # Lấy từ input hoặc mặc định
            }
            truong_phu_hop.append(truong_data)
        
        return truong_phu_hop

    def _chuan_bi_du_lieu_so_sanh(self, chuyen_nganh: str, truong_phu_hop: List[Dict]) -> str:
        """Chuẩn bị dữ liệu để gửi cho AI"""
        prompt = f"""
        Bạn là chuyên gia so sánh giáo dục quốc tế. Dựa trên chuyên ngành '{chuyen_nganh}', hãy so sánh các trường đại học sau:

        """
        for i, truong in enumerate(truong_phu_hop, 1):
            prompt += f"""
        Trường {i}: {truong.get('ten_truong', 'N/A')}
        - Quốc gia: {truong.get('quoc_gia', 'N/A')}
        - Xếp hạng thế giới: {truong.get('xep_hang_the_gioi', 'N/A')}
        - Học phí: {truong.get('hoc_phi', 'N/A')} USD/năm
        - Năm thành lập: {truong.get('nam_thanh_lap', 'N/A')}
        - Thời gian học: {truong.get('thoi_gian_hoc', 'N/A')}
        - Cấp độ: {truong.get('cap_do', 'N/A')}
        - Yêu cầu tuyển sinh: {', '.join([f'{k}: {v}' for k, v in truong.get('yeu_cau_tuyen_sinh', {}).items()]) or 'N/A'}
        - Tỷ lệ chấp nhận: {truong.get('ty_le_chap_nhan', 'N/A')}%
        - Có học bổng: {truong.get('co_hoc_bong', 'Không')}
        - Website: {truong.get('website', 'N/A')}
        """
        
        prompt += """
        Hãy đưa ra:
        1. So sánh chi tiết từng trường dựa trên các tiêu chí trên
        2. Xác định trường tốt nhất cho chuyên ngành và lý do
        3. Gợi ý hành động để chuẩn bị hồ sơ ứng tuyển
        Trả lời bằng tiếng Việt một cách chi tiết và khách quan.
        """
        return prompt

    def _goi_openai_api(self, prompt: str) -> str:
        """Gọi OpenAI API để so sánh"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'Bạn là chuyên gia so sánh giáo dục quốc tế.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"Lỗi API OpenAI: {response.status_code}")
                return self._so_sanh_mac_dinh('', [])
        except Exception as e:
            logger.error(f"Lỗi gọi OpenAI API: {str(e)}")
            return self._so_sanh_mac_dinh('', [])

    def _so_sanh_mac_dinh(self, chuyen_nganh: str, truong_phu_hop: List[Dict]) -> str:
        """So sánh mặc định khi không có API"""
        if not truong_phu_hop:
            return """
            <div class='alert alert-warning'>
                Không có trường nào để so sánh. Vui lòng chọn ít nhất 2 trường.
            </div>
            """
        
        so_sanh = f"""
        <div class='ai-consultation'>
            <h3>🎓 So sánh trường - Chuyên ngành: {chuyen_nganh}</h3>
            <div class='overview mb-4'>
                <h4>📊 Tổng quan:</h4>
                <p>So sánh <strong>{len(truong_phu_hop)} trường</strong> cho chuyên ngành {chuyen_nganh}.</p>
            </div>
            <div class='detailed-consultation mb-4'>
                <h4>🏆 So sánh chi tiết:</h4>
        """
        
        for truong in truong_phu_hop:
            uu_diem = []
            nhuoc_diem = []
            if truong.get('xep_hang_the_gioi', 0) <= 100:
                uu_diem.append("Xếp hạng cao trên thế giới")
            if truong.get('hoc_phi', 0) <= 30000:
                uu_diem.append("Học phí thấp")
            if truong.get('ty_le_chap_nhan', 0) >= 30:
                uu_diem.append("Tỷ lệ chấp nhận cao")
            if truong.get('co_hoc_bong', False):
                uu_diem.append("Có cơ hội nhận học bổng")
            if truong.get('xep_hang_the_gioi', 0) > 200:
                nhuoc_diem.append("Xếp hạng không quá cao")
            if truong.get('hoc_phi', 0) > 50000:
                nhuoc_diem.append("Học phí cao")
            
            so_sanh += f"""
            <div class='truong-consultation mb-4'>
                <h5>🏫 {truong.get('ten_truong', 'N/A')}</h5>
                <div class='row'>
                    <div class='col-md-6'>
                        <strong>✅ Ưu điểm:</strong>
                        <ul>
                            {''.join([f'<li>{uu}</li>' for uu in uu_diem]) if uu_diem else '<li>Không xác định</li>'}
                        </ul>
                    </div>
                    <div class='col-md-6'>
                        <strong>⚠️ Nhược điểm:</strong>
                        <ul>
                            {''.join([f'<li>{nhuoc}</li>' for nhuoc in nhuoc_diem]) if nhuoc_diem else '<li>Không đáng kể</li>'}
                        </ul>
                    </div>
                </div>
            </div>
            """
        
        so_sanh += """
            </div>
            <div class='recommendations'>
                <h4>💡 Lưu ý:</h4>
                <div class='alert alert-info'>
                    Đây là so sánh tự động. Để có đánh giá chính xác hơn, hãy tham khảo ý kiến chuyên gia giáo dục.
                </div>
            </div>
        </div>
        """
        return so_sanh

    def _tinh_diem_truong(self, truong_phu_hop: List[Dict]) -> Dict:
        """Tính điểm so sánh cho từng trường"""
        bang_diem = {}
        for truong in truong_phu_hop:
            ten_truong = truong.get('ten_truong', 'N/A')
            diem_xep_hang = self._tinh_diem_xep_hang(truong.get('xep_hang_the_gioi', 0))
            diem_hoc_phi = self._tinh_diem_hoc_phi(truong.get('hoc_phi', 0))
            diem_ty_le = self._tinh_diem_ty_le(truong.get('ty_le_chap_nhan', 0))
            diem_hoc_bong = 10 if truong.get('co_hoc_bong', False) else 0
            
            diem_tong = (
                diem_xep_hang * 0.4 +
                diem_hoc_phi * 0.3 +
                diem_ty_le * 0.2 +
                diem_hoc_bong * 0.1
            )
            
            bang_diem[ten_truong] = {
                'diem_tong': round(diem_tong, 2),
                'diem_xep_hang': diem_xep_hang,
                'diem_hoc_phi': diem_hoc_phi,
                'diem_ty_le': diem_ty_le,
                'diem_hoc_bong': diem_hoc_bong,
                'xep_loai': self._xep_loai_truong(diem_tong)
            }
        
        return bang_diem

    def _tinh_diem_xep_hang(self, xep_hang: int) -> float:
        if not xep_hang or xep_hang <= 0:
            return 0
        elif xep_hang <= 10:
            return 100
        elif xep_hang <= 50:
            return 90
        elif xep_hang <= 100:
            return 80
        elif xep_hang <= 200:
            return 70
        elif xep_hang <= 500:
            return 60
        else:
            return 40

    def _tinh_diem_hoc_phi(self, hoc_phi: float) -> float:
        if not hoc_phi or hoc_phi <= 0:
            return 0
        elif hoc_phi <= 20000:
            return 100
        elif hoc_phi <= 30000:
            return 85
        elif hoc_phi <= 40000:
            return 70
        elif hoc_phi <= 50000:
            return 50
        else:
            return 30

    def _tinh_diem_ty_le(self, ty_le: float) -> float:
        if not ty_le or ty_le <= 0:
            return 0
        elif ty_le >= 80:
            return 100
        elif ty_le >= 60:
            return 85
        elif ty_le >= 40:
            return 70
        elif ty_le >= 20:
            return 50
        else:
            return 30

    def _xep_loai_truong(self, diem_tong: float) -> str:
        if diem_tong >= 85:
            return "Xuất sắc"
        elif diem_tong >= 75:
            return "Tốt"
        elif diem_tong >= 65:
            return "Khá"
        elif diem_tong >= 50:
            return "Trung bình"
        else:
            return "Kém"

    def _tao_du_lieu_bieu_do(self, bang_diem: Dict) -> Dict:
        """Tạo dữ liệu cho biểu đồ so sánh"""
        labels = list(bang_diem.keys())
        bar_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Điểm So Sánh',
                    'data': [bang_diem.get(label, {}).get('diem_tong', 0) for label in labels],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                    ]
                }
            ]
        }
        return {'bar': bar_data}

    def _tim_truong_tot_nhat(self, bang_diem: Dict) -> Dict:
        if not bang_diem:
            return {}
        truong_tot_nhat = max(bang_diem.items(), key=lambda x: x[1]['diem_tong'])
        return {
            'ten_truong': truong_tot_nhat[0],
            'diem_tong': truong_tot_nhat[1]['diem_tong'],
            'xep_loai': truong_tot_nhat[1]['xep_loai']
        }

    def _tao_khuyen_nghi(self, chuyen_nganh: str, bang_diem: Dict) -> List[str]:
        khuyen_nghi = []
        if not bang_diem:
            khuyen_nghi.append("Không có trường nào để so sánh. Vui lòng chọn ít nhất 2 trường.")
            return khuyen_nghi
        
        truong_sap_xep = sorted(bang_diem.items(), key=lambda x: x[1]['diem_tong'], reverse=True)
        truong_dau = truong_sap_xep[0]
        khuyen_nghi.append(
            f"🏆 {truong_dau[0]} là lựa chọn tốt nhất cho chuyên ngành {chuyen_nganh} với điểm {truong_dau[1]['diem_tong']}/100 ({truong_dau[1]['xep_loai']})."
        )
        khuyen_nghi.append("💡 Xem xét yêu cầu tuyển sinh của các trường để chuẩn bị hồ sơ phù hợp.")
        return khuyen_nghi

    def _ket_qua_mac_dinh(self, chuyen_nganh: str) -> Dict:
        return {
            'ket_qua_ai': "Không thể thực hiện so sánh do lỗi. Vui lòng thử lại.",
            'bang_diem': {},
            'ket_qua_bieu_do': {'bar': {'labels': [], 'datasets': []}},
            'truong_tot_nhat': {},
            'khuyen_nghi': ["Không có đủ dữ liệu để so sánh."],
            'truong_duoc_chon': [],
            'ten_chuyen_nganh': chuyen_nganh
        }