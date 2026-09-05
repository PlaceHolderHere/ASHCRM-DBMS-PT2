USE ashcrm;

-- === 1. PARENT TABLES (No Foreign Key Dependencies) === ---
-- Sample Students
INSERT INTO student (name, section, address, date_of_birth, religion, nationality, emergency_contact_number, family_history, medical_history, immunizations, psychosocial_history, sexual_history) VALUES
	('Juan Dela Cruz', '12-A', '123 Main St, Davao City', '2008-05-14', 'Roman Catholic', 'Filipino', '+639171234567', '{"hypertension": true, "diabetes": false}', '{"allergies": ["Penicillin"], "asthma": false}', '{"covid19": "Fully Vaccinated", "tetanus": "Up to date"}', '{"stress_level": "Moderate"}', '{"active": false}'),
	('Maria Santos', '11-B', '456 Sampaguita St, Davao City', '2009-08-22', 'Seventh-day Adventist', 'Filipino', '+639182345678', '{"hypertension": false, "diabetes": true}', '{"allergies": [], "asthma": true}', '{"covid19": "Fully Vaccinated", "flu": "2025"}', '{"stress_level": "Low"}', '{"active": false}'),
	('Mark Lee', '12-C', '789 Acacia St, Davao City', '2010-01-10', 'Christian', 'Filipino', '+639193456789', '{"hypertension": false, "diabetes": false}', '{"allergies": ["Dust"], "asthma": false}', '{"covid19": "Fully Vaccinated"}', '{"stress_level": "High"}', '{"active": false}');

-- Sample Staff
INSERT INTO staff (name, position, email, contact_number) VALUES
	('Dr. Angela Reyes', 'School Physician', 'areyes@ashcrm.edu.ph', '+639179990001'),
	('Nurse Sarah Gomez', 'Head Nurse', 'sgomez@ashcrm.edu.ph', '+639179990002'),
	('Nurse Josh Damares', 'Assistant Nurse', 'jdamares@ashcrm.edu.ph', '+639179990003');

-- Sample Medical Supplies
INSERT INTO medical_supplies (name, quantity) VALUES
	('Paracetamol 500mg', 100),
	('Adhesive Bandage', 250),
	('Isopropyl Alcohol 70%', 20),
	('Gauze Pad 4x4', 80),
	('Antiseptic Ointment', 15);

-- Sample Medical Equipment
INSERT INTO medical_equipment (type) VALUES
	('Wheelchair'),
	('Digital Sphygmomanometer'),
	('Stethoscope'),
	('Crutches');
-- -------------------------------------------------------------------------------------------------------------------------

-- === 2. SECONDARY TABLES (Depend on Student/Staff) === --
-- Sample Clinic Visits
INSERT INTO clinic_visit (student_id, date, time_in, time_out, chief_complaints, treatment) VALUES
	(1, '2026-07-28', '09:15:00', '09:45:00', 'Headache and mild fever', 'Administered 1 tab Paracetamol 500mg and advised 30 mins rest.'),
	(2, '2026-08-09', '10:30:00', '10:50:00', 'Minor cut on right index finger', 'Cleaned with alcohol, applied antiseptic ointment and adhesive bandage.');
DESCRIBE clinic_visit;
-- Sample Incidents
INSERT INTO incident (student_id, date, time, description, treatment) VALUES
	(3, '2026-09-01', '14:00:00', 'Slipped on wet floor in the hallway, mild sprain on left ankle.', 'Applied cold compress, elevated leg, provided temporary crutches.');

-- Sample Medical Service Forms
INSERT INTO medical_service_form (student_id, staff_id, time_start, time_end, date, purpose) VALUES
	(1, 1, '08:00:00', '08:30:00', '2026-08-15', 'Annual Routine Physical Examination'),
	(2, 2, '13:00:00', '13:30:00', '2026-08-20', 'Varsity Sports Clearance Examination');

-- Sample Medical Certificates
INSERT INTO medical_certificates (student_id, staff_id, date_approved, event_name) VALUES
	(2, 1, '2026-08-20', 'Intramural Athletic Meet 2026');
-- -------------------------------------------------------------------------------------------------------------------------

-- === 3. JUNCTION & DETAIL TABLES (Depend on Multiple Parent Records) === --
-- Borrowed Items (borrow_log_id references medical_service_form)
INSERT INTO borrowed_items (borrow_log_id, equipment_id) VALUES
	(1, 2),
	(2, 3);

-- Supplies Used in Clinic Visits
INSERT INTO medical_supplies_used_clinic_visit (medical_item_id, visit_id, quantity) VALUES
	(1, 1, 1),
	(2, 2, 1);

-- Supplies Used in Incidents
INSERT INTO medical_supplies_used_incidents (medical_item_id, incident_id, quantity) VALUES
	(4, 1, 2);

-- Supplies Used in Service Forms
INSERT INTO medical_supplies_used_service_form (medical_item_id, service_form_id, quantity) VALUES
	(3, 1, 1);

-- Staff Involved in Clinic Visits
INSERT INTO involved_staff_clinic_visit (visit_id, staff_id) VALUES
	(1, 2),
	(2, 3);

-- Staff Involved in Incidents
INSERT INTO involved_staff_incidents (incident_id, staff_id) VALUES
	(1, 2),
	(1, 1);

-- Staff Involved in Service Forms
INSERT INTO involved_staff_medical_service_form (service_form_id, staff_id) VALUES
	(1, 1),
	(2, 2);
-- -------------------------------------------------------------------------------------------------------------------------