# seed.py
"""
Database seeder — populates the database with realistic test data.

Run from inside backend/ with:
    python seed.py

WARNING: This will DELETE all existing data and recreate it.
Only use in development.
"""

from app import create_app, db
from app.models.user import User, UserRole, LeaveStatus
from app.models.crew import Crew, Shift
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus
from app.models.incident import Incident, IncidentType, IncidentStatus, IncidentPriority
from app.models.task import Task, TaskType, TaskStatus
from datetime import datetime, timedelta


def seed():
    app = create_app('development')

    with app.app_context():
        print("⚠️  Dropping all tables...")
        db.drop_all()
        print("✅ Creating all tables...")
        db.create_all()

        # ── Users ──────────────────────────────────────────────────────────────
        print("👤 Creating users...")

        admin = User(
            first_name='Иван', last_name='Петров',
            username='admin', email='admin@gdpbzn.bg',
            badge_number='ADM-001', role=UserRole.ADMIN
        )
        admin.set_password('admin1234')

        ops1 = User(
            first_name='Мария', last_name='Георгиева',
            username='ops1', email='m.georgieva@gdpbzn.bg',
            badge_number='OPS-001', role=UserRole.OPERATIONS_CENTER
        )
        ops1.set_password('ops11234')

        dispatcher1 = User(
            first_name='Петър', last_name='Димитров',
            username='dispatcher1', email='p.dimitrov@gdpbzn.bg',
            badge_number='DSP-001', role=UserRole.DISPATCHER
        )
        dispatcher1.set_password('disp1234')

        ff1 = User(
            first_name='Георги', last_name='Иванов',
            username='ff1', email='g.ivanov@gdpbzn.bg',
            badge_number='FF-001', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_DUTY
        )
        ff1.set_password('fire1234')

        ff2 = User(
            first_name='Николай', last_name='Стоянов',
            username='ff2', email='n.stoyanov@gdpbzn.bg',
            badge_number='FF-002', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_DUTY
        )
        ff2.set_password('fire1234')

        ff3 = User(
            first_name='Стефан', last_name='Тодоров',
            username='ff3', email='s.todorov@gdpbzn.bg',
            badge_number='FF-003', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_LEAVE
        )
        ff3.set_password('fire1234')

        db.session.add_all([admin, ops1, dispatcher1, ff1, ff2, ff3])
        db.session.commit()

        # ── Vehicles ───────────────────────────────────────────────────────────
        print("🚒 Creating vehicles...")

        v1 = Vehicle(
            plate_number='A 1234 BB', call_sign='Бургас-1',
            make='MAN', model='TGM 18.290', year=2019,
            vehicle_type=VehicleType.FIRE_TRUCK,
            status=VehicleStatus.AVAILABLE,
            water_capacity_liters=4000, crew_capacity=6,
            home_station='РСПБЗН Бургас'
        )
        v2 = Vehicle(
            plate_number='A 5678 CC', call_sign='Бургас-2',
            make='Iveco', model='Eurocargo', year=2017,
            vehicle_type=VehicleType.WATER_TANKER,
            status=VehicleStatus.AVAILABLE,
            water_capacity_liters=10000, crew_capacity=3,
            home_station='РСПБЗН Бургас'
        )
        v3 = Vehicle(
            plate_number='A 9999 DD', call_sign='Бургас-3',
            make='Mercedes', model='Atego', year=2015,
            vehicle_type=VehicleType.RESCUE_VEHICLE,
            status=VehicleStatus.MAINTENANCE,
            home_station='РСПБЗН Бургас'
        )
        db.session.add_all([v1, v2, v3])
        db.session.commit()

        # ── Crews ──────────────────────────────────────────────────────────────
        print("👨‍🚒 Creating crews...")

        crew_alpha = Crew(
            name='Алфа', station='РСПБЗН Бургас',
            description='Primary response crew'
        )
        crew_beta = Crew(
            name='Бета', station='РСПБЗН Бургас',
            description='Secondary response crew'
        )
        db.session.add_all([crew_alpha, crew_beta])
        db.session.commit()

        # Add members
        crew_alpha.members.append(ff1)
        crew_alpha.members.append(ff2)
        crew_beta.members.append(ff3)
        db.session.commit()

        # ── Shifts ─────────────────────────────────────────────────────────────
        print("🕐 Creating shifts...")

        shift1 = Shift(
            crew_id=crew_alpha.id,
            vehicle_id=v1.id,
            start_time=datetime.utcnow() - timedelta(hours=4),
            is_active=True
        )
        db.session.add(shift1)
        db.session.commit()

        # ── Incidents ──────────────────────────────────────────────────────────
        print("🔥 Creating incidents...")

        inc1 = Incident(
            incident_type=IncidentType.STRUCTURE_FIRE,
            priority=IncidentPriority.HIGH,
            status=IncidentStatus.IN_PROGRESS,
            address='ул. Александровска 42',
            city='Бургас',
            latitude=42.4993, longitude=27.4699,
            caller_name='Тодор Василев', caller_phone='+359887123456',
            description='Пожар на третия етаж. Евакуацията е в ход.',
            hazard_notes='Газова инсталация в мазето.',
            registered_by_id=dispatcher1.id,
            assigned_crew_id=crew_alpha.id,
            reported_at=datetime.utcnow() - timedelta(minutes=45),
            dispatched_at=datetime.utcnow() - timedelta(minutes=40),
            on_scene_at=datetime.utcnow() - timedelta(minutes=30),
        )
        inc1.reference_number = 'INC-2024-00001'

        inc2 = Incident(
            incident_type=IncidentType.WILDFIRE,
            priority=IncidentPriority.CRITICAL,
            status=IncidentStatus.DISPATCHED,
            address='Природен парк Странджа, сектор 7',
            city='Малко Търново',
            latitude=41.9940, longitude=27.5270,
            description='Горски пожар. Обхванати около 5 дка.',
            hazard_notes='Силен вятър. Труден терен.',
            registered_by_id=ops1.id,
            reported_at=datetime.utcnow() - timedelta(minutes=15),
            dispatched_at=datetime.utcnow() - timedelta(minutes=10),
        )
        inc2.reference_number = 'INC-2024-00002'

        inc3 = Incident(
            incident_type=IncidentType.VEHICLE_FIRE,
            priority=IncidentPriority.MEDIUM,
            status=IncidentStatus.PENDING,
            address='Бул. Сан Стефано 88',
            city='Бургас',
            latitude=42.5080, longitude=27.4680,
            caller_phone='+359888654321',
            description='Лек автомобил с признаци на запалване.',
            registered_by_id=dispatcher1.id,
            reported_at=datetime.utcnow() - timedelta(minutes=5),
        )
        inc3.reference_number = 'INC-2024-00003'

        db.session.add_all([inc1, inc2, inc3])
        db.session.commit()

        # ── Tasks ──────────────────────────────────────────────────────────────
        print("📋 Creating tasks...")

        task1 = Task(
            title='Доставка на вода — Александровска',
            description='Нужни допълнителни 6000л вода за потушаване.',
            task_type=TaskType.WATER_DELIVERY,
            status=TaskStatus.PENDING,
            incident_id=inc1.id,
            assigned_crew_id=crew_beta.id,
            created_by_id=ops1.id
        )
        db.session.add(task1)
        db.session.commit()

        # Summary
        print("\n✅ Seed complete! Test accounts:")
        print("  admin       / admin1234  (Admin)")
        print("  ops1        / ops11234   (Operations Center)")
        print("  dispatcher1 / disp1234   (Dispatcher)")
        print("  ff1         / fire1234   (Firefighter)")
        print("  ff2         / fire1234   (Firefighter)")
        print(f"\n  Incidents created: 3")
        print(f"  Crews: Алфа, Бета")
        print(f"  Vehicles: 3")


if __name__ == '__main__':
    seed()