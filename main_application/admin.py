from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    # Core Administrative
    County, SubCounty, Ward,
    
    # Users & Access Control
    User, Role,
    
    # Facilities & Community
    Facility, CommunityUnit, CommunityHealthVolunteer,
    
    # Population & Households
    Household, Person,
    
    # Surveillance & Reports
    SurveillanceReport, MortalityReport,
    
    # Programs & M&E
    Program, Indicator, MonthlyReport, Campaign,
    
    # Commodities & Supply Chain
    Commodity, Supplier, Stock, StockTransaction,
    ProcurementRequest, PurchaseOrder,
    
    # Laboratory
    LabTestOrder, LabResult,
    
    # Training & HR
    StaffProfile, Training, TrainingAttendance,
    
    # Maternal & Child Health
    PregnancyRecord, ANCVisit, ImmunizationRecord,
    
    # Public Health Activities
    HouseholdVisit, OutreachEvent, Screening,
    
    # Referrals
    Referral, ReferralFollowUp,
)


# ==================== CORE ADMINISTRATIVE ====================

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'population', 'contact_person', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code', 'contact_person', 'email']
    ordering = ['name']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'population')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'phone', 'email')
        }),
        ('System Information', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'county', 'population', 'ward_count', 'created_at']
    list_filter = ['county', 'created_at']
    search_fields = ['name', 'code', 'county__name']
    ordering = ['county', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['county']
    
    def ward_count(self, obj):
        return obj.wards.count()
    ward_count.short_description = 'Wards'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('county', 'name', 'code', 'population')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'subcounty', 'get_county', 'population', 'facility_count', 'created_at']
    list_filter = ['subcounty__county', 'subcounty', 'created_at']
    search_fields = ['name', 'code', 'subcounty__name']
    ordering = ['subcounty', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['subcounty']
    
    def get_county(self, obj):
        return obj.subcounty.county.name
    get_county.short_description = 'County'
    get_county.admin_order_field = 'subcounty__county'
    
    def facility_count(self, obj):
        return obj.facilities.count()
    facility_count.short_description = 'Facilities'


# ==================== USERS & ACCESS CONTROL ====================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name_display', 'level', 'user_count', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-level', 'name']
    readonly_fields = ['id', 'created_at']
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description', 'level')
        }),
        ('System Information', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'phone', 'get_roles', 'county', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'county', 'roles', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone', 'national_id']
    ordering = ['-date_joined']
    readonly_fields = ['id', 'date_joined', 'last_login']
    filter_horizontal = ['roles', 'groups', 'user_permissions']
    
    def get_roles(self, obj):
        return ", ".join([role.get_name_display() for role in obj.roles.all()[:3]])
    get_roles.short_description = 'Roles'
    
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
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


# ==================== FACILITIES & COMMUNITY ====================

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'facility_code', 'facility_type', 'ward', 'is_operational', 'bed_capacity', 'created_at']
    list_filter = ['facility_type', 'is_operational', 'subcounty', 'created_at']
    search_fields = ['name', 'facility_code', 'ward__name', 'phone', 'email']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['ward', 'subcounty']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'facility_code', 'facility_type', 'bed_capacity')
        }),
        ('Location', {
            'fields': ('ward', 'subcounty', 'physical_address', 'latitude', 'longitude')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Operational Status', {
            'fields': ('is_operational',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommunityUnit)
class CommunityUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'ward', 'linked_facility', 'target_population', 'volunteer_count', 'is_active', 'established_date']
    list_filter = ['is_active', 'ward__subcounty', 'established_date']
    search_fields = ['name', 'code', 'ward__name']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['ward', 'linked_facility']
    
    def volunteer_count(self, obj):
        return obj.volunteers.filter(is_active=True).count()
    volunteer_count.short_description = 'Active CHVs'


@admin.register(CommunityHealthVolunteer)
class CommunityHealthVolunteerAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'chv_number', 'community_unit', 'gender', 'is_active', 'households_assigned', 'certification_expiry']
    list_filter = ['is_active', 'gender', 'community_unit__ward__subcounty', 'certification_expiry']
    search_fields = ['user__first_name', 'user__last_name', 'national_id', 'chv_number']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['user', 'community_unit']
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'
    get_name.admin_order_field = 'user__first_name'
    
    fieldsets = (
        ('CHV Information', {
            'fields': ('user', 'community_unit', 'chv_number', 'national_id')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender')
        }),
        ('Certification', {
            'fields': ('training_date', 'certification_date', 'certification_expiry')
        }),
        ('Work Assignment', {
            'fields': ('is_active', 'households_assigned')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== POPULATION & HOUSEHOLDS ====================

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['household_number', 'ward', 'community_unit', 'assigned_chv', 'number_of_members', 'is_active', 'registration_date']
    list_filter = ['is_active', 'ward__subcounty', 'registration_date']
    search_fields = ['household_number', 'village', 'ward__name']
    ordering = ['-registration_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['community_unit', 'ward', 'assigned_chv']
    
    fieldsets = (
        ('Identification', {
            'fields': ('household_number', 'community_unit', 'ward', 'assigned_chv')
        }),
        ('Location', {
            'fields': ('village', 'physical_address', 'latitude', 'longitude')
        }),
        ('Household Details', {
            'fields': ('number_of_members', 'has_toilet', 'water_source')
        }),
        ('Status', {
            'fields': ('registration_date', 'is_active')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['get_full_name_display', 'national_id', 'gender', 'get_age_display', 'household', 'is_household_head', 'is_alive']
    list_filter = ['gender', 'is_household_head', 'is_alive', 'household__ward__subcounty', 'created_at']
    search_fields = ['first_name', 'last_name', 'national_id', 'nhif_number', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['household']
    
    def get_full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name_display.short_description = 'Name'
    get_full_name_display.admin_order_field = 'first_name'
    
    def get_age_display(self, obj):
        return f"{obj.get_age()} years"
    get_age_display.short_description = 'Age'
    
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
        ('Location', {
            'fields': ('household', 'is_household_head')
        }),
        ('Health Information', {
            'fields': ('blood_group', 'chronic_conditions', 'allergies')
        }),
        ('Status', {
            'fields': ('is_alive', 'date_of_death')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== SURVEILLANCE & REPORTS ====================

@admin.register(SurveillanceReport)
class SurveillanceReportAdmin(admin.ModelAdmin):
    list_display = ['report_number', 'disease_name', 'report_date', 'ward', 'cases_confirmed', 'deaths', 'outbreak_declared', 'response_initiated']
    list_filter = ['outbreak_declared', 'response_initiated', 'source', 'report_date', 'ward__subcounty']
    search_fields = ['report_number', 'disease_name', 'disease_code', 'ward__name']
    ordering = ['-report_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['ward', 'facility', 'reported_by']
    date_hierarchy = 'report_date'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_number', 'disease_name', 'disease_code', 'report_date')
        }),
        ('Reporting Period', {
            'fields': ('reporting_period_start', 'reporting_period_end')
        }),
        ('Location & Source', {
            'fields': ('ward', 'facility', 'source', 'reported_by')
        }),
        ('Case Statistics', {
            'fields': ('cases_suspected', 'cases_confirmed', 'deaths')
        }),
        ('Demographics', {
            'fields': ('cases_under_5', 'cases_5_to_15', 'cases_over_15', 'males', 'females'),
            'classes': ('collapse',)
        }),
        ('Response', {
            'fields': ('outbreak_declared', 'response_initiated', 'response_details')
        }),
        ('Additional Information', {
            'fields': ('notes', 'attachments'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MortalityReport)
class MortalityReportAdmin(admin.ModelAdmin):
    list_display = ['get_deceased_name', 'death_category', 'date_of_death', 'place_of_death', 'ward', 'pregnancy_related', 'report_date']
    list_filter = ['death_category', 'pregnancy_related', 'date_of_death', 'ward__subcounty']
    search_fields = ['deceased_person__first_name', 'deceased_person__last_name', 'immediate_cause']
    ordering = ['-date_of_death']
    readonly_fields = ['id', 'created_at']
    autocomplete_fields = ['deceased_person', 'facility', 'ward', 'reported_by']
    date_hierarchy = 'date_of_death'
    
    def get_deceased_name(self, obj):
        return obj.deceased_person.get_full_name() if obj.deceased_person else "Unknown"
    get_deceased_name.short_description = 'Deceased'


# ==================== PROGRAMS & M&E ====================

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'county', 'program_manager', 'start_date', 'end_date', 'is_active', 'budget']
    list_filter = ['is_active', 'county', 'start_date']
    search_fields = ['name', 'code', 'description']
    ordering = ['-start_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['county', 'program_manager']
    date_hierarchy = 'start_date'


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'program', 'indicator_type', 'target_value', 'baseline_value', 'is_active']
    list_filter = ['indicator_type', 'is_active', 'program']
    search_fields = ['name', 'code', 'program__name']
    ordering = ['program', 'code']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['program']


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['get_report_period', 'facility', 'subcounty', 'outpatient_visits', 'deliveries', 'approved', 'submission_date']
    list_filter = ['approved', 'year', 'month', 'facility__subcounty']
    search_fields = ['facility__name', 'subcounty__name']
    ordering = ['-year', '-month']
    readonly_fields = ['id', 'created_at', 'updated_at', 'submission_date']
    autocomplete_fields = ['facility', 'subcounty', 'submitted_by', 'approved_by']
    
    def get_report_period(self, obj):
        return f"{obj.year}-{obj.month:02d}"
    get_report_period.short_description = 'Period'
    get_report_period.admin_order_field = 'year'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'program', 'start_date', 'end_date', 'target_population', 'people_reached', 'status']
    list_filter = ['status', 'campaign_type', 'start_date', 'program']
    search_fields = ['name', 'program__name', 'target_area']
    ordering = ['-start_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['program', 'campaign_manager']
    filter_horizontal = ['wards']
    date_hierarchy = 'start_date'


# ==================== COMMODITIES & SUPPLY CHAIN ====================

@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = ['name', 'commodity_code', 'commodity_type', 'unit_of_measure', 'reorder_level', 'is_essential', 'is_active']
    list_filter = ['commodity_type', 'is_essential', 'is_active']
    search_fields = ['name', 'commodity_code', 'generic_name']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier_code', 'contact_person', 'phone', 'email', 'rating', 'is_active']
    list_filter = ['is_active', 'rating']
    search_fields = ['name', 'supplier_code', 'contact_person', 'kra_pin']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['commodity', 'facility', 'quantity', 'batch_number', 'expiry_date', 'last_updated']
    list_filter = ['facility', 'commodity__commodity_type', 'expiry_date']
    search_fields = ['commodity__name', 'facility__name', 'batch_number']
    ordering = ['expiry_date']
    readonly_fields = ['id', 'last_updated']
    autocomplete_fields = ['commodity', 'facility', 'updated_by']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('commodity', 'facility')


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'transaction_type', 'stock', 'quantity', 'transaction_date', 'performed_by']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['transaction_number', 'reference_number', 'stock__commodity__name']
    ordering = ['-transaction_date']
    readonly_fields = ['id', 'created_at']
    autocomplete_fields = ['stock', 'from_facility', 'to_facility', 'performed_by', 'approved_by']
    date_hierarchy = 'transaction_date'


@admin.register(ProcurementRequest)
class ProcurementRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'facility', 'status', 'priority', 'request_date', 'requested_by']
    list_filter = ['status', 'priority', 'request_date']
    search_fields = ['request_number', 'facility__name']
    ordering = ['-request_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['facility', 'requested_by', 'reviewed_by', 'approved_by']
    date_hierarchy = 'request_date'


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'status', 'po_date', 'expected_delivery_date', 'total_amount']
    list_filter = ['status', 'po_date', 'supplier']
    search_fields = ['po_number', 'supplier__name']
    ordering = ['-po_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['supplier', 'procurement_request', 'created_by', 'approved_by']
    date_hierarchy = 'po_date'


# ==================== LABORATORY ====================

@admin.register(LabTestOrder)
class LabTestOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'patient', 'facility', 'status', 'priority', 'order_date']
    list_filter = ['status', 'priority', 'order_date', 'facility']
    search_fields = ['order_number', 'patient__first_name', 'patient__last_name']
    ordering = ['-order_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['patient', 'facility', 'ordered_by', 'sample_collected_by']
    date_hierarchy = 'order_date'


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'lab_order', 'result_value', 'result_status', 'test_date', 'tested_by']
    list_filter = ['result_status', 'test_date']
    search_fields = ['test_name', 'test_code', 'lab_order__order_number']
    ordering = ['-test_date']
    readonly_fields = ['id', 'created_at']
    autocomplete_fields = ['lab_order', 'tested_by', 'verified_by']
    date_hierarchy = 'test_date'


# ==================== TRAINING & HR ====================

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'employee_number', 'cadre', 'primary_facility', 'employment_status', 'license_expiry']
    list_filter = ['cadre', 'employment_status', 'primary_facility__subcounty', 'license_expiry']
    search_fields = ['user__first_name', 'user__last_name', 'employee_number', 'license_number']
    ordering = ['-employment_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['user', 'primary_facility']
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'
    get_name.admin_order_field = 'user__first_name'


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'start_date', 'end_date', 'venue', 'trainer', 'attendee_count']
    list_filter = ['start_date', 'training_organization']
    search_fields = ['course_name', 'course_code', 'trainer', 'venue']
    ordering = ['-start_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['organized_by']
    date_hierarchy = 'start_date'
    
    def attendee_count(self, obj):
        return obj.attendees.count()
    attendee_count.short_description = 'Attendees'


class TrainingAttendanceInline(admin.TabularInline):
    model = TrainingAttendance
    extra = 1
    autocomplete_fields = ['staff']


# ==================== MATERNAL & CHILD HEALTH ====================

@admin.register(PregnancyRecord)
class PregnancyRecordAdmin(admin.ModelAdmin):
    list_display = ['get_woman_name', 'lmp_date', 'edd', 'gravida', 'parity', 'is_high_risk', 'anc_visits_completed', 'is_active']
    list_filter = ['is_high_risk', 'is_active', 'edd']
    search_fields = ['woman__first_name', 'woman__last_name']
    ordering = ['-edd']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['woman', 'delivery_facility']
    date_hierarchy = 'edd'
    
    def get_woman_name(self, obj):
        return obj.woman.get_full_name()
    get_woman_name.short_description = 'Woman'


@admin.register(ANCVisit)
class ANCVisitAdmin(admin.ModelAdmin):
    list_display = ['get_woman_name', 'visit_number', 'visit_date', 'gestation_weeks', 'facility', 'attended_by']
    list_filter = ['visit_date', 'facility']
    search_fields = ['pregnancy__woman__first_name', 'pregnancy__woman__last_name']
    ordering = ['-visit_date']
    readonly_fields = ['id', 'created_at']
    autocomplete_fields = ['pregnancy', 'facility', 'attended_by']
    date_hierarchy = 'visit_date'
    
    def get_woman_name(self, obj):
        return obj.pregnancy.woman.get_full_name()
    get_woman_name.short_description = 'Woman'


@admin.register(ImmunizationRecord)
class ImmunizationRecordAdmin(admin.ModelAdmin):
    list_display = ['get_child_name', 'vaccine_name', 'dose_number', 'administration_date', 'facility', 'administered_by']
    list_filter = ['vaccine_name', 'administration_date', 'facility']
    search_fields = ['child__first_name', 'child__last_name', 'vaccine_name', 'vaccine_code']
    ordering = ['-administration_date']
    readonly_fields = ['id', 'created_at']
    autocomplete_fields = ['child', 'facility', 'administered_by']
    date_hierarchy = 'administration_date'
    
    def get_child_name(self, obj):
        return obj.child.get_full_name()
    get_child_name.short_description = 'Child'


# ==================== PUBLIC HEALTH ACTIVITIES ====================

@admin.register(HouseholdVisit)
class HouseholdVisitAdmin(admin.ModelAdmin):
    list_display = ['household', 'chv', 'visit_date', 'visit_type', 'members_present', 'referrals_made']
    list_filter = ['visit_type', 'visit_date']
    search_fields = ['household__household_number', 'chv__user__first_name']
    ordering = ['-visit_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['household', 'chv']
    date_hierarchy = 'visit_date'


@admin.register(OutreachEvent)
class OutreachEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'start_date', 'end_date', 'ward', 'target_population', 'people_reached']
    list_filter = ['event_type', 'start_date', 'ward__subcounty']
    search_fields = ['name', 'location', 'ward__name']
    ordering = ['-start_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['ward', 'organizing_facility']
    date_hierarchy = 'start_date'


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ['get_person_name', 'screening_type', 'result', 'screening_date', 'facility', 'follow_up_required']
    list_filter = ['screening_type', 'result', 'follow_up_required', 'screening_date']
    search_fields = ['person__first_name', 'person__last_name']
    ordering = ['-screening_date']
    readonly_fields = ['id', 'created_at']
    autocomplete_fields = ['person', 'facility', 'screened_by', 'outreach_event']
    date_hierarchy = 'screening_date'
    
    def get_person_name(self, obj):
        return obj.person.get_full_name()
    get_person_name.short_description = 'Person'


# ==================== REFERRALS ====================

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referral_number', 'get_person_name', 'from_facility', 'to_facility', 'urgency', 'status', 'referral_date']
    list_filter = ['status', 'urgency', 'referral_date', 'from_facility__subcounty']
    search_fields = ['referral_number', 'person__first_name', 'person__last_name', 'reason']
    ordering = ['-referral_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['person', 'from_facility', 'to_facility', 'referred_by', 'accepted_by']
    date_hierarchy = 'referral_date'
    
    def get_person_name(self, obj):
        return obj.person.get_full_name()
    get_person_name.short_description = 'Patient'
    
    fieldsets = (
        ('Referral Information', {
            'fields': ('referral_number', 'person', 'referral_date', 'urgency')
        }),
        ('Facilities', {
            'fields': ('from_facility', 'to_facility')
        }),
        ('Clinical Details', {
            'fields': ('reason', 'diagnosis', 'treatment_given')
        }),
        ('Status Tracking', {
            'fields': ('status', 'referred_by', 'accepted_by', 'accepted_date', 'arrival_date', 'completion_date')
        }),
        ('Outcome', {
            'fields': ('outcome', 'feedback_to_referring_facility'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ReferralFollowUpInline(admin.TabularInline):
    model = ReferralFollowUp
    extra = 0
    readonly_fields = ['created_at']
    autocomplete_fields = ['followed_up_by']
    fields = ['follow_up_date', 'followed_up_by', 'status_update', 'action_taken']


@admin.register(ReferralFollowUp)
class ReferralFollowUpAdmin(admin.ModelAdmin):
    list_display = ['referral', 'follow_up_date', 'followed_up_by', 'status_update']
    list_filter = ['follow_up_date']
    search_fields = ['referral__referral_number', 'status_update']
    ordering = ['-follow_up_date']
    readonly_fields = ['id', 'created_at']
    autocomplete_fields = ['referral', 'followed_up_by']
    date_hierarchy = 'follow_up_date'


# ==================== CUSTOM ADMIN SITE CONFIGURATION ====================

# Customize the admin site header and titles
admin.site.site_header = "Wajir County Health System Administration"
admin.site.site_title = "Wajir Health Admin"
admin.site.index_title = "Health Information System Management"


# ==================== INLINE ADMIN CLASSES ====================

class SubCountyInline(admin.TabularInline):
    model = SubCounty
    extra = 0
    fields = ['name', 'code', 'population']
    show_change_link = True


class WardInline(admin.TabularInline):
    model = Ward
    extra = 0
    fields = ['name', 'code', 'population']
    show_change_link = True


class ANCVisitInline(admin.TabularInline):
    model = ANCVisit
    extra = 0
    fields = ['visit_number', 'visit_date', 'gestation_weeks', 'facility', 'weight', 'blood_pressure']
    readonly_fields = ['created_at']
    autocomplete_fields = ['facility', 'attended_by']
    show_change_link = True


class ImmunizationInline(admin.TabularInline):
    model = ImmunizationRecord
    extra = 0
    fields = ['vaccine_name', 'dose_number', 'administration_date', 'facility']
    readonly_fields = ['created_at']
    autocomplete_fields = ['facility', 'administered_by']
    show_change_link = True


# Add inlines to existing admin classes
CountyAdmin.inlines = [SubCountyInline]
SubCountyAdmin.inlines = [WardInline]
PregnancyRecordAdmin.inlines = [ANCVisitInline]
PersonAdmin.inlines = [ImmunizationInline]
ReferralAdmin.inlines = [ReferralFollowUpInline]
TrainingAdmin.inlines = [TrainingAttendanceInline]


# ==================== CUSTOM ACTIONS ====================

@admin.action(description='Mark selected as active')
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description='Mark selected as inactive')
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description='Approve selected reports')
def approve_reports(modeladmin, request, queryset):
    from django.utils import timezone
    queryset.update(approved=True, approved_by=request.user, approval_date=timezone.now())


@admin.action(description='Mark facilities as operational')
def make_operational(modeladmin, request, queryset):
    queryset.update(is_operational=True)


@admin.action(description='Mark facilities as non-operational')
def make_non_operational(modeladmin, request, queryset):
    queryset.update(is_operational=False)


# Add actions to relevant admin classes
FacilityAdmin.actions = [make_operational, make_non_operational]
CommunityUnitAdmin.actions = [make_active, make_inactive]
CommunityHealthVolunteerAdmin.actions = [make_active, make_inactive]
HouseholdAdmin.actions = [make_active, make_inactive]
CommodityAdmin.actions = [make_active, make_inactive]
SupplierAdmin.actions = [make_active, make_inactive]
ProgramAdmin.actions = [make_active, make_inactive]
IndicatorAdmin.actions = [make_active, make_inactive]
MonthlyReportAdmin.actions = [approve_reports]
PregnancyRecordAdmin.actions = [make_active, make_inactive]


# ==================== SEARCH FIELD AUTOCOMPLETE ====================

# Enable autocomplete for foreign key fields
County.search_fields = ['name', 'code']
SubCounty.search_fields = ['name', 'code']
Ward.search_fields = ['name', 'code']
User.search_fields = ['email', 'first_name', 'last_name', 'phone']
Facility.search_fields = ['name', 'facility_code']
Person.search_fields = ['first_name', 'last_name', 'national_id', 'nhif_number']
Household.search_fields = ['household_number', 'village']
CommunityUnit.search_fields = ['name', 'code']
CommunityHealthVolunteer.search_fields = ['user__first_name', 'user__last_name', 'chv_number']
Commodity.search_fields = ['name', 'commodity_code']
Supplier.search_fields = ['name', 'supplier_code']
Program.search_fields = ['name', 'code']
StaffProfile.search_fields = ['user__first_name', 'user__last_name', 'employee_number']


# ==================== LIST DISPLAY CUSTOMIZATION ====================

# Add colored status indicators
def colored_status(obj, field_name, true_color='green', false_color='red'):
    """Helper function to add colored status indicators"""
    value = getattr(obj, field_name)
    color = true_color if value else false_color
    text = 'Yes' if value else 'No'
    return format_html(
        '<span style="color: {}; font-weight: bold;">●</span> {}',
        color, text
    )


# Enhance User Admin with colored status
def user_active_status(self, obj):
    return colored_status(obj, 'is_active')
user_active_status.short_description = 'Active'

UserAdmin.list_display = list(UserAdmin.list_display)
if 'is_active' in UserAdmin.list_display:
    idx = UserAdmin.list_display.index('is_active')
    UserAdmin.list_display[idx] = user_active_status


# ==================== ADMIN LIST FILTERS ====================

class ActiveStatusFilter(admin.SimpleListFilter):
    """Custom filter for active/inactive status"""
    title = 'Status'
    parameter_name = 'active_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)


class OperationalStatusFilter(admin.SimpleListFilter):
    """Custom filter for operational status"""
    title = 'Operational Status'
    parameter_name = 'operational'

    def lookups(self, request, model_admin):
        return (
            ('operational', 'Operational'),
            ('non_operational', 'Non-Operational'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'operational':
            return queryset.filter(is_operational=True)
        if self.value() == 'non_operational':
            return queryset.filter(is_operational=False)


class ExpiredStockFilter(admin.SimpleListFilter):
    """Filter for expired stock"""
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('expired', 'Expired'),
            ('expiring_soon', 'Expiring Soon (30 days)'),
            ('valid', 'Valid'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        
        if self.value() == 'expired':
            return queryset.filter(expiry_date__lt=today)
        if self.value() == 'expiring_soon':
            thirty_days = today + timedelta(days=30)
            return queryset.filter(expiry_date__gte=today, expiry_date__lte=thirty_days)
        if self.value() == 'valid':
            return queryset.filter(expiry_date__gt=today + timedelta(days=30))


# Add custom filters to admin classes
FacilityAdmin.list_filter = list(FacilityAdmin.list_filter) + [OperationalStatusFilter]
StockAdmin.list_filter = list(StockAdmin.list_filter) + [ExpiredStockFilter]


# ==================== EXPORT ACTIONS ====================

@admin.action(description='Export selected to CSV')
def export_to_csv(modeladmin, request, queryset):
    """Export selected records to CSV"""
    import csv
    from django.http import HttpResponse
    from django.utils import timezone
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model.__name__}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Get field names
    fields = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(fields)
    
    # Write data rows
    for obj in queryset:
        row = [getattr(obj, field) for field in fields]
        writer.writerow(row)
    
    return response


# Add export action to key admin classes
UserAdmin.actions = list(UserAdmin.actions or []) + [export_to_csv]
FacilityAdmin.actions = list(FacilityAdmin.actions or []) + [export_to_csv]
PersonAdmin.actions = list(PersonAdmin.actions or []) + [export_to_csv]
HouseholdAdmin.actions = list(HouseholdAdmin.actions or []) + [export_to_csv]
SurveillanceReportAdmin.actions = [export_to_csv]
MonthlyReportAdmin.actions = list(MonthlyReportAdmin.actions or []) + [export_to_csv]
ReferralAdmin.actions = [export_to_csv]


# ==================== ADMIN DASHBOARD STATISTICS ====================

class HealthSystemAdminSite(admin.AdminSite):
    """Custom admin site with dashboard statistics"""
    site_header = "Wajir County Health System"
    site_title = "Wajir Health Admin"
    index_title = "Health Information System Dashboard"
    
    def index(self, request, extra_context=None):
        """Add custom statistics to admin index page"""
        extra_context = extra_context or {}
        
        # Add quick statistics
        extra_context['total_facilities'] = Facility.objects.count()
        extra_context['active_pregnancies'] = PregnancyRecord.objects.filter(is_active=True).count()
        extra_context['pending_referrals'] = Referral.objects.filter(status__in=['PENDING', 'ACCEPTED', 'IN_TRANSIT']).count()
        extra_context['total_population'] = Person.objects.filter(is_alive=True).count()
        
        return super().index(request, extra_context)


# Uncomment below to use custom admin site
# admin_site = HealthSystemAdminSite(name='health_admin')
# Then register all models with admin_site instead of admin.site


# ==================== READONLY FIELDS FOR SECURITY ====================

class SecureModelAdmin(admin.ModelAdmin):
    """Base admin class with common security settings"""
    
    def get_readonly_fields(self, request, obj=None):
        """Make UUID and timestamp fields readonly"""
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:  # Editing an existing object
            readonly.extend(['id', 'created_at'])
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete"""
        return request.user.is_superuser
    
    def save_model(self, request, obj, form, change):
        """Auto-populate user fields"""
        if not change and hasattr(obj, 'created_by'):
            obj.created_by = request.user
        if hasattr(obj, 'updated_by'):
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# Apply security settings to sensitive models
SurveillanceReportAdmin.__bases__ = (SecureModelAdmin,)
MortalityReportAdmin.__bases__ = (SecureModelAdmin,)
MonthlyReportAdmin.__bases__ = (SecureModelAdmin,)
ReferralAdmin.__bases__ = (SecureModelAdmin,)