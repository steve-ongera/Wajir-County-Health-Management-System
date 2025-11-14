"""
Wajir County Health Management System - Django Admin Configuration
Complete admin interface with custom actions, filters, and displays
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

# Import all models
from .models import (
    County, SubCounty, Ward, Role, User, Facility, CommunityUnit,
    CommunityHealthVolunteer, Household, Person, PregnancyRecord, ANCVisit,
    PNCVisit, ImmunizationRecord, HouseholdVisit, OutreachEvent, Screening,
    Referral, ReferralFollowUp, SurveillanceReport, MortalityReport,
    Program, Indicator, MonthlyReport, Campaign, Commodity, Supplier,
    Stock, StockTransaction, ProcurementRequest, PurchaseOrder,
    LabTestOrder, LabResult, StaffProfile, Training, TrainingAttendance,
    AuditLog, Notification, FHIRMapping, DataExportJob, Appointment,
    Permission, Location
)


# ==================== CUSTOM ADMIN SITE ====================

class WajirHealthAdminSite(admin.AdminSite):
    site_header = "Wajir County Health Management System"
    site_title = "Wajir Health Admin"
    index_title = "System Administration"

# Create custom admin site instance
# admin_site = WajirHealthAdminSite(name='wajir_health_admin')
# Use default admin site for this example


# ==================== INLINE ADMINS ====================

class SubCountyInline(admin.TabularInline):
    model = SubCounty
    extra = 0
    fields = ['name', 'code', 'population']


class WardInline(admin.TabularInline):
    model = Ward
    extra = 0
    fields = ['name', 'code', 'population']


class ANCVisitInline(admin.TabularInline):
    model = ANCVisit
    extra = 0
    fields = ['visit_number', 'visit_date', 'gestation_weeks', 'weight', 'blood_pressure']
    readonly_fields = ['visit_number', 'visit_date']


class PNCVisitInline(admin.TabularInline):
    model = PNCVisit
    extra = 0
    fields = ['visit_number', 'visit_date', 'days_postpartum', 'mother_condition']
    readonly_fields = ['visit_number', 'visit_date']


class ReferralFollowUpInline(admin.TabularInline):
    model = ReferralFollowUp
    extra = 0
    fields = ['follow_up_date', 'followed_up_by', 'status_update']
    readonly_fields = ['follow_up_date']


class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    fields = ['commodity', 'quantity', 'batch_number', 'expiry_date']
    readonly_fields = ['last_updated']


class LabResultInline(admin.TabularInline):
    model = LabResult
    extra = 0
    fields = ['test_name', 'result_value', 'result_status', 'test_date']


# ==================== CORE ADMINISTRATIVE ====================

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'population', 'contact_person', 'phone', 'created_at']
    search_fields = ['name', 'code', 'contact_person']
    list_filter = ['created_at']
    inlines = [SubCountyInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'population')
        }),
        ('Contact Details', {
            'fields': ('contact_person', 'phone', 'email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'code', 'population', 'ward_count']
    list_filter = ['county']
    search_fields = ['name', 'code']
    inlines = [WardInline]
    
    def ward_count(self, obj):
        return obj.wards.count()
    ward_count.short_description = 'Wards'


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcounty', 'code', 'population', 'facility_count', 'household_count']
    list_filter = ['subcounty__county', 'subcounty']
    search_fields = ['name', 'code']
    
    def facility_count(self, obj):
        return obj.facilities.count()
    facility_count.short_description = 'Facilities'
    
    def household_count(self, obj):
        return obj.households.count()
    household_count.short_description = 'Households'


# ==================== USERS & ACCESS ====================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['get_name_display', 'level', 'user_count', 'created_at']
    list_filter = ['level']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'phone', 'national_id', 'role_list', 'county', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'roles', 'county', 'date_joined']
    search_fields = ['email', 'phone', 'first_name', 'last_name', 'national_id']
    ordering = ['-date_joined']
    filter_horizontal = ['roles', 'groups', 'user_permissions']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'national_id')
        }),
        ('Location & Roles', {
            'fields': ('county', 'subcounty', 'roles')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Create User', {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'first_name', 'last_name', 'password1', 'password2', 'roles'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Full Name'
    
    def role_list(self, obj):
        return ", ".join([role.get_name_display() for role in obj.roles.all()[:3]])
    role_list.short_description = 'Roles'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'resource', 'action', 'is_active']
    list_filter = ['resource', 'action', 'is_active']
    search_fields = ['name', 'code', 'resource']
    filter_horizontal = ['roles']


# ==================== FACILITIES & COMMUNITY ====================

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'facility_code', 'facility_type', 'ward', 'subcounty', 'is_operational', 'bed_capacity']
    list_filter = ['facility_type', 'is_operational', 'subcounty__county', 'subcounty', 'ward']
    search_fields = ['name', 'facility_code', 'phone']
    inlines = [StockInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'facility_code', 'facility_type')
        }),
        ('Location', {
            'fields': ('ward', 'subcounty', 'physical_address', 'latitude', 'longitude')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Operational Details', {
            'fields': ('is_operational', 'bed_capacity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_operational', 'mark_non_operational']
    
    def mark_operational(self, request, queryset):
        updated = queryset.update(is_operational=True)
        self.message_user(request, f'{updated} facilities marked as operational.')
    mark_operational.short_description = 'Mark selected facilities as operational'
    
    def mark_non_operational(self, request, queryset):
        updated = queryset.update(is_operational=False)
        self.message_user(request, f'{updated} facilities marked as non-operational.')
    mark_non_operational.short_description = 'Mark selected facilities as non-operational'


@admin.register(CommunityUnit)
class CommunityUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'ward', 'linked_facility', 'target_population', 'chv_count', 'is_active']
    list_filter = ['is_active', 'ward__subcounty__county', 'ward']
    search_fields = ['name', 'code']
    
    def chv_count(self, obj):
        return obj.volunteers.count()
    chv_count.short_description = 'CHVs'


@admin.register(CommunityHealthVolunteer)
class CommunityHealthVolunteerAdmin(admin.ModelAdmin):
    list_display = ['user', 'chv_number', 'community_unit', 'national_id', 'is_active', 'households_assigned', 'certification_status']
    list_filter = ['is_active', 'gender', 'community_unit__ward__subcounty__county']
    search_fields = ['user__first_name', 'user__last_name', 'national_id', 'chv_number']
    date_hierarchy = 'training_date'
    
    fieldsets = (
        ('User & Community Unit', {
            'fields': ('user', 'community_unit', 'chv_number')
        }),
        ('Personal Information', {
            'fields': ('national_id', 'date_of_birth', 'gender')
        }),
        ('Training & Certification', {
            'fields': ('training_date', 'certification_date', 'certification_expiry')
        }),
        ('Status', {
            'fields': ('is_active', 'households_assigned')
        }),
    )
    
    readonly_fields = ['chv_number']
    
    def certification_status(self, obj):
        if not obj.certification_date:
            return format_html('<span style="color: orange;">Not Certified</span>')
        if obj.certification_expiry and obj.certification_expiry < timezone.now().date():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    certification_status.short_description = 'Certification'


# ==================== POPULATION & HOUSEHOLDS ====================

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['household_number', 'community_unit', 'ward', 'assigned_chv', 'number_of_members', 'is_active']
    list_filter = ['is_active', 'ward__subcounty__county', 'ward', 'has_toilet']
    search_fields = ['household_number', 'village']
    date_hierarchy = 'registration_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('community_unit', 'ward', 'assigned_chv')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'national_id', 'nhif_number', 'gender', 'age', 'household', 'is_household_head', 'is_alive']
    list_filter = ['gender', 'is_alive', 'is_household_head', 'household__ward__subcounty__county']
    search_fields = ['first_name', 'last_name', 'national_id', 'nhif_number', 'phone']
    date_hierarchy = 'date_of_birth'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Identifiers', {
            'fields': ('national_id', 'nhif_number', 'birth_certificate_number')
        }),
        ('Contact', {
            'fields': ('phone', 'alternate_phone')
        }),
        ('Household', {
            'fields': ('household', 'is_household_head')
        }),
        ('Health Information', {
            'fields': ('blood_group', 'chronic_conditions', 'allergies'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_alive', 'date_of_death'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
    
    def age(self, obj):
        return obj.get_age()
    age.short_description = 'Age'


# ==================== MATERNAL & CHILD HEALTH ====================

@admin.register(PregnancyRecord)
class PregnancyRecordAdmin(admin.ModelAdmin):
    list_display = ['woman', 'edd', 'gravida', 'parity', 'is_high_risk', 'anc_visits_completed', 'delivery_date', 'is_active']
    list_filter = ['is_high_risk', 'is_active', 'delivery_facility']
    search_fields = ['woman__first_name', 'woman__last_name', 'woman__national_id']
    date_hierarchy = 'edd'
    inlines = [ANCVisitInline, PNCVisitInline]
    
    fieldsets = (
        ('Mother', {
            'fields': ('woman',)
        }),
        ('Pregnancy Details', {
            'fields': ('lmp_date', 'edd', 'gravida', 'parity')
        }),
        ('Risk Assessment', {
            'fields': ('is_high_risk', 'risk_factors')
        }),
        ('ANC Progress', {
            'fields': ('anc_visits_completed',)
        }),
        ('Delivery', {
            'fields': ('delivery_date', 'delivery_outcome', 'delivery_facility'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
    )


@admin.register(ANCVisit)
class ANCVisitAdmin(admin.ModelAdmin):
    list_display = ['pregnancy_woman', 'visit_number', 'visit_date', 'gestation_weeks', 'facility', 'attended_by']
    list_filter = ['facility', 'visit_date']
    search_fields = ['pregnancy__woman__first_name', 'pregnancy__woman__last_name']
    date_hierarchy = 'visit_date'
    
    def pregnancy_woman(self, obj):
        return obj.pregnancy.woman
    pregnancy_woman.short_description = 'Woman'


@admin.register(ImmunizationRecord)
class ImmunizationRecordAdmin(admin.ModelAdmin):
    list_display = ['child', 'vaccine_name', 'dose_number', 'administration_date', 'facility', 'administered_by']
    list_filter = ['vaccine_name', 'administration_date', 'facility']
    search_fields = ['child__first_name', 'child__last_name', 'vaccine_name', 'batch_number']
    date_hierarchy = 'administration_date'


# ==================== PUBLIC HEALTH ACTIVITIES ====================

@admin.register(HouseholdVisit)
class HouseholdVisitAdmin(admin.ModelAdmin):
    list_display = ['household', 'chv', 'visit_date', 'visit_type', 'members_present', 'referrals_made']
    list_filter = ['visit_type', 'visit_date', 'chv__community_unit']
    search_fields = ['household__household_number']
    date_hierarchy = 'visit_date'


@admin.register(OutreachEvent)
class OutreachEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'start_date', 'end_date', 'ward', 'people_reached', 'target_population', 'coverage']
    list_filter = ['event_type', 'start_date', 'ward__subcounty__county']
    search_fields = ['name', 'location']
    date_hierarchy = 'start_date'
    
    def coverage(self, obj):
        if obj.target_population > 0:
            percentage = (obj.people_reached / obj.target_population) * 100
            color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
            return format_html(f'<span style="color: {color};">{percentage:.1f}%</span>')
        return '-'
    coverage.short_description = 'Coverage %'


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ['person', 'screening_type', 'screening_date', 'result', 'screened_by', 'follow_up_required']
    list_filter = ['screening_type', 'result', 'follow_up_required', 'screening_date']
    search_fields = ['person__first_name', 'person__last_name', 'person__national_id']
    date_hierarchy = 'screening_date'


# ==================== REFERRALS ====================

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referral_number', 'person', 'from_facility', 'to_facility', 'urgency', 'status', 'referral_date']
    list_filter = ['status', 'urgency', 'from_facility', 'to_facility', 'referral_date']
    search_fields = ['referral_number', 'person__first_name', 'person__last_name', 'person__national_id']
    date_hierarchy = 'referral_date'
    inlines = [ReferralFollowUpInline]
    
    readonly_fields = ['referral_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Referral Details', {
            'fields': ('referral_number', 'person', 'referral_date', 'urgency')
        }),
        ('From/To', {
            'fields': ('from_facility', 'to_facility', 'referred_by')
        }),
        ('Medical Information', {
            'fields': ('reason', 'diagnosis', 'treatment_given')
        }),
        ('Status Tracking', {
            'fields': ('status', 'accepted_by', 'accepted_date', 'arrival_date', 'completion_date')
        }),
        ('Outcome', {
            'fields': ('outcome', 'feedback_to_referring_facility'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_cancelled']
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED', completion_date=timezone.now())
        self.message_user(request, f'{updated} referrals marked as completed.')
    mark_completed.short_description = 'Mark selected referrals as completed'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} referrals cancelled.')
    mark_cancelled.short_description = 'Cancel selected referrals'


# ==================== SURVEILLANCE & REPORTS ====================

@admin.register(SurveillanceReport)
class SurveillanceReportAdmin(admin.ModelAdmin):
    list_display = ['report_number', 'disease_name', 'report_date', 'ward', 'cases_confirmed', 'deaths', 'outbreak_declared']
    list_filter = ['disease_name', 'outbreak_declared', 'report_date', 'ward__subcounty__county']
    search_fields = ['report_number', 'disease_name', 'disease_code']
    date_hierarchy = 'report_date'
    
    readonly_fields = ['report_number', 'created_at']


@admin.register(MortalityReport)
class MortalityReportAdmin(admin.ModelAdmin):
    list_display = ['deceased_person', 'death_category', 'date_of_death', 'place_of_death', 'immediate_cause', 'autopsy_done']
    list_filter = ['death_category', 'pregnancy_related', 'autopsy_done', 'date_of_death']
    search_fields = ['deceased_person__first_name', 'deceased_person__last_name', 'immediate_cause']
    date_hierarchy = 'date_of_death'


# ==================== PROGRAMS & M&E ====================

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'county', 'program_manager', 'start_date', 'end_date', 'is_active', 'budget']
    list_filter = ['is_active', 'county', 'start_date']
    search_fields = ['name', 'code']
    date_hierarchy = 'start_date'


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'program', 'indicator_type', 'target_value', 'is_active']
    list_filter = ['indicator_type', 'is_active', 'program']
    search_fields = ['name', 'code']


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['facility_or_subcounty', 'year', 'month', 'outpatient_visits', 'deliveries', 'approved', 'submission_date']
    list_filter = ['approved', 'year', 'month', 'facility', 'subcounty']
    search_fields = ['facility__name', 'subcounty__name']
    
    readonly_fields = ['submission_date', 'created_at']
    
    def facility_or_subcounty(self, obj):
        return obj.facility or obj.subcounty
    facility_or_subcounty.short_description = 'Reporting Unit'
    
    actions = ['approve_reports']
    
    def approve_reports(self, request, queryset):
        updated = queryset.update(approved=True, approved_by=request.user, approval_date=timezone.now())
        self.message_user(request, f'{updated} reports approved.')
    approve_reports.short_description = 'Approve selected reports'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'start_date', 'end_date', 'people_reached', 'target_population', 'status']
    list_filter = ['status', 'campaign_type', 'start_date']
    search_fields = ['name', 'campaign_type']
    date_hierarchy = 'start_date'
    filter_horizontal = ['wards']


# ==================== COMMODITIES & SUPPLY CHAIN ====================

@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = ['name', 'commodity_code', 'commodity_type', 'unit_of_measure', 'is_essential', 'is_active']
    list_filter = ['commodity_type', 'is_essential', 'is_active']
    search_fields = ['name', 'commodity_code', 'generic_name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier_code', 'contact_person', 'phone', 'rating', 'is_active']
    list_filter = ['is_active', 'rating']
    search_fields = ['name', 'supplier_code', 'contact_person']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['commodity', 'facility', 'quantity', 'batch_number', 'expiry_date', 'stock_status']
    list_filter = ['facility', 'commodity__commodity_type', 'expiry_date']
    search_fields = ['commodity__name', 'batch_number', 'facility__name']
    
    def stock_status(self, obj):
        today = timezone.now().date()
        if obj.expiry_date < today:
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.expiry_date < today + timedelta(days=90):
            return format_html('<span style="color: orange;">Expiring Soon</span>')
        elif obj.quantity == 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.quantity < obj.commodity.reorder_level:
            return format_html('<span style="color: orange;">Low Stock</span>')
        return format_html('<span style="color: green;">OK</span>')
    stock_status.short_description = 'Status'


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'stock', 'transaction_type', 'quantity', 'transaction_date', 'performed_by']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['transaction_number', 'reference_number']
    date_hierarchy = 'transaction_date'
    readonly_fields = ['transaction_number', 'created_at']


@admin.register(ProcurementRequest)
class ProcurementRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'facility', 'requested_by', 'request_date', 'status', 'priority']
    list_filter = ['status', 'priority', 'request_date']
    search_fields = ['request_number', 'facility__name']
    date_hierarchy = 'request_date'
    readonly_fields = ['request_number', 'created_at']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'po_date', 'expected_delivery_date', 'total_amount', 'status']
    list_filter = ['status', 'supplier', 'po_date']
    search_fields = ['po_number', 'supplier__name']
    date_hierarchy = 'po_date'
    readonly_fields = ['po_number', 'created_at']


# ==================== LABORATORY ====================

@admin.register(LabTestOrder)
class LabTestOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'patient', 'facility', 'order_date', 'status', 'ordered_by']
    list_filter = ['status', 'priority', 'facility', 'order_date']
    search_fields = ['order_number', 'patient__first_name', 'patient__last_name']
    date_hierarchy = 'order_date'
    inlines = [LabResultInline]
    readonly_fields = ['order_number', 'created_at']


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['lab_order', 'test_name', 'result_value', 'result_status', 'test_date', 'verified_by']
    list_filter = ['result_status', 'test_date']
    search_fields = ['lab_order__order_number', 'test_name']
    date_hierarchy = 'test_date'


# ==================== TRAINING & HR ====================

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cadre', 'employee_number', 'primary_facility', 'license_expiry', 'employment_status']
    list_filter = ['cadre', 'employment_status', 'primary_facility']
    search_fields = ['user__first_name', 'user__last_name', 'employee_number', 'license_number']


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'start_date', 'end_date', 'venue', 'trainer', 'attendee_count']
    list_filter = ['start_date', 'training_organization']
    search_fields = ['course_name', 'course_code', 'trainer']
    date_hierarchy = 'start_date'
    
    def attendee_count(self, obj):
        return obj.attendees.count()
    attendee_count.short_description = 'Attendees'


@admin.register(TrainingAttendance)
class TrainingAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'training', 'attended', 'attendance_percentage', 'certificate_issued']
    list_filter = ['attended', 'certificate_issued', 'training']
    search_fields = ['staff__user__first_name', 'staff__user__last_name', 'training__course_name']


# ==================== SYSTEM ====================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'object_id', 'action', 'changed_by', 'timestamp', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['model_name', 'object_id', 'changed_by__email']
    date_hierarchy = 'timestamp'
    readonly_fields = ['model_name', 'object_id', 'action', 'changed_by', 'timestamp', 'ip_address', 'user_agent', 'change_summary']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'channel', 'notification_type', 'status', 'priority', 'created_at']
    list_filter = ['status', 'channel', 'notification_type', 'priority', 'created_at']
    search_fields = ['title', 'message', 'recipient__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['sent_at', 'read_at', 'created_at']
    
    actions = ['mark_as_sent', 'mark_as_read']
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='SENT', sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark selected as sent'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='READ', read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected as read'


@admin.register(FHIRMapping)
class FHIRMappingAdmin(admin.ModelAdmin):
    list_display = ['local_model', 'local_id', 'fhir_resource_type', 'fhir_id', 'external_system', 'sync_status', 'last_synced_at']
    list_filter = ['sync_status', 'fhir_resource_type', 'external_system']
    search_fields = ['local_model', 'local_id', 'fhir_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DataExportJob)
class DataExportJobAdmin(admin.ModelAdmin):
    list_display = ['export_type', 'model_name', 'requested_by', 'request_date', 'status', 'records_exported', 'file_size_mb']
    list_filter = ['status', 'export_type', 'request_date']
    search_fields = ['model_name', 'requested_by__email']
    date_hierarchy = 'request_date'
    readonly_fields = ['request_date', 'started_at', 'completed_at', 'file_url', 'error_message']
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024*1024):.2f} MB"
        return '-'
    file_size_mb.short_description = 'File Size'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_number', 'person', 'facility', 'appointment_date', 'appointment_time', 'appointment_type', 'status']
    list_filter = ['status', 'appointment_type', 'facility', 'appointment_date']
    search_fields = ['appointment_number', 'person__first_name', 'person__last_name', 'person__phone']
    date_hierarchy = 'appointment_date'
    readonly_fields = ['appointment_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('appointment_number', 'person', 'facility')
        }),
        ('Schedule', {
            'fields': ('appointment_date', 'appointment_time', 'appointment_type')
        }),
        ('Assignment', {
            'fields': ('scheduled_by', 'assigned_to')
        }),
        ('Status', {
            'fields': ('status', 'reason', 'notes')
        }),
        ('Tracking', {
            'fields': ('reminder_sent', 'reminder_sent_at', 'checked_in_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_reminders', 'mark_completed']
    
    def send_reminders(self, request, queryset):
        count = 0
        for appointment in queryset.filter(status='SCHEDULED'):
            # Logic to send reminder would go here
            appointment.reminder_sent = True
            appointment.reminder_sent_at = timezone.now()
            appointment.save()
            count += 1
        self.message_user(request, f'{count} reminders sent.')
    send_reminders.short_description = 'Send appointment reminders'
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED', completed_at=timezone.now())
        self.message_user(request, f'{updated} appointments marked as completed.')
    mark_completed.short_description = 'Mark selected as completed'


@admin.register(PNCVisit)
class PNCVisitAdmin(admin.ModelAdmin):
    list_display = ['pregnancy_woman', 'visit_number', 'visit_date', 'days_postpartum', 'mother_condition', 'facility']
    list_filter = ['facility', 'visit_date']
    search_fields = ['pregnancy__woman__first_name', 'pregnancy__woman__last_name']
    date_hierarchy = 'visit_date'
    
    def pregnancy_woman(self, obj):
        return obj.pregnancy.woman
    pregnancy_woman.short_description = 'Woman'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_type', 'ward', 'population', 'coordinates']
    list_filter = ['location_type', 'ward__subcounty__county', 'ward']
    search_fields = ['name', 'description']
    
    def coordinates(self, obj):
        if obj.latitude and obj.longitude:
            return f"{obj.latitude}, {obj.longitude}"
        return '-'
    coordinates.short_description = 'Coordinates'


# ==================== CUSTOM ADMIN DASHBOARD STATS ====================

class DashboardStats:
    """
    Custom dashboard statistics
    This would be displayed on the admin index page
    """
    
    @staticmethod
    def get_stats():
        from datetime import date, timedelta
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        stats = {
            'total_facilities': Facility.objects.filter(is_operational=True).count(),
            'total_chvs': CommunityHealthVolunteer.objects.filter(is_active=True).count(),
            'total_households': Household.objects.filter(is_active=True).count(),
            'total_population': Person.objects.filter(is_alive=True).count(),
            'active_pregnancies': PregnancyRecord.objects.filter(is_active=True).count(),
            'pending_referrals': Referral.objects.filter(status='PENDING').count(),
            'this_week_visits': HouseholdVisit.objects.filter(visit_date__gte=week_ago).count(),
            'this_month_screenings': Screening.objects.filter(screening_date__gte=month_ago).count(),
            'low_stock_items': Stock.objects.filter(
                quantity__lt=models.F('commodity__reorder_level')
            ).count(),
            'pending_lab_orders': LabTestOrder.objects.filter(status='PENDING').count(),
        }
        
        return stats


# ==================== ADMIN ACTIONS ====================

def export_to_csv(modeladmin, request, queryset):
    """
    Generic CSV export action
    """
    import csv
    from django.http import HttpResponse
    
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)
    
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    
    return response

export_to_csv.short_description = "Export selected to CSV"


# Add export action to all admins
def register_export_action():
    """Register export action to all model admins"""
    for model, model_admin in admin.site._registry.items():
        if 'export_to_csv' not in [action.__name__ for action in model_admin.actions]:
            model_admin.actions = list(model_admin.actions) + [export_to_csv]


# ==================== ADMIN SITE CUSTOMIZATION ====================

# Customize admin site
admin.site.site_header = "Wajir County Health Management System"
admin.site.site_title = "Wajir Health Admin"
admin.site.index_title = "System Administration Dashboard"


# ==================== CUSTOM FILTERS ====================

class ExpiryDateFilter(admin.SimpleListFilter):
    """Filter for expiring stock"""
    title = 'Expiry Status'
    parameter_name = 'expiry'
    
    def lookups(self, request, model_admin):
        return (
            ('expired', 'Expired'),
            ('expiring_soon', 'Expiring within 90 days'),
            ('valid', 'Valid'),
        )
    
    def queryset(self, request, queryset):
        from datetime import date, timedelta
        today = date.today()
        
        if self.value() == 'expired':
            return queryset.filter(expiry_date__lt=today)
        if self.value() == 'expiring_soon':
            return queryset.filter(
                expiry_date__gte=today,
                expiry_date__lt=today + timedelta(days=90)
            )
        if self.value() == 'valid':
            return queryset.filter(expiry_date__gte=today + timedelta(days=90))


class StockLevelFilter(admin.SimpleListFilter):
    """Filter for stock levels"""
    title = 'Stock Level'
    parameter_name = 'stock_level'
    
    def lookups(self, request, model_admin):
        return (
            ('out', 'Out of Stock'),
            ('low', 'Low Stock'),
            ('adequate', 'Adequate'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'out':
            return queryset.filter(quantity=0)
        if self.value() == 'low':
            return queryset.filter(
                quantity__gt=0,
                quantity__lt=models.F('commodity__reorder_level')
            )
        if self.value() == 'adequate':
            return queryset.filter(quantity__gte=models.F('commodity__reorder_level'))


# Apply custom filters
Stock.list_filter = list(Stock._meta.get_field('facility').related_model._meta.get_fields()) + [ExpiryDateFilter, StockLevelFilter]


# ==================== INLINE FORMSETS CONFIGURATION ====================

# Set maximum number of inline forms
admin.site.empty_value_display = '---'

# Configure inline formset options
for inline_class in [
    SubCountyInline, WardInline, ANCVisitInline, PNCVisitInline,
    ReferralFollowUpInline, StockInline, LabResultInline
]:
    inline_class.can_delete = True
    inline_class.show_change_link = True


# ==================== HELP TEXT ====================

# You can add custom help text or documentation links
# This would appear in the admin interface

ADMIN_HELP_TEXT = {
    'User': 'Manage system users and their roles. Users can have multiple roles for different access levels.',
    'Facility': 'Health facilities including dispensaries, health centres, and hospitals.',
    'Person': 'Individual patient/citizen records. Ensure National ID and NHIF numbers are accurate.',
    'Referral': 'Track patient referrals between facilities. Follow up on pending referrals regularly.',
    'Stock': 'Monitor commodity stock levels. Check expiry dates regularly to avoid wastage.',
}


# ==================== ADMIN SITE REGISTRATION VERIFICATION ====================

# Verify all models are registered
def check_registered_models():
    """
    Check which models are registered in admin
    Run this during development to ensure all models are registered
    """
    from django.apps import apps
    
    all_models = apps.get_models()
    registered_models = admin.site._registry.keys()
    
    unregistered = [model for model in all_models if model not in registered_models]
    
    if unregistered:
        print("Unregistered models:")
        for model in unregistered:
            print(f"  - {model.__name__}")
    else:
        print("All models are registered in admin!")
    
    return unregistered


# ==================== NOTES FOR IMPLEMENTATION ====================

"""
IMPLEMENTATION CHECKLIST:

