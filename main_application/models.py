from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

# ==================== AUDIT & NOTIFICATIONS ====================

class AuditLog(models.Model):
    """Audit trail for sensitive operations"""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"
    
# ==================== CORE ADMINISTRATIVE MODELS ====================

class County(models.Model):
    """County administrative unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    population = models.IntegerField(null=True, blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Follow-up on {self.referral.referral_number}"
    



class SubCounty(models.Model):
    """Sub-county administrative unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='subcounties')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    population = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sub-counties"
        unique_together = [['county', 'name']]
        ordering = ['county', 'name']
        indexes = [
            models.Index(fields=['county', 'code']),
        ]

    def __str__(self):
        return f"{self.name} - {self.county.name}"


class Ward(models.Model):
    """Ward administrative unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='wards')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    population = models.IntegerField(null=True, blank=True)
    # Optional PostGIS fields
    # coordinates = models.PointField(null=True, blank=True, srid=4326)
    # boundary = models.PolygonField(null=True, blank=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['subcounty', 'name']]
        ordering = ['subcounty', 'name']
        indexes = [
            models.Index(fields=['subcounty', 'code']),
        ]

    def __str__(self):
        return f"{self.name} - {self.subcounty.name}"


# ==================== USERS & ACCESS CONTROL ====================

class Role(models.Model):
    """User roles in the health system"""
    ROLE_CHOICES = [
        ('COUNTY_ADMIN', 'County Administrator'),
        ('PUBLIC_HEALTH_OFFICER', 'Public Health Officer'),
        ('ME_OFFICER', 'M&E Officer'),
        ('FACILITY_MANAGER', 'Facility Manager'),
        ('CLINICAL_OFFICER', 'Clinical Officer'),
        ('NURSE', 'Nurse'),
        ('LAB_TECH', 'Laboratory Technician'),
        ('PHARMACIST', 'Pharmacist'),
        ('DATA_CLERK', 'Data Clerk'),
        ('CHV', 'Community Health Volunteer'),
        ('CHEW', 'Community Health Extension Worker'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    level = models.IntegerField(default=1, help_text="Higher level = more access")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_name_display()


class CustomUserManager(BaseUserManager):
    """Custom user manager for email/phone authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with Kenyan-specific fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15, 
        unique=True,
        validators=[RegexValidator(regex=r'^\+?254\d{9}$', message='Valid Kenyan phone format')]
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']

    class Meta:
        indexes = [
            models.Index(fields=['email', 'national_id']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"




# ==================== FACILITIES & COMMUNITY ====================

class Facility(models.Model):
    """Health facility"""
    FACILITY_TYPES = [
        ('DISPENSARY', 'Dispensary'),
        ('HEALTH_CENTRE', 'Health Centre'),
        ('SUB_COUNTY_HOSPITAL', 'Sub-County Hospital'),
        ('COUNTY_REFERRAL', 'County Referral Hospital'),
        ('PRIVATE_CLINIC', 'Private Clinic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    facility_code = models.CharField(max_length=20, unique=True, db_index=True)
    facility_type = models.CharField(max_length=30, choices=FACILITY_TYPES)
    
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='facilities')
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='facilities')
    
    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    # coordinates = models.PointField(null=True, blank=True, srid=4326)  # PostGIS
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    physical_address = models.TextField(blank=True)
    
    # Operational
    is_operational = models.BooleanField(default=True)
    bed_capacity = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ['name']
        indexes = [
            models.Index(fields=['facility_code', 'ward']),
        ]

    def __str__(self):
        return f"{self.name} ({self.facility_code})"


class CommunityUnit(models.Model):
    """Community Health Unit (CHU)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='community_units')
    linked_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, related_name='community_units')
    
    target_population = models.IntegerField(help_text="Expected catchment population")
    target_households = models.IntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    established_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.ward.name}"


class CommunityHealthVolunteer(models.Model):
    """Community Health Volunteer (CHV)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chv_profile')
    community_unit = models.ForeignKey(CommunityUnit, on_delete=models.CASCADE, related_name='volunteers')
    
    national_id = models.CharField(max_length=20, unique=True, db_index=True)
    chv_number = models.CharField(max_length=20, unique=True, blank=True)
    
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    
    training_date = models.DateField(null=True, blank=True)
    certification_date = models.DateField(null=True, blank=True)
    certification_expiry = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    households_assigned = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Community Health Volunteer"
        indexes = [
            models.Index(fields=['national_id', 'community_unit']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.community_unit.name}"
    

# ==================== POPULATION & HOUSEHOLDS ====================

class Household(models.Model):
    """Household record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    community_unit = models.ForeignKey(CommunityUnit, on_delete=models.CASCADE, related_name='households')
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='households')
    assigned_chv = models.ForeignKey(CommunityHealthVolunteer, on_delete=models.SET_NULL, null=True, related_name='assigned_households')
    
    village = models.CharField(max_length=100, blank=True)
    physical_address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    number_of_members = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    has_toilet = models.BooleanField(null=True, blank=True)
    water_source = models.CharField(max_length=50, blank=True)
    
    registration_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['household_number', 'ward']),
        ]

    def __str__(self):
        return f"HH-{self.household_number}"



class Person(models.Model):
    """Individual person/patient record"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Demographics
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Identifiers
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    nhif_number = models.CharField(max_length=20, blank=True, db_index=True)
    birth_certificate_number = models.CharField(max_length=50, blank=True)
    
    # Contact
    phone = models.CharField(max_length=15, blank=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    
    # Location
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='members')
    is_household_head = models.BooleanField(default=False)
    
    # Health
    blood_group = models.CharField(max_length=5, blank=True)
    chronic_conditions = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    allergies = models.TextField(blank=True)
    
    # Status
    is_alive = models.BooleanField(default=True)
    date_of_death = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "People"
        indexes = [
            models.Index(fields=['national_id', 'nhif_number']),
            models.Index(fields=['household', 'is_household_head']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )





# ==================== SURVEILLANCE & REPORTS ====================

class SurveillanceReport(models.Model):
    """Disease surveillance report"""
    SOURCE_CHOICES = [
        ('FACILITY', 'Health Facility'),
        ('CHV', 'Community Health Volunteer'),
        ('LABORATORY', 'Laboratory'),
        ('SCHOOL', 'School'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_number = models.CharField(max_length=50, unique=True)
    
    disease_name = models.CharField(max_length=100)
    disease_code = models.CharField(max_length=20, blank=True, help_text="ICD code")
    
    report_date = models.DateField()
    reporting_period_start = models.DateField()
    reporting_period_end = models.DateField()
    
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='surveillance_reports')
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Case counts
    cases_suspected = models.IntegerField(default=0)
    cases_confirmed = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    
    # Demographics breakdown
    cases_under_5 = models.IntegerField(default=0)
    cases_5_to_15 = models.IntegerField(default=0)
    cases_over_15 = models.IntegerField(default=0)
    
    males = models.IntegerField(default=0)
    females = models.IntegerField(default=0)
    
    # Response
    outbreak_declared = models.BooleanField(default=False)
    response_initiated = models.BooleanField(default=False)
    response_details = models.TextField(blank=True)
    
    attachments = models.JSONField(default=list, blank=True, help_text="S3 URLs to attachments")
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['disease_name', 'report_date']),
        ]

    def __str__(self):
        return f"{self.disease_name} - {self.report_date}"


class MortalityReport(models.Model):
    """Mortality tracking report"""
    DEATH_CATEGORIES = [
        ('NEONATAL', 'Neonatal (0-28 days)'),
        ('INFANT', 'Infant (29 days - 1 year)'),
        ('CHILD', 'Child (1-5 years)'),
        ('MATERNAL', 'Maternal'),
        ('ADULT', 'Adult (15+ years)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    deceased_person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name='mortality_report')
    
    death_category = models.CharField(max_length=20, choices=DEATH_CATEGORIES)
    date_of_death = models.DateField()
    place_of_death = models.CharField(max_length=100, help_text="Home/Facility/Transit")
    
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='mortality_reports')
    
    # Cause
    immediate_cause = models.CharField(max_length=200)
    underlying_cause = models.CharField(max_length=200, blank=True)
    contributing_factors = models.TextField(blank=True)
    
    # For maternal deaths
    pregnancy_related = models.BooleanField(default=False)
    timing = models.CharField(max_length=50, blank=True, help_text="During pregnancy/labor/postpartum")
    
    # Reporting
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    report_date = models.DateField(default=timezone.now)
    
    autopsy_done = models.BooleanField(default=False)
    autopsy_findings = models.TextField(blank=True)
    
    death_certificate_issued = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Death Report - {self.death_category} ({self.date_of_death})"


# ==================== PROGRAMS & M&E ====================

class Program(models.Model):
    """Health program"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    
    description = models.TextField()
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='programs')
    program_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_programs')
    
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Indicator(models.Model):
    """M&E Indicator"""
    INDICATOR_TYPES = [
        ('INPUT', 'Input'),
        ('OUTPUT', 'Output'),
        ('OUTCOME', 'Outcome'),
        ('IMPACT', 'Impact'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='indicators')
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    indicator_type = models.CharField(max_length=20, choices=INDICATOR_TYPES)
    
    definition = models.TextField()
    
    numerator_definition = models.TextField()
    denominator_definition = models.TextField(blank=True)
    
    calculation_method = models.TextField()
    
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    baseline_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    reporting_frequency = models.CharField(max_length=20, help_text="Monthly/Quarterly/Annual")
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class MonthlyReport(models.Model):
    """Monthly aggregated health metrics report"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='monthly_reports', null=True, blank=True)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='monthly_reports', null=True, blank=True)
    
    year = models.IntegerField()
    month = models.IntegerField(validators=[MinValueValidator(1), MinValueValidator(12)])
    
    # Service statistics
    outpatient_visits = models.IntegerField(default=0)
    inpatient_admissions = models.IntegerField(default=0)
    anc_visits = models.IntegerField(default=0)
    deliveries = models.IntegerField(default=0)
    immunizations_given = models.IntegerField(default=0)
    
    # Disease data
    malaria_cases = models.IntegerField(default=0)
    tb_cases = models.IntegerField(default=0)
    hiv_tests = models.IntegerField(default=0)
    
    # Additional metrics as JSON
    indicators = models.JSONField(default=dict, blank=True, help_text="Indicator code: value pairs")
    
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reports')
    approval_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['facility', 'year', 'month']]
        ordering = ['-year', '-month']

    def __str__(self):
        return f"Report {self.year}-{self.month:02d} - {self.facility or self.subcounty}"


class Campaign(models.Model):
    """Time-bound health campaign"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='campaigns')
    
    name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=50)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    target_area = models.CharField(max_length=100, help_text="Geographic scope")
    wards = models.ManyToManyField(Ward, related_name='campaigns', blank=True)
    
    target_population = models.IntegerField()
    people_reached = models.IntegerField(default=0)
    
    objectives = models.TextField()
    activities = models.JSONField(default=list, blank=True)
    
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    actual_expenditure = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    campaign_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, default='PLANNED')
    
    final_report = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


# ==================== COMMODITIES & SUPPLY CHAIN ====================

class Commodity(models.Model):
    """Health commodity/medicine"""
    COMMODITY_TYPES = [
        ('MEDICINE', 'Medicine'),
        ('VACCINE', 'Vaccine'),
        ('SUPPLY', 'Medical Supply'),
        ('EQUIPMENT', 'Equipment'),
        ('REAGENT', 'Laboratory Reagent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200)
    commodity_code = models.CharField(max_length=50, unique=True, db_index=True)
    commodity_type = models.CharField(max_length=20, choices=COMMODITY_TYPES)
    
    generic_name = models.CharField(max_length=200, blank=True)
    dosage_form = models.CharField(max_length=50, blank=True)
    strength = models.CharField(max_length=50, blank=True)
    
    unit_of_measure = models.CharField(max_length=20, help_text="Tablets/Vials/Boxes")
    
    reorder_level = models.IntegerField(default=0)
    ideal_stock_level = models.IntegerField(default=0)
    
    is_essential = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Commodities"
        indexes = [
            models.Index(fields=['commodity_code', 'commodity_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.commodity_code})"


class Supplier(models.Model):
    """Commodity supplier"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200)
    supplier_code = models.CharField(max_length=50, unique=True)
    
    contact_person = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    physical_address = models.TextField()
    
    kra_pin = models.CharField(max_length=20, blank=True)
    
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, help_text="0-5 rating")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Stock(models.Model):
    """Current stock at facility/warehouse"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='stocks')
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='stocks')
    
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = [['commodity', 'facility', 'batch_number']]
        indexes = [
            models.Index(fields=['facility', 'commodity']),
        ]

    def __str__(self):
        return f"{self.commodity.name} at {self.facility.name} - {self.quantity}"


class StockTransaction(models.Model):
    """Stock movement transaction"""
    TRANSACTION_TYPES = [
        ('IN', 'Stock In (Receipt)'),
        ('OUT', 'Stock Out (Issue)'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRANSFER', 'Transfer'),
        ('EXPIRED', 'Expired/Damaged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    quantity = models.IntegerField()
    transaction_date = models.DateTimeField(default=timezone.now)
    
    from_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_sent')
    to_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_received')
    
    reference_number = models.CharField(max_length=50, blank=True, help_text="PO/GRN/Issue number")
    
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transactions')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_number}"


class ProcurementRequest(models.Model):
    """Procurement/requisition request"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ORDERED', 'Ordered'),
        ('DELIVERED', 'Delivered'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_number = models.CharField(max_length=50, unique=True)
    
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='procurement_requests')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    request_date = models.DateField(default=timezone.now)
    
    items = models.JSONField(default=list, help_text="List of {commodity_id, quantity, justification}")
    
    justification = models.TextField()
    priority = models.CharField(max_length=20, default='NORMAL')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approval_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Procurement {self.request_number} - {self.facility.name}"


class PurchaseOrder(models.Model):
    """Purchase order to supplier"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Supplier'),
        ('CONFIRMED', 'Confirmed by Supplier'),
        ('PARTIAL_DELIVERY', 'Partially Delivered'),
        ('DELIVERED', 'Fully Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    po_number = models.CharField(max_length=50, unique=True)
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    procurement_request = models.ForeignKey(ProcurementRequest, on_delete=models.SET_NULL, null=True, blank=True)
    
    po_date = models.DateField(default=timezone.now)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    items = models.JSONField(default=list, help_text="List of {commodity_id, quantity, unit_price}")
    
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pos')
    
    terms_and_conditions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO {self.po_number} - {self.supplier.name}"


# ==================== LABORATORY ====================

class LabTestOrder(models.Model):
    """Laboratory test order"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SAMPLE_COLLECTED', 'Sample Collected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    
    patient = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='lab_orders')
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='lab_orders')
    
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_orders_made')
    order_date = models.DateTimeField(default=timezone.now)
    
    tests_requested = ArrayField(models.CharField(max_length=100), help_text="List of test names/codes")
    clinical_notes = models.TextField(blank=True)
    
    priority = models.CharField(max_length=20, default='ROUTINE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    sample_collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='samples_collected')
    sample_collection_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lab Order {self.order_number} - {self.patient.get_full_name()}"


class LabResult(models.Model):
    """Laboratory test result"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_order = models.ForeignKey(LabTestOrder, on_delete=models.CASCADE, related_name='results')
    
    test_name = models.CharField(max_length=100)
    test_code = models.CharField(max_length=50, blank=True)
    
    result_value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    
    result_status = models.CharField(max_length=20, help_text="Normal/Abnormal/Critical")
    
    tested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tests_performed')
    test_date = models.DateTimeField()
    
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='results_verified')
    verification_date = models.DateTimeField(null=True, blank=True)
    
    attachments = models.JSONField(default=list, blank=True, help_text="S3 URLs")
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_name} - {self.lab_order.order_number}"


# ==================== TRAINING & HR ====================

class StaffProfile(models.Model):
    """Extended staff profile"""
    CADRE_CHOICES = [
        ('DOCTOR', 'Medical Doctor'),
        ('CLINICAL_OFFICER', 'Clinical Officer'),
        ('NURSE', 'Registered Nurse'),
        ('ENROLLED_NURSE', 'Enrolled Nurse'),
        ('LAB_TECH', 'Laboratory Technician'),
        ('PHARMACIST', 'Pharmacist'),
        ('PHARMACEUTICAL_TECH', 'Pharmaceutical Technician'),
        ('NUTRITIONIST', 'Nutritionist'),
        ('HEALTH_RECORDS', 'Health Records Officer'),
        ('PUBLIC_HEALTH_OFFICER', 'Public Health Officer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    
    cadre = models.CharField(max_length=30, choices=CADRE_CHOICES)
    employee_number = models.CharField(max_length=50, unique=True)
    
    qualification = models.CharField(max_length=200)
    institution = models.CharField(max_length=200, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    
    license_number = models.CharField(max_length=50, blank=True)
    licensing_body = models.CharField(max_length=100, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    
    specialization = models.CharField(max_length=200, blank=True)
    years_of_experience = models.IntegerField(default=0)
    
    primary_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, related_name='primary_staff')
    
    employment_date = models.DateField()
    employment_status = models.CharField(max_length=20, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.cadre}"


class Training(models.Model):
    """Training session record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=50, blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=200)
    
    trainer = models.CharField(max_length=200)
    training_organization = models.CharField(max_length=200, blank=True)
    
    attendees = models.ManyToManyField(StaffProfile, through='TrainingAttendance', related_name='trainings')
    
    objectives = models.TextField()
    content_summary = models.TextField(blank=True)
    
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    organized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_name} ({self.start_date})"


