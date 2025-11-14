"""
Django management command to seed Wajir County health data
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.apps import apps
from datetime import date, timedelta
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds Wajir County health system data'

    def handle(self, *args, **kwargs):
        # Import models dynamically to avoid circular import
        self.County = apps.get_model('main_application', 'County')
        self.SubCounty = apps.get_model('main_application', 'SubCounty')
        self.Ward = apps.get_model('main_application', 'Ward')
        self.Role = apps.get_model('main_application', 'Role')
        self.User = apps.get_model('main_application', 'User')
        self.Facility = apps.get_model('main_application', 'Facility')
        self.CommunityUnit = apps.get_model('main_application', 'CommunityUnit')
        self.CommunityHealthVolunteer = apps.get_model('main_application', 'CommunityHealthVolunteer')
        self.Household = apps.get_model('main_application', 'Household')
        self.Person = apps.get_model('main_application', 'Person')
        self.Commodity = apps.get_model('main_application', 'Commodity')
        self.Supplier = apps.get_model('main_application', 'Supplier')
        self.Stock = apps.get_model('main_application', 'Stock')
        self.Program = apps.get_model('main_application', 'Program')
        self.Indicator = apps.get_model('main_application', 'Indicator')
        self.StaffProfile = apps.get_model('main_application', 'StaffProfile')
        self.PregnancyRecord = apps.get_model('main_application', 'PregnancyRecord')
        self.ANCVisit = apps.get_model('main_application', 'ANCVisit')
        self.ImmunizationRecord = apps.get_model('main_application', 'ImmunizationRecord')
        self.SurveillanceReport = apps.get_model('main_application', 'SurveillanceReport')
        self.MortalityReport = apps.get_model('main_application', 'MortalityReport')
        self.Training = apps.get_model('main_application', 'Training')
        self.TrainingAttendance = apps.get_model('main_application', 'TrainingAttendance')
        self.HouseholdVisit = apps.get_model('main_application', 'HouseholdVisit')
        self.OutreachEvent = apps.get_model('main_application', 'OutreachEvent')
        self.Screening = apps.get_model('main_application', 'Screening')
        self.Referral = apps.get_model('main_application', 'Referral')
        
        self.stdout.write('Starting Wajir County data seeding...')
        
        # Clear existing data (optional - comment out if you want to preserve data)
        self.stdout.write('Clearing existing data...')
        self.clear_data()
        
        # Seed in order of dependencies
        self.seed_county()
        self.seed_subcounties()
        self.seed_wards()
        self.seed_roles()
        self.seed_users()
        self.seed_facilities()
        self.seed_community_units()
        self.seed_chvs()
        self.seed_households()
        self.seed_persons()
        self.seed_commodities()
        self.seed_suppliers()
        self.seed_stocks()
        self.seed_programs()
        self.seed_indicators()
        self.seed_staff_profiles()
        self.seed_pregnancies()
        self.seed_anc_visits()
        self.seed_immunizations()
        self.seed_surveillance_reports()
        self.seed_mortality_reports()
        self.seed_trainings()
        self.seed_household_visits()
        self.seed_outreach_events()
        self.seed_screenings()
        self.seed_referrals()
        
        self.stdout.write(self.style.SUCCESS('✓ Wajir County data seeded successfully!'))

    def clear_data(self):
        """Clear existing data"""
        models_to_clear = [
            self.Referral, self.Screening, self.OutreachEvent, self.HouseholdVisit, 
            self.TrainingAttendance, self.Training, self.MortalityReport, 
            self.SurveillanceReport, self.ImmunizationRecord, self.ANCVisit, 
            self.PregnancyRecord, self.StaffProfile, self.Indicator, self.Program, 
            self.Stock, self.Supplier, self.Commodity, self.Person, self.Household, 
            self.CommunityHealthVolunteer, self.CommunityUnit, self.Facility, 
            self.User, self.Role, self.Ward, self.SubCounty, self.County
        ]
        for model in models_to_clear:
            model.objects.all().delete()

    def seed_county(self):
        self.stdout.write('Seeding county...')
        self.county = self.County.objects.create(
            name='Wajir',
            code='WJR',
            population=781263,  # 2019 Census
            contact_person='Dr. Ahmed Hassan',
            phone='+254720123456',
            email='health@wajir.go.ke'
        )

    def seed_subcounties(self):
        self.stdout.write('Seeding sub-counties...')
        subcounties_data = [
            {'name': 'Wajir North', 'code': 'WJR-N', 'population': 89456},
            {'name': 'Wajir East', 'code': 'WJR-E', 'population': 145234},
            {'name': 'Wajir West', 'code': 'WJR-W', 'population': 123567},
            {'name': 'Wajir South', 'code': 'WJR-S', 'population': 178934},
            {'name': 'Tarbaj', 'code': 'WJR-TB', 'population': 112456},
            {'name': 'Eldas', 'code': 'WJR-EL', 'population': 131616},
        ]
        
        self.subcounties = []
        for data in subcounties_data:
            sc = self.SubCounty.objects.create(county=self.county, **data)
            self.subcounties.append(sc)

    def seed_wards(self):
        self.stdout.write('Seeding wards...')
        wards_data = {
            'Wajir North': ['Bute', 'Danyere', 'Gurar', 'Batalu'],
            'Wajir East': ['Wagberi', 'Township', 'Barwaqo', 'Khorof Harar'],
            'Wajir West': ['Hadado Athibohol', 'Ganyure Wagalla', 'Iftin', 'Ademasajide'],
            'Wajir South': ['Habasweyn', 'Diif', 'Benane', 'Lagboghol'],
            'Tarbaj': ['Tarbaj', 'Wargadud', 'Elben', 'Sarman'],
            'Eldas': ['Della', 'Lakoley', 'Elnur', 'Goreale'],
        }
        
        self.wards = []
        ward_counter = 1
        for subcounty in self.subcounties:
            for ward_name in wards_data[subcounty.name]:
                ward = self.Ward.objects.create(
                    subcounty=subcounty,
                    name=ward_name,
                    code=f'{subcounty.code}-W{ward_counter:02d}',
                    population=random.randint(15000, 35000)
                )
                self.wards.append(ward)
                ward_counter += 1

    def seed_roles(self):
        self.stdout.write('Seeding roles...')
        roles_data = [
            ('COUNTY_ADMIN', 'County level administrator', 10),
            ('PUBLIC_HEALTH_OFFICER', 'Public health officer', 8),
            ('ME_OFFICER', 'Monitoring and evaluation officer', 7),
            ('FACILITY_MANAGER', 'Health facility manager', 6),
            ('CLINICAL_OFFICER', 'Clinical officer', 5),
            ('NURSE', 'Registered nurse', 5),
            ('LAB_TECH', 'Laboratory technician', 4),
            ('PHARMACIST', 'Pharmacist', 4),
            ('DATA_CLERK', 'Data entry clerk', 3),
            ('CHV', 'Community health volunteer', 2),
            ('CHEW', 'Community health extension worker', 3),
        ]
        
        self.roles = {}
        for name, desc, level in roles_data:
            role = self.Role.objects.create(name=name, description=desc, level=level)
            self.roles[name] = role

    def seed_users(self):
        self.stdout.write('Seeding users...')
        users_data = [
            {
                'email': 'admin@wajir.health.go.ke',
                'phone': '+254720000001',
                'first_name': 'Ahmed',
                'last_name': 'Hassan',
                'national_id': '12345678',
                'roles': ['COUNTY_ADMIN'],
                'subcounty': None,
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'pho@wajir.health.go.ke',
                'phone': '+254720000002',
                'first_name': 'Fatuma',
                'last_name': 'Ibrahim',
                'national_id': '23456789',
                'roles': ['PUBLIC_HEALTH_OFFICER'],
                'subcounty': 0
            },
            {
                'email': 'me@wajir.health.go.ke',
                'phone': '+254720000003',
                'first_name': 'Hassan',
                'last_name': 'Mohamed',
                'national_id': '34567890',
                'roles': ['ME_OFFICER'],
                'subcounty': 0
            },
        ]
        
        # Add facility managers
        manager_names = [
            ('Abdi', 'Ali'), ('Halima', 'Hussein'), ('Omar', 'Abdi'),
            ('Amina', 'Mohamed'), ('Yusuf', 'Ibrahim'), ('Zamzam', 'Hassan')
        ]
        for i, (fname, lname) in enumerate(manager_names):
            users_data.append({
                'email': f'{fname.lower()}.{lname.lower()}@wajir.health.go.ke',
                'phone': f'+25472000001{i+4}',
                'first_name': fname,
                'last_name': lname,
                'national_id': f'{45678900 + i}',
                'roles': ['FACILITY_MANAGER'],
                'subcounty': i
            })
        
        # Add staff
        staff_data = [
            ('Clinical Officers', 'CLINICAL_OFFICER', 15),
            ('Nurses', 'NURSE', 25),
            ('Lab Technicians', 'LAB_TECH', 10),
            ('Pharmacists', 'PHARMACIST', 8),
            ('Data Clerks', 'DATA_CLERK', 12),
        ]
        
        first_names = ['Abdi', 'Fatuma', 'Hassan', 'Halima', 'Omar', 'Amina', 'Yusuf', 'Zamzam', 'Ali', 'Maryam']
        last_names = ['Ali', 'Ibrahim', 'Mohamed', 'Hassan', 'Abdi', 'Hussein', 'Ahmed', 'Omar']
        
        counter = 100
        for role_name, role_key, count in staff_data:
            for i in range(count):
                fname = random.choice(first_names)
                lname = random.choice(last_names)
                users_data.append({
                    'email': f'{role_key.lower()}{counter}@wajir.health.go.ke',
                    'phone': f'+254720{counter:06d}',
                    'first_name': fname,
                    'last_name': lname,
                    'national_id': f'{56789000 + counter}',
                    'roles': [role_key],
                    'subcounty': random.randint(0, len(self.subcounties) - 1)
                })
                counter += 1
        
        self.users = []
        for data in users_data:
            roles = data.pop('roles')
            subcounty_idx = data.pop('subcounty')
            
            user = self.User.objects.create(
                password=make_password('password123'),
                county=self.county,
                subcounty=self.subcounties[subcounty_idx] if subcounty_idx is not None else None,
                is_active=True,
                **data
            )
            
            for role_name in roles:
                user.roles.add(self.roles[role_name])
            
            self.users.append(user)

    def seed_facilities(self):
        self.stdout.write('Seeding facilities...')
        
        major_facilities = [
            {
                'name': 'Wajir County Referral Hospital',
                'facility_code': 'WCRH001',
                'facility_type': 'COUNTY_REFERRAL',
                'ward_idx': 5,
                'bed_capacity': 150,
                'lat': 1.7471,
                'lon': 40.0573
            },
            {
                'name': 'Habaswein Sub-County Hospital',
                'facility_code': 'HSCH002',
                'facility_type': 'SUB_COUNTY_HOSPITAL',
                'ward_idx': 12,
                'bed_capacity': 80,
                'lat': 1.5234,
                'lon': 39.9876
            },
            {
                'name': 'Tarbaj Sub-County Hospital',
                'facility_code': 'TSCH003',
                'facility_type': 'SUB_COUNTY_HOSPITAL',
                'ward_idx': 16,
                'bed_capacity': 60,
                'lat': 1.8923,
                'lon': 40.2341
            },
        ]
        
        health_centres = [
            'Wagberi HC', 'Barwaqo HC', 'Bute HC', 'Hadado HC',
            'Ganyure HC', 'Iftin HC', 'Diif HC', 'Benane HC',
            'Wargadud HC', 'Elben HC', 'Della HC', 'Lakoley HC'
        ]
        
        dispensary_names = [
            'Danyere', 'Gurar', 'Batalu', 'Khorof Harar', 'Ademasajide',
            'Lagboghol', 'Sarman', 'Elnur', 'Goreale', 'Diff'
        ]
        
        self.facilities = []
        facility_code = 100
        
        for data in major_facilities:
            ward_idx = data.pop('ward_idx')
            facility_type = data.pop('facility_type')
            lat = data.pop('lat')
            lon = data.pop('lon')
            
            facility = self.Facility.objects.create(
                ward=self.wards[ward_idx],
                subcounty=self.wards[ward_idx].subcounty,
                facility_type=facility_type,
                phone=f'+254720{facility_code:06d}',
                email=f'{data["facility_code"].lower()}@wajir.health.go.ke',
                is_operational=True,
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lon)),
                **data
            )
            self.facilities.append(facility)
            facility_code += 1
        
        for i, name in enumerate(health_centres):
            ward = self.wards[i % len(self.wards)]
            facility = self.Facility.objects.create(
                name=name,
                facility_code=f'HC{facility_code:04d}',
                facility_type='HEALTH_CENTRE',
                ward=ward,
                subcounty=ward.subcounty,
                bed_capacity=random.randint(20, 40),
                phone=f'+254720{facility_code:06d}',
                is_operational=True
            )
            self.facilities.append(facility)
            facility_code += 1
        
        for name in dispensary_names:
            ward = random.choice(self.wards)
            facility = self.Facility.objects.create(
                name=f'{name} Dispensary',
                facility_code=f'DISP{facility_code:04d}',
                facility_type='DISPENSARY',
                ward=ward,
                subcounty=ward.subcounty,
                bed_capacity=random.randint(5, 15),
                phone=f'+254720{facility_code:06d}',
                is_operational=True
            )
            self.facilities.append(facility)
            facility_code += 1

    def seed_community_units(self):
        self.stdout.write('Seeding community units...')
        self.community_units = []
        
        for i, ward in enumerate(self.wards[:15]):
            chu = self.CommunityUnit.objects.create(
                name=f'{ward.name} CHU',
                code=f'CHU{i+1:03d}',
                ward=ward,
                linked_facility=random.choice([f for f in self.facilities if f.ward == ward]) if any(f.ward == ward for f in self.facilities) else random.choice(self.facilities),
                target_population=random.randint(3000, 8000),
                target_households=random.randint(500, 1200),
                is_active=True,
                established_date=date(2018, random.randint(1, 12), random.randint(1, 28))
            )
            self.community_units.append(chu)

    def seed_chvs(self):
        self.stdout.write('Seeding CHVs...')
        self.chvs = []
        
        first_names = ['Abdi', 'Fatuma', 'Hassan', 'Halima', 'Omar', 'Amina', 'Yusuf', 'Zamzam', 'Ali', 'Maryam',
                      'Ibrahim', 'Safia', 'Mohamed', 'Asha', 'Ahmed']
        last_names = ['Ali', 'Ibrahim', 'Mohamed', 'Hassan', 'Abdi', 'Hussein', 'Ahmed', 'Omar', 'Yusuf', 'Osman']
        
        chv_counter = 1
        for chu in self.community_units:
            num_chvs = random.randint(5, 10)
            for i in range(num_chvs):
                fname = random.choice(first_names)
                lname = random.choice(last_names)
                gender = random.choice(['M', 'F'])
                
                user = self.User.objects.create(
                    email=f'chv{chv_counter:04d}@wajir.health.go.ke',
                    phone=f'+254721{chv_counter:06d}',
                    first_name=fname,
                    last_name=lname,
                    national_id=f'{67890000 + chv_counter}',
                    password=make_password('password123'),
                    county=self.county,
                    subcounty=chu.ward.subcounty,
                    is_active=True
                )
                user.roles.add(self.roles['CHV'])
                
                chv = self.CommunityHealthVolunteer.objects.create(
                    user=user,
                    community_unit=chu,
                    national_id=f'{67890000 + chv_counter}',
                    chv_number=f'CHV{chv_counter:05d}',
                    date_of_birth=date(random.randint(1985, 2000), random.randint(1, 12), random.randint(1, 28)),
                    gender=gender,
                    training_date=date(2019, random.randint(1, 12), random.randint(1, 28)),
                    certification_date=date(2020, random.randint(1, 12), random.randint(1, 28)),
                    is_active=True,
                    households_assigned=random.randint(20, 40)
                )
                self.chvs.append(chv)
                chv_counter += 1

    def seed_households(self):
        self.stdout.write('Seeding households...')
        self.households = []
        
        villages = ['Central', 'East', 'West', 'North', 'South', 'Upper', 'Lower']
        water_sources = ['Borehole', 'River', 'Rain Water', 'Piped Water', 'Water Vendor']
        
        hh_counter = 1
        for chu in self.community_units:
            num_households = random.randint(80, 150)
            for i in range(num_households):
                chv = random.choice([c for c in self.chvs if c.community_unit == chu])
                
                hh = self.Household.objects.create(
                    household_number=f'WJR-HH{hh_counter:06d}',
                    community_unit=chu,
                    ward=chu.ward,
                    assigned_chv=chv,
                    village=f'{random.choice(villages)} {chu.ward.name}',
                    number_of_members=random.randint(3, 12),
                    has_toilet=random.choice([True, False, None]),
                    water_source=random.choice(water_sources),
                    registration_date=date(2020, random.randint(1, 12), random.randint(1, 28)),
                    is_active=True
                )
                self.households.append(hh)
                hh_counter += 1
                
                if hh_counter > 2000:
                    break
            if hh_counter > 2000:
                break

    def seed_persons(self):
        self.stdout.write('Seeding persons...')
        self.persons = []
        
        first_names_male = ['Abdi', 'Hassan', 'Omar', 'Yusuf', 'Ali', 'Ibrahim', 'Mohamed', 'Ahmed', 'Abdullahi', 'Ismail']
        first_names_female = ['Fatuma', 'Halima', 'Amina', 'Zamzam', 'Maryam', 'Safia', 'Asha', 'Fadumo', 'Habiba', 'Suad']
        last_names = ['Ali', 'Ibrahim', 'Mohamed', 'Hassan', 'Abdi', 'Hussein', 'Ahmed', 'Omar', 'Yusuf', 'Osman']
        
        person_counter = 1
        for hh in self.households[:500]:
            num_members = hh.number_of_members
            
            for i in range(num_members):
                gender = random.choice(['M', 'F'])
                is_head = (i == 0)
                
                age = random.choices(
                    [random.randint(0, 5), random.randint(6, 17), random.randint(18, 60), random.randint(61, 85)],
                    weights=[0.2, 0.3, 0.4, 0.1]
                )[0]
                
                dob = date.today() - timedelta(days=age*365)
                
                fname = random.choice(first_names_male if gender == 'M' else first_names_female)
                lname = random.choice(last_names)
                
                person = self.Person.objects.create(
                    first_name=fname,
                    last_name=lname,
                    date_of_birth=dob,
                    gender=gender,
                    national_id=f'{78900000 + person_counter}' if age >= 18 else None,
                    phone=f'+254722{person_counter:06d}' if age >= 18 and random.random() > 0.5 else '',
                    household=hh,
                    is_household_head=is_head,
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', '']),
                    is_alive=True
                )
                self.persons.append(person)
                person_counter += 1

    def seed_commodities(self):
        self.stdout.write('Seeding commodities...')
        commodities_data = [
            {'name': 'Paracetamol 500mg', 'code': 'PARA500', 'type': 'MEDICINE', 'generic': 'Paracetamol', 'form': 'Tablet', 'strength': '500mg', 'uom': 'Tablets'},
            {'name': 'Amoxicillin 250mg', 'code': 'AMOX250', 'type': 'MEDICINE', 'generic': 'Amoxicillin', 'form': 'Capsule', 'strength': '250mg', 'uom': 'Capsules'},
            {'name': 'Artemether/Lumefantrine (AL)', 'code': 'AL', 'type': 'MEDICINE', 'generic': 'AL', 'form': 'Tablet', 'strength': '20/120mg', 'uom': 'Tablets'},
            {'name': 'ORS Sachets', 'code': 'ORS', 'type': 'MEDICINE', 'generic': 'ORS', 'form': 'Powder', 'strength': '', 'uom': 'Sachets'},
            {'name': 'Measles Vaccine', 'code': 'MEASLES', 'type': 'VACCINE', 'generic': 'Measles', 'form': 'Injection', 'strength': '', 'uom': 'Vials'},
            {'name': 'BCG Vaccine', 'code': 'BCG', 'type': 'VACCINE', 'generic': 'BCG', 'form': 'Injection', 'strength': '', 'uom': 'Vials'},
            {'name': 'Pentavalent Vaccine', 'code': 'PENTA', 'type': 'VACCINE', 'generic': 'Pentavalent', 'form': 'Injection', 'strength': '', 'uom': 'Vials'},
            {'name': 'Gloves (Surgical)', 'code': 'GLOVE-S', 'type': 'SUPPLY', 'generic': '', 'form': '', 'strength': '', 'uom': 'Pairs'},
            {'name': 'Syringes 5ml', 'code': 'SYR5', 'type': 'SUPPLY', 'generic': '', 'form': '', 'strength': '5ml', 'uom': 'Pieces'},
            {'name': 'HIV Test Kits', 'code': 'HIV-TEST', 'type': 'REAGENT', 'generic': '', 'form': '', 'strength': '', 'uom': 'Tests'},
        ]
        
        self.commodities = []
        for data in commodities_data:
            commodity = self.Commodity.objects.create(
                name=data['name'],
                commodity_code=data['code'],
                commodity_type=data['type'],
                generic_name=data['generic'],
                dosage_form=data['form'],
                strength=data['strength'],
                unit_of_measure=data['uom'],
                reorder_level=random.randint(100, 500),
                ideal_stock_level=random.randint(1000, 5000),
                is_essential=random.choice([True, False]),
                is_active=True
            )
            self.commodities.append(commodity)

    def seed_suppliers(self):
        self.stdout.write('Seeding suppliers...')
        suppliers_data = [
            {'name': 'KEMSA', 'code': 'KEMSA', 'contact': 'John Kamau', 'phone': '+254722111111', 'email': 'orders@kemsa.co.ke'},
            {'name': 'Dawa Ltd', 'code': 'DAWA', 'contact': 'Mary Njeri', 'phone': '+254722222222', 'email': 'sales@dawaltd.co.ke'},
            {'name': 'MedSupply Kenya', 'code': 'MEDSUP', 'contact': 'Peter Otieno', 'phone': '+254722333333', 'email': 'info@medsupply.co.ke'},
        ]
        
        self.suppliers = []
        for data in suppliers_data:
            supplier = self.Supplier.objects.create(
                name=data['name'],
                supplier_code=data['code'],
                contact_person=data['contact'],
                phone=data['phone'],
                email=data['email'],
                physical_address='Nairobi, Kenya',
                is_active=True
            )
            self.suppliers.append(supplier)

    def seed_stocks(self):
        self.stdout.write('Seeding stock records...')
        
        for facility in self.facilities[:10]:
            for commodity in self.commodities:
                self.Stock.objects.create(
                    commodity=commodity,
                    facility=facility,
                    quantity=random.randint(50, 1000),
                    batch_number=f'BATCH{random.randint(1000, 9999)}',
                    expiry_date=date.today() + timedelta(days=random.randint(180, 730)),
                    unit_cost=Decimal(str(random.uniform(5, 500))),
                    updated_by=random.choice(self.users)
                )

    def seed_programs(self):
        self.stdout.write('Seeding programs...')
        programs_data = [
            {'name': 'Maternal & Child Health', 'code': 'MCH', 'desc': 'Maternal and child health services'},
            {'name': 'Malaria Control', 'code': 'MAL', 'desc': 'Malaria prevention and treatment'},
            {'name': 'TB Control', 'code': 'TB', 'desc': 'Tuberculosis prevention and treatment'},
            {'name': 'HIV/AIDS Program', 'code': 'HIV', 'desc': 'HIV prevention, testing, and treatment'},
        ]
        
        self.programs = []
        for data in programs_data:
            program = self.Program.objects.create(
                name=data['name'],
                code=data['code'],
                description=data['desc'],
                start_date=date(2020, 1, 1),
                county=self.county,
                program_manager=random.choice([u for u in self.users if self.roles['PUBLIC_HEALTH_OFFICER'] in u.roles.all()]),
                budget=Decimal(str(random.randint(5000000, 20000000))),
                is_active=True
            )
            self.programs.append(program)

    def seed_indicators(self):
        self.stdout.write('Seeding indicators...')
        
        for program in self.programs:
            for i in range(3):
                self.Indicator.objects.create(
                    program=program,
                    name=f'{program.name} Indicator {i+1}',
                    code=f'{program.code}-IND{i+1}',
                    indicator_type=random.choice(['OUTPUT', 'OUTCOME', 'IMPACT']),
                    definition=f'Indicator definition for {program.name}',
                    numerator_definition='Number of cases',
                    denominator_definition='Target population',
                    calculation_method='(Numerator/Denominator) * 100',
                    target_value=Decimal(str(random.randint(60, 95))),
                    baseline_value=Decimal(str(random.randint(30, 60))),
                    reporting_frequency='Monthly',
                    is_active=True
                )

    def seed_staff_profiles(self):
        self.stdout.write('Seeding staff profiles...')
        
        clinical_users = [u for u in self.users if any(
            r.name in ['CLINICAL_OFFICER', 'NURSE', 'LAB_TECH', 'PHARMACIST'] 
            for r in u.roles.all()
        )]
        
        cadre_map = {
            'CLINICAL_OFFICER': 'CLINICAL_OFFICER',
            'NURSE': 'NURSE',
            'LAB_TECH': 'LAB_TECH',
            'PHARMACIST': 'PHARMACIST'
        }
        
        qualifications = {
            'CLINICAL_OFFICER': 'Diploma in Clinical Medicine',
            'NURSE': 'Diploma in Nursing',
            'LAB_TECH': 'Diploma in Medical Laboratory Sciences',
            'PHARMACIST': 'Bachelor of Pharmacy'
        }
        
        institutions = ['Kenya Medical Training College', 'University of Nairobi', 'Moi University', 'Kenyatta University']
        
        self.staff_profiles = []
        emp_counter = 1000
        
        for user in clinical_users[:30]:
            role_name = user.roles.first().name
            cadre = cadre_map.get(role_name)
            
            if cadre:
                profile = self.StaffProfile.objects.create(
                    user=user,
                    cadre=cadre,
                    employee_number=f'WJR-EMP{emp_counter:05d}',
                    qualification=qualifications[cadre],
                    institution=random.choice(institutions),
                    graduation_year=random.randint(2005, 2020),
                    license_number=f'LIC{random.randint(10000, 99999)}',
                    licensing_body='Nursing Council of Kenya' if cadre == 'NURSE' else 'Clinical Officers Council',
                    license_expiry=date.today() + timedelta(days=random.randint(365, 1095)),
                    years_of_experience=random.randint(2, 20),
                    primary_facility=random.choice(self.facilities),
                    employment_date=date(random.randint(2015, 2023), random.randint(1, 12), 1),
                    employment_status='ACTIVE'
                )
                self.staff_profiles.append(profile)
                emp_counter += 1

    def seed_pregnancies(self):
        self.stdout.write('Seeding pregnancy records...')
        self.pregnancies = []
        
        women = [p for p in self.persons if p.gender == 'F' and 15 <= p.get_age() <= 49][:50]
        
        for woman in women:
            if random.random() > 0.7:
                lmp = date.today() - timedelta(days=random.randint(30, 250))
                edd = lmp + timedelta(days=280)
                
                pregnancy = self.PregnancyRecord.objects.create(
                    woman=woman,
                    lmp_date=lmp,
                    edd=edd,
                    gravida=random.randint(1, 6),
                    parity=random.randint(0, 5),
                    risk_factors=['None'] if random.random() > 0.3 else ['Anemia', 'Previous C-Section'],
                    is_high_risk=random.choice([True, False]),
                    anc_visits_completed=random.randint(0, 4),
                    is_active=True if edd > date.today() else False,
                    delivery_date=None if edd > date.today() else edd + timedelta(days=random.randint(-7, 7)),
                    delivery_outcome='Live Birth' if edd <= date.today() else '',
                    delivery_facility=random.choice(self.facilities) if edd <= date.today() else None
                )
                self.pregnancies.append(pregnancy)

    def seed_anc_visits(self):
        self.stdout.write('Seeding ANC visits...')
        
        for pregnancy in self.pregnancies:
            num_visits = pregnancy.anc_visits_completed
            
            for visit_num in range(1, num_visits + 1):
                weeks = 12 + (visit_num - 1) * 8
                visit_date = pregnancy.lmp_date + timedelta(weeks=weeks)
                
                if visit_date <= date.today():
                    self.ANCVisit.objects.create(
                        pregnancy=pregnancy,
                        visit_number=visit_num,
                        visit_date=visit_date,
                        gestation_weeks=weeks,
                        facility=random.choice(self.facilities),
                        attended_by=random.choice(self.users),
                        weight=Decimal(str(random.uniform(55, 85))),
                        blood_pressure=f'{random.randint(110, 140)}/{random.randint(70, 90)}',
                        hemoglobin=Decimal(str(random.uniform(9.5, 13.5))),
                        tests_done=['HIV Test', 'Blood Group', 'Urinalysis'],
                        supplements_given=['Iron', 'Folic Acid', 'Calcium'],
                        next_visit_date=visit_date + timedelta(weeks=8)
                    )

    def seed_immunizations(self):
        self.stdout.write('Seeding immunization records...')
        
        children = [p for p in self.persons if p.get_age() < 5][:100]
        
        vaccines = [
            ('BCG', 'BCG', 1, 0),
            ('OPV', 'OPV0', 1, 0),
            ('Pentavalent', 'PENTA1', 1, 6),
            ('Pentavalent', 'PENTA2', 2, 10),
            ('Pentavalent', 'PENTA3', 3, 14),
            ('Measles', 'MEASLES1', 1, 36),
        ]
        
        for child in children:
            age_weeks = child.get_age() * 52
            
            for vaccine_name, vaccine_code, dose, min_weeks in vaccines:
                if age_weeks >= min_weeks:
                    admin_date = child.date_of_birth + timedelta(weeks=min_weeks + random.randint(0, 4))
                    
                    if admin_date <= date.today():
                        self.ImmunizationRecord.objects.create(
                            child=child,
                            vaccine_name=vaccine_name,
                            vaccine_code=vaccine_code,
                            dose_number=dose,
                            administration_date=admin_date,
                            administered_by=random.choice(self.users),
                            facility=random.choice(self.facilities),
                            batch_number=f'BATCH{random.randint(1000, 9999)}',
                            expiry_date=admin_date + timedelta(days=365),
                            site='Left Thigh' if dose == 1 else 'Right Thigh'
                        )

    def seed_surveillance_reports(self):
        self.stdout.write('Seeding surveillance reports...')
        
        diseases = [
            ('Malaria', 'P51'),
            ('Acute Watery Diarrhea', 'A09'),
            ('Measles', 'B05'),
            ('Tuberculosis', 'A15'),
            ('Cholera', 'A00'),
        ]
        
        report_counter = 1
        for i in range(20):
            disease_name, disease_code = random.choice(diseases)
            report_date = date.today() - timedelta(days=random.randint(1, 180))
            
            self.SurveillanceReport.objects.create(
                report_number=f'SURV-WJR-{report_counter:05d}',
                disease_name=disease_name,
                disease_code=disease_code,
                report_date=report_date,
                reporting_period_start=report_date - timedelta(days=7),
                reporting_period_end=report_date,
                ward=random.choice(self.wards),
                facility=random.choice(self.facilities),
                source=random.choice(['FACILITY', 'CHV', 'LABORATORY']),
                reported_by=random.choice(self.users),
                cases_suspected=random.randint(5, 50),
                cases_confirmed=random.randint(2, 30),
                deaths=random.randint(0, 3),
                cases_under_5=random.randint(1, 15),
                cases_5_to_15=random.randint(1, 10),
                cases_over_15=random.randint(1, 20),
                males=random.randint(5, 25),
                females=random.randint(5, 25),
                outbreak_declared=random.choice([True, False]),
                response_initiated=random.choice([True, False])
            )
            report_counter += 1

    def seed_mortality_reports(self):
        self.stdout.write('Seeding mortality reports...')
        
        deceased_persons = random.sample(self.persons, min(10, len(self.persons)))
        
        categories = ['NEONATAL', 'INFANT', 'CHILD', 'MATERNAL', 'ADULT']
        causes = [
            'Respiratory Failure',
            'Severe Malaria',
            'Complications of Childbirth',
            'Pneumonia',
            'Diarrheal Disease'
        ]
        
        for person in deceased_persons:
            death_date = date.today() - timedelta(days=random.randint(1, 365))
            person.is_alive = False
            person.date_of_death = death_date
            person.save()
            
            age = person.get_age()
            if age < 0.08:
                category = 'NEONATAL'
            elif age < 1:
                category = 'INFANT'
            elif age < 5:
                category = 'CHILD'
            elif person.gender == 'F' and 15 <= age <= 49:
                category = random.choice(['MATERNAL', 'ADULT'])
            else:
                category = 'ADULT'
            
            self.MortalityReport.objects.create(
                deceased_person=person,
                death_category=category,
                date_of_death=death_date,
                place_of_death=random.choice(['Home', 'Facility', 'Transit']),
                facility=random.choice(self.facilities) if random.random() > 0.5 else None,
                ward=person.household.ward,
                immediate_cause=random.choice(causes),
                underlying_cause=random.choice(causes),
                pregnancy_related=(category == 'MATERNAL'),
                timing='Postpartum' if category == 'MATERNAL' else '',
                reported_by=random.choice(self.users),
                report_date=death_date + timedelta(days=random.randint(1, 7)),
                autopsy_done=random.choice([True, False]),
                death_certificate_issued=True
            )

    def seed_trainings(self):
        self.stdout.write('Seeding training records...')
        self.trainings = []
        
        courses = [
            'Integrated Management of Childhood Illness (IMCI)',
            'Maternal Newborn Child Health',
            'TB DOTS Training',
            'HIV Testing and Counseling',
            'Infection Prevention and Control',
            'Emergency Obstetric Care'
        ]
        
        for i in range(10):
            start_date = date.today() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(3, 7))
            
            training = self.Training.objects.create(
                course_name=random.choice(courses),
                course_code=f'TRN{i+1:03d}',
                start_date=start_date,
                end_date=end_date,
                venue=f'{random.choice(self.facilities).name}',
                trainer='Ministry of Health Trainer',
                training_organization='Ministry of Health',
                objectives='Improve clinical skills and knowledge',
                budget=Decimal(str(random.randint(50000, 200000))),
                organized_by=random.choice(self.users)
            )
            self.trainings.append(training)

    def seed_household_visits(self):
        self.stdout.write('Seeding household visits...')
        
        services = [
            'Health Education',
            'Malaria Prevention',
            'Child Growth Monitoring',
            'Immunization Reminder',
            'ANC Follow-up',
            'Disease Surveillance'
        ]
        
        for hh in self.households[:200]:
            num_visits = random.randint(2, 8)
            
            for i in range(num_visits):
                visit_date = date.today() - timedelta(days=random.randint(1, 180))
                
                self.HouseholdVisit.objects.create(
                    household=hh,
                    chv=hh.assigned_chv,
                    visit_date=visit_date,
                    visit_type=random.choice(['ROUTINE', 'FOLLOW_UP', 'REFERRAL_CHECK']),
                    members_present=random.randint(1, hh.number_of_members),
                    services_provided=random.sample(services, k=random.randint(1, 3)),
                    findings='Household members in good health',
                    action_taken='Provided health education',
                    referrals_made=random.randint(0, 2),
                    next_visit_date=visit_date + timedelta(days=30)
                )

    def seed_outreach_events(self):
        self.stdout.write('Seeding outreach events...')
        
        event_types = [
            ('IMMUNIZATION', 'Mass Immunization Campaign'),
            ('SCREENING', 'Diabetes & Hypertension Screening'),
            ('DEWORMING', 'School Deworming Campaign'),
            ('EDUCATION', 'Malaria Prevention Education'),
        ]
        
        for i in range(8):
            event_type, event_name = random.choice(event_types)
            start_date = date.today() - timedelta(days=random.randint(30, 180))
            end_date = start_date + timedelta(days=random.randint(1, 5))
            
            target = random.randint(500, 3000)
            
            self.OutreachEvent.objects.create(
                name=event_name,
                event_type=event_type,
                start_date=start_date,
                end_date=end_date,
                location=f'{random.choice(self.wards).name} Village',
                ward=random.choice(self.wards),
                target_population=target,
                people_reached=int(target * random.uniform(0.6, 0.95)),
                organizing_facility=random.choice(self.facilities),
                partners='Ministry of Health, WHO',
                services_offered=['Screening', 'Treatment', 'Referrals'],
                budget=Decimal(str(random.randint(100000, 500000))),
                actual_cost=Decimal(str(random.randint(80000, 450000))),
                report='Event successfully completed with good community turnout'
            )

    def seed_screenings(self):
        self.stdout.write('Seeding screening records...')
        
        screening_types = ['TB', 'HIV', 'DIABETES', 'HYPERTENSION', 'MALNUTRITION']
        
        for person in self.persons[:100]:
            if person.get_age() >= 5:
                num_screenings = random.randint(0, 3)
                
                for i in range(num_screenings):
                    screening_date = date.today() - timedelta(days=random.randint(1, 365))
                    
                    self.Screening.objects.create(
                        person=person,
                        screening_type=random.choice(screening_types),
                        screening_date=screening_date,
                        screened_by=random.choice(self.users),
                        facility=random.choice(self.facilities),
                        result=random.choice(['NEGATIVE', 'POSITIVE', 'INCONCLUSIVE']),
                        result_details={},
                        follow_up_required=random.choice([True, False]),
                        follow_up_date=screening_date + timedelta(days=30) if random.choice([True, False]) else None
                    )

    def seed_referrals(self):
        self.stdout.write('Seeding referral records...')
        
        ref_counter = 1
        statuses = ['PENDING', 'ACCEPTED', 'ARRIVED', 'COMPLETED']
        
        for person in self.persons[:30]:
            if random.random() > 0.7:
                ref_date = timezone.now() - timedelta(days=random.randint(1, 90))
                
                from_facility = random.choice(self.facilities[:10])
                to_facility = random.choice([f for f in self.facilities if f.facility_type in ['COUNTY_REFERRAL', 'SUB_COUNTY_HOSPITAL']])
                
                status = random.choice(statuses)
                
                self.Referral.objects.create(
                    referral_number=f'REF-WJR-{ref_counter:06d}',
                    person=person,
                    from_facility=from_facility,
                    to_facility=to_facility,
                    referred_by=random.choice(self.users),
                    referral_date=ref_date,
                    urgency=random.choice(['ROUTINE', 'URGENT', 'EMERGENCY']),
                    reason='Patient requires specialized care not available at referring facility',
                    diagnosis='Suspected complicated malaria',
                    treatment_given='Initial antimalarials administered',
                    status=status,
                    accepted_by=random.choice(self.users) if status != 'PENDING' else None,
                    accepted_date=ref_date + timedelta(hours=2) if status != 'PENDING' else None,
                    arrival_date=ref_date + timedelta(hours=4) if status in ['ARRIVED', 'COMPLETED'] else None,
                    completion_date=ref_date + timedelta(days=3) if status == 'COMPLETED' else None,
                    outcome='Patient treated and stabilized' if status == 'COMPLETED' else '',
                    feedback_to_referring_facility='Patient responded well to treatment' if status == 'COMPLETED' else ''
                )
                ref_counter += 1