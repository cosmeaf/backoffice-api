# Generated by Django 4.2.21 on 2025-06-01 22:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cep', models.CharField(max_length=10)),
                ('logradouro', models.CharField(max_length=255)),
                ('complemento', models.CharField(blank=True, max_length=255, null=True)),
                ('bairro', models.CharField(max_length=100)),
                ('localidade', models.CharField(max_length=100)),
                ('uf', models.CharField(max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Endereço',
                'verbose_name_plural': 'Endereços',
            },
        ),
        migrations.CreateModel(
            name='AllowedCity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('localidade', models.CharField(max_length=100)),
                ('uf', models.CharField(max_length=2)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Cidade Permitida',
                'verbose_name_plural': 'Cidades Permitidas',
            },
        ),
        migrations.CreateModel(
            name='ExamDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
            options={
                'verbose_name': 'Data de Exame',
                'verbose_name_plural': 'Datas de Exame',
            },
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpf', models.CharField(max_length=14, unique=True)),
                ('birth_date', models.DateField()),
                ('social_name', models.CharField(blank=True, max_length=255, null=True)),
                ('celphone', models.CharField(max_length=20)),
                ('guardian_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('allowed_city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='seletivo.allowedcity')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_data', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dados do Usuário',
                'verbose_name_plural': 'Dados dos Usuários',
            },
        ),
        migrations.CreateModel(
            name='RegistrationData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profession', models.CharField(max_length=255)),
                ('maritial_status', models.CharField(max_length=50)),
                ('family_income', models.CharField(max_length=100)),
                ('education_level', models.CharField(max_length=100)),
                ('pcd', models.CharField(max_length=255)),
                ('internet_type', models.CharField(max_length=100)),
                ('public_school', models.BooleanField(default=False)),
                ('user_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='registration_data', to='seletivo.userdata')),
            ],
            options={
                'verbose_name': 'Dados de Registro',
                'verbose_name_plural': 'Dados de Registro',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('professional_status', models.CharField(max_length=255, verbose_name='Status Profissional')),
                ('experience', models.TextField(verbose_name='Experiência')),
                ('experience_duration', models.CharField(max_length=100, verbose_name='Duração da Experiência')),
                ('programming_knowledge_level', models.CharField(max_length=100, verbose_name='Nível de Programação')),
                ('motivation_level', models.CharField(max_length=100, verbose_name='Nível de Motivação')),
                ('project_priority', models.CharField(max_length=100, verbose_name='Prioridade de Projeto')),
                ('weekly_available_hours', models.CharField(max_length=50, verbose_name='Horas Semanais Disponíveis')),
                ('study_commitment', models.CharField(max_length=100, verbose_name='Comprometimento com Estudo')),
                ('frustration_handling', models.CharField(max_length=255, verbose_name='Lidar com Frustração')),
                ('user_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='persona', to='seletivo.userdata')),
            ],
            options={
                'verbose_name': 'Persona',
                'verbose_name_plural': 'Personas',
            },
        ),
        migrations.CreateModel(
            name='Guardian',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('cpf', models.CharField(max_length=14)),
                ('nationality', models.CharField(max_length=100)),
                ('cellphone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('user_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guardians', to='seletivo.userdata')),
            ],
            options={
                'verbose_name': 'Responsável',
                'verbose_name_plural': 'Responsáveis',
            },
        ),
        migrations.CreateModel(
            name='ExamLocal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('full_address', models.TextField()),
                ('allowed_city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='seletivo.allowedcity')),
            ],
            options={
                'verbose_name': 'Local de Exame',
                'verbose_name_plural': 'Locais de Exame',
            },
        ),
        migrations.CreateModel(
            name='ExamHour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour', models.TimeField()),
                ('exam_date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hours', to='seletivo.examdate')),
            ],
            options={
                'verbose_name': 'Horário de Exame',
                'verbose_name_plural': 'Horários de Exame',
            },
        ),
        migrations.AddField(
            model_name='examdate',
            name='local',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dates', to='seletivo.examlocal'),
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('status', models.CharField(max_length=50)),
                ('exam_scheduled_hour', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exams', to='seletivo.examhour')),
                ('user_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='seletivo.userdata')),
            ],
            options={
                'verbose_name': 'Exame',
                'verbose_name_plural': 'Exames',
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=100)),
                ('user_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='seletivo.userdata')),
            ],
            options={
                'verbose_name': 'Contrato',
                'verbose_name_plural': 'Contratos',
            },
        ),
        migrations.AddIndex(
            model_name='allowedcity',
            index=models.Index(fields=['localidade', 'uf'], name='seletivo_al_localid_2b1ac1_idx'),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='userdata',
            index=models.Index(fields=['cpf'], name='seletivo_us_cpf_cec1fb_idx'),
        ),
        migrations.AddIndex(
            model_name='registrationdata',
            index=models.Index(fields=['profession', 'education_level'], name='seletivo_re_profess_831f5b_idx'),
        ),
        migrations.AddIndex(
            model_name='persona',
            index=models.Index(fields=['professional_status'], name='seletivo_pe_profess_cccf31_idx'),
        ),
        migrations.AddIndex(
            model_name='persona',
            index=models.Index(fields=['programming_knowledge_level'], name='seletivo_pe_program_6fa232_idx'),
        ),
        migrations.AddIndex(
            model_name='guardian',
            index=models.Index(fields=['cpf', 'name'], name='seletivo_gu_cpf_948990_idx'),
        ),
        migrations.AddIndex(
            model_name='examlocal',
            index=models.Index(fields=['name'], name='seletivo_ex_name_dd790c_idx'),
        ),
        migrations.AddIndex(
            model_name='examhour',
            index=models.Index(fields=['hour'], name='seletivo_ex_hour_eeb1d3_idx'),
        ),
        migrations.AddIndex(
            model_name='examdate',
            index=models.Index(fields=['date'], name='seletivo_ex_date_f68a9c_idx'),
        ),
        migrations.AddIndex(
            model_name='exam',
            index=models.Index(fields=['status'], name='seletivo_ex_status_ea7e48_idx'),
        ),
        migrations.AddIndex(
            model_name='contract',
            index=models.Index(fields=['status'], name='seletivo_co_status_b5c8db_idx'),
        ),
        migrations.AddIndex(
            model_name='address',
            index=models.Index(fields=['cep'], name='seletivo_ad_cep_bf057d_idx'),
        ),
    ]
