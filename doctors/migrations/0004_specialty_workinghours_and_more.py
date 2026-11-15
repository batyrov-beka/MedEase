import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


SPECIALTIES = [
    # slug, name, icon, image, short, description
    ('terapevt', 'Терапевт', 'fa-user-doctor', '',
     'Первичный приём взрослых: диагностика, лечение и направление к узким специалистам.',
     'Терапевт — врач первого контакта. Он оценит общее состояние здоровья, назначит обследования, '
     'поставит диагноз при распространённых заболеваниях и при необходимости направит к узкому специалисту.'),
    ('pediatr', 'Педиатр', 'fa-baby', 'css/img/pre.jpg',
     'Универсальный врач для детей: рост и развитие, прививки, лечение детских болезней.',
     'Здоровье вашего ребёнка — наш главный приоритет. Наши педиатры найдут подход к каждому маленькому '
     'пациенту, обеспечат профессиональный уход и ответят на все вопросы родителей о развитии ребёнка.'),
    ('hirurg', 'Хирург', 'fa-syringe', 'css/img/hirurg1.jpg',
     'Травмы, гнойные воспаления и заболевания, которые требуют операции или перевязки.',
     'Наши хирурги проводят операции с использованием современных методик и оборудования. '
     'Мы обеспечиваем безопасность и тщательный контроль на каждом этапе выздоровления.'),
    ('kardiolog', 'Кардиолог', 'fa-heart-pulse', 'css/img/952019fa9c573904c4e3db649ef83f19.jpg',
     'Сердце и сосуды: боли в груди, одышка, проблемы с давлением.',
     'Здоровье сердца — основа долгой и активной жизни. Кардиологи помогут вовремя выявить риски, '
     'проведут точную диагностику и подберут программу лечения и профилактики.'),
    ('nevrolog', 'Невролог', 'fa-brain', '',
     'Головные боли, головокружение, боли в спине, нарушения сна и чувствительности.',
     'Невролог занимается заболеваниями головного и спинного мозга, нервов. Поможет разобраться с причинами '
     'головной боли, болей в спине, онемения, нарушений сна и памяти.'),
    ('ginekolog', 'Гинеколог', 'fa-person-pregnant', '',
     'Женское здоровье, профилактические осмотры, ведение беременности.',
     'Гинеколог проводит профилактические осмотры, диагностику и лечение заболеваний женской репродуктивной '
     'системы, консультирует по планированию и ведению беременности.'),
    ('infekcionist', 'Инфекционист', 'fa-virus', 'css/img/13a2822d25c4434d371ec2981883ce3f.jpg',
     'Инфекционные болезни: от гриппа и кишечных инфекций до вирусов и паразитов.',
     'Специалисты проводят диагностику и лечение широкого спектра инфекционных заболеваний, используя '
     'лабораторные методы, чтобы быстро выявить возбудителя.'),
    ('gastroenterolog', 'Гастроэнтеролог', 'fa-pills', 'css/img/b26128ee5998ea789c20ef44c689d6c4.jpg',
     'Пищеварение: желудок, кишечник, печень и поджелудочная железа.',
     'Здоровье пищеварительной системы — залог хорошего самочувствия. Специалист выявит причины дискомфорта, '
     'проведёт диагностику и подберёт план лечения и питания.'),
    ('endokrinolog', 'Эндокринолог', 'fa-vial', '',
     'Щитовидная железа, сахарный диабет, гормональные нарушения и обмен веществ.',
     'Эндокринолог диагностирует и лечит заболевания щитовидной железы, сахарный диабет, нарушения обмена '
     'веществ и гормонального фона.'),
    ('ortoped', 'Ортопед', 'fa-bone', 'css/img/chto-lechit-ortoped.jpg.pagespeed.ce_.zymofn6uhl.jpg',
     'Осанка, плоскостопие, хронические болезни суставов и костей.',
     'Верните себе радость движения без боли. Специалисты лечат заболевания опорно-двигательного аппарата '
     'и помогают сохранить здоровье суставов в любом возрасте.'),
    ('lor', 'ЛОР', 'fa-ear-listen', 'css/img/bbaebc996bbceddcdb0a6c7d3e075af4.jpg',
     'Ухо, горло и нос: насморк, гайморит, ангина, боли в ушах.',
     'ЛОР-врачи проводят диагностику и лечение острых и хронических заболеваний уха, горла и носа, '
     'возвращая свободное дыхание и комфорт.'),
    ('oftalmolog', 'Офтальмолог', 'fa-eye', 'css/img/EnMitUqXIA4inBE.jpg',
     'Проверка зрения, лечение воспалений глаз, подбор очков и линз.',
     'Офтальмологи помогут сохранить остроту зрения, проведут полную диагностику и подберут лечение '
     'или коррекцию с учётом особенностей ваших глаз.'),
    ('dermatolog', 'Дерматолог', 'fa-hand-dots', '',
     'Кожа, волосы и ногти: сыпь, акне, аллергические реакции, родинки.',
     'Дерматолог диагностирует и лечит заболевания кожи, волос и ногтей, проводит осмотр родинок '
     'и подбирает лечение аллергических и воспалительных реакций.'),
    ('stomatolog', 'Стоматолог', 'fa-tooth', '',
     'Лечение и профилактика заболеваний зубов и дёсен, гигиена полости рта.',
     'Стоматологи проводят профилактические осмотры, лечение кариеса и заболеваний дёсен, '
     'профессиональную гигиену полости рта.'),
    ('reanimatolog', 'Реаниматолог', 'fa-truck-medical', 'css/img/anesthesiologist.webp',
     'Поддержка пациентов в критических состояниях и анестезия.',
     'Специалисты обеспечивают круглосуточную поддержку пациентов в критических состояниях, используя '
     'современное оборудование для мониторинга и жизнеобеспечения.'),
]


