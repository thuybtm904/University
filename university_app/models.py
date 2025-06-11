from django.db import models

class Country(models.Model):
    """Model cho countries table với primary key"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Tên quốc gia")
    
    class Meta:
        db_table = 'countries'
        managed = False  # Django không quản lý table structure
        verbose_name = "Quốc gia"
        verbose_name_plural = "Quốc gia"
        
    def __str__(self):
        return self.name

class University(models.Model):
    """Model cho universities table với foreign key"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Tên trường")
    short_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên viết tắt")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='country_id', verbose_name="Quốc gia")
    founded_year = models.IntegerField(blank=True, null=True, verbose_name="Năm thành lập")
    website = models.CharField(max_length=255, blank=True, null=True, verbose_name="Website")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    
    class Meta:
        db_table = 'universities'
        managed = False
        verbose_name = "Trường đại học"
        verbose_name_plural = "Trường đại học"
        
    def __str__(self):
        return self.name

class RankingSource(models.Model):
    """Model cho ranking_sources table"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Tên nguồn xếp hạng")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    
    class Meta:
        db_table = 'ranking_sources'
        managed = False
        verbose_name = "Nguồn xếp hạng"
        verbose_name_plural = "Nguồn xếp hạng"
        
    def __str__(self):
        return self.name

class Ranking(models.Model):
    """Model cho rankings table với foreign keys"""
    id = models.AutoField(primary_key=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, db_column='university_id', verbose_name="Trường đại học")
    ranking_sources = models.ForeignKey(RankingSource, on_delete=models.CASCADE, db_column='ranking_sources_id', verbose_name="Nguồn xếp hạng")
    fyear = models.IntegerField(verbose_name="Năm xếp hạng")
    frank = models.IntegerField(verbose_name="Thứ hạng")
    
    class Meta:
        db_table = 'rankings'
        managed = False
        verbose_name = "Xếp hạng"
        verbose_name_plural = "Xếp hạng"
        
    def __str__(self):
        return f"{self.university.name} - #{self.frank} ({self.fyear})"

class Program(models.Model):
    """Model cho programs table"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Tên chương trình")
    level = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cấp độ")
    
    class Meta:
        db_table = 'programs'
        managed = False
        verbose_name = "Chương trình học"
        verbose_name_plural = "Chương trình học"
        
    def __str__(self):
        return f"{self.name} ({self.level})" if self.level else self.name

class Major(models.Model):
    """Model cho majors table"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Tên chuyên ngành")
    
    class Meta:
        db_table = 'majors'
        managed = False
        verbose_name = "Chuyên ngành"
        verbose_name_plural = "Chuyên ngành"
        
    def __str__(self):
        return self.name

class UniversityProgram(models.Model):
    """Model cho university_programs table với foreign keys"""
    id = models.AutoField(primary_key=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, db_column='university_id', verbose_name="Trường đại học")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, db_column='program_id', verbose_name="Chương trình học")
    major = models.ForeignKey(Major, on_delete=models.CASCADE, db_column='major_id', verbose_name="Chuyên ngành")
    tuition_fee = models.FloatField(blank=True, null=True, verbose_name="Học phí")
    duration = models.CharField(max_length=255, blank=True, null=True, verbose_name="Thời gian học")
    
    class Meta:
        db_table = 'university_programs'
        managed = False
        verbose_name = "Chương trình trường"
        verbose_name_plural = "Chương trình trường"
        
    def __str__(self):
        return f"{self.university.name} - {self.major.name}"

class Criteria(models.Model):
    """Model cho criteria table"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Tên tiêu chí")
    unit = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đơn vị")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    
    class Meta:
        db_table = 'criteria'
        managed = False
        verbose_name = "Tiêu chí"
        verbose_name_plural = "Tiêu chí"
        
    def __str__(self):
        return self.name

class UniversityAdmissionRequirement(models.Model):
    """Model cho university_admission_requirements table với foreign keys"""
    id = models.AutoField(primary_key=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, db_column='university_id', verbose_name="Trường đại học")
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE, db_column='criteria_id', verbose_name="Tiêu chí")
    value = models.CharField(max_length=255, blank=True, null=True, verbose_name="Giá trị yêu cầu")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, db_column='program_id', blank=True, null=True, verbose_name="Chương trình học")
    
    class Meta:
        db_table = 'university_admission_requirements'
        managed = False
        verbose_name = "Yêu cầu tuyển sinh"
        verbose_name_plural = "Yêu cầu tuyển sinh"
        
    def __str__(self):
        return f"{self.university.name} - {self.criteria.name}: {self.value}"

# Legacy aliases để tương thích ngược
QuocGia = Country
TruongDaiHoc = University
ChuyenNganh = Major
YeuCauTuyenSinh = UniversityAdmissionRequirement