class TrainingAttendance(models.Model):
    """Training attendance record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    
    attended = models.BooleanField(default=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    pre_test_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    post_test_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    certificate_issued = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=50, blank=True)
    
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['training', 'staff']]

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.training.course_name}"





# ==================== MATERNAL & CHILD HEALTH ====================

class PregnancyRecord(models.Model):
    """Pregnancy tracking record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    woman = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='pregnancies')
    
    lmp_date = models.DateField(help_text="Last Menstrual Period")
    edd = models.DateField(help_text="Estimated Delivery Date")
    
    gravida = models.IntegerField(help_text="Total pregnancies")
    parity = models.IntegerField(help_text="Number of births")
    
    risk_factors = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    is_high_risk = models.BooleanField(default=False)
    
    anc_visits_completed = models.IntegerField(default=0)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_outcome = models.CharField(max_length=50, blank=True)
    delivery_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pregnancy - {self.woman.get_full_name()} (EDD: {self.edd})"


class ANCVisit(models.Model):
    """Antenatal Care Visit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pregnancy = models.ForeignKey(PregnancyRecord, on_delete=models.CASCADE, related_name='anc_visits')
    
    visit_number = models.IntegerField()
    visit_date = models.DateField()
    gestation_weeks = models.IntegerField()
    
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True)
    attended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    hemoglobin = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    tests_done = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    supplements_given = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    next_visit_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pregnancy', 'visit_number']
        unique_together = [['pregnancy', 'visit_number']]

    def __str__(self):
        return f"ANC Visit {self.visit_number} - {self.pregnancy.woman.get_full_name()}"


class ImmunizationRecord(models.Model):
    """Child immunization record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='immunizations')
    
    vaccine_name = models.CharField(max_length=100)
    vaccine_code = models.CharField(max_length=20)
    dose_number = models.IntegerField()
    
    administration_date = models.DateField()
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True)
    
    batch_number = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    site = models.CharField(max_length=50, blank=True, help_text="Administration site")
    adverse_reaction = models.TextField(blank=True)
    
    next_dose_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['child', 'administration_date']

    def __str__(self):
        return f"{self.vaccine_name} - {self.child.get_full_name()}"


