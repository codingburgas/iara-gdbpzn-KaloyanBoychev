# seed.py
"""
Database seeder — populates the database with showcase/demo data.

Run from inside backend/ with:
    python seed.py

WARNING: This will DELETE all existing data (test accounts, incidents,
tasks, everything) and recreate it from scratch. Use before a demo/
presentation, or in development — never against a real production DB.
"""

from app import create_app, db
from app.models.user import User, UserRole, LeaveStatus
from app.models.crew import Crew, Shift
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus
from app.models.incident import Incident, IncidentType, IncidentStatus, IncidentPriority
from app.models.task import Task, TaskType, TaskStatus
from app.models.message import Message, MessageType, SOSAlert, SOSAlertStatus
from datetime import datetime, timedelta

YEAR = datetime.utcnow().year


def seed():
    app = create_app('development')

    with app.app_context():
        print("⚠️  Dropping all tables...")
        db.drop_all()
        print("✅ Creating all tables...")
        db.create_all()

        # ── Users ────────────────────────────────────────────────────────────
        print("👤 Creating users...")

        admin = User(
            first_name='Николай', last_name='Радев',
            username='admin', email='admin@gdpbzn.bg',
            badge_number='ADM-001', role=UserRole.ADMIN
        )
        admin.set_password('admin1234')

        ops1 = User(
            first_name='Мария', last_name='Стоянова',
            username='ops1', email='m.stoyanova@gdpbzn.bg',
            badge_number='OPS-001', role=UserRole.OPERATIONS_CENTER
        )
        ops1.set_password('ops11234')

        dispatcher1 = User(
            first_name='Петър', last_name='Илиев',
            username='dispatcher1', email='p.iliev@gdpbzn.bg',
            badge_number='DSP-001', role=UserRole.DISPATCHER
        )
        dispatcher1.set_password('disp1234')

        ff1 = User(
            first_name='Георги', last_name='Димитров',
            username='ff1', email='g.dimitrov@gdpbzn.bg',
            badge_number='FF-001', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_DUTY
        )
        ff1.set_password('fire1234')

        ff2 = User(
            first_name='Стефан', last_name='Колев',
            username='ff2', email='s.kolev@gdpbzn.bg',
            badge_number='FF-002', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_DUTY
        )
        ff2.set_password('fire1234')

        ff3 = User(
            first_name='Иван', last_name='Тодоров',
            username='ff3', email='i.todorov@gdpbzn.bg',
            badge_number='FF-003', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_DUTY
        )
        ff3.set_password('fire1234')

        ff4 = User(
            first_name='Ангел', last_name='Николов',
            username='ff4', email='a.nikolov@gdpbzn.bg',
            badge_number='FF-004', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_DUTY
        )
        ff4.set_password('fire1234')

        ff5 = User(
            first_name='Красимир', last_name='Петков',
            username='ff5', email='k.petkov@gdpbzn.bg',
            badge_number='FF-005', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_MISSION
        )
        ff5.set_password('fire1234')

        ff6 = User(
            first_name='Дамян', last_name='Георгиев',
            username='ff6', email='d.georgiev@gdpbzn.bg',
            badge_number='FF-006', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_DUTY
        )
        ff6.set_password('fire1234')

        ff7 = User(
            first_name='Явор', last_name='Симеонов',
            username='ff7', email='y.simeonov@gdpbzn.bg',
            badge_number='FF-007', role=UserRole.FIREFIGHTER,
            leave_status=LeaveStatus.ON_LEAVE
        )
        ff7.set_password('fire1234')

        db.session.add_all([admin, ops1, dispatcher1, ff1, ff2, ff3, ff4, ff5, ff6, ff7])
        db.session.commit()

        # ── Vehicles ─────────────────────────────────────────────────────────
        print("🚒 Creating vehicles...")

        v1 = Vehicle(
            plate_number='A 1234 BB', call_sign='Бургас-1',
            make='MAN', model='TGM 18.290', year=2019,
            vehicle_type=VehicleType.FIRE_TRUCK,
            status=VehicleStatus.DEPLOYED,
            water_capacity_liters=4000, crew_capacity=6,
            home_station='РСПБЗН Бургас'
        )
        v2 = Vehicle(
            plate_number='A 5678 CC', call_sign='Бургас-2',
            make='Iveco', model='Eurocargo', year=2017,
            vehicle_type=VehicleType.WATER_TANKER,
            status=VehicleStatus.DEPLOYED,
            water_capacity_liters=10000, crew_capacity=3,
            home_station='РСПБЗН Бургас'
        )
        v3 = Vehicle(
            plate_number='A 9999 DD', call_sign='Бургас-3',
            make='Mercedes', model='Atego', year=2015,
            vehicle_type=VehicleType.RESCUE_VEHICLE,
            status=VehicleStatus.DEPLOYED,
            crew_capacity=4,
            home_station='РСПБЗН Бургас'
        )
        v4 = Vehicle(
            plate_number='A 3456 EE', call_sign='Бургас-4',
            make='Scania', model='P320', year=2021,
            vehicle_type=VehicleType.LADDER_TRUCK,
            status=VehicleStatus.MAINTENANCE,
            crew_capacity=4,
            home_station='РСПБЗН Бургас',
            notes='Планов технически преглед — очаква се готовност утре.'
        )
        v5 = Vehicle(
            plate_number='A 7890 FF', call_sign='Бургас-5',
            make='Toyota', model='Land Cruiser', year=2020,
            vehicle_type=VehicleType.COMMAND_VEHICLE,
            status=VehicleStatus.AVAILABLE,
            crew_capacity=4,
            home_station='РСПБЗН Бургас'
        )
        db.session.add_all([v1, v2, v3, v4, v5])
        db.session.commit()

        # ── Crews ────────────────────────────────────────────────────────────
        print("👨‍🚒 Creating crews...")

        crew_alpha = Crew(
            name='Алфа', station='РСПБЗН Бургас',
            description='Primary structure-fire response crew'
        )
        crew_beta = Crew(
            name='Бета', station='РСПБЗН Бургас',
            description='Technical rescue & logistics crew'
        )
        crew_gamma = Crew(
            name='Гама', station='РСПБЗН Бургас',
            description='Wildland / wildfire response crew'
        )
        db.session.add_all([crew_alpha, crew_beta, crew_gamma])
        db.session.commit()

        crew_alpha.members.append(ff1)
        crew_alpha.members.append(ff2)
        crew_beta.members.append(ff3)
        crew_beta.members.append(ff4)
        crew_gamma.members.append(ff5)
        crew_gamma.members.append(ff6)
        db.session.commit()

        # ── Shifts ───────────────────────────────────────────────────────────
        print("🕐 Creating shifts...")

        shift1 = Shift(crew_id=crew_alpha.id, vehicle_id=v1.id,
                       start_time=datetime.utcnow() - timedelta(hours=5), is_active=True)
        shift2 = Shift(crew_id=crew_beta.id, vehicle_id=v3.id,
                       start_time=datetime.utcnow() - timedelta(hours=3), is_active=True)
        shift3 = Shift(crew_id=crew_gamma.id, vehicle_id=v2.id,
                       start_time=datetime.utcnow() - timedelta(hours=2), is_active=True)
        db.session.add_all([shift1, shift2, shift3])
        db.session.commit()

        # ── Incidents ────────────────────────────────────────────────────────
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
            action_plan='1. Establish water supply from nearest hydrant.\n'
                        '2. Evacuate floors 1-3 immediately.\n'
                        '3. Do NOT enter basement — gas shutoff required first.\n'
                        '4. Secondary unit covers rear stairwell.',
            registered_by_id=dispatcher1.id,
            assigned_crew_id=crew_alpha.id,
            assigned_vehicle_id=v1.id,
            reported_at=datetime.utcnow() - timedelta(minutes=45),
            dispatched_at=datetime.utcnow() - timedelta(minutes=40),
            on_scene_at=datetime.utcnow() - timedelta(minutes=30),
        )
        inc1.reference_number = f'INC-{YEAR}-00001'

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
            assigned_crew_id=crew_gamma.id,
            assigned_vehicle_id=v2.id,
            reported_at=datetime.utcnow() - timedelta(minutes=25),
            dispatched_at=datetime.utcnow() - timedelta(minutes=20),
        )
        inc2.reference_number = f'INC-{YEAR}-00002'

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
        inc3.reference_number = f'INC-{YEAR}-00003'

        inc4 = Incident(
            incident_type=IncidentType.TECHNICAL_RESCUE,
            priority=IncidentPriority.HIGH,
            status=IncidentStatus.ON_SCENE,
            address='ул. Струга 15',
            city='Бургас',
            latitude=42.5021, longitude=27.4715,
            caller_name='Силвия Маринова', caller_phone='+359898112233',
            description='Лице заклещено между асансьор и стена.',
            registered_by_id=ops1.id,
            assigned_crew_id=crew_beta.id,
            assigned_vehicle_id=v3.id,
            reported_at=datetime.utcnow() - timedelta(hours=1, minutes=10),
            dispatched_at=datetime.utcnow() - timedelta(hours=1, minutes=5),
            on_scene_at=datetime.utcnow() - timedelta(minutes=50),
        )
        inc4.reference_number = f'INC-{YEAR}-00004'

        inc5 = Incident(
            incident_type=IncidentType.FALSE_ALARM,
            priority=IncidentPriority.LOW,
            status=IncidentStatus.RESOLVED,
            address='бул. Демокрация 3',
            city='Бургас',
            latitude=42.4950, longitude=27.4630,
            description='Задействана пожароизвестителна система — фалшива тревога.',
            registered_by_id=dispatcher1.id,
            reported_at=datetime.utcnow() - timedelta(hours=3),
            dispatched_at=datetime.utcnow() - timedelta(hours=2, minutes=55),
            on_scene_at=datetime.utcnow() - timedelta(hours=2, minutes=45),
            resolved_at=datetime.utcnow() - timedelta(hours=2, minutes=30),
        )
        inc5.reference_number = f'INC-{YEAR}-00005'

        db.session.add_all([inc1, inc2, inc3, inc4, inc5])
        db.session.commit()

        # ── Tasks ────────────────────────────────────────────────────────────
        print("📋 Creating tasks...")

        # Featured task: already assigned & pending — ready to edit live in the demo.
        task_water = Task(
            title='Доставка на вода — Александровска',
            description='Нужни допълнителни 6000л вода за потушаване.',
            task_type=TaskType.WATER_DELIVERY,
            status=TaskStatus.PENDING,
            location_notes='Достъп от задната алея, до хидранта',
            incident_id=inc1.id,
            assigned_crew_id=crew_beta.id,
            created_by_id=ops1.id
        )

        task_ventilation = Task(
            title='Проветряване — трети етаж',
            description='Пробиване на отвори за отвеждане на дима преди навлизане.',
            task_type=TaskType.VENTILATION,
            status=TaskStatus.IN_PROGRESS,
            incident_id=inc1.id,
            assigned_crew_id=crew_alpha.id,
            created_by_id=ops1.id
        )

        task_perimeter = Task(
            title='Периметър и контрол на достъпа',
            description='Ограничаване на достъпа до горски участък, сектор 7.',
            task_type=TaskType.PERIMETER_CONTROL,
            status=TaskStatus.PENDING,
            incident_id=inc2.id,
            assigned_crew_id=crew_gamma.id,
            created_by_id=ops1.id
        )

        task_rescue_doc = Task(
            title='Документиране на инцидент — Струга 15',
            description='Попълване на протокол след успешно освобождаване на лицето.',
            task_type=TaskType.DOCUMENTATION,
            status=TaskStatus.COMPLETED,
            incident_id=inc4.id,
            assigned_crew_id=crew_beta.id,
            created_by_id=dispatcher1.id,
            completed_at=datetime.utcnow() - timedelta(minutes=20)
        )

        task_unassigned = Task(
            title='Обратна връзка след инцидент',
            description='Кратък дебрифинг на екипа след потушаването.',
            task_type=TaskType.DEBRIEF,
            status=TaskStatus.PENDING,
            incident_id=inc1.id,
            assigned_crew_id=None,
            created_by_id=ops1.id
        )

        db.session.add_all([
            task_water, task_ventilation, task_perimeter,
            task_rescue_doc, task_unassigned
        ])
        db.session.commit()

        # ── Chat messages (on the featured incident) ────────────────────────
        print("💬 Creating chat messages...")

        msg1 = Message(
            content='Пристигнахме на място. Пушек от третия етаж, видимост слаба.',
            message_type=MessageType.TEXT,
            sender_id=ff1.id, incident_id=inc1.id,
            sent_at=datetime.utcnow() - timedelta(minutes=28)
        )
        msg2 = Message(
            content='Прекратете подаването на газ преди навлизане в мазето.',
            message_type=MessageType.TEXT,
            sender_id=ops1.id, incident_id=inc1.id,
            sent_at=datetime.utcnow() - timedelta(minutes=25)
        )
        msg3 = Message(
            content='Разбрано. Екип Бета тръгва с допълнителна вода.',
            message_type=MessageType.TEXT,
            sender_id=ff3.id, incident_id=inc1.id,
            sent_at=datetime.utcnow() - timedelta(minutes=22)
        )
        db.session.add_all([msg1, msg2, msg3])
        db.session.commit()

        # ── SOS alert (for the SOS button / SOS history demo) ───────────────
        print("🆘 Creating SOS alert...")

        sos1 = SOSAlert(
            firefighter_id=ff6.id,
            incident_id=inc2.id,
            latitude=41.9945, longitude=27.5265,
            status=SOSAlertStatus.ACTIVE,
            notes='Влошена видимост, необходимо е потвърждение на позицията.',
            triggered_at=datetime.utcnow() - timedelta(minutes=6)
        )
        db.session.add(sos1)
        db.session.commit()

        # Summary
        print("\n✅ Seed complete! Showcase accounts:")
        print("  admin       / admin1234  (Admin)")
        print("  ops1        / ops11234   (Operations Center)")
        print("  dispatcher1 / disp1234   (Dispatcher)")
        print("  ff1-ff7     / fire1234   (Firefighters — ff5 on mission, ff7 on leave)")
        print(f"\n  Crews: Алфа, Бета, Гама")
        print(f"  Vehicles: 5 (2 deployed, 1 in maintenance, 1 available, 1 command)")
        print(f"  Incidents: 5 (spanning pending → dispatched → on scene → in progress → resolved)")
        print(f"  Tasks: 5 — including one PENDING task on {inc1.reference_number} assigned to")
        print(f"         crew Бета ('{task_water.title}') ready to demo the edit-task feature.")
        print(f"  Chat messages: 3 on {inc1.reference_number}")
        print(f"  Active SOS alert: 1 (from ff6, on {inc2.reference_number})")


if __name__ == '__main__':
    seed()
