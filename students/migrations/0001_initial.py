# Generated by Django 5.1.2 on 2024-12-15 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(unique=True, verbose_name='ปีการศึกษา')),
            ],
            options={
                'verbose_name': 'ปีการศึกษา',
                'verbose_name_plural': 'ปีการศึกษา',
            },
        ),
        migrations.CreateModel(
            name='Amphoe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='อำเภอ/เขต')),
            ],
            options={
                'verbose_name': 'อำเภอ/เขต',
                'verbose_name_plural': 'อำเภอ/เขต',
            },
        ),
        migrations.CreateModel(
            name='CurrentSemester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(choices=[(1, 'เทอม 1'), (2, 'เทอม 2')], default=1, verbose_name='ภาคการศึกษา')),
                ('year', models.PositiveIntegerField(default=2024, verbose_name='ปีการศึกษา')),
            ],
            options={
                'verbose_name': 'ภาคการศึกษา',
                'verbose_name_plural': 'ภาคการศึกษา',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='ชื่อระดับชั้น')),
            ],
            options={
                'verbose_name': 'ระดับชั้น',
                'verbose_name_plural': 'ระดับชั้น',
            },
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='อาชีพ')),
            ],
            options={
                'verbose_name': 'อาชีพ',
                'verbose_name_plural': 'อาชีพ',
            },
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='จังหวัด')),
            ],
            options={
                'verbose_name': 'จังหวัด',
                'verbose_name_plural': 'จังหวัด',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='ชื่อโรงเรียน')),
                ('english_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อโรงเรียน (ภาษาอังกฤษ)')),
                ('education_district', models.IntegerField(default=80, verbose_name='หน่วยสอบ')),
            ],
            options={
                'verbose_name': 'โรงเรียน',
                'verbose_name_plural': 'โรงเรียน',
            },
        ),
        migrations.CreateModel(
            name='StudentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField(blank=True, null=True, verbose_name='รหัสนักเรียน')),
                ('student_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='ชื่อนักเรียน')),
                ('school_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='ชื่อโรงเรียน')),
                ('level_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='ระดับชั้น')),
                ('semester', models.CharField(blank=True, max_length=50, null=True, verbose_name='ภาคการศึกษา')),
                ('academic_year', models.CharField(blank=True, max_length=4, null=True, verbose_name='ปีการศึกษา')),
                ('total_marks', models.IntegerField(blank=True, default=0, null=True, verbose_name='คะแนนเต็ม')),
                ('obtained_marks', models.IntegerField(blank=True, default=0, null=True, verbose_name='คะแนนที่ได้')),
                ('grade_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='เปอร์เซ็นต์คะแนน')),
                ('subject_marks', models.JSONField(blank=True, null=True, verbose_name='คะแนนตามวิชา')),
                ('pass_or_fail', models.CharField(blank=True, max_length=4, null=True, verbose_name='ผ่าน/ไม่ผ่าน')),
            ],
            options={
                'verbose_name': 'ประวัติการศึกษา',
                'verbose_name_plural': 'ประวัติการศึกษา',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='ชื่อวิชา')),
                ('total_marks', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='คะแนนเต็ม')),
            ],
            options={
                'verbose_name': 'วิชา',
                'verbose_name_plural': 'วิชา',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.CharField(editable=False, max_length=9, primary_key=True, serialize=False, verbose_name='Teacher ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='ชื่อ')),
                ('last_name', models.CharField(max_length=100, verbose_name='นามสกุล')),
                ('date_of_birth', models.DateField(verbose_name='วันเกิด')),
                ('id_number', models.CharField(blank=True, max_length=13, null=True, unique=True, verbose_name='เลขบัตรประชาชน')),
                ('gender', models.CharField(blank=True, choices=[('ชาย', 'ชาย'), ('หญิง', 'หญิง')], max_length=10, null=True, verbose_name='เพศ')),
                ('subject', models.CharField(blank=True, max_length=100, null=True, verbose_name='วิชา')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='teacher_profile_pics/', verbose_name='รูปโปรไฟล์')),
                ('status', models.CharField(choices=[('กำลังสอน', 'กำลังสอน'), ('เกษียณ', 'เกษียณ')], default='กำลังสอน', max_length=20, verbose_name='สถานะ')),
                ('password', models.CharField(editable=False, max_length=8, verbose_name='Password')),
            ],
            options={
                'verbose_name': 'ครู',
                'verbose_name_plural': 'ครู',
            },
        ),
        migrations.CreateModel(
            name='Workplace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='สถานที่ทำงาน')),
            ],
            options={
                'verbose_name': 'สถานที่ทำงาน',
                'verbose_name_plural': 'สถานที่ทำงาน',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='บ้านเลขที่')),
                ('street', models.CharField(blank=True, max_length=100, null=True, verbose_name='ซอย/ถนน')),
                ('moo', models.IntegerField(blank=True, default=0, null=True, verbose_name='หมู่')),
                ('zipcode', models.CharField(blank=True, max_length=5, null=True, verbose_name='รหัสไปรษณีย์')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.amphoe', verbose_name='อำเภอ/เขต')),
                ('province', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.province', verbose_name='จังหวัด')),
            ],
            options={
                'verbose_name': 'ที่อยู่',
                'verbose_name_plural': 'ที่อยู่',
            },
        ),
        migrations.AddField(
            model_name='amphoe',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amphoes', to='students.province', verbose_name='จังหวัด'),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.CharField(editable=False, max_length=9, primary_key=True, serialize=False, verbose_name='Student ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='ชื่อ')),
                ('last_name', models.CharField(max_length=100, verbose_name='นามสกุล')),
                ('english_first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อภาษาอังกฤษ')),
                ('english_last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อภาษาอังกฤษ')),
                ('arabic_first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อภาษาอาหรับ')),
                ('arabic_last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อภาษาอาหรับ')),
                ('date_of_birth', models.DateField(verbose_name='วันเกิด')),
                ('id_number', models.CharField(max_length=13, unique=True, verbose_name='เลขบัตรประชาชน')),
                ('gender', models.CharField(blank=True, choices=[('ชาย', 'เด็กชาย'), ('หญิง', 'เด็กหญิง')], max_length=10, null=True, verbose_name='คำนำหน้า')),
                ('special_status', models.CharField(blank=True, choices=[('เด็กกำพร้า', 'เด็กกำพร้า'), ('เด็กยากไร้', 'เด็กยากไร้'), ('เด็กพิการ', 'เด็กพิการ'), ('เด็กมุอัลลัฟ', 'เด็กมุอัลลัฟ')], max_length=20, null=True, verbose_name='สถานะพิเศษ')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/', verbose_name='รูปโปรไฟล์')),
                ('status', models.CharField(choices=[('กำลังศึกษา', 'กำลังศึกษา'), ('จบแล้ว', 'จบแล้ว')], default='กำลังศึกษา', max_length=10, verbose_name='สถานะ')),
                ('exam_unit_number', models.CharField(default='80', max_length=2, verbose_name='หน่วยสอบ')),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.address', verbose_name='ที่อยู่')),
            ],
            options={
                'verbose_name': 'นักเรียน',
                'verbose_name_plural': 'นักเรียน',
            },
        ),
        migrations.CreateModel(
            name='Mother',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อ')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='นามสกุล')),
                ('date_of_birth', models.DateField(verbose_name='วันเกิด')),
                ('occupation', models.CharField(blank=True, max_length=255, null=True, verbose_name='อาชีพ')),
                ('workplace', models.CharField(blank=True, max_length=255, null=True, verbose_name='สถานที่ทำงาน')),
                ('income', models.IntegerField(blank=True, null=True, verbose_name='รายได้')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='หมายเลขโทรศัพท์')),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.address', verbose_name='ที่อยู่')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='students.student', verbose_name='นักเรียน')),
            ],
            options={
                'verbose_name': 'มารดา',
                'verbose_name_plural': 'มารดา',
            },
        ),
        migrations.CreateModel(
            name='Guardian',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อ')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='นามสกุล')),
                ('date_of_birth', models.DateField(verbose_name='วันเกิด')),
                ('occupation', models.CharField(blank=True, max_length=255, null=True, verbose_name='อาชีพ')),
                ('workplace', models.CharField(blank=True, max_length=255, null=True, verbose_name='สถานที่ทำงาน')),
                ('income', models.IntegerField(blank=True, null=True, verbose_name='รายได้')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='หมายเลขโทรศัพท์')),
                ('relationship_with_student', models.CharField(blank=True, choices=[('พ่อ', 'พ่อ'), ('แม่', 'แม่'), ('ไม่ใช่พ่อแม่', 'ไม่ใช่พ่อแม่')], max_length=50, null=True, verbose_name='ความสัมพันธ์กับนักเรียน')),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.address', verbose_name='ที่อยู่')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='students.student', verbose_name='นักเรียน')),
            ],
            options={
                'verbose_name': 'ผู้ปกครอง',
                'verbose_name_plural': 'ผู้ปกครอง',
            },
        ),
        migrations.CreateModel(
            name='Father',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='ชื่อ')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='นามสกุล')),
                ('date_of_birth', models.DateField(verbose_name='วันเกิด')),
                ('occupation', models.CharField(blank=True, max_length=255, null=True, verbose_name='อาชีพ')),
                ('workplace', models.CharField(blank=True, max_length=255, null=True, verbose_name='สถานที่ทำงาน')),
                ('income', models.IntegerField(blank=True, null=True, verbose_name='รายได้')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='หมายเลขโทรศัพท์')),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.address', verbose_name='ที่อยู่')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='students.student', verbose_name='นักเรียน')),
            ],
            options={
                'verbose_name': 'บิดา',
                'verbose_name_plural': 'บิดา',
            },
        ),
        migrations.CreateModel(
            name='CurrentStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.currentsemester', verbose_name='ภาคการศึกษา')),
                ('level', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.level', verbose_name='ระดับชั้น')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.school', verbose_name='โรงเรียน')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='current_study', to='students.student', verbose_name='นักเรียน')),
            ],
            options={
                'verbose_name': 'การศึกษาในปัจจุบัน',
                'verbose_name_plural': 'การศึกษาในปัจจุบัน',
            },
        ),
        migrations.CreateModel(
            name='SubjectToStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(choices=[(1, 'เทอม 1'), (2, 'เทอม 2')], default=1, verbose_name='ภาคการศึกษา')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.level', verbose_name='ระดับชั้น')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.subject', verbose_name='วิชา')),
            ],
            options={
                'verbose_name': 'วิชาที่เรียน',
                'verbose_name_plural': 'วิชาที่เรียน',
            },
        ),
        migrations.CreateModel(
            name='StudentMarkForSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks_obtained', models.IntegerField(blank=True, default=0, null=True, verbose_name='คะแนนที่ได้')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student', verbose_name='นักเรียน')),
                ('subject_to_study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.subjecttostudy', verbose_name='วิชาที่เรียน')),
            ],
            options={
                'verbose_name': 'คะแนนนักเรียนสำหรับวิชา',
                'verbose_name_plural': 'คะแนนนักเรียนสำหรับวิชา',
            },
        ),
        migrations.CreateModel(
            name='Tambon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='ตำบล/แขวง')),
                ('zipcode', models.CharField(max_length=5, verbose_name='รหัสไปรษณีย์')),
                ('amphoe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tambons', to='students.amphoe', verbose_name='อำเภอ/เขต')),
            ],
            options={
                'verbose_name': 'ตำบล/แขวง',
                'verbose_name_plural': 'ตำบล/แขวง',
            },
        ),
        migrations.AddField(
            model_name='address',
            name='subdistrict',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='students.tambon', verbose_name='ตำบล/แขวง'),
        ),
    ]