# ==================== PUBLIC HEALTH ACTIVITIES ====================

class HouseholdVisit(models.Model):
    """CHV household visit record"""
    VISIT_TYPES = [
        ('ROUTINE', 'Routine Visit'),
        ('FOLLOW_UP', 'Follow-up'),
        ('REFERRAL_CHECK', 'Referral Follow-up'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='visits')
    chv = models.ForeignKey(CommunityHealthVolunteer, on_delete=models.SET_NULL, null=True)
    
    visit_date = models.DateField()
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPES)
    
    members_present = models.IntegerField(default=0)
    services_provided = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    
    findings = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    referrals_made = models.IntegerField(default=0)
    
    next_visit_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"Visit to {self.household} on {self.visit_date}"


class OutreachEvent(models.Model):
    """Mass outreach/screening event"""
    EVENT_TYPES = [
        ('IMMUNIZATION', 'Mass Immunization'),
        ('SCREENING', 'Health Screening'),
        ('EDUCATION', 'Health Education'),
        ('DEWORMING', 'Deworming Campaign'),
        ('NUTRITION', 'Nutrition Program'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    location = models.CharField(max_length=200)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='outreach_events')
    
    target_population = models.IntegerField()
    people_reached = models.IntegerField(default=0)
    
    organizing_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True)
    partners = models.TextField(blank=True, help_text="Partner organizations")
    
    services_offered = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    commodities_used = models.JSONField(default=dict, blank=True)
    
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    report = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.start_date})"


