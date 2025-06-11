from django.contrib import admin
from .models import (
    Country, University, Major, Program, Criteria, 
    RankingSource, Ranking, UniversityAdmissionRequirement,
    UniversityProgram
)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name', 'country', 'founded_year')
    list_filter = ('country', 'founded_year')
    search_fields = ('name', 'short_name', 'description')
    ordering = ('name',)
    raw_id_fields = ('country',)
    list_per_page = 25

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'level')
    list_filter = ('level',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(RankingSource)
class RankingSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('id', 'university', 'ranking_sources', 'fyear', 'frank')
    list_filter = ('fyear', 'ranking_sources')
    search_fields = ('university__name', 'ranking_sources__name')
    ordering = ('fyear', 'frank')
    raw_id_fields = ('university', 'ranking_sources')
    list_per_page = 25

@admin.register(UniversityAdmissionRequirement)
class UniversityAdmissionRequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'university', 'criteria', 'value', 'program')
    list_filter = ('criteria', 'program')
    search_fields = ('university__name', 'criteria__name')
    ordering = ('id',)
    raw_id_fields = ('university', 'criteria', 'program')
    list_per_page = 25
    list_select_related = ('university', 'criteria', 'program')

@admin.register(UniversityProgram)
class UniversityProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'university', 'program', 'major', 'tuition_fee', 'duration')
    list_filter = ('program', 'major')
    search_fields = ('university__name', 'major__name', 'program__name')
    ordering = ('id',)
    raw_id_fields = ('university', 'program', 'major')
    list_per_page = 25
    list_select_related = ('university', 'program', 'major') 