def seed_specialties(apps, schema_editor):
    Specialty = apps.get_model('doctors', 'Specialty')
    for order, (slug, name, icon, image, short, desc) in enumerate(SPECIALTIES, start=1):
        Specialty.objects.get_or_create(
            slug=slug,
            defaults=dict(name=name, icon=icon, image=image, short_description=short,
                          description=desc, order=order),
        )


def move_specialty_text_to_fk(apps, schema_editor):
    Doctor = apps.get_model('doctors', 'Doctor')
    Specialty = apps.get_model('doctors', 'Specialty')
    default = Specialty.objects.get(slug='terapevt')
    for doctor in Doctor.objects.all():
        text = (doctor.specialty_old or '').strip().lower()
        match = Specialty.objects.filter(name__iexact=text).first() if text else None
        doctor.specialty = match or default
        if text and not match and not doctor.position:
            doctor.position = doctor.specialty_old
        doctor.save(update_fields=['specialty', 'position'])


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0003_doctor_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Specialty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Адрес (slug)')),
                ('icon', models.CharField(default='fa-stethoscope', help_text='Например: fa-heart-pulse, fa-tooth, fa-baby', max_length=50, verbose_name='Иконка Font Awesome')),
                ('short_description', models.CharField(max_length=255, verbose_name='Кратко')),
                ('description', models.TextField(blank=True, verbose_name='Подробное описание')),
                ('image', models.CharField(blank=True, help_text='Например: css/img/pre.jpg. Можно оставить пустым.', max_length=255, verbose_name='Картинка (путь в static)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Показывать на сайте')),
            ],
            options={
                'verbose_name': 'Направление',
                'verbose_name_plural': 'Направления',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.RunPython(seed_specialties, migrations.RunPython.noop),

        migrations.RenameField('doctor', 'specialty', 'specialty_old'),
        migrations.AddField(
            model_name='doctor',
            name='position',
            field=models.CharField(blank=True, help_text='Например: «Врач-кардиолог высшей категории».', max_length=150, verbose_name='Должность'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='specialty',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='doctors', to='doctors.specialty', verbose_name='Направление'),
        ),
        migrations.RunPython(move_specialty_text_to_fk, migrations.RunPython.noop),
        migrations.RemoveField('doctor', 'specialty_old'),
        migrations.AlterField(
            model_name='doctor',
            name='specialty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='doctors', to='doctors.specialty', verbose_name='Направление'),
        ),

        migrations.AddField(
            model_name='doctor',
            name='education',
            field=models.TextField(blank=True, verbose_name='Образование'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='price',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Стоимость приёма (сом)'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='slot_minutes',
            field=models.PositiveSmallIntegerField(choices=[(15, '15 минут'), (20, '20 минут'), (30, '30 минут'), (45, '45 минут'), (60, '60 минут')], default=30, verbose_name='Длительность приёма (мин)'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Принимает пациентов'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='name',
            field=models.CharField(max_length=150, verbose_name='ФИО'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='experience',
            field=models.PositiveIntegerField(default=0, verbose_name='Стаж (лет)'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='bio',
            field=models.TextField(blank=True, verbose_name='О враче'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='doctors/', verbose_name='Фото'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='user',
            field=models.OneToOneField(blank=True, help_text='Аккаунт, через который врач входит в «Панель врача».', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doctor', to=settings.AUTH_USER_MODEL, verbose_name='Аккаунт врача'),
        ),
        migrations.AlterModelOptions(
            name='doctor',
            options={'ordering': ['name'], 'verbose_name': 'Врач', 'verbose_name_plural': 'Врачи'},
        ),

        migrations.CreateModel(
            name='WorkingHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.PositiveSmallIntegerField(choices=[(0, 'Понедельник'), (1, 'Вторник'), (2, 'Среда'), (3, 'Четверг'), (4, 'Пятница'), (5, 'Суббота'), (6, 'Воскресенье')], verbose_name='День недели')),
                ('start_time', models.TimeField(verbose_name='Начало')),
                ('end_time', models.TimeField(verbose_name='Конец')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='working_hours', to='doctors.doctor', verbose_name='Врач')),
            ],
            options={
                'verbose_name': 'Рабочие часы',
                'verbose_name_plural': 'График работы',
                'ordering': ['weekday', 'start_time'],
                'constraints': [
                    models.UniqueConstraint(fields=('doctor', 'weekday'), name='unique_doctor_weekday'),
                    models.CheckConstraint(condition=models.Q(('end_time__gt', models.F('start_time'))), name='working_hours_end_after_start'),
                ],
            },
        ),
    ]