class Screening(models.Model):
    """Individual screening record"""
    SCREENING_TYPES = [
        ('TB', 'Tuberculosis'),
        ('HIV', 'HIV'),
        ('DIABETES', 'Diabetes'),
        ('HYPERTENSION', 'Hypertension'),
        ('MALNUTRITION', 'Malnutrition'),
        ('CERVICAL_CANCER', 'Cervical Cancer'),
    ]
    
    RESULT_CHOICES = [
        ('NEGATIVE', 'Negative'),
        ('POSITIVE', 'Positive'),
        ('INCONCLUSIVE', 'Inconclusive'),
        ('REFERRED', 'Referred for Further Testing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='screenings')
    
    screening_type = models.CharField(max_length=30, choices=SCREENING_TYPES)
    screening_date = models.DateField()
    
    screened_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    outreach_event = models.ForeignKey(OutreachEvent, on_delete=models.SET_NULL, null=True, blank=True)
    
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    result_details = models.JSONField(default=dict, blank=True)
    
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.screening_type} - {self.person.get_full_name()}"


# ==================== REFERRALS ====================

class Referral(models.Model):
    """Patient referral tracking"""
    URGENCY_LEVELS = [
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('IN_TRANSIT', 'In Transit'),
        ('ARRIVED', 'Arrived'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referral_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='referrals')
    
    from_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, related_name='referrals_sent')
    to_facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, related_name='referrals_received')
    
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='referrals_made')
    
    referral_date = models.DateTimeField(default=timezone.now)
    urgency = models.CharField(max_length=20, choices=URGENCY_LEVELS)
    
    reason = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment_given = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals_accepted')
    accepted_date = models.DateTimeField(null=True, blank=True)
    
    arrival_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    outcome = models.TextField(blank=True)
    feedback_to_referring_facility = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-referral_date']
        indexes = [
            models.Index(fields=['referral_number', 'status']),
        ]

    def __str__(self):
        return f"Referral {self.referral_number} - {self.person.get_full_name()}"


class ReferralFollowUp(models.Model):
    """Follow-up on referral"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='follow_ups')
    
    follow_up_date = models.DateTimeField(default=timezone.now)
    followed_up_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    status_update = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    
    created_at = models