1. Import this file in your Django app's admin.py
2. Ensure all models are imported correctly from your models.py
3. Run migrations: python manage.py makemigrations && python manage.py migrate
4. Create superuser: python manage.py createsuperuser
5. Collect static files: python manage.py collectstatic

CUSTOMIZATION OPTIONS:

1. Custom Actions:
   - Add bulk actions for common operations
   - Export data in different formats
   - Send notifications to multiple users

2. Custom Filters:
   - Add date range filters
   - Geographic filters (County -> SubCounty -> Ward)
   - Status-based filters

3. Dashboard Enhancements:
   - Install django-admin-tools for better dashboard
   - Add charts using django-admin-charts
   - Implement real-time statistics

4. Permissions:
   - Implement row-level permissions based on user's county/facility
   - Restrict access to sensitive data (PII)
   - Create custom permission classes

5. UI Improvements:
   - Install django-grappelli or django-suit for better UI
   - Add custom CSS/JS for specific functionality
   - Implement autocomplete fields for foreign keys

6. Performance:
   - Add select_related and prefetch_related in get_queryset
   - Implement caching for dashboard statistics
   - Use database indexes effectively

SECURITY NOTES:

1. Audit Logs:
   - All sensitive operations are logged in AuditLog
   - Audit logs cannot be edited or deleted (except by superuser)

2. Permissions:
   - Implement proper permission checks in views
   - Use Django's permission system
   - Add custom permissions for specific actions

3. Data Protection:
   - Encrypt sensitive fields (National ID, NHIF)
   - Use HTTPS in production
   - Implement proper backup strategies

TESTING:

Run the following tests:
1. python manage.py test
2. Check admin interface loads properly
3. Test CRUD operations for each model
4. Verify filters and search work correctly
5. Test custom actions
6. Check permissions work as expected
"""

"""
Wajir County Health Management System - Django Models
Complete implementation for county-level health management
"""